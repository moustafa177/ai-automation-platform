"""
🧪 اختبارات نظام المصادقة
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRegister:
    """اختبارات التسجيل"""

    async def test_register_success(self, client: AsyncClient, sample_register_data):
        """تسجيل ناجح لمستخدم جديد"""
        response = await client.post("/api/v1/auth/register", json=sample_register_data)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == sample_register_data["email"]

    async def test_register_duplicate_email(self, client: AsyncClient, sample_register_data):
        """رفض البريد المكرر"""
        await client.post("/api/v1/auth/register", json=sample_register_data)
        response = await client.post("/api/v1/auth/register", json=sample_register_data)
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient, sample_register_data):
        """رفض كلمة المرور الضعيفة"""
        sample_register_data["password"] = "weakpass"
        response = await client.post("/api/v1/auth/register", json=sample_register_data)
        assert response.status_code == 422

    async def test_register_invalid_slug(self, client: AsyncClient, sample_register_data):
        """رفض الـ slug غير الصالح"""
        sample_register_data["org_slug"] = "Invalid Slug!"
        response = await client.post("/api/v1/auth/register", json=sample_register_data)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """اختبارات تسجيل الدخول"""

    async def test_login_success(self, client: AsyncClient, sample_register_data):
        """تسجيل دخول ناجح"""
        await client.post("/api/v1/auth/register", json=sample_register_data)
        response = await client.post("/api/v1/auth/login", json={
            "email": sample_register_data["email"],
            "password": sample_register_data["password"],
        })
        assert response.status_code == 200
        assert "access_token" in response.json()["data"]

    async def test_login_wrong_password(self, client: AsyncClient, sample_register_data):
        """رفض كلمة المرور الخاطئة"""
        await client.post("/api/v1/auth/register", json=sample_register_data)
        response = await client.post("/api/v1/auth/login", json={
            "email": sample_register_data["email"],
            "password": "WrongPass123",
        })
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """رفض مستخدم غير موجود"""
        response = await client.post("/api/v1/auth/login", json={
            "email": "ghost@test.com",
            "password": "TestPass123",
        })
        assert response.status_code == 401


@pytest.mark.asyncio
class TestProtectedRoutes:
    """اختبارات المسارات المحمية"""

    async def test_get_me_authenticated(self, client: AsyncClient, sample_register_data):
        """جلب بيانات المستخدم بعد تسجيل الدخول"""
        register_resp = await client.post("/api/v1/auth/register", json=sample_register_data)
        token = register_resp.json()["data"]["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["email"] == sample_register_data["email"]

    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """رفض الوصول بدون token"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
