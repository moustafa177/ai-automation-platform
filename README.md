<div align="center">

# 🧠 منصة الذكاء — AI Platform

### منصة متكاملة للذكاء الاصطناعي والأتمتة الرقمية للشركات

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red?logo=python)](https://sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

## نظرة عامة

**منصة الذكاء** هي منصة متقدمة للذكاء الاصطناعي والأتمتة الرقمية، تقدم حلولاً تقنية ذكية مصممة لرفع كفاءة الأعمال وتحسين الأداء التشغيلي داخل الشركات. توفر المنصة أدوات متطورة لتحليل البيانات، مراقبة البنية التحتية والشبكات، إنشاء التقارير الدورية تلقائياً، وإدارة العمليات التشغيلية بكفاءة عالية.

### الخدمات الرئيسية

| الخدمة | الوصف |
|--------|-------|
| 🤖 AI Chatbot Builder | بناء روبوتات محادثة بالذكاء الاصطناعي |
| ⚡ أتمتة العمليات | Workflows ذكية مدمجة مع n8n |
| 📊 التقارير والتحليلات | لوحات بيانات متقدمة مع Chart.js |
| 🌐 مراقبة الشبكة | Network Intelligence في الوقت الفعلي |
| 📚 قاعدة المعرفة | إدارة المستندات والبيانات |
| 👥 إدارة الفريق | نظام صلاحيات متعدد الأدوار (RBAC) |
| 💬 شات داخلي | WebSocket للتواصل الفوري بين الأقسام |
| 💳 نظام الاشتراكات | Starter / Pro / Enterprise |

---

## هيكل المشروع

```
myproject/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── auth.py           # JWT Auth + Multi-tenancy
│   │   │   ├── chatbot.py        # AI Chatbot CRUD
│   │   │   ├── knowledge.py      # Knowledge Base
│   │   │   ├── network.py        # Network Devices
│   │   │   ├── team.py           # Team Management
│   │   │   ├── reports.py        # Analytics Reports
│   │   │   ├── billing.py        # Subscriptions
│   │   │   ├── internal_chat.py  # WebSocket Chat
│   │   │   └── settings.py       # Org Settings
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic Settings
│   │   │   ├── database.py       # Async SQLAlchemy
│   │   │   ├── security.py       # JWT + bcrypt
│   │   │   └── dependencies.py   # FastAPI DI
│   │   ├── models/               # SQLAlchemy Models
│   │   ├── schemas/              # Pydantic Schemas
│   │   ├── services/             # Business Logic
│   │   └── static/               # Frontend SPA
│   │       ├── index.html        # Landing Page
│   │       ├── dashboard.html    # Main Dashboard
│   │       ├── chatbot.html      # Bot Builder
│   │       ├── automation.html   # Workflows
│   │       ├── knowledge.html    # KB Manager
│   │       ├── network.html      # Network Map
│   │       ├── reports.html      # Analytics
│   │       ├── billing.html      # Subscription Plans
│   │       ├── team.html         # Team Manager
│   │       ├── settings.html     # Settings Panel
│   │       ├── actions.html      # Quick Actions
│   │       ├── platform-ui.css   # Design System (31 sections)
│   │       ├── platform-i18n.js  # AR/EN i18n (200+ strings)
│   │       ├── chat-widget.js    # Floating Chat Widget
│   │       └── ninja-charts.js   # Chart.js Theme
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

---

## التثبيت والتشغيل

### المتطلبات
- Python 3.11+

### خطوات سريعة

```bash
# استنساخ المشروع
git clone https://github.com/YOUR_USERNAME/ai-platform.git
cd ai-platform/backend

# إعداد البيئة
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد المتغيرات البيئية
cp .env.example .env
# عدّل .env وأضف مفاتيح API

# تشغيل السيرفر
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### روابط الصفحات
```
http://localhost:8000           # الصفحة الرئيسية
http://localhost:8000/dashboard # لوحة التحكم
http://localhost:8000/chatbot   # بناء الروبوتات
http://localhost:8000/reports   # التقارير
http://localhost:8000/billing   # الاشتراكات
http://localhost:8000/docs      # API Documentation
```

---

## API Reference

### Authentication
```http
POST /api/v1/auth/register    # إنشاء حساب + منظمة جديدة
POST /api/v1/auth/login       # تسجيل الدخول
POST /api/v1/auth/refresh     # تجديد Access Token
POST /api/v1/auth/logout      # تسجيل الخروج
GET  /api/v1/auth/me          # بيانات المستخدم الحالي
POST /api/v1/auth/forgot-password
```

### Core APIs
```http
GET|POST /api/v1/chatbots             # إدارة الروبوتات
GET|POST /api/v1/knowledge            # قواعد المعرفة
GET|POST /api/v1/network              # أجهزة الشبكة
GET      /api/v1/reports/summary      # ملخص التقارير
GET      /api/v1/reports/trends       # اتجاهات البيانات
GET      /api/v1/billing/plans        # خطط الاشتراك
POST     /api/v1/billing/upgrade      # ترقية الخطة
GET      /api/v1/chat/channels        # قنوات الشات
WS       /api/v1/chat/ws/{channel_id} # WebSocket
```

---

## الامان

| الميزة | التفاصيل |
|--------|----------|
| JWT Auth | Access (15 min) + Refresh (30 days) في HttpOnly Cookie |
| bcrypt | تشفير كلمات المرور |
| Rate Limiting | Login 10/min · Register 5/min · Forgot 3/min |
| XSS Protection | تعقيم المدخلات + Content-Security |
| Security Headers | X-Frame-Options · X-Content-Type · HSTS (prod) |
| Multi-tenancy | عزل كامل لبيانات كل منظمة بـ org_id |
| RBAC | 4 أدوار: Owner · Admin · Member · Viewer |

---

## التقنيات

**Backend:** FastAPI · SQLAlchemy 2.0 (Async) · SQLite/PostgreSQL · JWT · WebSocket · slowapi

**Frontend:** HTML5 · CSS3 · Vanilla JS · Chart.js 4.4 · Cairo + Inter Fonts

**AI:** Anthropic Claude · Google Gemini

**i18n:** Arabic (RTL) / English (LTR) — تبديل بنقرة واحدة

---

## Overview (English)

**AI Platform** is an advanced AI and digital automation platform providing intelligent solutions to enhance business efficiency and operational performance.

### Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/ai-platform.git
cd ai-platform/backend
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app.main:app --reload
# Open http://localhost:8000
```

### Architecture
- **FastAPI** async backend with JWT multi-tenancy
- **SQLAlchemy 2.0** with async SQLite (dev) / PostgreSQL (prod)
- **WebSocket** real-time internal chat
- **Vanilla SPA** frontend (no framework dependency)
- **AR/EN i18n** with RTL/LTR switching

---

<div align="center">
  Built with FastAPI · SQLAlchemy · Chart.js · Claude AI
</div>
