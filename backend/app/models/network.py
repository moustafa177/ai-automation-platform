"""
📡 نماذج Network Intelligence
"""
import enum
from sqlalchemy import Boolean, Float, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.models.base import BaseModel


class DeviceType(str, enum.Enum):
    ROUTER    = "router"
    SWITCH    = "switch"
    FIREWALL  = "firewall"
    SERVER    = "server"
    AP        = "ap"          # Access Point
    CAMERA    = "camera"
    PRINTER   = "printer"
    OTHER     = "other"


class DeviceStatus(str, enum.Enum):
    UP        = "up"
    DOWN      = "down"
    DEGRADED  = "degraded"
    UNKNOWN   = "unknown"


class NetworkDevice(BaseModel):
    __tablename__ = "network_devices"

    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )

    # Identity
    name:        Mapped[str]            = mapped_column(String(255), nullable=False)
    hostname:    Mapped[str | None]     = mapped_column(String(255))
    ip_address:  Mapped[str]            = mapped_column(String(45),  nullable=False)
    mac_address: Mapped[str | None]     = mapped_column(String(17))
    device_type: Mapped[DeviceType]     = mapped_column(String(20), default=DeviceType.OTHER)
    vendor:      Mapped[str | None]     = mapped_column(String(100))
    model:       Mapped[str | None]     = mapped_column(String(100))
    location:    Mapped[str | None]     = mapped_column(String(255))
    description: Mapped[str | None]     = mapped_column(Text)

    # Network
    port:        Mapped[int | None]     = mapped_column(Integer)   # SNMP / SSH port
    snmp_community: Mapped[str | None]  = mapped_column(String(100))
    tags:        Mapped[dict]           = mapped_column(JSON, default=list)

    # Status & Metrics
    status:      Mapped[DeviceStatus]   = mapped_column(String(20), default=DeviceStatus.UNKNOWN)
    is_active:   Mapped[bool]           = mapped_column(Boolean, default=True)

    # Latest metrics (refreshed periodically)
    latency_ms:      Mapped[float | None]  = mapped_column(Float)
    packet_loss_pct: Mapped[float | None]  = mapped_column(Float, default=0.0)
    uptime_pct:      Mapped[float | None]  = mapped_column(Float, default=100.0)
    cpu_pct:         Mapped[float | None]  = mapped_column(Float)
    mem_pct:         Mapped[float | None]  = mapped_column(Float)

    # Topology
    parent_id:   Mapped[str | None]     = mapped_column(String(36))   # parent device id
    x_pos:       Mapped[float]          = mapped_column(Float, default=0.0)
    y_pos:       Mapped[float]          = mapped_column(Float, default=0.0)
