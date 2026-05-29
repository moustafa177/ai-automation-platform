"""
🧪 اختبار شامل عبر HTTP — تسجيل + إنشاء روبوت + دردشة مع Gemini
يعمل مع السيرفر الشغّال على http://localhost:8000
"""
import sys
import json
import time
import uuid
import urllib.request
import urllib.error

BASE = "http://localhost:8000/api/v1"


def req(method: str, path: str, body: dict = None, token: str = None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
    except Exception as ex:
        return 0, {"error": str(ex)}


# ── 1. تسجيل مستخدم جديد ─────────────────────────────────
slug = f"test-{uuid.uuid4().hex[:6]}"
email = f"test_{uuid.uuid4().hex[:6]}@example.com"

print("\n" + "="*55)
print("  🧪 اختبار Gemini Integration")
print("="*55)

print(f"\n[1] تسجيل مستخدم: {email}")
status, data = req("POST", "/auth/register", {
    "name": "مصطفى اختبار",
    "email": email,
    "password": "Test1234",
    "org_name": "شركة الاختبار",
    "org_slug": slug,
})
print(f"    الحالة: {status}")

if status not in (200, 201):
    print(f"    ❌ فشل التسجيل: {data}")
    sys.exit(1)

token = data.get("data", {}).get("access_token", "")
user_name = data.get("data", {}).get("user", {}).get("name", "—")
print(f"    ✅ نجح! المستخدم: {user_name}")
print(f"    🔑 Token: {token[:40]}...")


# ── 2. إنشاء روبوت ───────────────────────────────────────
print(f"\n[2] إنشاء روبوت جديد")
status, data = req("POST", "/chatbots", {
    "name": "روبوت الاختبار",
    "description": "روبوت للتحقق من Gemini",
    "avatar_emoji": "🤖",
    "system_prompt": "أنت مساعد ذكي ودود. أجب دائماً بالعربية بإيجاز.",
    "model": "models/gemini-2.5-flash",
    "temperature": 0.7,
    "max_tokens": 500,
    "language": "ar",
    "platform": "website",
    "widget_config": {},
}, token=token)
print(f"    الحالة: {status}")

if status not in (200, 201):
    print(f"    ❌ فشل الإنشاء: {data}")
    sys.exit(1)

bot_id  = data["data"]["id"]
api_key = data["data"].get("api_key", "")
print(f"    ✅ نجح! معرّف الروبوت: {bot_id}")
print(f"    🔑 API Key: {api_key[:16]}...")


# ── 3. تفعيل الروبوت ──────────────────────────────────────
print(f"\n[3] تفعيل الروبوت")
status, data = req("POST", f"/chatbots/{bot_id}/activate", token=token)
print(f"    الحالة: {status}")
if status == 200:
    print(f"    ✅ الحالة: {data['data']['status']}")
else:
    print(f"    ⚠️  {data}")


# ── 4. إرسال رسالة ────────────────────────────────────────
print(f"\n[4] إرسال رسالة للروبوت عبر Gemini")
print(f"    السؤال: 'ما هو الذكاء الاصطناعي؟ اشرح بجملتين.'")

status, data = req("POST", f"/chatbots/{bot_id}/chat", {
    "message": "ما هو الذكاء الاصطناعي؟ اشرح بجملتين.",
    "session_id": uuid.uuid4().hex,
}, token=token)
print(f"    الحالة: {status}")

if status == 200:
    reply       = data["data"]["reply"]
    in_tok      = data["data"]["input_tokens"]
    out_tok     = data["data"]["output_tokens"]

    is_mock = "يبدو أن خدمة الذكاء الاصطناعي غير متاحة" in reply

    print(f"\n    {'⚠️  رد وهمي (Gemini غير متاح)' if is_mock else '✅ رد حقيقي من Gemini!'}")
    print(f"    📝 الرد: {reply}")
    print(f"    📊 Tokens: دخل={in_tok}, خرج={out_tok}")
else:
    print(f"    ❌ فشل: {data}")
    sys.exit(1)


# ── 5. سؤال ثانٍ (مع تأخير لتجنب rate limit) ─────────────
print(f"\n[5] انتظار 3 ثوانٍ قبل السؤال الثاني...")
time.sleep(3)
print(f"[5] سؤال ثانٍ: 'كيف تساعد الشركات؟'")
status, data = req("POST", f"/chatbots/{bot_id}/chat", {
    "message": "كيف يمكن للذكاء الاصطناعي أن يساعد الشركات الصغيرة؟",
}, token=token)
if status == 200:
    reply = data["data"]["reply"]
    is_mock = "يبدو أن خدمة الذكاء الاصطناعي غير متاحة" in reply
    print(f"    {'⚠️  رد وهمي' if is_mock else '✅ Gemini'}: {reply[:120]}...")
else:
    print(f"    ❌ {data}")


print("\n" + "="*55)
print("  🎉 انتهى الاختبار بنجاح!")
print("="*55 + "\n")
