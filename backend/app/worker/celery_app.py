"""
⚙️ Celery — المهام الخلفية والجدولة
"""
from celery import Celery

from app.core.config import settings

# إنشاء تطبيق Celery
celery_app = Celery(
    "platform_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.worker.tasks.ai_tasks",
        "app.worker.tasks.automation_tasks",
        "app.worker.tasks.report_tasks",
        "app.worker.tasks.network_tasks",
    ],
)

# الإعدادات
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Riyadh",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

# المهام الدورية
celery_app.conf.beat_schedule = {
    # فحص الأجهزة الشبكية كل دقيقة
    "network-polling": {
        "task": "app.worker.tasks.network_tasks.poll_devices",
        "schedule": 60.0,
    },
    # تنظيف جلسات المحادثة القديمة يومياً
    "cleanup-old-sessions": {
        "task": "app.worker.tasks.ai_tasks.cleanup_old_sessions",
        "schedule": 86400.0,
    },
}
