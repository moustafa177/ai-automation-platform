/**
 * 💬 Internal Chat Widget — شات داخلي مشترك لجميع الصفحات
 * يُحقن تلقائياً عبر <script src="/static/chat-widget.js">
 */
(function () {
  'use strict';

  const API = '/api/v1';
  const POLL_INTERVAL = 4000; // ms — fallback polling when WS disconnects

  // ══════════════════════════════════════════════════════════
  //  CSS Injection
  // ══════════════════════════════════════════════════════════
  const CSS = `
  #cw-btn {
    position:fixed; bottom:28px; left:28px; z-index:9999;
    width:52px; height:52px; border-radius:50%;
    background:linear-gradient(135deg,#6366f1,#8b5cf6);
    box-shadow:0 4px 24px rgba(99,102,241,.55);
    border:none; cursor:pointer; color:#fff; font-size:22px;
    display:flex; align-items:center; justify-content:center;
    transition:.25s; user-select:none;
  }
  #cw-btn:hover { transform:scale(1.08); box-shadow:0 6px 32px rgba(99,102,241,.7); }
  #cw-badge {
    position:absolute; top:-4px; right:-4px;
    background:#ef4444; color:#fff; font-size:10px; font-weight:700;
    width:18px; height:18px; border-radius:50%;
    display:none; align-items:center; justify-content:center;
    border:2px solid #020617;
  }
  #cw-panel {
    position:fixed; bottom:92px; left:28px; z-index:9998;
    width:440px; height:540px; border-radius:16px;
    background:rgba(15,23,42,.95); border:1px solid rgba(99,102,241,.25);
    backdrop-filter:blur(24px); box-shadow:0 20px 60px rgba(0,0,0,.6);
    display:none; flex-direction:column; overflow:hidden;
    animation:cwSlideIn .2s ease;
  }
  @keyframes cwSlideIn {
    from { opacity:0; transform:translateY(12px) scale(.97); }
    to   { opacity:1; transform:none; }
  }
  #cw-header {
    padding:14px 18px; background:rgba(99,102,241,.15);
    border-bottom:1px solid rgba(99,102,241,.2);
    display:flex; align-items:center; gap:10px; flex-shrink:0;
  }
  #cw-header-icon { font-size:20px; }
  #cw-header-title { font-size:14px; font-weight:700; color:#e2e8f0; flex:1; }
  #cw-header-status {
    font-size:10px; color:#22d3ee;
    display:flex; align-items:center; gap:4px;
  }
  .cw-dot { width:7px; height:7px; border-radius:50%; background:#22d3ee; animation:cwPulse 1.8s infinite; }
  @keyframes cwPulse { 0%,100%{opacity:1} 50%{opacity:.4} }
  #cw-close {
    background:none; border:none; color:#94a3b8; font-size:18px;
    cursor:pointer; padding:2px 6px; border-radius:6px; transition:.15s;
  }
  #cw-close:hover { background:rgba(255,255,255,.08); color:#e2e8f0; }
  #cw-body { display:flex; flex:1; overflow:hidden; }
  #cw-channels {
    width:140px; min-width:140px; border-left:1px solid rgba(99,102,241,.15);
    overflow-y:auto; padding:10px 6px; flex-shrink:0;
  }
  #cw-channels::-webkit-scrollbar { width:3px; }
  #cw-channels::-webkit-scrollbar-thumb { background:#334155; border-radius:3px; }
  .cw-ch-label { font-size:9.5px; font-weight:600; color:#64748b; text-transform:uppercase;
    letter-spacing:.6px; padding:6px 6px 3px; }
  .cw-ch-item {
    display:flex; align-items:center; gap:7px; padding:8px 8px; border-radius:9px;
    cursor:pointer; color:#94a3b8; font-size:12.5px; transition:.15s; margin-bottom:2px;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  }
  .cw-ch-item:hover { background:rgba(99,102,241,.12); color:#e2e8f0; }
  .cw-ch-item.active { background:linear-gradient(135deg,rgba(99,102,241,.28),rgba(139,92,246,.18));
    color:#fff; border:1px solid rgba(99,102,241,.3); }
  .cw-ch-icon { font-size:14px; flex-shrink:0; }
  .cw-ch-unread {
    margin-right:auto; background:#6366f1; color:#fff; font-size:9px;
    font-weight:700; min-width:16px; height:16px; border-radius:8px;
    display:none; align-items:center; justify-content:center; padding:0 3px;
  }
  #cw-area { flex:1; display:flex; flex-direction:column; overflow:hidden; }
  #cw-ch-name {
    padding:10px 14px 8px; font-size:12px; font-weight:600;
    color:#94a3b8; border-bottom:1px solid rgba(99,102,241,.1); flex-shrink:0;
    display:flex; align-items:center; gap:6px;
  }
  #cw-messages {
    flex:1; overflow-y:auto; padding:12px 14px;
    display:flex; flex-direction:column; gap:8px;
  }
  #cw-messages::-webkit-scrollbar { width:3px; }
  #cw-messages::-webkit-scrollbar-thumb { background:#334155; border-radius:3px; }
  .cw-msg { display:flex; gap:8px; align-items:flex-start; }
  .cw-msg.own { flex-direction:row-reverse; }
  .cw-av {
    width:30px; height:30px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,#6366f1,#8b5cf6);
    display:flex; align-items:center; justify-content:center;
    font-size:13px; font-weight:700; color:#fff;
  }
  .cw-bubble {
    max-width:72%; padding:8px 12px; border-radius:12px;
    font-size:12.5px; line-height:1.5; color:#e2e8f0;
    background:rgba(30,41,59,.9); border:1px solid rgba(99,102,241,.15);
    word-break:break-word;
  }
  .cw-msg.own .cw-bubble {
    background:linear-gradient(135deg,rgba(99,102,241,.35),rgba(139,92,246,.25));
    border-color:rgba(99,102,241,.35);
  }
  .cw-meta { font-size:10px; color:#475569; margin-top:3px; }
  .cw-sys {
    text-align:center; font-size:11px; color:#475569;
    padding:4px; font-style:italic;
  }
  .cw-empty {
    flex:1; display:flex; flex-direction:column; align-items:center;
    justify-content:center; color:#475569; font-size:13px; gap:8px;
  }
  .cw-empty-icon { font-size:36px; opacity:.4; }
  #cw-input-area {
    padding:10px 12px; border-top:1px solid rgba(99,102,241,.15);
    display:flex; gap:8px; align-items:center; flex-shrink:0;
  }
  #cw-input {
    flex:1; background:rgba(30,41,59,.7); border:1px solid rgba(99,102,241,.2);
    border-radius:10px; padding:8px 12px; color:#e2e8f0; font-size:13px;
    outline:none; transition:.15s; font-family:inherit; direction:rtl;
  }
  #cw-input:focus { border-color:rgba(99,102,241,.5); background:rgba(30,41,59,.95); }
  #cw-input::placeholder { color:#475569; }
  #cw-send {
    width:36px; height:36px; border-radius:10px;
    background:linear-gradient(135deg,#6366f1,#8b5cf6);
    border:none; cursor:pointer; color:#fff; font-size:16px;
    display:flex; align-items:center; justify-content:center; transition:.2s;
    flex-shrink:0;
  }
  #cw-send:hover { transform:scale(1.06); }
  #cw-send:disabled { opacity:.4; cursor:not-allowed; transform:none; }
  .cw-login-note {
    padding:20px; text-align:center; color:#64748b; font-size:12.5px; line-height:1.7;
  }
  .cw-login-note a { color:#6366f1; text-decoration:none; }
  `;

  // ══════════════════════════════════════════════════════════
  //  HTML Injection
  // ══════════════════════════════════════════════════════════
  const HTML = `
  <button id="cw-btn" title="الشات الداخلي">
    💬
    <span id="cw-badge"></span>
  </button>
  <div id="cw-panel">
    <div id="cw-header">
      <span id="cw-header-icon">💬</span>
      <span id="cw-header-title">الشات الداخلي</span>
      <span id="cw-header-status"><span class="cw-dot"></span> متصل</span>
      <button id="cw-close">✕</button>
    </div>
    <div id="cw-body">
      <div id="cw-channels">
        <div class="cw-ch-label">القنوات</div>
        <div id="cw-ch-list"></div>
      </div>
      <div id="cw-area">
        <div id="cw-ch-name"><span id="cw-ch-icon">🏠</span><span id="cw-ch-title">عام</span></div>
        <div id="cw-messages">
          <div class="cw-empty">
            <div class="cw-empty-icon">💬</div>
            <div>اختر قناة للبدء</div>
          </div>
        </div>
        <div id="cw-input-area">
          <input id="cw-input" placeholder="اكتب رسالة..." autocomplete="off" />
          <button id="cw-send">↑</button>
        </div>
      </div>
    </div>
  </div>
  `;

  // ══════════════════════════════════════════════════════════
  //  State
  // ══════════════════════════════════════════════════════════
  let state = {
    open:       false,
    channels:   [],
    activeId:   null,
    messages:   {},     // channel_id → []
    unread:     {},     // channel_id → count
    ws:         null,
    pollTimer:  null,
    myUserId:   null,
  };

  // ══════════════════════════════════════════════════════════
  //  Helpers
  // ══════════════════════════════════════════════════════════
  const tok  = () => localStorage.getItem('access_token') || '';
  const headers = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${tok()}` });

  function parseJwt(token) {
    try {
      return JSON.parse(atob(token.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));
    } catch { return null; }
  }

  function timeAgo(iso) {
    const d = new Date(iso);
    const diff = Math.floor((Date.now() - d) / 1000);
    if (diff < 60) return 'الآن';
    if (diff < 3600) return `${Math.floor(diff / 60)} د`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} س`;
    return d.toLocaleDateString('ar-SA');
  }

  function initials(name) {
    return name ? name.charAt(0).toUpperCase() : '?';
  }

  // ══════════════════════════════════════════════════════════
  //  Auth check
  // ══════════════════════════════════════════════════════════
  function checkAuth() {
    const t = tok();
    if (!t) return false;
    const p = parseJwt(t);
    if (!p || (p.exp && p.exp * 1000 < Date.now())) return false;
    state.myUserId = p.sub;
    return true;
  }

  // ══════════════════════════════════════════════════════════
  //  API calls
  // ══════════════════════════════════════════════════════════
  async function fetchChannels() {
    try {
      const r = await fetch(`${API}/chat/channels`, { headers: headers() });
      if (!r.ok) return;
      const d = await r.json();
      state.channels = d.data || [];
      renderChannels();
      if (state.channels.length && !state.activeId) {
        selectChannel(state.channels[0].id);
      }
    } catch (e) { console.debug('[cw] fetchChannels error', e); }
  }

  async function fetchMessages(channelId) {
    try {
      const r = await fetch(`${API}/chat/channels/${channelId}/messages?limit=60`, { headers: headers() });
      if (!r.ok) return;
      const d = await r.json();
      state.messages[channelId] = d.data || [];
      if (state.activeId === channelId) renderMessages();
    } catch (e) { console.debug('[cw] fetchMessages error', e); }
  }

  async function sendMessage() {
    const input = document.getElementById('cw-input');
    const content = input.value.trim();
    if (!content || !state.activeId) return;

    input.value = '';
    document.getElementById('cw-send').disabled = true;

    try {
      const r = await fetch(`${API}/chat/channels/${state.activeId}/messages`, {
        method:  'POST',
        headers: headers(),
        body:    JSON.stringify({ content }),
      });
      if (r.ok) {
        const d = await r.json();
        addMessage(state.activeId, d.data);
        scrollToBottom();
      }
    } catch (e) { console.debug('[cw] send error', e); }
    finally {
      document.getElementById('cw-send').disabled = false;
      input.focus();
    }
  }

  // ══════════════════════════════════════════════════════════
  //  WebSocket
  // ══════════════════════════════════════════════════════════
  function connectWS(channelId) {
    if (state.ws) { try { state.ws.close(); } catch {} }
    if (!channelId || !tok()) return;

    const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${proto}//${location.host}${API}/chat/ws/${channelId}?token=${encodeURIComponent(tok())}`;

    try {
      const ws = new WebSocket(url);
      state.ws = ws;

      ws.onopen = () => {
        clearInterval(state.pollTimer);
        updateStatus(true);
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === 'message') {
            const { channel_id, message } = data;
            addMessage(channel_id, message);
            if (channel_id === state.activeId) scrollToBottom();
            else incrementUnread(channel_id);
          }
        } catch {}
      };

      ws.onclose = () => {
        updateStatus(false);
        // Fallback polling
        state.pollTimer = setInterval(() => {
          if (state.activeId) fetchMessages(state.activeId);
        }, POLL_INTERVAL);
      };

      ws.onerror = () => ws.close();
    } catch {
      updateStatus(false);
    }
  }

  function updateStatus(online) {
    const s = document.getElementById('cw-header-status');
    if (!s) return;
    s.innerHTML = online
      ? '<span class="cw-dot"></span> متصل'
      : '<span class="cw-dot" style="background:#f59e0b"></span> غير متصل';
    s.style.color = online ? '#22d3ee' : '#f59e0b';
  }

  // ══════════════════════════════════════════════════════════
  //  Render
  // ══════════════════════════════════════════════════════════
  function renderChannels() {
    const list = document.getElementById('cw-ch-list');
    if (!list) return;

    list.innerHTML = state.channels.map(ch => `
      <div class="cw-ch-item ${ch.id === state.activeId ? 'active' : ''}"
           data-id="${ch.id}" data-icon="${ch.icon}" data-name="${ch.name}">
        <span class="cw-ch-icon">${ch.icon}</span>
        <span style="overflow:hidden;text-overflow:ellipsis">${ch.name}</span>
        <span class="cw-ch-unread" id="unread-${ch.id}"
              style="display:${(state.unread[ch.id]||0)>0?'flex':'none'}">
          ${state.unread[ch.id]||''}
        </span>
      </div>
    `).join('');

    list.querySelectorAll('.cw-ch-item').forEach(el => {
      el.addEventListener('click', () => selectChannel(el.dataset.id));
    });
  }

  function renderMessages() {
    const container = document.getElementById('cw-messages');
    if (!container) return;

    const msgs = state.messages[state.activeId] || [];

    if (msgs.length === 0) {
      container.innerHTML = `
        <div class="cw-empty">
          <div class="cw-empty-icon">💬</div>
          <div>لا توجد رسائل بعد — كن أول من يكتب!</div>
        </div>`;
      return;
    }

    container.innerHTML = msgs.map(m => buildMsgHTML(m)).join('');
    scrollToBottom();
  }

  function buildMsgHTML(m) {
    const isOwn = m.user_id === state.myUserId;
    if (m.message_type === 'system') {
      return `<div class="cw-sys">${m.content}</div>`;
    }
    return `
      <div class="cw-msg${isOwn ? ' own' : ''}">
        <div class="cw-av">${initials(m.user_name)}</div>
        <div>
          ${!isOwn ? `<div style="font-size:10px;color:#94a3b8;margin-bottom:3px">${m.user_name}</div>` : ''}
          <div class="cw-bubble">${escapeHtml(m.content)}</div>
          <div class="cw-meta">${timeAgo(m.created_at)}</div>
        </div>
      </div>`;
  }

  function addMessage(channelId, msg) {
    if (!state.messages[channelId]) state.messages[channelId] = [];
    // avoid duplicates
    if (!state.messages[channelId].find(m => m.id === msg.id)) {
      state.messages[channelId].push(msg);
    }
    if (state.activeId === channelId) renderMessages();
  }

  function incrementUnread(channelId) {
    state.unread[channelId] = (state.unread[channelId] || 0) + 1;
    updateBadge();
    const el = document.getElementById(`unread-${channelId}`);
    if (el) { el.textContent = state.unread[channelId]; el.style.display = 'flex'; }
  }

  function updateBadge() {
    const total = Object.values(state.unread).reduce((s, v) => s + v, 0);
    const badge = document.getElementById('cw-badge');
    if (!badge) return;
    badge.textContent = total > 9 ? '9+' : total;
    badge.style.display = total > 0 ? 'flex' : 'none';
  }

  function scrollToBottom() {
    const c = document.getElementById('cw-messages');
    if (c) c.scrollTop = c.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
              .replace(/"/g,'&quot;').replace(/\n/g,'<br>');
  }

  // ══════════════════════════════════════════════════════════
  //  Channel selection
  // ══════════════════════════════════════════════════════════
  function selectChannel(id) {
    const ch = state.channels.find(c => c.id === id);
    if (!ch) return;

    state.activeId = id;
    state.unread[id] = 0;

    // Update header
    const icon  = document.getElementById('cw-ch-icon');
    const title = document.getElementById('cw-ch-title');
    if (icon)  icon.textContent  = ch.icon;
    if (title) title.textContent = ch.name;

    // Update channel list active state
    renderChannels();
    updateBadge();

    // Load messages (cache or fetch)
    if (state.messages[id]) {
      renderMessages();
    } else {
      const container = document.getElementById('cw-messages');
      if (container) container.innerHTML = `
        <div class="cw-empty"><div class="cw-empty-icon" style="animation:cwPulse 1s infinite">⏳</div><div>جار التحميل...</div></div>`;
      fetchMessages(id);
    }

    // WS
    connectWS(id);
  }

  // ══════════════════════════════════════════════════════════
  //  Toggle open/close
  // ══════════════════════════════════════════════════════════
  function openPanel() {
    state.open = true;
    const panel = document.getElementById('cw-panel');
    panel.style.display = 'flex';

    const messagesArea = document.getElementById('cw-messages');

    if (!checkAuth()) {
      // Show login prompt
      const chList = document.getElementById('cw-ch-list');
      if (chList) chList.innerHTML = '';
      if (messagesArea) messagesArea.innerHTML = `
        <div class="cw-login-note">
          🔐 سجّل الدخول أولاً للوصول إلى الشات الداخلي.<br><br>
          <a href="/">تسجيل الدخول</a>
        </div>`;
      return;
    }

    if (state.channels.length === 0) fetchChannels();
    else if (state.activeId) renderMessages();
  }

  function closePanel() {
    state.open = false;
    document.getElementById('cw-panel').style.display = 'none';
    clearInterval(state.pollTimer);
    if (state.ws) { try { state.ws.close(); } catch {} state.ws = null; }
  }

  // ══════════════════════════════════════════════════════════
  //  Init
  // ══════════════════════════════════════════════════════════
  function init() {
    // Inject CSS
    const style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    // Inject HTML
    const wrap = document.createElement('div');
    wrap.innerHTML = HTML;
    document.body.appendChild(wrap);

    // Events
    document.getElementById('cw-btn').addEventListener('click', () => {
      state.open ? closePanel() : openPanel();
    });
    document.getElementById('cw-close').addEventListener('click', closePanel);

    document.getElementById('cw-send').addEventListener('click', sendMessage);
    document.getElementById('cw-input').addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });

    // Keyboard shortcut: Ctrl+Shift+C
    document.addEventListener('keydown', e => {
      if (e.ctrlKey && e.shiftKey && e.key === 'C') {
        state.open ? closePanel() : openPanel();
      }
    });
  }

  // Wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
