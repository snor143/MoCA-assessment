import html
import json
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="超級市場大搜查 (Supermarket Shopping Adventure)",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- VISUAL CSS & SUPERMARKET IMMERSION STYLING ---
st.markdown(
    """
<style>
/* Full Supermarket Store Background Image with Blur Overlay */
.stApp {
    background: linear-gradient(rgba(245, 247, 248, 0.88), rgba(245, 247, 248, 0.88)),
                url('https://images.unsplash.com/photo-1578916171728-46686eac8d58?q=80&w=1600&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Supermarket Banner Style */
.market-banner {
    background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
    color: #FFFFFF !important;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}

/* NPC Staff & Speech Bubble Layout */
.npc-container {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 15px;
    margin-bottom: 20px;
}

.npc-avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid #2E7D32;
    background-color: #E8F5E9;
    object-fit: cover;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    flex-shrink: 0;
}

.speech-bubble {
    position: relative;
    background: #FFFFFF;
    border: 3px solid #2E7D32;
    border-radius: 18px;
    padding: 16px 20px;
    max-width: 450px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    font-size: 20px !important;
    color: #1C3125;
    font-weight: 600;
    line-height: 1.4 !important;
}

.speech-bubble:after {
    content: '';
    position: absolute;
    left: -14px;
    bottom: 25px;
    border-width: 8px 14px 8px 0;
    border-style: solid;
    border-color: transparent #2E7D32 transparent transparent;
    display: block;
    width: 0;
}

/* Supermarket Shelf / Display Card */
.market-shelf-card {
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #81C784;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.product-image {
    width: 220px;
    height: 220px;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid #C8E6C9;
    margin: 10px auto;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.item-badge {
    display: inline-block;
    background: #FF9800;
    color: #FFFFFF;
    font-weight: bold;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 18px;
    margin-bottom: 10px;
}

/* Input & Button Customization */
.stTextInput > div > div > input {
    font-size: 22px !important;
    height: 58px !important;
    border-radius: 12px !important;
}

.stButton>button {
    width: 100% !important;
    height: 60px !important;
    font-size: 22px !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    background-color: #2E7D32 !important;
    color: #FFFFFF !important;
    border: none !important;
    margin-top: 10px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.12) !important;
}

.stButton>button:hover {
    background-color: #1B5E20 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State
for key, value in {
    "stage": "intro",
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "moca_memory_score": 0,
    "reg_trial_1_items": [],
    "reg_trial_2_items": [],
    "recalled_free_items": [],
    "missed_items": [],
    "cued_current_index": 0,
    "cued_sub_step": "category",
    "recalled_cued_items": {},
    "recalled_choice_items": {},
    "game1_data": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- GAME DATA ---
MEMORY_ITEMS = [
    {"id": "mem_1", "name": "雪櫃", "category": "一種電器", "options": ["雪櫃", "風扇", "電視"]},
    {"id": "mem_2", "name": "郵局", "category": "一種建築物", "options": ["消防局", "郵局", "醫院"]},
    {"id": "mem_3", "name": "榕樹", "category": "一種植物", "options": ["橡樹", "榕樹", "松樹"]},
    {"id": "mem_4", "name": "塑膠", "category": "一種物料", "options": ["紙張", "金屬", "塑膠"]},
    {"id": "mem_5", "name": "藍色", "category": "一種顏色", "options": ["藍色", "紅色", "綠色"]},
]

NAMING_ITEMS = [
    {
        "id": "item_1",
        "tier": "Warmup",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTa95wEIgRD64bergbVn9BgZ_w-Ia6eshD8OhL3ezEV1w&s=10",
        "primary_name": "蝴蝶",
        "acceptable_synonyms": ["蝴蝶", "呢個係蝴蝶", "這是蝴蝶", "呢隻係蝴蝶"],
        "moca_weight": 1,
        "story": "剛剛在超市外面看到這東西",
    },
    {
        "id": "item_2",
        "tier": "Moderate",
        "image_url": "https://cdn.vectorstock.com/i/750p/77/18/a-whimsical-black-and-white-line-drawing-vector-62527718.avif",
        "primary_name": "八爪魚",
        "acceptable_synonyms": ["八爪魚", "呢個係八爪魚", "這是八爪魚", "呢隻係八爪魚", "章魚"],
        "moca_weight": 1,
        "story": "進入超市後，檔主向你展示了這樣東西",
    },
    {
        "id": "item_3",
        "tier": "Low",
        "image_url": "https://www.publicdomainpictures.net/pictures/190000/velka/sloth-drawing.jpg",
        "primary_name": "樹懶",
        "acceptable_synonyms": ["樹懶", "呢個係樹懶", "這是樹懶", "呢隻係樹懶"],
        "moca_weight": 1,
        "story": "貨架上有一張圖片",
    },
]

# --- GAME 1 HTML CODE ---
GAME1_HTML = """
<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>街市接線遊戲</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }

  html, body {
    font-family: "Noto Sans TC", "PingFang HK", "Microsoft JhengHei", sans-serif;
    background: #2A1810;
    color: #2B1A08;
    overflow: hidden;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    font-size: 16px;
  }

  #game-wrap {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    touch-action: none;
  }

  #bg {
    position: absolute;
    inset: 0;
    background-color: #F5E6C8;
    background-image:
      radial-gradient(circle at 15% 25%, rgba(122, 31, 31, 0.08) 0%, transparent 45%),
      radial-gradient(circle at 85% 75%, rgba(212, 160, 23, 0.12) 0%, transparent 50%),
      repeating-linear-gradient(88deg,
        rgba(90, 40, 20, 0.04) 0 2px,
        transparent 2px 8px);
    pointer-events: none;
  }

  #canvas {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: 1;
    pointer-events: none;
  }

  .coin {
    position: absolute;
    cursor: grab;
    user-select: none;
    z-index: 10;
    touch-action: none;
    transition: transform 0.15s ease;
    filter: drop-shadow(0 3px 5px rgba(60, 30, 10, 0.4));
  }

  .coin.dragging {
    z-index: 100;
    transform: scale(1.12);
  }

  .coin.connected {
    filter: drop-shadow(0 0 12px rgba(255, 215, 0, 0.7))
            drop-shadow(0 0 20px rgba(255, 215, 0, 0.4))
            drop-shadow(0 3px 5px rgba(60, 30, 10, 0.35));
  }

  .coin.highlight {
    filter: drop-shadow(0 0 14px rgba(255, 215, 0, 0.85))
            drop-shadow(0 0 24px rgba(255, 215, 0, 0.55))
            drop-shadow(0 3px 5px rgba(60, 30, 10, 0.35));
    transform: scale(1.08);
  }

  .coin svg {
    width: 100%; height: 100%;
    pointer-events: none;
    display: block;
  }

  #footer {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    padding: 14px 18px;
    background: linear-gradient(180deg,
      rgba(245, 230, 200, 0.94) 0%,
      rgba(232, 212, 168, 0.98) 100%);
    border-top: 3px solid #7A1F1F;
    box-shadow: 0 -2px 0 #D4A017;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    z-index: 200;
  }

  #hint {
    font-size: 20px;
    font-weight: 700;
    color: #7A1F1F;
    width: 100%;
    text-align: center;
    line-height: 1.4;
  }

  #footer-buttons {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn {
    font-family: inherit;
    font-size: 20px;
    font-weight: 900;
    padding: 10px 18px;
    border: 3px solid #5A1515;
    border-radius: 10px;
    background: linear-gradient(180deg, #A83232 0%, #7A1F1F 100%);
    color: #F5E6C8;
    cursor: pointer;
    min-width: 90px;
    box-shadow: 0 3px 0 #5A1515;
  }

  .btn:active:not(:disabled) {
    transform: translateY(2px);
    box-shadow: 0 1px 0 #5A1515;
  }

  .btn:disabled {
    background: #C9B99A;
    border-color: #8A7A58;
    color: #6A5A40;
    cursor: not-allowed;
    box-shadow: 0 3px 0 #8A7A58;
  }

  .btn.secondary {
    background: linear-gradient(180deg, #F5E6C8 0%, #E8D4A8 100%);
    color: #7A1F1F;
    box-shadow: 0 3px 0 #7A1F1F;
  }

  #finish-popup {
    position: fixed;
    inset: 0;
    background: rgba(42,24,16,0.85);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 999999;
    padding: 24px;
  }

  #finish-popup.show {
    display: flex !important;
  }

  #finish-card {
    background: linear-gradient(180deg, #F5E6C8, #E8D4A8);
    border: 6px solid #7A1F1F;
    border-radius: 24px;
    padding: 28px 36px;
    max-width: 450px;
    text-align: center;
    box-shadow: 0 0 0 8px #D4A017, 0 30px 80px rgba(0,0,0,0.6);
    animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @keyframes popIn {
    0%   { opacity: 0; transform: scale(0.7); }
    100% { opacity: 1; transform: scale(1); }
  }

  #finish-card h2 {
    font-size: 28px;
    color: #7A1F1F;
    margin-bottom: 12px;
  }

  #finish-card p {
    font-size: 24px;
    color: #5A4030;
    line-height: 1.6;
  }
</style>
</head>
<body>

<div id="game-wrap">
  <div id="bg"></div>
  <svg id="canvas" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
    <g id="lines-layer"></g>
  </svg>
</div>

<div id="footer">
  <div id="hint">💡硬幣與紙幣交錯連接<br> 例： 1 元硬幣 → 10 元紙幣 → 2 元硬幣 → …… → 100 元紙幣</div>
  <div id="footer-buttons">
    <button class="btn secondary" id="undo-btn" disabled>↩️ 撤銷</button>
    <button class="btn" id="restart-btn">🔄 重新開始</button>
  </div>
</div>

<div id="finish-popup">
  <div id="finish-card">
    <h2>✅ 完成啦！</h2>
    <p>請拉向下撳<br>「➡️ 去下一關」</p>
  </div>
</div>

<script>
function injectValueIntoStreamlitWidget(text) {
  try {
    const win = window.parent;
    const currentUrl = new URL(win.location.href);
    currentUrl.searchParams.set("game1_result", text);
    win.history.replaceState({}, "", currentUrl.toString());
    console.log("✅ 已寫入 URL：", currentUrl.toString());
  } catch (e) {
    console.log("❌ URL 寫入失敗：", e);
    try {
      const doc = window.parent.document;
      const inputs = doc.querySelectorAll('input[type="text"], textarea');
      if (inputs.length > 0) {
        const target = inputs[0];
        const setter = Object.getOwnPropertyDescriptor(
          window.HTMLInputElement.prototype, "value"
        ).set;
        setter.call(target, text);
        target.dispatchEvent(new Event("input", { bubbles: true }));
        target.dispatchEvent(new Event("change", { bubbles: true }));
        console.log("✅ Fallback：已注入 text_input");
      }
    } catch (e2) {
      console.log("❌ Fallback 都失敗：", e2);
    }
  }
}

const ITEMS = [
  { id: "1d",   type: "coin",  text: "$1",   value: 1,  c1: "#F0D580", c2: "#B08F2E", c3: "#8A6F1E" },
  { id: "10b",  type: "bill",  text: "$10",  value: 10, c1: "#C9A0DC", c2: "#9B59B6", c3: "#6A3B8A" },
  { id: "2d",   type: "coin",  text: "$2",   value: 2,  c1: "#F0D580", c2: "#B08F2E", c3: "#8A6F1E" },
  { id: "20b",  type: "bill",  text: "$20",  value: 20, c1: "#8AB6E8", c2: "#4A7BC4", c3: "#2D4A8A" },
  { id: "5d",   type: "coin",  text: "$5",   value: 5,  c1: "#E8E8E8", c2: "#9A9A9A", c3: "#6A6A6A" },
  { id: "50b",  type: "bill",  text: "$50",  value: 50, c1: "#A0D9A0", c2: "#4A8A4E", c3: "#2D5A30" },
  { id: "10d",  type: "coin",  text: "$10",  value: 10, c1: "#D4B584", c2: "#8B6F3A", c3: "#6A4F28" },
  { id: "100b", type: "bill",  text: "$100", value: 100,c1: "#E88A8A", c2: "#C0392B", c3: "#7A1F1F" },
];

const CORRECT_SEQUENCE = ["1d", "10b", "2d", "20b", "5d", "50b", "10d", "100b"];
const TARGET_CONNECTIONS = ITEMS.length - 1;

const COIN_SIZE = 60;
const BILL_W = 85;
const BILL_H = 55;
const FOOTER_H = 150;

const FALLBACK_LAYOUT = [
  { id: "1d",   x: 0.25, y: 0.18 },
  { id: "10b",  x: 0.50, y: 0.15 },
  { id: "2d",   x: 0.75, y: 0.20 },
  { id: "50b",  x: 0.22, y: 0.45 },
  { id: "5d",   x: 0.50, y: 0.48 },
  { id: "20b",  x: 0.78, y: 0.45 },
  { id: "10d",  x: 0.22, y: 0.72 },
  { id: "100b", x: 0.55, y: 0.75 },
];

function getSizes() {
  return { coinSize: COIN_SIZE, billW: BILL_W, billH: BILL_H, footerH: FOOTER_H };
}

let SIZES = getSizes();

function getItemSize(item) {
  return item.type === "coin"
    ? { w: SIZES.coinSize, h: SIZES.coinSize }
    : { w: SIZES.billW, h: SIZES.billH };
}

let state = {
  items: [],
  connections: [],
  undoCount: 0,
  startTime: null,
  dragging: null,
  dragStart: null,
  currentPath: null,
};

function cross(o, a, b) {
  return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
}

function segmentsIntersect(a, b, c, d) {
  const d1 = cross(c, d, a);
  const d2 = cross(c, d, b);
  const d3 = cross(a, b, c);
  const d4 = cross(a, b, d);
  return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
         ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
}

function itemCenter(item) {
  return { x: item.x + item.w / 2, y: item.y + item.h / 2 };
}

function isInsideItem(px, py, item) {
  const c = itemCenter(item);
  const r = Math.max(item.w, item.h) / 2 + 15;
  return Math.hypot(px - c.x, py - c.y) <= r;
}

function willCrossExisting(from, to) {
  const a = itemCenter(from);
  const b = itemCenter(to);

  for (const conn of state.connections) {
    if (conn.from === from.id || conn.to === from.id) continue;
    if (conn.from === to.id || conn.to === to.id) continue;

    const c = state.items.find(x => x.id === conn.from);
    const d = state.items.find(x => x.id === conn.to);
    if (!c || !d) continue;

    if (segmentsIntersect(a, b, itemCenter(c), itemCenter(d))) {
      return true;
    }
  }
  return false;
}

function generateLayout(W, H) {
  for (let attempt = 0; attempt < 2000; attempt++) {
    const placed = [];
    let ok = true;

    for (let i = 0; i < ITEMS.length; i++) {
      const item = ITEMS[i];
      const size = getItemSize(item);
      let x, y, tries = 0, found = false;
      const minDist = Math.max(size.w, size.h) + 20;

      while (tries < 200) {
        const margin = 20;
        x = size.w / 2 + margin + Math.random() * (W - size.w - margin * 2);
        y = size.h / 2 + margin + Math.random() * (H - size.h - margin * 2);

        const conflict = placed.some(p => {
          const dx = p.x - x;
          const dy = p.y - y;
          return Math.hypot(dx, dy) < Math.max(minDist, p.minDist);
        });

        if (!conflict) { found = true; break; }
        tries++;
      }

      if (!found) { ok = false; break; }
      placed.push({ x, y, minDist });
    }

    if (!ok) continue;

    const candidate = ITEMS.map((item, i) => {
      const size = getItemSize(item);
      return {
        ...item,
        w: size.w, h: size.h,
        x: placed[i].x - size.w / 2,
        y: placed[i].y - size.h / 2,
        connectedFrom: false, connectedTo: false, el: null,
      };
    });

    if (sequenceHasNoCrossing(candidate, CORRECT_SEQUENCE)) return candidate;
  }

  return ITEMS.map(item => {
    const slot = FALLBACK_LAYOUT.find(s => s.id === item.id);
    const size = getItemSize(item);
    return {
      ...item,
      w: size.w, h: size.h,
      x: slot.x * W - size.w / 2,
      y: slot.y * H - size.h / 2,
      connectedFrom: false, connectedTo: false, el: null,
    };
  });
}

function sequenceHasNoCrossing(items, seq) {
  const lines = [];
  for (let i = 0; i < seq.length - 1; i++) {
    const a = items.find(c => c.id === seq[i]);
    const b = items.find(c => c.id === seq[i + 1]);
    if (!a || !b) return false;
    lines.push({ a: itemCenter(a), b: itemCenter(b) });
  }

  for (let i = 0; i < lines.length; i++) {
    for (let j = i + 1; j < lines.length; j++) {
      if (j === i + 1) continue;
      if (segmentsIntersect(lines[i].a, lines[i].b, lines[j].a, lines[j].b)) {
        return false;
      }
    }
  }

  return true;
}

function coinSvg(item) {
  const gid = "g-" + item.id + "-" + Math.random().toString(36).slice(2, 6);
  const sid = "s-" + item.id + "-" + Math.random().toString(36).slice(2, 6);
  const s = item.w;
  return `
    <svg viewBox="0 0 200 200" width="${s}" height="${s}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="${gid}" cx="35%" cy="30%" r="80%">
          <stop offset="0%" stop-color="#FFFBE8"/>
          <stop offset="25%" stop-color="${item.c1}"/>
          <stop offset="70%" stop-color="${item.c2}"/>
          <stop offset="100%" stop-color="${item.c3}"/>
        </radialGradient>
        <linearGradient id="${sid}" x1="20%" y1="10%" x2="80%" y2="90%">
          <stop offset="0%" stop-color="#FFF" stop-opacity=".5"/>
          <stop offset="50%" stop-color="#FFF" stop-opacity="0"/>
          <stop offset="100%" stop-color="#000" stop-opacity=".15"/>
        </linearGradient>
      </defs>
      <circle cx="100" cy="100" r="98" fill="${item.c3}" opacity=".7"/>
      <circle cx="100" cy="100" r="94" fill="url(#${gid})" stroke="${item.c3}" stroke-width="2.5"/>
      <circle cx="100" cy="100" r="88" fill="none" stroke="${item.c3}" stroke-width="2" stroke-dasharray="2 3" opacity=".7"/>
      <circle cx="100" cy="100" r="78" fill="none" stroke="${item.c2}" stroke-width="1.5" opacity=".6"/>
      <circle cx="100" cy="100" r="94" fill="url(#${sid})" opacity=".8"/>
      <text x="100" y="118" text-anchor="middle"
            font-family="Arial Black, sans-serif" font-size="65" font-weight="900"
            fill="#2B1A08">${item.text}</text>
      <ellipse cx="66" cy="58" rx="26" ry="16" fill="#FFF" opacity=".55" transform="rotate(-25 66 58)"/>
    </svg>
  `;
}

function billSvg(item) {
  const gid = "g-" + item.id + "-" + Math.random().toString(36).slice(2, 6);
  const w = item.w, h = item.h;
  return `
    <svg viewBox="0 0 200 130" width="${w}" height="${h}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="${gid}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="${item.c1}"/>
          <stop offset="50%" stop-color="${item.c2}"/>
          <stop offset="100%" stop-color="${item.c3}"/>
        </linearGradient>
      </defs>
      <rect x="4" y="4" width="192" height="122" rx="6" fill="url(#${gid})" stroke="${item.c3}" stroke-width="3"/>
      <rect x="14" y="14" width="172" height="102" rx="4" fill="none" stroke="${item.c1}" stroke-width="2" opacity="0.6"/>
      <text x="100" y="82" text-anchor="middle"
            font-family="Arial Black, sans-serif" font-size="55" font-weight="900"
            fill="#2B1A08" stroke="#FFF" stroke-width="1" paint-order="stroke fill">${item.text}</text>
      <circle cx="30" cy="30" r="8" fill="${item.c3}" opacity="0.4"/>
      <circle cx="170" cy="100" r="8" fill="${item.c3}" opacity="0.4"/>
    </svg>
  `;
}

function init() {
  SIZES = getSizes();

  const wrap = document.getElementById("game-wrap");
  const W = wrap.clientWidth;
  const H = wrap.clientHeight - SIZES.footerH;

  const svg = document.getElementById("canvas");
  svg.setAttribute("width", W);
  svg.setAttribute("height", wrap.clientHeight);
  svg.setAttribute("viewBox", `0 0 ${W} ${wrap.clientHeight}`);

  state.items = generateLayout(W, H);

  state.items.forEach(item => {
    const el = document.createElement("div");
    el.className = "coin";
    el.style.left = item.x + "px";
    el.style.top = item.y + "px";
    el.style.width = item.w + "px";
    el.style.height = item.h + "px";
    el.innerHTML = item.type === "coin" ? coinSvg(item) : billSvg(item);
    el.dataset.itemId = item.id;
    el.addEventListener("pointerdown", onItemPointerDown);
    wrap.appendChild(el);
    item.el = el;
  });

  document.getElementById("undo-btn").addEventListener("click", undo);
  document.getElementById("restart-btn").addEventListener("click", restart);

  state.startTime = performance.now();
}

function onItemPointerDown(e) {
  e.preventDefault();
  const id = e.currentTarget.dataset.itemId;
  const item = state.items.find(x => x.id === id);
  if (!item || item.connectedFrom) return;

  item.el.classList.add("dragging");
  state.dragging = item;
  state.dragStart = performance.now();

  state.currentPath = [];

  const a = itemCenter(item);
  const layer = document.getElementById("lines-layer");

  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", `M ${a.x} ${a.y}`);
  path.setAttribute("stroke", "#A83232");
  path.setAttribute("stroke-width", "6");
  path.setAttribute("stroke-linecap", "round");
  path.setAttribute("stroke-linejoin", "round");
  path.setAttribute("fill", "none");
  path.setAttribute("opacity", "0.9");
  path.id = "live-path";
  layer.appendChild(path);

  state.currentPath.push([a.x, a.y]);

  document.addEventListener("pointermove", onPointerMove);
  document.addEventListener("pointerup", onPointerUp);
}

function onPointerMove(e) {
  if (state.dragging && state.currentPath) {
    state.currentPath.push([e.clientX, e.clientY]);

    const path = document.getElementById("live-path");
    if (path) {
      const d = "M " + state.currentPath.map(p => `${p[0]} ${p[1]}`).join(" L ");
      path.setAttribute("d", d);
    }
  }

  state.items.forEach(item => {
    item.el.classList.remove("highlight");
    if (!item.connectedTo && item !== state.dragging &&
        isInsideItem(e.clientX, e.clientY, item)) {
      item.el.classList.add("highlight");
    }
  });
}

function onPointerUp(e) {
  const from = state.dragging;
  if (!from) return;

  from.el.classList.remove("dragging");
  state.items.forEach(item => item.el.classList.remove("highlight"));

  const target = state.items.find(item =>
    !item.connectedTo && item !== from && isInsideItem(e.clientX, e.clientY, item)
  );

  if (target) {
    makeConnection(from, target, state.dragStart);
  } else {
    const livePath = document.getElementById("live-path");
    if (livePath) livePath.remove();
  }

  state.dragging = null;
  state.dragStart = null;
  state.currentPath = null;
  document.removeEventListener("pointermove", onPointerMove);
  document.removeEventListener("pointerup", onPointerUp);
}

function makeConnection(from, to, startTime) {
  const time = (performance.now() - startTime) / 1000;
  const crosses = willCrossExisting(from, to);

  const livePath = document.getElementById("live-path");
  if (livePath) {
    livePath.id = "";
    livePath.classList.add("permanent-line");
  }

  state.connections.push({ from: from.id, to: to.id, time, crosses });
  from.connectedFrom = true;
  to.connectedTo = true;
  from.el.classList.add("connected");
  to.el.classList.add("connected");

  document.getElementById("undo-btn").disabled = false;

  if (state.connections.length === TARGET_CONNECTIONS) {
    document.getElementById("finish-popup").classList.add("show");
    document.getElementById("hint").textContent = "✅ 完成啦！請拉向下撳「➡️ 去下一關」";

    const seq = state.connections.map(c => c.from);
    seq.push(state.connections[state.connections.length - 1].to);

    const isOrderCorrect = JSON.stringify(seq) === JSON.stringify(CORRECT_SEQUENCE);
    const hasCrossing = state.connections.some(c => c.crosses);
    const isCorrect = isOrderCorrect && !hasCrossing;

    const resultData = {
      is_correct: isCorrect,
      sequence: seq,
      undo_count: state.undoCount,
      has_crossing: hasCrossing,
      is_order_correct: isOrderCorrect,
    };

    console.log("=== 遊戲結果 ===");
    console.log(JSON.stringify(resultData, null, 2));

    injectValueIntoStreamlitWidget(JSON.stringify(resultData));
  }
}

function undo() {
  if (state.connections.length === 0) return;
  state.connections.pop();

  const layer = document.getElementById("lines-layer");
  if (layer.lastChild) layer.removeChild(layer.lastChild);

  const still = new Set();
  state.connections.forEach(c => { still.add(c.from); still.add(c.to); });
  state.items.forEach(item => {
    item.connectedFrom = state.connections.some(x => x.from === item.id);
    item.connectedTo = state.connections.some(x => x.to === item.id);
    item.el.classList.toggle("connected", still.has(item.id));
  });

  state.undoCount++;
  document.getElementById("undo-btn").disabled = state.connections.length === 0;

  if (state.connections.length < TARGET_CONNECTIONS) {
    document.getElementById("finish-popup").classList.remove("show");
    document.getElementById("hint").textContent = "💡硬幣與紙幣交錯連接<br> 例： 1 元硬幣 → 10 元紙幣 → 2 元硬幣 → …… → 100 元紙幣";
  }
}

function restart() {
  document.querySelectorAll(".coin").forEach(el => el.remove());
  document.getElementById("lines-layer").innerHTML = "";
  document.getElementById("finish-popup").classList.remove("show");
  document.getElementById("hint").textContent = "💡硬幣與紙幣交錯連接<br> 例： 1 元硬幣 → 10 元紙幣 → 2 元硬幣 → …… → 100 元紙幣";

  state = {
    items: [], connections: [], undoCount: 0,
    startTime: null, dragging: null, dragStart: null,
    currentPath: null,
  };
  init();
}

window.addEventListener("load", init);
window.addEventListener("resize", () => {
  if (state.items.length && state.connections.length === 0) {
    restart();
  }
});
</script>

</body>
</html>
"""

# --- UI COMPONENT FUNCTIONS ---

def render_staff_npc(dialogue_text, staff_type="manager", staff_name="店長阿Ming"):
    """Renders the Store Staff NPC avatar alongside a retro speech bubble."""
    avatar_urls = {
        "manager": "https://cdn-icons-png.flaticon.com/512/4140/4140047.png",
        "cashier": "https://cdn-icons-png.flaticon.com/512/3052/3052217.png",
        "assistant": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    }
    avatar_src = avatar_urls.get(staff_type, avatar_urls["manager"])

    st.markdown(
        f"""
    <div class="npc-container">
        <img src="{avatar_src}" class="npc-avatar" alt="{staff_name}">
        <div class="speech-bubble">
            <b>{staff_name}：</b><br>「{dialogue_text}」
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_instruction_speaker_component(instruction_text, key_suffix):
    """Voice speaker component for staff NPC dialogue."""
    escaped_text = html.escape(instruction_text).replace("'", "\\'")
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; display:flex; justify-content:center; }}
    button {{ width:100%; max-width:340px; height:44px; font-size:16px; font-weight:bold; color:#FFFFFF !important; background:#FF9800; border:none; border-radius:8px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.15); }}
    button:hover {{ background:#E65100; }}
    </style></head><body>
    <button id="inst_btn_{key_suffix}" type="button">🔊 聽店長語音指引 (Listen)</button>

    <script>
    const text = "{escaped_text}";
    const btn = document.getElementById('inst_btn_{key_suffix}');

    function speakInstruction() {{
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-HK';
      utterance.rate = 0.9;

      const voices = window.speechSynthesis.getVoices();
      const hkVoice = voices.find(v => v.lang === 'zh-HK' || v.lang === 'yue-Hant-HK' || v.lang.includes('HK'));
      if (hkVoice) utterance.voice = hkVoice;

      window.speechSynthesis.speak(utterance);
    }}

    btn.onclick = speakInstruction;
    </script></body></html>
    """,
        height=50,
    )


def render_audio_speaker_component(words_list, key_suffix):
    """Audio broadcaster for store PA shopping list system."""
    words_js_array = str(words_list)
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; text-align:center; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#0D47A1; border:none; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#002171; }}
    .status {{ font-size:15px; margin-top:6px; font-weight:bold; color:#0D47A1; }}
    </style></head><body>
    <button id="speak_btn_{key_suffix}" type="button">📢 聽超市廣播</button>
    <div class="status" id="status_{key_suffix}">點擊收聽</div>

    <script>
    const words = {words_js_array};
    const btn = document.getElementById('speak_btn_{key_suffix}');
    const status = document.getElementById('status_{key_suffix}');
    let isPlaying = false;

    if ('speechSynthesis' in window) {{
      window.speechSynthesis.onvoiceschanged = () => {{ window.speechSynthesis.getVoices(); }};
    }}

    function speakWords() {{
      if (!('speechSynthesis' in window)) {{
        status.textContent = '❌ 不支援語音';
        return;
      }}
      if (isPlaying) return;

      window.speechSynthesis.cancel();
      isPlaying = true;
      btn.disabled = true;
      btn.style.background = '#757575';
      status.textContent = '🔊 廣播中...';

      let index = 0;

      function speakNext() {{
        if (index >= words.length) {{
          status.textContent = '✅ 廣播完畢';
          isPlaying = false;
          btn.disabled = false;
          btn.style.background = '#0D47A1';
          btn.textContent = '🔄 重播 (Replay)';
          return;
        }}

        const utterance = new SpeechSynthesisUtterance(words[index]);
        utterance.lang = 'zh-HK';
        utterance.rate = 0.85;

        const voices = window.speechSynthesis.getVoices();
        const hkVoice = voices.find(v => v.lang === 'zh-HK' || v.lang === 'yue-Hant-HK' || v.lang.includes('HK'));
        if (hkVoice) utterance.voice = hkVoice;

        utterance.onend = () => {{
          index++;
          if (index < words.length) setTimeout(speakNext, 1000);
          else {{
            status.textContent = '✅ 廣播完畢';
            isPlaying = false;
            btn.disabled = false;
            btn.style.background = '#0D47A1';
            btn.textContent = '🔄 重播 (Replay)';
          }}
        }};

        utterance.onerror = () => {{ index++; setTimeout(speakNext, 1000); }};
        window.speechSynthesis.speak(utterance);
      }}

      speakNext();
    }}

    btn.onclick = speakWords;
    </script></body></html>
    """,
        height=95,
    )


def render_mic_component(key_suffix, continuous_mode=False):
    """Voice speech-to-text recording input component."""
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#2E7D32; border:none; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#1B5E20; }}
    .status {{ font-size:15px; text-align:center; margin-top:6px; color:#2E7D32; font-weight:bold; }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 按此語音回答 (Speak)</button>
    <div class="status" id="status_{key_suffix}">請點擊按鈕開始說話</div>

    <script>
    const btn = document.getElementById('mic_{key_suffix}');
    const status = document.getElementById('status_{key_suffix}');
    let recognition = null;
    let isListening = false;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      recognition.lang = 'zh-HK';
      recognition.continuous = {'true' if continuous_mode else 'false'};
      recognition.interimResults = false;

      recognition.onstart = () => {{
        isListening = true;
        btn.style.background = '#C62828';
        btn.textContent = '🛑 聆聽中...請說話';
        status.textContent = '正在錄音...';
      }};

      recognition.onresult = (e) => {{
        let text = '';
        for (let i = e.resultIndex; i < e.results.length; ++i) {{
          text += e.results[i][0].transcript;
        }}
        text = text.trim();
        if (text) {{
          try {{
            const win = window.parent;
            const doc = win.document;
            const inputs = doc.querySelectorAll('input[type="text"], textarea');
            if (inputs.length > 0) {{
              const target = inputs[inputs.length - 1];
              const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
              setter.call(target, text);
              target.dispatchEvent(new Event('input', {{ bubbles: true }}));
              target.dispatchEvent(new Event('change', {{ bubbles: true }}));
              status.textContent = '✅ 已識別：' + text;
            }}
          }} catch(e) {{
            status.textContent = '識別完成：' + text;
          }}
        }}
      }};

      recognition.onerror = (e) => {{
        status.textContent = '❌ 語音識別出錯，請重試';
        resetBtn();
      }};

      recognition.onend = () => {{
        resetBtn();
      }};
    }} else {{
      btn.disabled = true;
      btn.style.background = '#757575';
      status.textContent = '❌ 瀏覽器不支援語音輸入';
    }}

    function resetBtn() {{
      isListening = false;
      btn.style.background = '#2E7D32';
      btn.textContent = '🎤 按此語音回答 (Speak)';
    }}

    btn.onclick = () => {{
      if (!recognition) return;
      if (isListening) {{
        recognition.stop();
      }} else {{
        recognition.start();
      }}
    }};
    </script></body></html>
    """,
        height=95,
    )


# --- STAGE CONTROLLER & RENDERERS ---

st.markdown(
    """
<div class="market-banner">
    <h1 style="margin:0; font-size: 30px;">🛒 超級市場大搜查</h1>
    <p style="margin:5px 0 0 0; font-size: 18px;">Supermarket Cognitive Assessment Adventure</p>
</div>
""",
    unsafe_allow_html=True,
)

# STAGE 0: INTRO
if st.session_state.stage == "intro":
    intro_text = "歡迎黎到超級市場！今天店長需要你協助完成幾項特別任務，順便購物，準備好就開始啦！"
    render_staff_npc(intro_text, staff_type="manager", staff_name="店長阿Ming")
    render_instruction_speaker_component(intro_text, "intro")

    if st.button("🚀 開始搜查任務 (Start Adventure)"):
        st.session_state.stage = "mem_reg_intro"
        st.rerun()

# STAGE 1.1: MEMORY REGISTRATION INTRO
elif st.session_state.stage == "mem_reg_intro":
    text = "首先，廣播會讀出 5 樣需要買嘅物品，請仔細聽並記住佢哋！廣播完畢後請重複說出物品。"
    render_staff_npc(text, staff_type="manager")
    render_instruction_speaker_component(text, "mem_reg_intro")

    if st.button("📢 進入聽力廣播 (Listen Shopping List)"):
        st.session_state.stage = "mem_reg_trial_1"
        st.rerun()

# STAGE 1.2: MEMORY REGISTRATION TRIAL 1
elif st.session_state.stage == "mem_reg_trial_1":
    text = "請點擊按鈕收聽第一輪超市廣播，然後將記得嘅物品說出或填寫在下方："
    render_staff_npc(text, staff_type="manager")

    words = [item["name"] for item in MEMORY_ITEMS]
    render_audio_speaker_component(words, "trial_1")

    st.markdown("---")
    render_mic_component("trial_1", continuous_mode=True)

    user_input = st.text_input(
        "請輸入或語音回答記得的物品 (可以用空格或逗號隔開)：", key="input_trial_1"
    )

    if st.button("➡️ 提交第 1 輪記憶"):
        st.session_state.reg_trial_1_items = [
            w.strip() for w in user_input.replace("，", " ").replace(",", " ").split() if w.strip()
        ]
        st.session_state.stage = "mem_reg_trial_2"
        st.rerun()

# STAGE 1.3: MEMORY REGISTRATION TRIAL 2
elif st.session_state.stage == "mem_reg_trial_2":
    text = "非常好！現在會再廣播多一次該 5 樣物品，請再次仔細聽並補充你記得的物品："
    render_staff_npc(text, staff_type="manager")

    words = [item["name"] for item in MEMORY_ITEMS]
    render_audio_speaker_component(words, "trial_2")

    st.markdown("---")
    render_mic_component("trial_2", continuous_mode=True)

    user_input = st.text_input(
        "請輸入或語音回答記得的物品 (可以用空格隔開)：", key="input_trial_2"
    )

    if st.button("➡️ 完成記憶學習，進入下一關"):
        st.session_state.reg_trial_2_items = [
            w.strip() for w in user_input.replace("，", " ").replace(",", " ").split() if w.strip()
        ]
        st.session_state.stage = "game_trail_making"
        st.rerun()

# STAGE 2: GAME STAGE (街市接線遊戲 / Trail Making Game)
elif st.session_state.stage == "game_trail_making":
    text = "好棒！現在請幫店長整理一下街市的錢幣。請依照『1元硬幣 → 10元紙幣 → 2元硬幣 → 20元紙幣...』交錯連接！"
    render_staff_npc(text, staff_type="cashier", staff_name="收銀員阿花")

    # 隱藏式 Input 用於接受來自 iframe URL/JS 的資料
    game1_res_raw = st.text_input("game1_result", key="game1_result_input", label_visibility="collapsed")

    # 檢查 URL query params 是否有結果
    query_params = st.query_params
    if "game1_result" in query_params:
        try:
            res_str = query_params["game1_result"]
            st.session_state.game1_data = json.loads(res_str)
        except Exception as e:
            pass
    elif game1_res_raw:
        try:
            st.session_state.game1_data = json.loads(game1_res_raw)
        except Exception as e:
            pass

    # 渲染連線遊戲 Component
    components.html(GAME1_HTML, height=620, scrolling=False)

    if st.session_state.game1_data:
        st.success("✅ 已順利完成接線挑戰！")

    if st.button("➡️ 去下一關 (Next Challenge)"):
        st.session_state.stage = "naming_intro"
        st.rerun()

# STAGE 3.1: NAMING INTRO
elif st.session_state.stage == "naming_intro":
    text = "接線任務完成得好好！現在請協助店長辨認幾樣在超市內出現的特別物品。"
    render_staff_npc(text, staff_type="manager")
    render_instruction_speaker_component(text, "naming_intro")

    if st.button("➡️ 開始辨認物品 (Start Naming Task)"):
        st.session_state.stage = "naming_task"
        st.session_state.current_item_index = 0
        st.session_state.item_start_time = time.time()
        st.rerun()

# STAGE 3.2: NAMING TASK
elif st.session_state.stage == "naming_task":
    idx = st.session_state.current_item_index
    item = NAMING_ITEMS[idx]

    text = f"第 {idx + 1} 樣物品：{item['story']}。請問這是什麼？"
    render_staff_npc(text, staff_type="assistant", staff_name="店員小傑")

    st.markdown(
        f"""
    <div class="market-shelf-card">
        <span class="item-badge">物品 {idx + 1} / {len(NAMING_ITEMS)}</span><br>
        <img src="{item['image_url']}" class="product-image" alt="Item Image"><br>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_mic_component(f"naming_{idx}")

    ans_input = st.text_input("請輸入或語音回答物品名稱：", key=f"naming_ans_{idx}")

    if st.button("➡️ 提交答案 (Submit Answer)"):
        rt = round(time.time() - (st.session_state.item_start_time or time.time()), 2)
        is_correct = any(syn in ans_input.strip() for syn in item["acceptable_synonyms"])

        if is_correct:
            st.session_state.moca_naming_score += item["moca_weight"]

        st.session_state.telemetry_logs.append(
            {
                "item_id": item["id"],
                "response": ans_input,
                "is_correct": is_correct,
                "response_time": rt,
            }
        )

        if idx + 1 < len(NAMING_ITEMS):
            st.session_state.current_item_index += 1
            st.session_state.item_start_time = time.time()
            st.rerun()
        else:
            st.session_state.stage = "mem_recall_free"
            st.rerun()

# STAGE 4.1: MEMORY FREE RECALL
elif st.session_state.stage == "mem_recall_free":
    text = "逛完超市啦！還記得剛才一開始廣播中需要購買的 5 樣物品嗎？請盡量說出或填寫出來："
    render_staff_npc(text, staff_type="manager")
    render_instruction_speaker_component(text, "mem_recall_free")

    render_mic_component("recall_free", continuous_mode=True)

    free_input = st.text_input("請輸入或語音回答記得的物品 (空格隔開)：", key="free_recall_input")

    if st.button("➡️ 提交自由回想答案"):
        recalled = [
            w.strip() for w in free_input.replace("，", " ").replace(",", " ").split() if w.strip()
        ]
        st.session_state.recalled_free_items = recalled

        target_names = [m["name"] for m in MEMORY_ITEMS]
        missed = [m for m in MEMORY_ITEMS if m["name"] not in recalled]
        st.session_state.missed_items = missed
        st.session_state.moca_memory_score = len(target_names) - len(missed)

        if missed:
            st.session_state.stage = "mem_recall_cued"
            st.session_state.cued_current_index = 0
            st.session_state.cued_sub_step = "category"
        else:
            st.session_state.stage = "report"
        st.rerun()

# STAGE 4.2: MEMORY CUED RECALL
elif st.session_state.stage == "mem_recall_cued":
    missed = st.session_state.missed_items
    c_idx = st.session_state.cued_current_index
    item = missed[c_idx]

    if st.session_state.cued_sub_step == "category":
        text = f"其中有一樣物品是『{item['category']}』，你記得是什麼嗎？"
        render_staff_npc(text, staff_type="manager")

        render_mic_component(f"cued_cat_{c_idx}")
        cued_ans = st.text_input("請回答類別提示物品：", key=f"cued_cat_ans_{c_idx}")

        if st.button("➡️ 提交類別提示答案"):
            if item["name"] in cued_ans:
                st.session_state.recalled_cued_items[item["id"]] = True
                if c_idx + 1 < len(missed):
                    st.session_state.cued_current_index += 1
                else:
                    st.session_state.stage = "report"
            else:
                st.session_state.recalled_cued_items[item["id"]] = False
                st.session_state.cued_sub_step = "choice"
            st.rerun()

    elif st.session_state.cued_sub_step == "choice":
        text = f"沒關係！請在下面選項中選出正確的物品："
        render_staff_npc(text, staff_type="manager")

        choice = st.radio("請選擇：", item["options"], key=f"choice_{c_idx}")

        if st.button("➡️ 提交選擇題答案"):
            st.session_state.recalled_choice_items[item["id"]] = choice == item["name"]
            if c_idx + 1 < len(missed):
                st.session_state.cued_current_index += 1
                st.session_state.cued_sub_step = "category"
            else:
                st.session_state.stage = "report"
            st.rerun()

# STAGE 5: REPORT & SUMMARY
elif st.session_state.stage == "report":
    st.balloons()
    text = "太棒了！你已經完成了今天所有的超級市場大搜查任務！這是你的測驗總結報告："
    render_staff_npc(text, staff_type="manager")

    st.markdown("### 📊 搜查任務評估報告 Summary Report")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("命名能力得分 (MoCA Naming)", f"{st.session_state.moca_naming_score} / 3")
    with col2:
        st.metric("自由回想得分 (MoCA Memory)", f"{st.session_state.moca_memory_score} / 5")

    st.markdown("---")
    st.markdown("#### 🎮 街市接線遊戲結果 Game 1 Result")
    g1 = st.session_state.game1_data
    if g1:
        st.json(g1)
    else:
        st.write("未取得遊戲數據。")

    st.markdown("---")
    st.markdown("#### 📋 物品命名反應數據 Naming Response Logs")
    df_logs = pd.DataFrame(st.session_state.telemetry_logs)
    st.dataframe(df_logs, use_container_width=True)

    if st.button("🔄 重新開始新體驗 (Restart Adventure)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
