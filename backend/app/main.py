"""FastAPI Application — AI Platform"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

logger = structlog.get_logger()
STATIC_DIR = Path(__file__).parent / "static"

# ── Rate Limiter ───────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ── Security Headers Middleware ────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    يضيف HTTP Security Headers لكل response
    يمنع: Clickjacking, MIME sniffing, XSS
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # auto-create tables in dev mode
    if settings.is_development:
        from app.core.database import engine
        from app.models import base  # noqa: registers all models
        import app.models.organization  # noqa
        import app.models.user         # noqa
        import app.models.subscription # noqa
        import app.models.chatbot      # noqa
        import app.models.knowledge    # noqa
        import app.models.network      # noqa
        import app.models.internal_chat # noqa
        from app.core.database import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("AI Platform starting", env=settings.APP_ENV)
    yield
    logger.info("AI Platform shutting down")


# ── تعطيل Docs في الإنتاج ─────────────────────────────────
_docs_url   = None if settings.is_production else "/docs"
_redoc_url  = None if settings.is_production else "/redoc"
_openapi_url = None if settings.is_production else f"{settings.API_V1_PREFIX}/openapi.json"

app = FastAPI(
    title=settings.APP_NAME,
    description="AI & Automation Platform for Businesses",
    version="0.1.0",
    openapi_url=_openapi_url,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    lifespan=lifespan,
)

# ── Middlewares ───────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin",
                   "X-Requested-With"],
)

# ── خدمة الملفات الثابتة ──────────────────────────────────
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── معالجة الأخطاء ────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(l) for l in e["loc"] if l != "body"), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": {"code": "VALIDATION_ERROR",
                                              "message": "البيانات المدخلة غير صحيحة",
                                              "details": errors}},
    )


@app.exception_handler(Exception)
async def general_handler(request: Request, exc: Exception):
    logger.error("Unhandled error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {"code": "INTERNAL_ERROR",
                                              "message": "حدث خطأ داخلي"}},
    )


# ── Routes ────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "healthy", "app": settings.APP_NAME, "version": "0.1.0"}


@app.get("/", include_in_schema=False)
async def landing():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "AI Platform API", "docs": "/docs"}


@app.get("/dashboard", include_in_schema=False)
async def dashboard():
    dash = STATIC_DIR / "dashboard.html"
    if dash.exists():
        return FileResponse(str(dash))
    return {"message": "Dashboard not found"}


@app.get("/chatbot", include_in_schema=False)
async def chatbot_page():
    page = STATIC_DIR / "chatbot.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Chatbot page not found"}


@app.get("/automation", include_in_schema=False)
async def automation_page():
    page = STATIC_DIR / "automation.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Automation page not found"}


@app.get("/knowledge", include_in_schema=False)
async def knowledge_page():
    page = STATIC_DIR / "knowledge.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Knowledge page not found"}


@app.get("/network", include_in_schema=False)
async def network_page():
    page = STATIC_DIR / "network.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Network page not found"}


@app.get("/actions", include_in_schema=False)
async def actions_page():
    page = STATIC_DIR / "actions.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Actions page not found"}


@app.get("/team", include_in_schema=False)
async def team_page():
    page = STATIC_DIR / "team.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Team page not found"}


@app.get("/settings", include_in_schema=False)
async def settings_page():
    page = STATIC_DIR / "settings.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Settings page not found"}


@app.get("/reports", include_in_schema=False)
async def reports_page():
    page = STATIC_DIR / "reports.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Reports page not found"}


@app.get("/billing", include_in_schema=False)
async def billing_page():
    page = STATIC_DIR / "billing.html"
    if page.exists():
        return FileResponse(str(page))
    return {"message": "Billing page not found"}


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
