/**
 * ╔══════════════════════════════════════════════════════════╗
 * ║   Platform i18n — Arabic ↔ English                      ║
 * ║   Handles: text, direction, font, localStorage          ║
 * ╚══════════════════════════════════════════════════════════╝
 */
(function () {
  'use strict';

  /* ═══════════════════════════════════════════════════════
     § 1  TRANSLATION DICTIONARY  (AR → EN)
  ═══════════════════════════════════════════════════════ */
  const T = {
    /* ── Sidebar: Sections ── */
    'الرئيسية':           'Main',
    'الخدمات':            'Services',
    'الإدارة':            'Management',

    /* ── Sidebar: Nav Items ── */
    'لوحة التحكم':        'Dashboard',
    'نظرة عامة':          'Overview',
    'التحليلات':          'Analytics',
    'التقارير':           'Reports',
    'AI Chatbot Builder': 'AI Chatbot Builder',
    'أتمتة العمليات':     'Automation',
    'قاعدة المعرفة':      'Knowledge Base',
    'مراقبة الشبكة':      'Network Monitor',
    'الإجراءات السريعة':  'Quick Actions',
    'الفريق':             'Team',
    'الاشتراكات':         'Billing',
    'الإعدادات':          'Settings',
    'تسجيل الخروج':       'Logout',
    'الفواتير':           'Invoices',

    /* ── Sidebar: User Card ── */
    '⚡ Pro Plan':        '⚡ Pro Plan',

    /* ── Topbar ── */
    'ابحث في المنصة...':  'Search platform...',
    'نظرة عامة':          'Overview',
    '/ لوحة التحكم':      '/ Dashboard',
    'إدارة خطة Pro':      'Manage Pro Plan',
    'الاشتراكات والفواتير': 'Billing & Subscriptions',

    /* ── Dashboard: Welcome ── */
    'مرحباً،':                  'Hello,',
    'خدمة جديدة':               'New Service',
    'ابدأ مشروعاً':              'Start a Project',
    'لديك':                     "You have",
    'روبوتات نشطة':              'active bots',
    'workflow':                 'workflows',
    'يعملان الآن. كل شيء يسير بشكل ممتاز.': 'running now. Everything is going great.',

    /* ── Dashboard: KPI ── */
    'رسالة AI هذا الشهر':        'AI messages this month',
    'الروبوتات النشطة':           'Active Chatbots',
    'Workflows نشطة الآن':        'Active Workflows',
    'جهاز شبكي مراقَب':           'Monitored Devices',

    /* ── Dashboard: Charts ── */
    'نشاط الرسائل':               'Message Activity',
    '7 أيام':                    '7 Days',
    '30 يوم':                    '30 Days',
    '3 أشهر':                    '3 Months',
    'الرسائل الكلية':             'Total Messages',
    'المستخدمون الفريدون':        'Unique Users',

    /* ── Dashboard: Quick Actions ── */
    'إجراءات سريعة':              'Quick Actions',
    'روبوت جديد':                 'New Bot',
    'Workflow':                  'Workflow',
    'تصدير تقرير':               'Export Report',
    'دعوة عضو':                  'Invite Member',

    /* ── Dashboard: Subscription ── */
    'اشتراكك':                   'Your Plan',
    'نشط':                       'Active',
    'ينتهي':                     'Expires',
    'الرسائل':                   'Messages',
    'Workflows':                 'Workflows',
    'ترقية للـ Enterprise':       'Upgrade to Enterprise',

    /* ── Dashboard: Services ── */
    'حالة الخدمات':               'Services Status',
    'تفعيل خدمة':                'Enable Service',
    'روبوتات · 48K رسالة / شهر': 'bots · 48K messages/month',
    'Workflow · n8n مدمج':        'Workflows · n8n integrated',
    'تحليلات متقدمة مع Grafana':  'Advanced analytics with Grafana',
    'جهاز · 1 تنبيه نشط':        'devices · 1 active alert',
    'Analytics Dashboard':       'Analytics Dashboard',
    'Network Intelligence':      'Network Intelligence',
    'قريباً':                    'Coming Soon',

    /* ── Dashboard: Activity ── */
    'آخر النشاطات':               'Recent Activity',
    'عرض الكل':                  'View All',
    'روبوت الدعم':                'Support Bot',
    'أجاب على 42 رسالة':         'answered 42 messages',
    'منذ 3 دقائق':               '3 minutes ago',
    'إرسال تقارير يومية اكتمل':   'Daily report workflow completed',
    'منذ 18 دقيقة':              '18 minutes ago',
    'انقطع الاتصال':             'disconnected',
    'منذ 45 دقيقة':              '45 minutes ago',
    'انضم إلى الفريق':           'joined the team',
    'منذ ساعة':                  '1 hour ago',
    'مزامنة CRM تم تفعيله':       'CRM sync workflow activated',
    'منذ 3 ساعات':               '3 hours ago',

    /* ── Dashboard: Bots ── */
    'الروبوتات النشطة':           'Active Chatbots',
    'روبوت الدعم الفني':          'Support Bot',
    'موقع الويب · Claude AI':     'Website · Claude AI',
    'روبوت المبيعات':             'Sales Bot',
    'واتساب · Claude AI':         'WhatsApp · Claude AI',
    'روبوت HR الداخلي':           'Internal HR Bot',
    'تيليغرام · Claude AI':       'Telegram · Claude AI',
    'رسالة / اليوم':              'messages/day',
    'رسالة اليوم':                'messages today',

    /* ── Dashboard: Network ── */
    'الشبكة':                    'Network',
    'متصل':                      'Connected',
    'أجهزة متصلة':               'Connected Devices',
    'تنبيه نشط':                 'Active Alert',

    /* ── Billing Page ── */
    'الخطة الحالية':              'Current Plan',
    'اشتراك نشط':                'Active Subscription',
    'تجديد تلقائي في':            'Auto-renews on',
    'استخدام الحصة الشهرية':      'Monthly Usage',
    'يتجدد في':                  'Renews on',
    'دورة مايو 2026':            'May 2026 Cycle',
    'اختر خطتك':                 'Choose Your Plan',
    'ترقية أو تخفيض في أي وقت · بدون عقود': 'Upgrade or downgrade anytime · No contracts',
    'شهري':                      'Monthly',
    'سنوي':                      'Yearly',
    'وفر 20%':                   'Save 20%',
    'سجل الفواتير':               'Invoice History',
    'تصدير':                     'Export',
    'طريقة الدفع':               'Payment Method',
    'تغيير':                     'Change',
    'تنتهي':                     'Expires',
    'افتراضية':                  'Default',
    'مدفوعاتك محمية بتشفير SSL 256-bit': 'Payments secured with 256-bit SSL encryption',
    'إلغاء الاشتراك':             'Cancel Subscription',
    'رقم الفاتورة':               'Invoice #',
    'التاريخ':                   'Date',
    'الخطة':                     'Plan',
    'المبلغ':                    'Amount',
    'الحالة':                    'Status',
    'مدفوعة':                    'Paid',
    'مجانية':                    'Free',
    'متأخرة':                    'Overdue',
    'المبتدئ':                   'Starter',
    'الاحترافي':                 'Pro',
    'المؤسسي':                   'Enterprise',
    'للشركات الناشئة':            'For startups',
    'للفرق المحترفة':             'For professional teams',
    'للمؤسسات الكبرى':            'For large enterprises',
    'الميزات المتضمنة':           'Included Features',
    'خطتك الحالية':              'Current Plan',
    'تواصل مع المبيعات':          'Contact Sales',
    'تخفيض للمجاني':              'Downgrade to Free',
    'مجاني':                     'Free',
    'للأبد · بدون بطاقة ائتمان':  'Forever · No credit card',
    'رسالة':                     'message',
    'روبوت':                     'bot',
    'عضو':                       'member',
    'شهر':                       'month',
    'سنة':                       'year',
    'تسعير مخصص':                'Custom Pricing',
    'غير محدود':                 'Unlimited',
    'تواصل معنا للحصول على عرض': 'Contact us for a quote',
    'وفر':                       'Save',
    'يُدفع سنوياً':              '· billed annually',
    'ترقية خطتك':                'Upgrade Your Plan',
    'اختر الخطة التي تناسب احتياجاتك': 'Choose the plan that fits your needs',
    'سيتم إرسال رابط الدفع على بريدك الإلكتروني. يمكنك الإلغاء في أي وقت.':
      'A payment link will be sent to your email. You can cancel anytime.',
    'متابعة الترقية':             'Continue Upgrade',
    'إلغاء':                     'Cancel',
    'ترقية إلى الاحترافي':        'Upgrade to Pro',
    'رسائل':                     'Messages',
    'الروبوتات':                  'Chatbots',
    'الأعضاء':                   'Members',
    'المستندات':                  'Documents',
    'API Calls':                 'API Calls',
    'لكل شهر':                   'per month',
    'لكل شهر · $468/سنة':       'per month · $468/yr',

    /* ── Reports ── */
    'التقارير والإحصاءات':        'Reports & Analytics',
    'تحديث البيانات':             'Refresh Data',
    'تصدير Excel':               'Export Excel',
    'مجموع الرسائل':              'Total Messages',
    'جلسات المحادثة':             'Chat Sessions',
    'متوسط التقييم':              'Avg. Rating',
    'قاعدة المعرفة':              'Knowledge Base',
    'أجهزة الشبكة':               'Network Devices',
    'Uptime الشبكة':             'Network Uptime',
    'اتجاه الرسائل':              'Message Trends',
    'توزيع المنصات':              'Platform Distribution',
    'توزيع اللغات':               'Language Distribution',
    'أداء الروبوتات':             'Bot Performance',
    'آخر النشاطات':               'Recent Activity',
    'مقارنة الأقسام':             'Department Comparison',
    'الروبوت':                   'Bot',
    'المنصة':                    'Platform',
    'الرسائل':                   'Messages',
    'الجلسات':                   'Sessions',
    'معدل الإجابة':               'Response Rate',
    'التقييم':                   'Rating',

    /* ── Common Buttons & Labels ── */
    'حفظ':                       'Save',
    'حفظ التغييرات':              'Save Changes',
    'إضافة':                     'Add',
    'تعديل':                     'Edit',
    'حذف':                       'Delete',
    'تأكيد':                     'Confirm',
    'بحث':                       'Search',
    'تصفية':                     'Filter',
    'مسح':                       'Clear',
    'إغلاق':                     'Close',
    'تفاصيل':                    'Details',
    'عرض':                       'View',
    'رفع':                       'Upload',
    'تنزيل':                     'Download',
    'نسخ':                       'Copy',
    'نشر':                       'Publish',
    'إيقاف':                     'Pause',
    'تشغيل':                     'Start',
    'اختبار':                    'Test',
    'نعم':                       'Yes',
    'لا':                        'No',
    'جديد':                      'New',
    'جديد +':                    'New +',

    /* ── Status ── */
    'نشط':                       'Active',
    'غير نشط':                   'Inactive',
    'معلق':                      'Draft',
    'مكتمل':                     'Completed',
    'فشل':                       'Failed',
    'قيد التشغيل':                'Running',
    'متوقف':                     'Stopped',

    /* ── Settings ── */
    'الإعدادات العامة':           'General Settings',
    'اسم المنظمة':                'Organization Name',
    'الملف الشخصي':               'Profile',
    'الأمان':                    'Security',
    'الإشعارات':                  'Notifications',
    'المظهر':                    'Appearance',
    'الاتصالات':                  'Integrations',
    'تغيير كلمة المرور':          'Change Password',
    'كلمة المرور الحالية':        'Current Password',
    'كلمة المرور الجديدة':        'New Password',
    'تأكيد كلمة المرور':          'Confirm Password',
    'حفظ التغييرات':              'Save Changes',
    'منطقة الخطر':               'Danger Zone',
    'حذف المنظمة':               'Delete Organization',

    /* ── Team ── */
    'أعضاء الفريق':               'Team Members',
    'دعوة عضو جديد':             'Invite New Member',
    'البريد الإلكتروني':          'Email',
    'الدور':                     'Role',
    'تاريخ الانضمام':             'Join Date',
    'آخر نشاط':                  'Last Active',
    'مالك':                      'Owner',
    'مشرف':                      'Admin',
    'عضو':                       'Member',
    'مشاهد':                     'Viewer',
    'دعوة':                      'Invite',

    /* ── Network ── */
    'مراقبة الشبكة':              'Network Monitor',
    'الأجهزة':                   'Devices',
    'التنبيهات':                  'Alerts',
    'إضافة جهاز':                'Add Device',
    'الحالة':                    'Status',
    'عنوان IP':                  'IP Address',
    'آخر فحص':                   'Last Check',
    'زمن الاستجابة':              'Latency',
    'متصل':                      'Online',
    'غير متصل':                  'Offline',

    /* ── Automation ── */
    'Workflows':                 'Workflows',
    'إنشاء Workflow':            'Create Workflow',
    'المشغل':                    'Trigger',
    'الإجراء':                   'Action',
    'آخر تشغيل':                 'Last Run',
    'عدد التشغيلات':              'Total Runs',
    'تشغيلات ناجحة':             'Successful Runs',

    /* ── Knowledge ── */
    'قواعد المعرفة':              'Knowledge Bases',
    'إنشاء قاعدة':               'Create Base',
    'المستندات':                 'Documents',
    'رفع ملف':                   'Upload File',
    'إضافة رابط':                'Add URL',
    'تدريب النموذج':             'Train Model',
    'حجم البيانات':               'Data Size',

    /* ── Page specific ── */
    'إدارة الاشتراك':             'Manage Subscription',
    'دورة مايو 2026':            'May 2026 Cycle',
    'سيتم إرسال رابط الدفع':    'Payment link will be sent',

    /* ── Months ── */
    'يناير':'January','فبراير':'February','مارس':'March',
    'أبريل':'April','مايو':'May','يونيو':'June',
    'يوليو':'July','أغسطس':'August','سبتمبر':'September',
    'أكتوبر':'October','نوفمبر':'November','ديسمبر':'December',

    /* ── Days ── */
    'الأحد':'Sunday','الاثنين':'Monday','الثلاثاء':'Tuesday',
    'الأربعاء':'Wednesday','الخميس':'Thursday','الجمعة':'Friday','السبت':'Saturday',
  };

  /* ═══════════════════════════════════════════════════════
     § 2  STATE
  ═══════════════════════════════════════════════════════ */
  let currentLang = localStorage.getItem('platform_lang') || 'ar';

  /* ═══════════════════════════════════════════════════════
     § 3  TRANSLATE A STRING
  ═══════════════════════════════════════════════════════ */
  function translate(text, toLang) {
    if (!text || !text.trim()) return text;
    const t = text.trim();
    if (toLang === 'en') {
      return T[t] || text;
    } else {
      // en → ar: reverse lookup
      const entry = Object.entries(T).find(([, v]) => v === t);
      return entry ? entry[0] : text;
    }
  }

  /* ═══════════════════════════════════════════════════════
     § 4  WALK DOM & REPLACE TEXT NODES
  ═══════════════════════════════════════════════════════ */
  function translateNode(node, toLang) {
    if (node.nodeType === Node.TEXT_NODE) {
      const original = node.textContent;
      const trimmed  = original.trim();
      if (!trimmed || trimmed.length < 2) return;
      const translated = translate(trimmed, toLang);
      if (translated !== trimmed) {
        node.textContent = original.replace(trimmed, translated);
      }
      return;
    }

    // Skip: script, style, code
    const skip = ['SCRIPT','STYLE','CODE','PRE','INPUT','TEXTAREA','SELECT','CANVAS','SVG'];
    if (skip.includes(node.nodeName)) return;

    // Use data-i18n attribute if available
    if (node.dataset && node.dataset.i18n) {
      const key = node.dataset.i18n;
      node.textContent = toLang === 'en'
        ? (T[key] || key)
        : (Object.entries(T).find(([,v]) => v === key)?.[0] || key);
      return;
    }

    // Translate placeholder
    if (node.placeholder) {
      node.placeholder = translate(node.placeholder, toLang);
    }

    // Translate title attribute
    if (node.title) {
      node.title = translate(node.title, toLang);
    }

    node.childNodes.forEach(child => translateNode(child, toLang));
  }

  /* ═══════════════════════════════════════════════════════
     § 5  APPLY LANGUAGE TO PAGE
  ═══════════════════════════════════════════════════════ */
  function applyLanguage(lang, firstLoad) {
    const html = document.documentElement;

    if (lang === 'en') {
      // Direction & Language
      html.setAttribute('lang', 'en');
      html.setAttribute('dir', 'ltr');

      // Font
      document.body.style.fontFamily = "'Inter', system-ui, sans-serif";

      // Translate all text nodes
      if (!firstLoad) {
        translateNode(document.body, 'en');
      }

      // Update toggle button
      const btn = document.getElementById('i18n-toggle-btn');
      if (btn) {
        btn.innerHTML = `<span style="font-size:16px">🇸🇦</span> <span style="font-size:12px;font-weight:600">عربي</span>`;
        btn.title = 'Switch to Arabic';
      }

    } else {
      // Arabic
      html.setAttribute('lang', 'ar');
      html.setAttribute('dir', 'rtl');

      document.body.style.fontFamily = "'Cairo', system-ui, sans-serif";

      if (!firstLoad) {
        // Reload page to restore Arabic (simpler than reverse translation)
        window.location.reload();
        return;
      }

      const btn = document.getElementById('i18n-toggle-btn');
      if (btn) {
        btn.innerHTML = `<span style="font-size:16px">🇬🇧</span> <span style="font-size:12px;font-weight:600">English</span>`;
        btn.title = 'Switch to English';
      }
    }
  }

  /* ═══════════════════════════════════════════════════════
     § 6  INJECT TOGGLE BUTTON INTO TOPBAR
  ═══════════════════════════════════════════════════════ */
  function injectToggleButton() {
    // Find topbar
    const topbar = document.querySelector('.topbar, .topbar-actions, header.topbar');
    if (!topbar) return;

    // Find tb-right or topbar-actions to append button
    const container = topbar.querySelector('.tb-right, .topbar-actions, .topbar-title');

    const btn = document.createElement('button');
    btn.id = 'i18n-toggle-btn';
    btn.title = currentLang === 'ar' ? 'Switch to English' : 'Switch to Arabic';
    btn.style.cssText = `
      display:inline-flex; align-items:center; gap:5px;
      padding:5px 12px; border-radius:8px;
      border:1px solid #e2e8f0; background:#f8fafc;
      color:#475569; cursor:pointer; font-family:inherit;
      font-size:11.5px; font-weight:600;
      transition:all .18s; white-space:nowrap; flex-shrink:0;
    `;

    if (currentLang === 'ar') {
      btn.innerHTML = `<span style="font-size:16px">🇬🇧</span><span>English</span>`;
    } else {
      btn.innerHTML = `<span style="font-size:16px">🇸🇦</span><span>عربي</span>`;
    }

    btn.addEventListener('mouseenter', () => {
      btn.style.background = '#eff6ff';
      btn.style.borderColor = '#bfdbfe';
      btn.style.color = '#1b6ac9';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.background = '#f8fafc';
      btn.style.borderColor = '#e2e8f0';
      btn.style.color = '#475569';
    });

    btn.addEventListener('click', toggleLanguage);

    if (container) {
      // Insert before last child (usually avatar)
      container.insertBefore(btn, container.lastElementChild);
    } else {
      topbar.appendChild(btn);
    }
  }

  /* ═══════════════════════════════════════════════════════
     § 7  TOGGLE LANGUAGE
  ═══════════════════════════════════════════════════════ */
  function toggleLanguage() {
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    localStorage.setItem('platform_lang', newLang);
    currentLang = newLang;
    applyLanguage(newLang, false);
  }

  /* ═══════════════════════════════════════════════════════
     § 8  LTR LAYOUT FIXES (when switching to English)
  ═══════════════════════════════════════════════════════ */
  function injectLtrStyles() {
    const styleId = 'i18n-ltr-style';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      /* LTR overrides for English mode */
      [dir="ltr"] .sidebar {
        right: auto !important;
        left: 0 !important;
        border-left: none !important;
        border-right: 1px solid rgba(255,255,255,.07) !important;
      }
      [dir="ltr"] .main-wrap, [dir="ltr"] .main {
        margin-right: 0 !important;
        margin-left: var(--sb-w, 252px) !important;
      }
      [dir="ltr"] .nav-link.active {
        border-right: none !important;
        border-left: 2.5px solid #1b6ac9 !important;
      }
      [dir="ltr"] .nav-item.active {
        border-right: none !important;
        border-left: 2px solid #1b6ac9 !important;
      }
      [dir="ltr"] table thead th,
      [dir="ltr"] table tbody td {
        text-align: left !important;
      }
      [dir="ltr"] .topbar .tb-breadcrumb {
        direction: ltr !important;
      }
      [dir="ltr"] input, [dir="ltr"] textarea {
        text-align: left !important;
      }
      /* Keep numbers and code LTR always */
      .inv-id, code, pre, [class*="-ip"], [class*="version"] {
        direction: ltr !important;
        unicode-bidi: embed !important;
      }
    `;
    document.head.appendChild(style);
  }

  /* ═══════════════════════════════════════════════════════
     § 9  INIT
  ═══════════════════════════════════════════════════════ */
  function init() {
    injectLtrStyles();

    // Wait for DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', onReady);
    } else {
      onReady();
    }
  }

  function onReady() {
    injectToggleButton();

    // If saved lang is English, apply immediately
    if (currentLang === 'en') {
      applyLanguage('en', true);
      // Translate after short delay to let page render
      requestAnimationFrame(() => {
        setTimeout(() => translateNode(document.body, 'en'), 50);
      });
    }
  }

  /* ═══════════════════════════════════════════════════════
     § 10  PUBLIC API
  ═══════════════════════════════════════════════════════ */
  window.PlatformI18n = {
    translate,
    toggle: toggleLanguage,
    setLang: (lang) => {
      localStorage.setItem('platform_lang', lang);
      currentLang = lang;
      applyLanguage(lang, false);
    },
    getLang: () => currentLang,
    T,
  };

  init();
})();
