import { useState, useEffect, useRef, useCallback, useMemo } from "react";

// ─── API CONFIG ──────────────────────────────────────
const API = "http://localhost:8000";
const SSE_BASE = "http://localhost:8000";

// ─── API CLIENT ──────────────────────────────────────
const api = {
  headers: (token) => ({
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }),
  post: async (path, body, token) => {
    const r = await fetch(`${API}${path}`, {
      method: "POST",
      headers: api.headers(token),
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.detail || "Request failed");
    }
    return r.json();
  },
  get: async (path, token) => {
    const r = await fetch(`${API}${path}`, {
      headers: api.headers(token),
    });
    if (!r.ok) throw new Error("Request failed");
    return r.json();
  },
  del: async (path, token) => {
    const r = await fetch(`${API}${path}`, {
      method: "DELETE",
      headers: api.headers(token),
    });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.detail || "Request failed");
    }
    return r.json();
  },
};

// ─── STYLES ──────────────────────────────────────────
const injectStyles = () => {
  const style = document.createElement("style");
  style.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg-deep:     #080b12;
      --bg-dark:     #0d1117;
      --bg-surface:  #111827;
      --bg-elevated: #1a2332;
      --glass:       rgba(255,255,255,0.04);
      --glass-border:rgba(255,255,255,0.08);
      --primary:     #6366f1;
      --primary-glow:#818cf8;
      --accent:      #22d3ee;
      --accent2:     #a78bfa;
      --success:     #34d399;
      --warning:     #fbbf24;
      --danger:      #f87171;
      --text-1:      #f0f4ff;
      --text-2:      #8892a4;
      --text-3:      #4b5563;
      --radius:      14px;
      --radius-sm:   8px;
      --shadow:      0 8px 32px rgba(0,0,0,0.4);
      --shadow-glow: 0 0 40px rgba(99,102,241,0.15);
    }

    html, body, #root { height: 100%; font-family: 'Outfit', sans-serif; background: var(--bg-deep); color: var(--text-1); }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

    .app { display: flex; height: 100vh; overflow: hidden; }

    /* ── SIDEBAR ── */
    .sidebar {
      width: 280px; min-width: 280px;
      background: var(--bg-surface);
      border-right: 1px solid var(--glass-border);
      display: flex; flex-direction: column;
      position: relative; overflow: hidden;
    }
    .sidebar::before {
      content:''; position:absolute; inset:0; pointer-events:none;
      background: radial-gradient(ellipse at 30% 0%, rgba(99,102,241,0.08) 0%, transparent 70%);
    }

    .sidebar-header {
      padding: 20px 18px 16px;
      border-bottom: 1px solid var(--glass-border);
      display: flex; align-items: center; gap: 12px;
    }
    .brand-logo {
      width: 36px; height: 36px; border-radius: 10px;
      background: linear-gradient(135deg, var(--primary), var(--accent2));
      display:flex; align-items:center; justify-content:center;
      font-size: 18px; box-shadow: 0 0 20px rgba(99,102,241,0.4);
    }
    .brand-name { font-size: 18px; font-weight: 700; letter-spacing: -0.5px; }
    .brand-tag { font-size: 11px; color: var(--text-2); font-weight: 400; }

    .sidebar-section { padding: 16px 12px 8px; }
    .sidebar-label {
      font-size: 10px; font-weight: 600; letter-spacing: 1.2px;
      color: var(--text-3); text-transform: uppercase; padding: 0 6px 8px;
    }

    .room-item {
      display: flex; align-items: center; gap: 10px;
      padding: 9px 10px; border-radius: var(--radius-sm);
      cursor: pointer; transition: all 0.15s ease;
      position: relative;
    }
    .room-item:hover { background: var(--glass); }
    .room-item.active {
      background: rgba(99,102,241,0.15);
      box-shadow: inset 3px 0 0 var(--primary);
    }
    .room-icon { font-size: 16px; min-width: 20px; text-align: center; }
    .room-name { font-size: 14px; font-weight: 500; flex: 1; }
    .room-count {
      font-size: 11px; background: var(--glass); color: var(--text-2);
      padding: 1px 7px; border-radius: 20px; font-family: 'JetBrains Mono';
    }

    .sidebar-footer {
      margin-top: auto;
      padding: 12px;
      border-top: 1px solid var(--glass-border);
    }

    /* ── PROFILE DROPDOWN ── */
    .profile-btn {
      display: flex; align-items: center; gap: 10px;
      padding: 10px; border-radius: var(--radius-sm);
      cursor: pointer; transition: background 0.15s;
      position: relative;
    }
    .profile-btn:hover { background: var(--glass); }
    .avatar {
      width: 34px; height: 34px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 13px; font-weight: 700; color: white;
      flex-shrink: 0; position: relative;
    }
    .avatar-online::after {
      content:''; position:absolute; bottom:1px; right:1px;
      width:9px; height:9px; border-radius:50%;
      background: var(--success); border: 2px solid var(--bg-surface);
    }
    .profile-info { flex: 1; min-width: 0; }
    .profile-name { font-size: 13px; font-weight: 600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .profile-status { font-size: 11px; color: var(--success); }

    .dropdown {
      position: absolute; bottom: calc(100% + 8px); left: 0; right: 0;
      background: var(--bg-elevated); border: 1px solid var(--glass-border);
      border-radius: var(--radius); box-shadow: var(--shadow);
      overflow: hidden; animation: fadeUp 0.15s ease;
    }
    .dropdown-item {
      padding: 11px 16px; cursor: pointer; font-size: 13px;
      display: flex; align-items: center; gap: 10px;
      transition: background 0.1s;
    }
    .dropdown-item:hover { background: var(--glass); }
    .dropdown-item.danger { color: var(--danger); }
    .dropdown-divider { height: 1px; background: var(--glass-border); }

    @keyframes fadeUp {
      from { opacity:0; transform:translateY(8px); }
      to   { opacity:1; transform:translateY(0); }
    }

    /* ── MAIN CHAT ── */
    .chat-main {
      flex: 1; display: flex; flex-direction: column; overflow: hidden;
      background: var(--bg-dark);
      position: relative;
    }
    .chat-main::before {
      content:''; position:absolute; inset:0; pointer-events:none;
      background:
        radial-gradient(ellipse at 80% 20%, rgba(34,211,238,0.04) 0%, transparent 50%),
        radial-gradient(ellipse at 20% 80%, rgba(167,139,250,0.04) 0%, transparent 50%);
    }

    .chat-header {
      padding: 0 24px;
      height: 64px;
      display: flex; align-items: center; gap: 16px;
      border-bottom: 1px solid var(--glass-border);
      background: rgba(255,255,255,0.02);
      backdrop-filter: blur(12px);
      position: relative; z-index: 10;
      flex-shrink: 0;
    }
    .chat-room-name { font-size: 17px; font-weight: 600; }
    .chat-room-desc { font-size: 12px; color: var(--text-2); }
    .header-actions { margin-left: auto; display: flex; gap: 8px; }
    .icon-btn {
      width: 36px; height: 36px; border-radius: var(--radius-sm);
      border: 1px solid var(--glass-border); background: var(--glass);
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; font-size: 15px; transition: all 0.15s;
      color: var(--text-2);
    }
    .icon-btn:hover { background: rgba(255,255,255,0.08); color: var(--text-1); }
    .icon-btn.active { background: rgba(99,102,241,0.2); color: var(--primary-glow); border-color: rgba(99,102,241,0.3); }

    /* ── MESSAGES ── */
    .messages-area {
      flex: 1; overflow-y: auto; padding: 20px 24px;
      display: flex; flex-direction: column; gap: 2px;
      position: relative;
    }

    .day-divider {
      display: flex; align-items: center; gap: 12px;
      padding: 16px 0; color: var(--text-3); font-size: 11px;
      font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase;
    }
    .day-divider::before, .day-divider::after {
      content:''; flex:1; height:1px; background: var(--glass-border);
    }

    .msg-group { display: flex; flex-direction: column; gap: 1px; margin: 4px 0; }
    .msg-row { display: flex; align-items: flex-end; gap: 10px; animation: msgIn 0.25s ease; }
    .msg-row.own { flex-direction: row-reverse; }

    @keyframes msgIn {
      from { opacity:0; transform: translateY(10px) scale(0.97); }
      to   { opacity:1; transform: translateY(0) scale(1); }
    }

    .msg-avatar {
      width: 30px; height: 30px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 12px; font-weight: 700; flex-shrink: 0;
      margin-bottom: 2px;
    }
    .msg-avatar.ghost { visibility: hidden; }

    .msg-bubble-wrap { max-width: 68%; display: flex; flex-direction: column; }
    .msg-row.own .msg-bubble-wrap { align-items: flex-end; }

    .msg-meta {
      font-size: 11px; color: var(--text-3); margin-bottom: 4px;
      display: flex; align-items: center; gap: 6px;
    }
    .msg-sender { font-weight: 600; color: var(--text-2); }
    .msg-time { font-family: 'JetBrains Mono'; }

    .msg-bubble {
      padding: 10px 14px;
      border-radius: 16px;
      line-height: 1.5;
      font-size: 14px;
      word-break: break-word;
      position: relative;
      transition: all 0.2s ease;
    }
    .msg-bubble.other {
      background: var(--bg-elevated);
      border: 1px solid var(--glass-border);
      border-bottom-left-radius: 4px;
      color: var(--text-1);
    }
    .msg-bubble.own-bubble {
      background: linear-gradient(135deg, var(--primary) 0%, #4f46e5 100%);
      border-bottom-right-radius: 4px;
      color: white;
      box-shadow: 0 4px 16px rgba(99,102,241,0.3);
    }
    .msg-bubble.system-msg {
      background: rgba(251,191,36,0.08);
      border: 1px solid rgba(251,191,36,0.15);
      color: var(--warning);
      font-size: 12px; text-align: center;
      border-radius: 20px;
    }

    .msg-bubble:hover .msg-actions { opacity: 1; }
    .msg-actions {
      position: absolute; top: -32px; right: 0;
      display: flex; gap: 4px;
      opacity: 0; transition: opacity 0.15s;
      background: var(--bg-elevated);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm);
      padding: 4px;
    }
    .msg-action-btn {
      width: 24px; height: 24px; border-radius: 6px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; font-size: 12px; transition: background 0.1s;
      color: var(--text-2);
    }
    .msg-action-btn:hover { background: var(--glass); color: var(--text-1); }

    /* ── TYPING INDICATOR ── */
    .typing-bar {
      padding: 6px 24px;
      font-size: 12px; color: var(--text-2);
      min-height: 28px; display: flex; align-items: center; gap: 8px;
    }
    .typing-dots { display: flex; gap: 3px; }
    .typing-dot {
      width: 5px; height: 5px; border-radius: 50%;
      background: var(--accent);
      animation: dotBounce 1.2s infinite;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes dotBounce {
      0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
      40%           { transform: translateY(-5px); opacity: 1; }
    }

    /* ── INPUT ── */
    .input-area {
      padding: 12px 20px 16px;
      border-top: 1px solid var(--glass-border);
      background: rgba(255,255,255,0.01);
      position: relative; z-index: 5; flex-shrink: 0;
    }
    .input-wrapper {
      display: flex; align-items: flex-end; gap: 10px;
      background: var(--bg-elevated);
      border: 1px solid var(--glass-border);
      border-radius: 16px; padding: 10px 14px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .input-wrapper:focus-within {
      border-color: rgba(99,102,241,0.4);
      box-shadow: 0 0 0 3px rgba(99,102,241,0.08);
    }
    .msg-input {
      flex: 1; background: none; border: none; outline: none;
      color: var(--text-1); font-family: 'Outfit'; font-size: 14px;
      resize: none; max-height: 120px; line-height: 1.5;
    }
    .msg-input::placeholder { color: var(--text-3); }
    .send-btn {
      width: 36px; height: 36px; border-radius: 10px; border: none;
      background: linear-gradient(135deg, var(--primary), #4f46e5);
      color: white; cursor: pointer; font-size: 16px;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.15s; flex-shrink: 0;
      box-shadow: 0 4px 12px rgba(99,102,241,0.35);
    }
    .send-btn:hover { transform: scale(1.05); box-shadow: 0 6px 18px rgba(99,102,241,0.5); }
    .send-btn:active { transform: scale(0.96); }
    .send-btn:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

    .input-toolbar {
      display: flex; gap: 4px; margin-top: 8px;
      padding: 0 4px;
    }
    .toolbar-btn {
      font-size: 11px; padding: 4px 10px; border-radius: 20px;
      border: 1px solid var(--glass-border); background: transparent;
      color: var(--text-2); cursor: pointer; transition: all 0.15s;
      font-family: 'Outfit'; display: flex; align-items: center; gap: 5px;
    }
    .toolbar-btn:hover { background: var(--glass); color: var(--text-1); }
    .toolbar-btn.undo-btn:hover { border-color: rgba(248,113,113,0.4); color: var(--danger); }

    /* ── SEARCH PANEL ── */
    .search-panel {
      position: absolute; top: 65px; right: 20px;
      width: 360px;
      background: var(--bg-elevated);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      z-index: 100; overflow: hidden;
      animation: fadeDown 0.2s ease;
    }
    @keyframes fadeDown {
      from { opacity:0; transform:translateY(-8px); }
      to   { opacity:1; transform:translateY(0); }
    }
    .search-input-wrap {
      padding: 14px 16px;
      display: flex; align-items: center; gap: 10px;
      border-bottom: 1px solid var(--glass-border);
    }
    .search-icon { color: var(--text-3); font-size: 14px; }
    .search-field {
      flex: 1; background: none; border: none; outline: none;
      color: var(--text-1); font-family: 'Outfit'; font-size: 14px;
    }
    .search-field::placeholder { color: var(--text-3); }
    .search-results { max-height: 320px; overflow-y: auto; }
    .search-result-item {
      padding: 12px 16px; cursor: pointer;
      border-bottom: 1px solid rgba(255,255,255,0.04);
      transition: background 0.1s;
    }
    .search-result-item:hover { background: var(--glass); }
    .search-result-sender { font-size: 12px; font-weight: 600; color: var(--accent); margin-bottom: 3px; }
    .search-result-content { font-size: 13px; color: var(--text-2); }
    .search-result-content mark {
      background: rgba(99,102,241,0.3); color: var(--primary-glow);
      border-radius: 3px; padding: 0 2px;
    }
    .search-empty { padding: 28px; text-align: center; color: var(--text-3); font-size: 13px; }

    /* ── MEMBERS PANEL ── */
    .members-panel {
      width: 240px; min-width: 240px;
      background: var(--bg-surface);
      border-left: 1px solid var(--glass-border);
      display: flex; flex-direction: column; overflow: hidden;
    }
    .members-header {
      padding: 20px 16px 12px;
      border-bottom: 1px solid var(--glass-border);
      font-size: 12px; font-weight: 600; color: var(--text-2);
      letter-spacing: 0.8px; text-transform: uppercase;
    }
    .members-list { flex: 1; overflow-y: auto; padding: 8px; }
    .member-item {
      display: flex; align-items: center; gap: 10px;
      padding: 8px 10px; border-radius: var(--radius-sm);
    }
    .member-name { font-size: 13px; font-weight: 500; }
    .member-status { font-size: 11px; color: var(--text-3); }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .status-dot.online { background: var(--success); box-shadow: 0 0 6px rgba(52,211,153,0.6); }
    .status-dot.offline { background: var(--text-3); }

    /* ── AUTH SCREEN ── */
    .auth-screen {
      min-height: 100vh;
      display: flex; align-items: center; justify-content: center;
      background: var(--bg-deep);
      position: relative; overflow: hidden;
    }
    .auth-screen::before {
      content:''; position:absolute; inset:0; pointer-events:none;
      background:
        radial-gradient(ellipse at 25% 35%, rgba(99,102,241,0.12) 0%, transparent 55%),
        radial-gradient(ellipse at 75% 65%, rgba(34,211,238,0.08) 0%, transparent 55%);
    }
    .auth-grid {
      position: absolute; inset:0; pointer-events:none; opacity:0.03;
      background-image: linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px);
      background-size: 40px 40px;
    }

    .auth-card {
      width: 100%; max-width: 420px;
      background: var(--bg-surface);
      border: 1px solid var(--glass-border);
      border-radius: 24px;
      padding: 40px;
      position: relative; z-index: 1;
      box-shadow: var(--shadow), var(--shadow-glow);
    }
    .auth-logo {
      width: 52px; height: 52px; border-radius: 16px;
      background: linear-gradient(135deg, var(--primary), var(--accent2));
      display: flex; align-items: center; justify-content: center;
      font-size: 26px; margin: 0 auto 24px;
      box-shadow: 0 0 30px rgba(99,102,241,0.4);
    }
    .auth-title { font-size: 28px; font-weight: 700; text-align: center; letter-spacing: -0.5px; margin-bottom: 6px; }
    .auth-sub { font-size: 14px; color: var(--text-2); text-align: center; margin-bottom: 32px; }

    .field { margin-bottom: 16px; }
    .field label { display: block; font-size: 12px; font-weight: 600; color: var(--text-2); margin-bottom: 6px; letter-spacing: 0.5px; }
    .field input {
      width: 100%; padding: 11px 14px;
      background: var(--bg-elevated);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm); outline: none;
      color: var(--text-1); font-family: 'Outfit'; font-size: 14px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .field input:focus {
      border-color: rgba(99,102,241,0.5);
      box-shadow: 0 0 0 3px rgba(99,102,241,0.1);
    }
    .field input::placeholder { color: var(--text-3); }

    .btn-primary {
      width: 100%; padding: 12px;
      background: linear-gradient(135deg, var(--primary), #4f46e5);
      border: none; border-radius: var(--radius-sm);
      color: white; font-family: 'Outfit'; font-size: 15px; font-weight: 600;
      cursor: pointer; transition: all 0.2s;
      box-shadow: 0 4px 16px rgba(99,102,241,0.35);
      margin-top: 8px;
    }
    .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(99,102,241,0.5); }
    .btn-primary:active { transform: translateY(0); }
    .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

    .auth-switch {
      margin-top: 20px; text-align: center; font-size: 13px; color: var(--text-2);
    }
    .auth-switch span { color: var(--primary-glow); cursor: pointer; font-weight: 600; }
    .auth-switch span:hover { text-decoration: underline; }

    .error-msg {
      background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.25);
      color: var(--danger); border-radius: var(--radius-sm);
      padding: 10px 14px; font-size: 13px; margin-bottom: 16px;
    }

    /* ── EMPTY STATE ── */
    .empty-state {
      flex: 1; display: flex; flex-direction: column;
      align-items: center; justify-content: center; gap: 16px;
      color: var(--text-3);
    }
    .empty-icon { font-size: 48px; opacity: 0.3; }
    .empty-title { font-size: 18px; font-weight: 600; color: var(--text-2); }
    .empty-sub { font-size: 13px; max-width: 240px; text-align: center; line-height: 1.6; }

    /* ── NOTIFICATIONS BADGE ── */
    .notif-badge {
      position: absolute; top: 4px; right: 4px;
      min-width: 16px; height: 16px; border-radius: 8px;
      background: var(--danger); color: white;
      font-size: 10px; font-weight: 700;
      display: flex; align-items: center; justify-content: center;
      padding: 0 3px;
    }

    /* ── ROOM CREATOR MODAL ── */
    .modal-overlay {
      position: fixed; inset: 0; z-index: 1000;
      background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
      display: flex; align-items: center; justify-content: center;
      animation: fadeIn 0.15s ease;
    }
    @keyframes fadeIn { from{opacity:0}to{opacity:1} }
    .modal {
      width: 100%; max-width: 400px;
      background: var(--bg-elevated);
      border: 1px solid var(--glass-border);
      border-radius: 20px; padding: 28px;
      box-shadow: var(--shadow);
      animation: slideUp 0.2s ease;
    }
    @keyframes slideUp {
      from { transform:translateY(20px); opacity:0; }
      to   { transform:translateY(0); opacity:1; }
    }
    .modal-title { font-size: 18px; font-weight: 700; margin-bottom: 20px; }
    .modal-footer { display: flex; gap: 10px; margin-top: 20px; }
    .btn-ghost {
      flex:1; padding: 10px; border-radius: var(--radius-sm);
      border: 1px solid var(--glass-border); background: none;
      color: var(--text-2); font-family: 'Outfit'; font-size: 14px;
      cursor: pointer; transition: all 0.15s;
    }
    .btn-ghost:hover { background: var(--glass); color: var(--text-1); }

    .online-pill {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 3px 9px; border-radius: 20px;
      background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2);
      color: var(--success); font-size: 11px; font-weight: 600;
    }
    .online-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1}50%{opacity:0.4} }

    .toast-container { position:fixed; bottom:24px; right:24px; z-index:9999; display:flex; flex-direction:column; gap:8px; }
    .toast {
      padding: 12px 18px; border-radius: 12px;
      background: var(--bg-elevated); border: 1px solid var(--glass-border);
      box-shadow: var(--shadow); font-size: 13px;
      display: flex; align-items: center; gap: 10px;
      animation: toastIn 0.3s ease;
      max-width: 320px;
    }
    @keyframes toastIn {
      from { opacity:0; transform:translateX(20px); }
      to   { opacity:1; transform:translateX(0); }
    }
    .toast.success { border-color: rgba(52,211,153,0.3); }
    .toast.error   { border-color: rgba(248,113,113,0.3); }
    .toast.info    { border-color: rgba(99,102,241,0.3); }

    @media (max-width: 768px) {
      .sidebar { width: 60px; min-width: 60px; }
      .brand-name, .brand-tag, .room-name, .room-count, .sidebar-label, .profile-info { display: none; }
      .members-panel { display: none; }
      .room-item { justify-content: center; padding: 10px; }
      .room-icon { font-size: 20px; }
    }
  `;
  document.head.appendChild(style);
};

// ─── UTILS ───────────────────────────────────────────
const formatTime = (ts) => {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

const formatDate = (ts) => {
  const d = new Date(ts * 1000);
  const today = new Date();
  if (d.toDateString() === today.toDateString()) return "Today";
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === yesterday.toDateString()) return "Yesterday";
  return d.toLocaleDateString([], { weekday: "long", month: "short", day: "numeric" });
};

const getInitials = (name) => name?.slice(0, 2).toUpperCase() || "??";

const highlightText = (text, keyword) => {
  if (!keyword) return text;
  const parts = text.split(new RegExp(`(${keyword})`, "gi"));
  return parts.map((p, i) =>
    p.toLowerCase() === keyword.toLowerCase()
      ? `<mark>${p}</mark>`
      : p
  ).join("");
};

// ─── TOAST SYSTEM ────────────────────────────────────
let toastId = 0;

function ToastContainer({ toasts }) {
  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className={`toast ${t.type}`}>
          <span>{t.icon}</span>
          <span>{t.message}</span>
        </div>
      ))}
    </div>
  );
}

// ─── AUTH SCREEN ─────────────────────────────────────
function AuthScreen({ onAuth }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", password: "", display_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handle = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      if (mode === "register") {
        await api.post("/api/auth/register", form);
      }
      const res = await api.post("/api/auth/login", { username: form.username, password: form.password });
      onAuth(res.token, res.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-screen">
      <div className="auth-grid" />
      <div className="auth-card">
        <div className="auth-logo">⚡</div>
        <h1 className="auth-title">Nexus Chat</h1>
        <p className="auth-sub">
          {mode === "login" ? "Welcome back. Sign in to continue." : "Create your account to get started."}
        </p>
        {error && <div className="error-msg">⚠ {error}</div>}
        <form onSubmit={handle}>
          <div className="field">
            <label>USERNAME</label>
            <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="your_username" required autoFocus />
          </div>
          {mode === "register" && (
            <div className="field">
              <label>DISPLAY NAME</label>
              <input value={form.display_name} onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                placeholder="How others see you" />
            </div>
          )}
          <div className="field">
            <label>PASSWORD</label>
            <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="••••••••" required />
          </div>
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "…" : mode === "login" ? "Sign In →" : "Create Account →"}
          </button>
        </form>
        <div className="auth-switch">
          {mode === "login" ? (
            <>Don't have an account? <span onClick={() => setMode("register")}>Sign up</span></>
          ) : (
            <>Already have an account? <span onClick={() => setMode("login")}>Sign in</span></>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── CREATE ROOM MODAL ───────────────────────────────
function CreateRoomModal({ token, onClose, onCreated }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);

  const handle = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/api/rooms", { name, description }, token);
      onCreated(res.room);
      onClose();
    } catch {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-title">✦ Create New Room</div>
        <form onSubmit={handle}>
          <div className="field">
            <label>ROOM NAME</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. ✨ Announcements" required autoFocus />
          </div>
          <div className="field">
            <label>DESCRIPTION</label>
            <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What's this room about?" />
          </div>
          <div className="modal-footer">
            <button type="button" className="btn-ghost" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" style={{ flex: 1 }} disabled={loading}>
              {loading ? "Creating…" : "Create Room"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── SEARCH PANEL ────────────────────────────────────
function SearchPanel({ token, roomId, onClose }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);

  const doSearch = useCallback(async (q) => {
    if (!q.trim()) { setResults([]); setSearched(false); return; }
    try {
      const res = await api.get(`/api/rooms/${roomId}/search?q=${encodeURIComponent(q)}`, token);
      setResults(res.results || []);
      setSearched(true);
    } catch {}
  }, [token, roomId]);

  useEffect(() => {
    const t = setTimeout(() => doSearch(query), 300);
    return () => clearTimeout(t);
  }, [query, doSearch]);

  return (
    <div className="search-panel">
      <div className="search-input-wrap">
        <span className="search-icon">🔍</span>
        <input className="search-field" value={query} onChange={(e) => setQuery(e.target.value)}
          placeholder="Search messages…" autoFocus />
        <span style={{ cursor: "pointer", color: "var(--text-3)", fontSize: 18 }} onClick={onClose}>×</span>
      </div>
      <div className="search-results">
        {results.length > 0 ? results.map((r) => (
          <div key={r.message_id} className="search-result-item">
            <div className="search-result-sender">{r.sender}</div>
            <div className="search-result-content"
              dangerouslySetInnerHTML={{ __html: highlightText(r.content, query) }} />
          </div>
        )) : searched ? (
          <div className="search-empty">No messages found for "{query}"</div>
        ) : (
          <div className="search-empty">Type to search this room's messages</div>
        )}
      </div>
    </div>
  );
}

// ─── MESSAGE BUBBLE ──────────────────────────────────
function MessageBubble({ msg, isOwn, showMeta }) {
  if (msg.msg_type === "system") {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "8px 0" }}>
        <div className="msg-bubble system-msg">{msg.content}</div>
      </div>
    );
  }

  return (
    <div className={`msg-row ${isOwn ? "own" : ""}`}>
      <div className={`msg-avatar ${!showMeta ? "ghost" : ""}`}
        style={{ backgroundColor: msg.avatar_color || "#6366f1" }}>
        {showMeta ? getInitials(msg.sender) : ""}
      </div>
      <div className="msg-bubble-wrap">
        {showMeta && (
          <div className="msg-meta">
            {!isOwn && <span className="msg-sender">{msg.sender}</span>}
            <span className="msg-time">{formatTime(msg.timestamp)}</span>
          </div>
        )}
        <div style={{ position: "relative" }}>
          <div className={`msg-bubble ${isOwn ? "own-bubble" : "other"}`}>
            {msg.content}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── MEMBERS PANEL ───────────────────────────────────
function MembersPanel({ participants, onlineUsers }) {
  const online = participants.filter((p) => onlineUsers.includes(p.username));
  const offline = participants.filter((p) => !onlineUsers.includes(p.username));

  return (
    <div className="members-panel">
      <div className="members-header">
        Members · {participants.length}
      </div>
      <div className="members-list">
        {online.length > 0 && (
          <>
            <div style={{ fontSize: 10, color: "var(--text-3)", padding: "8px 10px 4px", letterSpacing: "0.8px", fontWeight: 600 }}>
              ONLINE — {online.length}
            </div>
            {online.map((p) => (
              <div key={p.username} className="member-item">
                <div className="avatar" style={{ backgroundColor: p.avatar_color, width: 28, height: 28, fontSize: 11 }}>
                  {getInitials(p.display_name)}
                </div>
                <div>
                  <div className="member-name">{p.display_name}</div>
                </div>
                <div className="status-dot online" style={{ marginLeft: "auto" }} />
              </div>
            ))}
          </>
        )}
        {offline.length > 0 && (
          <>
            <div style={{ fontSize: 10, color: "var(--text-3)", padding: "12px 10px 4px", letterSpacing: "0.8px", fontWeight: 600 }}>
              OFFLINE — {offline.length}
            </div>
            {offline.map((p) => (
              <div key={p.username} className="member-item" style={{ opacity: 0.5 }}>
                <div className="avatar" style={{ backgroundColor: p.avatar_color, width: 28, height: 28, fontSize: 11 }}>
                  {getInitials(p.display_name)}
                </div>
                <div>
                  <div className="member-name">{p.display_name}</div>
                </div>
                <div className="status-dot offline" style={{ marginLeft: "auto" }} />
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}

// ─── MAIN CHAT VIEW ──────────────────────────────────
function ChatView({ token, user, room, onlineUsers, toast }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [typingUsers, setTypingUsers] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [membersOpen, setMembersOpen] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [sending, setSending] = useState(false);

  const sseRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const typingTimeout = useRef(null);
  const typingUsers_ref = useRef({});  // username -> timeout id
  const isTyping = useRef(false);

  // Load initial messages
  useEffect(() => {
    if (!room) return;
    setMessages([]);
    setPage(1);
    loadMessages(1, true);
    loadParticipants();
    connectSSE();
    return () => { sseRef.current?.close(); };
  }, [room?.room_id]);

  const loadMessages = async (p = 1, reset = false) => {
    try {
      const res = await api.get(`/api/rooms/${room.room_id}/messages?page=${p}`, token);
      const msgs = res.messages || [];
      setMessages((prev) => reset ? msgs : [...msgs, ...prev]);
      setHasMore(res.has_more);
    } catch {}
  };

  const loadParticipants = async () => {
    try {
      const res = await api.get(`/api/rooms/${room.room_id}/participants`, token);
      setParticipants(res.participants || []);
    } catch {}
  };

  const connectSSE = () => {
    sseRef.current?.close();
    const es = new EventSource(`${SSE_BASE}/sse/${room.room_id}?token=${token}`);
    es.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "new_message") {
        setMessages((prev) => [...prev, data.message]);
        setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
      } else if (data.type === "message_deleted") {
        setMessages((prev) => prev.filter((m) => m.message_id !== data.message_id));
      } else if (data.type === "typing") {
        const typer = data.username;
        if (typer === user.username) return;
        if (data.is_typing) {
          clearTimeout(typingUsers_ref.current[typer]);
          typingUsers_ref.current[typer] = setTimeout(() => {
            setTypingUsers((prev) => prev.filter((u) => u !== typer));
            delete typingUsers_ref.current[typer];
          }, 3000);
          setTypingUsers((prev) => prev.includes(typer) ? prev : [...prev, typer]);
        } else {
          clearTimeout(typingUsers_ref.current[typer]);
          delete typingUsers_ref.current[typer];
          setTypingUsers((prev) => prev.filter((u) => u !== typer));
        }
      } else if (data.type === "user_joined" || data.type === "user_left") {
        loadParticipants();
      }
    };
    es.onerror = () => {
      // Reconnect after 2s on error
      setTimeout(connectSSE, 2000);
    };
    sseRef.current = es;
  };

  const sendTypingEvent = (typing) => {
    fetch(`${SSE_BASE}/sse/${room.room_id}/typing`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ is_typing: typing }),
    }).catch(() => {});
  };

  const handleInput = (e) => {
    setInput(e.target.value);
    if (!isTyping.current) {
      isTyping.current = true;
      sendTypingEvent(true);
    }
    clearTimeout(typingTimeout.current);
    typingTimeout.current = setTimeout(() => {
      isTyping.current = false;
      sendTypingEvent(false);
    }, 1200);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || sending) return;
    const content = input.trim();
    setInput("");
    setSending(true);
    clearTimeout(typingTimeout.current);
    isTyping.current = false;
    sendTypingEvent(false);
    try {
      await api.post(`/api/rooms/${room.room_id}/messages`, { content }, token);
    } catch (err) {
      toast(err.message, "error");
    } finally {
      setSending(false);
    }
    inputRef.current?.focus();
  };

  const undoMessage = async () => {
    try {
      await api.del(`/api/rooms/${room.room_id}/messages/undo`, token);
      toast("Message undone ↩", "info");
    } catch (err) {
      toast(err.message, "error");
    }
  };

  const handleScroll = async (e) => {
    if (e.target.scrollTop === 0 && hasMore && !loadingMore) {
      setLoadingMore(true);
      const nextPage = page + 1;
      setPage(nextPage);
      await loadMessages(nextPage, false);
      setLoadingMore(false);
    }
  };

  // Group messages by date
  const grouped = useMemo(() => {
    const groups = [];
    let lastDate = null;
    messages.forEach((msg) => {
      const d = formatDate(msg.timestamp);
      if (d !== lastDate) { groups.push({ type: "divider", label: d }); lastDate = d; }
      groups.push(msg);
    });
    return groups;
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (!room) return null;

  return (
    <>
      <div className="chat-main">
        {/* Header */}
        <div className="chat-header">
          <div>
            <div className="chat-room-name">{room.name}</div>
            <div className="chat-room-desc">{room.description}</div>
          </div>
          <div className="header-actions">
            <div className="online-pill">
              <div className="online-dot" />
              {onlineUsers.length} online
            </div>
            <div className={`icon-btn ${searchOpen ? "active" : ""}`} onClick={() => setSearchOpen(!searchOpen)} title="Search">🔍</div>
            <div className={`icon-btn ${membersOpen ? "active" : ""}`} onClick={() => setMembersOpen(!membersOpen)} title="Members">👥</div>
          </div>
        </div>

        {/* Search Panel */}
        {searchOpen && <SearchPanel token={token} roomId={room.room_id} onClose={() => setSearchOpen(false)} />}

        {/* Messages */}
        <div className="messages-area" onScroll={handleScroll}>
          {loadingMore && (
            <div style={{ textAlign: "center", padding: "10px", color: "var(--text-3)", fontSize: 12 }}>Loading more…</div>
          )}
          {grouped.map((item, i) => {
            if (item.type === "divider") {
              return <div key={`d-${i}`} className="day-divider">{item.label}</div>;
            }
            const prev = grouped[i - 1];
            const showMeta = !prev || prev.type === "divider" || prev.sender !== item.sender;
            return (
              <MessageBubble
                key={item.message_id}
                msg={item}
                isOwn={item.sender === user.username}
                showMeta={showMeta}
              />
            );
          })}
          <div ref={messagesEndRef} />
        </div>

        {/* Typing indicator */}
        <div className="typing-bar">
          {typingUsers.length > 0 && (
            <>
              <div className="typing-dots">
                <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
              </div>
              <span>{typingUsers.join(", ")} {typingUsers.length === 1 ? "is" : "are"} typing…</span>
            </>
          )}
        </div>

        {/* Input */}
        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              className="msg-input"
              value={input}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder={`Message ${room.name}…`}
              rows={1}
            />
            <button className="send-btn" onClick={sendMessage} disabled={!input.trim() || sending}>
              ➤
            </button>
          </div>
          <div className="input-toolbar">
            <button className="toolbar-btn undo-btn" onClick={undoMessage} title="Undo last message">
              ↩ Undo
            </button>
            <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--text-3)" }}>
              Enter to send · Shift+Enter for newline
            </span>
          </div>
        </div>
      </div>

      {/* Members Panel */}
      {membersOpen && (
        <MembersPanel participants={participants} onlineUsers={onlineUsers} />
      )}
    </>
  );
}

// ─── SIDEBAR ─────────────────────────────────────────
function Sidebar({ rooms, activeRoom, onRoomSelect, user, onCreateRoom, onLogout, notifications }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <div className="sidebar">
      {/* Brand */}
      <div className="sidebar-header">
        <div className="brand-logo">⚡</div>
        <div>
          <div className="brand-name">Nexus</div>
          <div className="brand-tag">Real-time Chat</div>
        </div>
      </div>

      {/* Rooms */}
      <div className="sidebar-section" style={{ flex: 1, overflowY: "auto" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 6px 8px" }}>
          <div className="sidebar-label">Rooms</div>
          <div className="icon-btn" onClick={onCreateRoom} title="Create room" style={{ width: 24, height: 24, fontSize: 16 }}>+</div>
        </div>
        {rooms.map((room) => (
          <div
            key={room.room_id}
            className={`room-item ${activeRoom?.room_id === room.room_id ? "active" : ""}`}
            onClick={() => onRoomSelect(room)}
          >
            <span className="room-icon">{room.name.match(/^\p{Emoji}/u)?.[0] || "#"}</span>
            <span className="room-name">{room.name.replace(/^\p{Emoji}\s*/u, "")}</span>
            <span className="room-count">{room.message_count}</span>
          </div>
        ))}
      </div>

      {/* Profile */}
      <div className="sidebar-footer">
        <div className="profile-btn" onClick={() => setDropdownOpen(!dropdownOpen)}>
          <div className="avatar avatar-online" style={{ backgroundColor: user.avatar_color }}>
            {getInitials(user.display_name)}
            {notifications > 0 && <div className="notif-badge">{notifications}</div>}
          </div>
          <div className="profile-info">
            <div className="profile-name">{user.display_name}</div>
            <div className="profile-status">● Online</div>
          </div>
          <span style={{ color: "var(--text-3)", fontSize: 12 }}>⌃</span>

          {dropdownOpen && (
            <div className="dropdown">
              <div className="dropdown-item">
                <span>👤</span> @{user.username}
              </div>
              <div className="dropdown-divider" />
              <div className="dropdown-item danger" onClick={onLogout}>
                <span>🚪</span> Sign Out
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── ROOT APP ────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => localStorage.getItem("nexus_token"));
  const [user, setUser] = useState(() => {
    const u = localStorage.getItem("nexus_user");
    return u ? JSON.parse(u) : null;
  });
  const [rooms, setRooms] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [showCreateRoom, setShowCreateRoom] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [notifCount, setNotifCount] = useState(0);

  // Inject styles once
  useEffect(() => { injectStyles(); }, []);

  const addToast = useCallback((message, type = "info") => {
    const id = ++toastId;
    const icons = { success: "✅", error: "❌", info: "💬" };
    setToasts((prev) => [...prev, { id, message, type, icon: icons[type] }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
  }, []);

  // Load rooms & online users on auth
  useEffect(() => {
    if (!token) return;
    const load = async () => {
      try {
        const [rRes, oRes] = await Promise.all([
          api.get("/api/rooms", token),
          api.get("/api/users/online", token),
        ]);
        setRooms(rRes.rooms || []);
        setOnlineUsers((oRes.users || []).map((u) => u.username));
      } catch {
        handleLogout();
      }
    };
    load();

    // Poll online users & notifications
    const interval = setInterval(async () => {
      try {
        const [oRes, nRes] = await Promise.all([
          api.get("/api/users/online", token),
          api.get("/api/users/notifications", token),
        ]);
        setOnlineUsers((oRes.users || []).map((u) => u.username));
        setNotifCount(nRes.notifications?.length || 0);
      } catch {}
    }, 5000);
    return () => clearInterval(interval);
  }, [token]);

  const handleAuth = (tok, usr) => {
    setToken(tok);
    setUser(usr);
    localStorage.setItem("nexus_token", tok);
    localStorage.setItem("nexus_user", JSON.stringify(usr));
  };

  const handleLogout = () => {
    api.post("/api/auth/logout", {}, token).catch(() => {});
    setToken(null); setUser(null);
    setRooms([]); setActiveRoom(null);
    localStorage.removeItem("nexus_token");
    localStorage.removeItem("nexus_user");
  };

  const handleRoomSelect = async (room) => {
    try {
      await api.post(`/api/rooms/${room.room_id}/join`, {}, token);
      setActiveRoom(room);
    } catch (err) {
      addToast(err.message, "error");
    }
  };

  const handleRoomCreated = (room) => {
    setRooms((prev) => [...prev, room]);
    handleRoomSelect(room);
    addToast(`Room "${room.name}" created!`, "success");
  };

  if (!token || !user) {
    return <AuthScreen onAuth={handleAuth} />;
  }

  return (
    <div className="app">
      <Sidebar
        rooms={rooms}
        activeRoom={activeRoom}
        onRoomSelect={handleRoomSelect}
        user={user}
        onCreateRoom={() => setShowCreateRoom(true)}
        onLogout={handleLogout}
        notifications={notifCount}
      />

      {activeRoom ? (
        <ChatView
          key={activeRoom.room_id}
          token={token}
          user={user}
          room={activeRoom}
          onlineUsers={onlineUsers}
          toast={addToast}
        />
      ) : (
        <div className="chat-main">
          <div className="empty-state">
            <div className="empty-icon">⚡</div>
            <div className="empty-title">Welcome to Nexus</div>
            <div className="empty-sub">Select a room from the sidebar to start chatting.</div>
          </div>
        </div>
      )}

      {showCreateRoom && (
        <CreateRoomModal
          token={token}
          onClose={() => setShowCreateRoom(false)}
          onCreated={handleRoomCreated}
        />
      )}

      <ToastContainer toasts={toasts} />
    </div>
  );
}
