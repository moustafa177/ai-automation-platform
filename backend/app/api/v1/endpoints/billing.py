"""
💳 Billing & Subscription Endpoints
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, status
from app.core.dependencies import CurrentOrgId, CurrentUserPayload, DBSession, AdminOrOwner
from app.schemas.common import APIResponse, MessageResponse
from pydantic import BaseModel

router = APIRouter(prefix="/billing", tags=["💳 الاشتراكات"])

# ── خطط الاشتراك (Static config) ───────────────────────────
PLANS = {
    "starter": {
        "id":           "starter",
        "name":         "Starter",
        "name_ar":      "المبتدئ",
        "price_monthly": 0,
        "price_yearly":  0,
        "color":        "#64748b",
        "icon":         "🌱",
        "popular":      False,
        "limits": {
            "messages":   5_000,
            "chatbots":   1,
            "workflows":  5,
            "members":    2,
            "kb_docs":    50,
            "api_calls":  1_000,
        },
        "features": [
            "1 روبوت محادثة",
            "5,000 رسالة / شهر",
            "5 Workflows",
            "عضوان في الفريق",
            "قاعدة معرفة واحدة",
            "دعم عبر البريد",
        ],
        "missing": [
            "API Access",
            "تحليلات متقدمة",
            "دعم ذو أولوية",
            "تكاملات مخصصة",
        ],
    },
    "pro": {
        "id":           "pro",
        "name":         "Pro",
        "name_ar":      "الاحترافي",
        "price_monthly": 49,
        "price_yearly":  39,
        "color":        "#1b6ac9",
        "icon":         "⚡",
        "popular":      True,
        "limits": {
            "messages":   30_000,
            "chatbots":   10,
            "workflows":  50,
            "members":    10,
            "kb_docs":    500,
            "api_calls":  50_000,
        },
        "features": [
            "10 روبوتات محادثة",
            "30,000 رسالة / شهر",
            "50 Workflows",
            "10 أعضاء في الفريق",
            "قواعد معرفة متعددة",
            "API Access كامل",
            "تحليلات متقدمة",
            "دعم ذو أولوية (24/7)",
            "تكاملات: WhatsApp · Telegram",
            "تصدير التقارير (Excel · PDF)",
        ],
        "missing": [],
    },
    "enterprise": {
        "id":           "enterprise",
        "name":         "Enterprise",
        "name_ar":      "المؤسسي",
        "price_monthly": None,
        "price_yearly":  None,
        "color":        "#7c3aed",
        "icon":         "🏢",
        "popular":      False,
        "limits": {
            "messages":   -1,    # unlimited
            "chatbots":   -1,
            "workflows":  -1,
            "members":    -1,
            "kb_docs":    -1,
            "api_calls":  -1,
        },
        "features": [
            "روبوتات ومحادثات غير محدودة",
            "Workflows غير محدودة",
            "أعضاء فريق غير محدودين",
            "مثيل مخصص (Dedicated)",
            "SLA 99.9% Uptime",
            "دعم مخصص + مدير حساب",
            "تكاملات مخصصة",
            "تدريب وإعداد مجاني",
            "عقد SLA + NDA",
            "تقارير مخصصة",
        ],
        "missing": [],
    },
}

# ── Demo: current subscription ─────────────────────────────
DEMO_SUBSCRIPTION = {
    "plan_id":     "pro",
    "status":      "active",
    "billing":     "monthly",
    "period_start": (datetime.now(timezone.utc) - timedelta(days=15)).isoformat(),
    "period_end":   (datetime.now(timezone.utc) + timedelta(days=15)).isoformat(),
    "next_invoice": 49.00,
    "currency":    "USD",
    "usage": {
        "messages":  {"used": 24150, "limit": 30000},
        "chatbots":  {"used": 3,     "limit": 10},
        "workflows": {"used": 12,    "limit": 50},
        "members":   {"used": 4,     "limit": 10},
        "kb_docs":   {"used": 87,    "limit": 500},
        "api_calls": {"used": 12430, "limit": 50000},
    },
}

DEMO_INVOICES = [
    {"id": "INV-2026-005", "date": "2026-05-01", "amount": 49.00, "status": "paid",   "plan": "Pro"},
    {"id": "INV-2026-004", "date": "2026-04-01", "amount": 49.00, "status": "paid",   "plan": "Pro"},
    {"id": "INV-2026-003", "date": "2026-03-01", "amount": 49.00, "status": "paid",   "plan": "Pro"},
    {"id": "INV-2026-002", "date": "2026-02-01", "amount": 49.00, "status": "paid",   "plan": "Pro"},
    {"id": "INV-2026-001", "date": "2026-01-01", "amount":  0.00, "status": "free",   "plan": "Starter"},
]


# ── ① خطط الاشتراك المتاحة ──────────────────────────────────
@router.get("/plans", response_model=APIResponse[dict], summary="خطط الاشتراك")
async def get_plans(payload: CurrentUserPayload):
    return APIResponse(data={"plans": list(PLANS.values())})


# ── ② الاشتراك الحالي ────────────────────────────────────────
@router.get("/subscription", response_model=APIResponse[dict], summary="الاشتراك الحالي")
async def get_subscription(payload: CurrentUserPayload, org_id: CurrentOrgId):
    sub = dict(DEMO_SUBSCRIPTION)
    sub["plan"] = PLANS[sub["plan_id"]]
    return APIResponse(data=sub)


# ── ③ سجل الفواتير ──────────────────────────────────────────
@router.get("/invoices", response_model=APIResponse[list], summary="سجل الفواتير")
async def get_invoices(payload: CurrentUserPayload, org_id: CurrentOrgId):
    return APIResponse(data=DEMO_INVOICES)


# ── ④ ترقية الخطة ────────────────────────────────────────────
class UpgradeRequest(BaseModel):
    plan_id: str
    billing: str = "monthly"   # monthly | yearly

@router.post("/upgrade", response_model=MessageResponse, summary="ترقية الخطة")
async def upgrade_plan(
    data: UpgradeRequest,
    payload: AdminOrOwner,
    org_id: CurrentOrgId,
):
    if data.plan_id not in PLANS:
        raise HTTPException(status_code=400, detail="خطة غير موجودة")

    plan = PLANS[data.plan_id]

    # في الإنتاج: ربط بـ Stripe / Paddle
    return MessageResponse(
        message=f"تم طلب الترقية إلى {plan['name_ar']} ✓ — سيتم إرسال رابط الدفع على بريدك الإلكتروني"
    )


# ── ⑤ إلغاء الاشتراك ────────────────────────────────────────
@router.post("/cancel", response_model=MessageResponse, summary="إلغاء الاشتراك")
async def cancel_subscription(payload: AdminOrOwner, org_id: CurrentOrgId):
    return MessageResponse(
        message="سيتم إلغاء اشتراكك في نهاية فترة الفوترة الحالية. يمكنك الاستمرار باستخدام Pro حتى ذلك الحين."
    )


# ── ⑥ استخدام الحصة ─────────────────────────────────────────
@router.get("/usage", response_model=APIResponse[dict], summary="استخدام الحصة")
async def get_usage(payload: CurrentUserPayload, org_id: CurrentOrgId):
    return APIResponse(data=DEMO_SUBSCRIPTION["usage"])
