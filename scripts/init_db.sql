-- ============================================
-- تهيئة قاعدة البيانات عند أول تشغيل
-- ============================================

-- إنشاء قاعدة بيانات n8n
CREATE DATABASE n8n_db;

-- منح الصلاحيات
GRANT ALL PRIVILEGES ON DATABASE n8n_db TO platform_user;

-- تفعيل امتداد UUID
\c platform_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- للبحث النصي السريع
CREATE EXTENSION IF NOT EXISTS "unaccent";  -- لدعم البحث بدون تشكيل
