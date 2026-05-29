# ── مرحلة البناء ────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# تثبيت أدوات النظام المطلوبة
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Poetry
RUN pip install poetry==1.8.4

# نسخ ملفات المتطلبات
COPY pyproject.toml poetry.lock* ./

# تثبيت المكتبات (بدون dev dependencies)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev

# ── مرحلة التشغيل ───────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# تثبيت مكتبات النظام المطلوبة وقت التشغيل
RUN apt-get update && apt-get install -y \
    libpq5 \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# نسخ المكتبات من مرحلة البناء
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# نسخ كود التطبيق
COPY . .

# فحص صحة الخدمة
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# تشغيل التطبيق
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
