"""📡 Network Intelligence API"""
import asyncio
import random
import uuid

import structlog
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import DBSession, CurrentUserPayload
from app.models.network import NetworkDevice, DeviceStatus
from app.schemas.network import DeviceCreate, DeviceUpdate, DeviceOut

logger = structlog.get_logger()
router = APIRouter(prefix="/network", tags=["Network"])


# ── Helpers ────────────────────────────────────────────────
async def get_device_or_404(dev_id: str, org_id: str, db: AsyncSession) -> NetworkDevice:
    result = await db.execute(
        select(NetworkDevice).where(
            NetworkDevice.id == dev_id,
            NetworkDevice.org_id == org_id,
            NetworkDevice.is_active == True,
        )
    )
    dev = result.scalar_one_or_none()
    if not dev:
        raise HTTPException(404, "الجهاز غير موجود")
    return dev


async def _ping_device(ip: str) -> tuple[float | None, float]:
    """محاكاة Ping — يُستبدل بـ icmplib في الإنتاج"""
    await asyncio.sleep(0.05)
    # simulate real-ish values
    if ip.startswith("192.168.") or ip.startswith("10."):
        base = random.uniform(1, 12)
    else:
        base = random.uniform(15, 80)
    loss = random.choices([0.0, 0.0, 0.0, 2.0, 5.0, 100.0],
                          weights=[60, 15, 10, 8, 5, 2])[0]
    return (None if loss == 100.0 else round(base + random.uniform(-2, 4), 2), loss)


# ══════════════════════════════════════════════════════════
# DEVICES CRUD
# ══════════════════════════════════════════════════════════

@router.get("", response_model=dict)
async def list_devices(payload: CurrentUserPayload, db: DBSession):
    result = await db.execute(
        select(NetworkDevice)
        .where(NetworkDevice.org_id == payload["org_id"], NetworkDevice.is_active == True)
        .order_by(NetworkDevice.created_at.desc())
    )
    devices = result.scalars().all()
    up    = sum(1 for d in devices if d.status == DeviceStatus.UP)
    down  = sum(1 for d in devices if d.status == DeviceStatus.DOWN)
    deg   = sum(1 for d in devices if d.status == DeviceStatus.DEGRADED)
    avg_lat = None
    lats = [d.latency_ms for d in devices if d.latency_ms is not None]
    if lats:
        avg_lat = round(sum(lats) / len(lats), 2)
    return {
        "success": True,
        "data": [DeviceOut.model_validate(d).model_dump() for d in devices],
        "stats": {"total": len(devices), "up": up, "down": down,
                  "degraded": deg, "avg_latency": avg_lat},
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_device(data: DeviceCreate, payload: CurrentUserPayload, db: DBSession):
    dev = NetworkDevice(
        org_id=payload["org_id"],
        **data.model_dump(),
    )
    db.add(dev)
    await db.commit()
    await db.refresh(dev)
    logger.info("device_created", id=dev.id, ip=dev.ip_address)
    return {"success": True, "data": DeviceOut.model_validate(dev).model_dump()}


@router.get("/{dev_id}", response_model=dict)
async def get_device(dev_id: str, payload: CurrentUserPayload, db: DBSession):
    dev = await get_device_or_404(dev_id, payload["org_id"], db)
    return {"success": True, "data": DeviceOut.model_validate(dev).model_dump()}


@router.put("/{dev_id}", response_model=dict)
async def update_device(
    dev_id: str, data: DeviceUpdate,
    payload: CurrentUserPayload, db: DBSession,
):
    dev = await get_device_or_404(dev_id, payload["org_id"], db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(dev, field, value)
    await db.commit()
    await db.refresh(dev)
    return {"success": True, "data": DeviceOut.model_validate(dev).model_dump()}


@router.delete("/{dev_id}", response_model=dict)
async def delete_device(dev_id: str, payload: CurrentUserPayload, db: DBSession):
    dev = await get_device_or_404(dev_id, payload["org_id"], db)
    dev.is_active = False
    await db.commit()
    return {"success": True, "message": "تم حذف الجهاز"}


# ══════════════════════════════════════════════════════════
# MONITORING
# ══════════════════════════════════════════════════════════

@router.post("/{dev_id}/ping", response_model=dict)
async def ping_device(dev_id: str, payload: CurrentUserPayload, db: DBSession):
    """اختبار Ping للجهاز وتحديث حالته"""
    dev = await get_device_or_404(dev_id, payload["org_id"], db)
    latency, loss = await _ping_device(dev.ip_address)

    dev.latency_ms      = latency
    dev.packet_loss_pct = loss

    if latency is None:
        dev.status = DeviceStatus.DOWN
    elif loss > 10 or latency > 200:
        dev.status = DeviceStatus.DEGRADED
    else:
        dev.status = DeviceStatus.UP

    await db.commit()
    return {
        "success": True,
        "data": {
            "ip": dev.ip_address, "latency_ms": latency,
            "packet_loss": loss, "status": dev.status,
        }
    }


@router.post("/scan/ping-all", response_model=dict)
async def ping_all(payload: CurrentUserPayload, db: DBSession):
    """اختبار جميع الأجهزة دفعة واحدة"""
    result = await db.execute(
        select(NetworkDevice).where(
            NetworkDevice.org_id == payload["org_id"],
            NetworkDevice.is_active == True,
        )
    )
    devices = result.scalars().all()
    results = []
    for dev in devices:
        latency, loss = await _ping_device(dev.ip_address)
        dev.latency_ms      = latency
        dev.packet_loss_pct = loss
        dev.status = (
            DeviceStatus.DOWN     if latency is None else
            DeviceStatus.DEGRADED if loss > 10 or latency > 200 else
            DeviceStatus.UP
        )
        results.append({"id": dev.id, "name": dev.name,
                        "latency_ms": latency, "status": dev.status})
    await db.commit()
    return {"success": True, "data": results, "scanned": len(results)}


@router.get("/{dev_id}/history", response_model=dict)
async def device_history(dev_id: str, payload: CurrentUserPayload, db: DBSession):
    """بيانات تاريخية مُحاكاة لرسومات الـ latency"""
    dev = await get_device_or_404(dev_id, payload["org_id"], db)
    base = dev.latency_ms or random.uniform(5, 50)
    points = []
    for i in range(60):   # آخر 60 دقيقة
        jitter = random.uniform(-base * 0.3, base * 0.3)
        spike  = random.choices([0, base * 2], weights=[90, 10])[0]
        points.append(round(max(0.5, base + jitter + spike), 2))
    return {"success": True, "data": {"latency": points, "device": dev.name}}
