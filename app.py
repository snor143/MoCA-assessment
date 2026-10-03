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

# --- GAME 1 HTML CODE (Coin Connect) ---
GAME1_HTML = """<!DOCTYPE html>
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
    padding: 12px 18px;
    background: linear-gradient(180deg,
      rgba(245, 230, 200, 0.94) 0%,
      rgba(232, 212, 168, 0.98) 100%);
    border-top: 3px solid #7A1F1F;
    box-shadow: 0 -2px 0 #D4A017;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    z-index: 200;
  }

  .btn {
    font-family: inherit;
    font-size: 22px;
    font-weight: 900;
    padding: 10px 22px;
    border: 3px solid #5A1515;
    border-radius: 10px;
    background: linear-gradient(180deg, #A83232 0%, #7A1F1F 100%);
    color: #F5E6C8;
    cursor: pointer;
    min-width: 110px;
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
    padding: 32px 40px;
    max-width: 450px;
    text-align: center;
    box-shadow: 0 0 0 8px #D4A017, 0 30px 80px rgba(0,0,0,0.6);
    animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @keyframes popIn {
    0%    { opacity: 0; transform: scale(0.7); }
    100% { opacity: 1; transform: scale(1); }
  }

  #finish-card h2 {
    font-size: 32px;
    color: #7A1F1F;
    margin-bottom: 12px;
  }

  #finish-card p {
    font-size: 30px;
    color: #5A4030;
    line-height: 1.6;
  }
</style>
</head>
<body>

<div id="game-wrap">
  <div id="bg"></div>
  <svg id="canvas" xmlns="http://www.w3.org/2000/svg"
       width="100%" height="100%">
    <g id="lines-layer"></g>
  </svg>
</div>

<div id="footer">
  <button class="btn secondary" id="undo-btn" disabled>↩️ 撤銷</button>
  <button class="btn" id="restart-btn">🔄 重新開始</button>
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
  } catch (e) {
    console.log("URL write failed:", e);
  }
}

const ITEMS = [
  { id: "1d",   type: "coin",  text: "$1",   value: 1,
    c1: "#F0D580", c2: "#B08F2E", c3: "#8A6F1E" },
  { id: "10b",  type: "bill",  text: "$10",  value: 10,
    c1: "#C9A0DC", c2: "#9B59B6", c3: "#6A3B8A" },
  { id: "2d",   type: "coin",  text: "$2",   value: 2,
    c1: "#F0D580", c2: "#B08F2E", c3: "#8A6F1E" },
  { id: "20b",  type: "bill",  text: "$20",  value: 20,
    c1: "#8AB6E8", c2: "#4A7BC4", c3: "#2D4A8A" },
  { id: "5d",   type: "coin",  text: "$5",   value: 5,
    c1: "#E8E8E8", c2: "#9A9A9A", c3: "#6A6A6A" },
  { id: "50b",  type: "bill",  text: "$50",  value: 50,
    c1: "#A0D9A0", c2: "#4A8A4E", c3: "#2D5A30" },
  { id: "10d",  type: "coin",  text: "$10",  value: 10,
    c1: "#D4B584", c2: "#8B6F3A", c3: "#6A4F28" },
  { id: "100b", type: "bill",  text: "$100", value: 100,
    c1: "#E88A8A", c2: "#C0392B", c3: "#7A1F1F" },
];

const CORRECT_SEQUENCE = ["1d", "10b", "2d", "20b", "5d", "50b", "10d", "100b"];
const TARGET_CONNECTIONS = ITEMS.length - 1;

const COIN_SIZE = 65;
const BILL_W = 90;
const BILL_H = 58;
const FOOTER_H = 75;

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

function segmentsIntersect(p1, p2, p3, p4) {
  const d1 = cross(p3, p4, p1);
  const d2 = cross(p3, p4, p2);
  const d3 = cross(p1, p2, p3);
  const d4 = cross(p1, p2, p4);

  if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
      ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
    return true;
  }
  return false;
}

function itemCenter(item) {
  return { x: item.x + item.w / 2, y: item.y + item.h / 2 };
}

function isInsideItem(px, py, item) {
  const c = itemCenter(item);
  const r = Math.max(item.w, item.h) / 2 + 15;
  return Math.hypot(px - c.x, py - c.y) <= r;
}

function checkPathCrossings(currentPath) {
  if (!currentPath || currentPath.length < 2) return false;

  for (let i = 0; i < currentPath.length - 3; i++) {
    const a1 = { x: currentPath[i][0], y: currentPath[i][1] };
    const a2 = { x: currentPath[i + 1][0], y: currentPath[i + 1][1] };

    for (let j = i + 2; j < currentPath.length - 1; j++) {
      if (i === 0 && j === currentPath.length - 2) continue;
      const b1 = { x: currentPath[j][0], y: currentPath[j][1] };
      const b2 = { x: currentPath[j + 1][0], y: currentPath[j + 1][1] };

      if (segmentsIntersect(a1, a2, b1, b2)) return true;
    }
  }

  for (const conn of state.connections) {
    const prevPath = conn.pathPoints;
    if (!prevPath || prevPath.length < 2) continue;

    for (let i = 0; i < currentPath.length - 1; i++) {
      const a1 = { x: currentPath[i][0], y: currentPath[i][1] };
      const a2 = { x: currentPath[i + 1][0], y: currentPath[i + 1][1] };

      for (let j = 0; j < prevPath.length - 1; j++) {
        const b1 = { x: prevPath[j][0], y: prevPath[j][1] };
        const b2 = { x: prevPath[j + 1][0], y: prevPath[j + 1][1] };

        const isEndpointTouch = (Math.hypot(a1.x - b1.x, a1.y - b1.y) < 15) ||
                                (Math.hypot(a1.x - b2.x, a1.y - b2.y) < 15) ||
                                (Math.hypot(a2.x - b1.x, a2.y - b1.y) < 15) ||
                                (Math.hypot(a2.x - b2.x, a2.y - b2.y) < 15);

        if (isEndpointTouch) continue;

        if (segmentsIntersect(a1, a2, b1, b2)) {
          return true;
        }
      }
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
        const margin = 30;
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
    const rect = document.getElementById("game-wrap").getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    state.currentPath.push([x, y]);

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
  
  const targetC = itemCenter(to);
  state.currentPath.push([targetC.x, targetC.y]);

  const crosses = checkPathCrossings(state.currentPath);

  const livePath = document.getElementById("live-path");
  if (livePath) {
    const snapD = "M " + state.currentPath.map(p => `${p[0]} ${p[1]}`).join(" L ");
    livePath.setAttribute("d", snapD);
    livePath.id = "";
    livePath.classList.add("permanent-line");
  }

  state.connections.push({
    from: from.id,
    to: to.id,
    time,
    crosses,
    pathPoints: [...state.currentPath]
  });

  from.connectedFrom = true;
  to.connectedTo = true;
  from.el.classList.add("connected");
  to.el.classList.add("connected");

  document.getElementById("undo-btn").disabled = false;

  if (state.connections.length === TARGET_CONNECTIONS) {
    document.getElementById("finish-popup").classList.add("show");

    const seq = state.connections.map(c => c.from);
    seq.push(state.connections[state.connections.length - 1].to);

    const isOrderCorrect = JSON.stringify(seq) === JSON.stringify(CORRECT_SEQUENCE);
    const hasCrossing = state.connections.some(c => c.crosses);
    
    const isCorrect = isOrderCorrect && !hasCrossing;
    const duration = (performance.now() - state.startTime) / 1000;

    const resultData = {
      is_correct: isCorrect,
      score: isCorrect ? 1 : 0,
      sequence: seq,
      undo_count: state.undoCount,
      has_crossing: hasCrossing,
      is_order_correct: isOrderCorrect,
      completion_time_sec: roundToTwo(duration)
    };

    injectValueIntoStreamlitWidget(JSON.stringify(resultData));
  }
}

function roundToTwo(num) {
    return +(Math.round(num + "e+2")  + "e-2");
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
  }
}

function restart() {
  document.querySelectorAll(".coin").forEach(el => el.remove());
  document.getElementById("lines-layer").innerHTML = "";
  document.getElementById("finish-popup").classList.remove("show");

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

# --- GAME 2 HTML CODE (Basket Drawing Game) ---
GAME2_HTML = """<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<title>畫購物籃</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    font-family: "Noto Sans TC", "PingFang HK", sans-serif;
    background: #F5E6C8;
    color: #2B1A08;
    overflow: hidden;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 0;
    font-size: 24px;
  }

  #wrap {
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 16px;
  gap: 12px;
  background: #FFF8E7; /* Outer card background */
  border-radius: 16px;
}
  #reference {
    background: linear-gradient(180deg, #FFF8E7, #F5E6C8);
    border: 4px solid #7A1F1F;
    border-radius: 14px;
    padding: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 28%;
    min-height: 120px;
    max-height: 160px;
    position: relative;
    flex-shrink: 0;
  }

  #reference::before {
    content: "📖 參考圖";
    position: absolute;
    top: 6px;
    left: 12px;
    font-size: 16px;
    font-weight: 700;
    color: #7A1F1F;
    opacity: 0.7;
  }

  #reference svg {
    height: 100%;
    max-height: 100%;
  }

  #canvas-wrap {
  flex: 1;
  background: #FFFEF8;
  border: 4px dashed #7A1F1F;
  border-radius: 14px;
  position: relative;
  box-shadow: inset 0 2px 8px rgba(90,21,21,0.1);
  min-height: 320px; /* Give it a concrete minimum height */
}

  #canvas-wrap::before {
    content: "✏️ 喺呢度畫";
    position: absolute;
    top: 6px;
    left: 12px;
    font-size: 16px;
    font-weight: 700;
    color: #7A1F1F;
    opacity: 0.5;
    pointer-events: none;
  }

  #canvas {
    width: 100%;
    height: 100%;
    cursor: crosshair;
    touch-action: none;
  }

  #footer {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-shrink: 0;
  }

  .btn {
    font-family: inherit;
    font-size: 22px;
    font-weight: 800;
    padding: 12px 28px;
    border: 4px solid #5A1515;
    border-radius: 14px;
    background: linear-gradient(180deg, #A83232, #7A1F1F);
    color: #F5E6C8;
    cursor: pointer;
    min-width: 140px;
    box-shadow: 0 4px 0 #5A1515, 0 6px 12px rgba(90,21,21,0.3);
  }

  .btn:hover {
    background: linear-gradient(180deg, #F0C952, #D4A017);
    color: #2B1A08;
    transform: translateY(-2px);
  }

  .btn.secondary {
    background: linear-gradient(180deg, #F5E6C8, #E8D4A8);
    color: #7A1F1F;
    box-shadow: 0 4px 0 #7A1F1F, 0 6px 12px rgba(90,21,21,0.2);
  }

  .btn:disabled {
    background: #C9B99A;
    border-color: #8A7A58;
    color: #6A5A40;
    cursor: not-allowed;
    box-shadow: 0 4px 0 #8A7A58;
  }

  #done-panel {
    position: fixed;
    inset: 0;
    background: rgba(42,24,16,0.9);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 999999;
    padding: 24px;
  }

  #done-panel.show { display: flex !important; }

  #done-card {
    background: linear-gradient(180deg, #F5E6C8, #E8D4A8);
    border: 6px solid #7A1F1F;
    border-radius: 24px;
    padding: 24px 32px;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
    text-align: center;
    box-shadow: 0 0 0 8px #D4A017, 0 30px 80px rgba(0,0,0,0.6);
  }

  #done-card h2 {
    font-size: 28px;
    color: #7A1F1F;
    margin-bottom: 8px;
  }

  #done-card p {
    font-size: 22px;
    color: #5A4030;
    margin-bottom: 16px;
  }

  #player-drawing {
    background: #FFFEF8;
    border: 4px solid #7A1F1F;
    border-radius: 12px;
    margin: 10px auto;
    padding: 8px;
    max-width: 280px;
    box-shadow: inset 0 2px 6px rgba(90,21,21,0.1);
  }

  #player-drawing img {
    width: 100%;
    display: block;
  }
</style>
</head>
<body>

  <div id="reference">
    <svg viewBox="0 0 280 280" xmlns="http://www.w3.org/2000/svg">
      <g stroke="#2B1A08" stroke-width="6" fill="none"
         stroke-linecap="round" stroke-linejoin="round">
        <rect x="60" y="100" width="140" height="140"/>
        <rect x="110" y="50" width="140" height="140"/>
        <line x1="60" y1="100" x2="110" y2="50"/>
        <line x1="200" y1="100" x2="250" y2="50"/>
        <line x1="60" y1="240" x2="110" y2="190"/>
        <line x1="200" y1="240" x2="250" y2="190"/>
      </g>
    </svg>
  </div>

  <div id="canvas-wrap">
    <canvas id="canvas"></canvas>
  </div>

  <div id="footer">
    <button class="btn secondary" id="clear-btn">🔄 清除</button>
    <button class="btn" id="done-btn" disabled>✅ 完成</button>
  </div>

<div id="done-panel">
  <div id="done-card">
    <h2>✅ 完成啦！</h2>
    <p>請拉向下撳<br>「➡️ 去下一關」</p>

    <div id="player-drawing">
      <img id="player-img" alt="玩家畫嘅購物籃">
    </div>
  </div>
</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

let isDrawing = false;
let hasDrawn = false;
let strokes = [];
let currentStroke = null;

function resizeCanvas() {
  const wrap = document.getElementById("canvas-wrap");
  const rect = wrap.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;

  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  canvas.style.width = rect.width + "px";
  canvas.style.height = rect.height + "px";

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.lineWidth = 3;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = "#2B1A08";

  redraw();
}

window.addEventListener("load", resizeCanvas);
window.addEventListener("resize", resizeCanvas);

function getPos(e) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
  };
}

function startDraw(e) {
  e.preventDefault();
  isDrawing = true;
  const pos = getPos(e);
  currentStroke = [pos];
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
}

function moveDraw(e) {
  if (!isDrawing) return;
  e.preventDefault();
  const pos = getPos(e);
  currentStroke.push(pos);
  ctx.lineTo(pos.x, pos.y);
  ctx.stroke();
  hasDrawn = true;
  document.getElementById("done-btn").disabled = false;
}

function endDraw(e) {
  if (!isDrawing) return;
  isDrawing = false;
  if (currentStroke && currentStroke.length > 0) {
    strokes.push(currentStroke);
  }
  currentStroke = null;
}

canvas.addEventListener("pointerdown", startDraw);
canvas.addEventListener("pointermove", moveDraw);
canvas.addEventListener("pointerup", endDraw);
canvas.addEventListener("pointercancel", endDraw);
canvas.addEventListener("pointerleave", endDraw);

function redraw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  strokes.forEach(stroke => {
    if (stroke.length === 0) return;
    ctx.beginPath();
    ctx.moveTo(stroke[0].x, stroke[0].y);
    for (let i = 1; i < stroke.length; i++) {
      ctx.lineTo(stroke[i].x, stroke[i].y);
    }
    ctx.stroke();
  });
}

document.getElementById("clear-btn").addEventListener("click", () => {
  strokes = [];
  hasDrawn = false;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  document.getElementById("done-btn").disabled = true;
});

function injectValueIntoStreamlitWidget(text) {
  try {
    const win = window.parent;
    const currentUrl = new URL(win.location.href);
    currentUrl.searchParams.set("game2_result", text);
    win.history.replaceState({}, "", currentUrl.toString());
  } catch (e) {
    console.log("URL write failed:", e);
  }
}

document.getElementById("done-btn").addEventListener("click", () => {
  const dataURL = canvas.toDataURL("image/png");
  document.getElementById("player-img").src = dataURL;
  document.getElementById("done-panel").classList.add("show");

  const result = {
    game_id: "game2",
    completed: true,
    stroke_count: strokes.length,
    total_points: strokes.reduce((sum, s) => sum + s.length, 0),
  };

  injectValueIntoStreamlitWidget(JSON.stringify(result));
});
</script>
</body>
</html>
"""

# --- VISUAL CSS & SUPERMARKET IMMERSION STYLING ---
st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(rgba(245, 247, 248, 0.88), rgba(245, 247, 248, 0.88)),
                url('https://images.unsplash.com/photo-1578916171728-46686eac8d58?q=80&w=1600&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.market-banner {
    background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
    color: #FFFFFF !important;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}

.game-instruction-card {
    background: linear-gradient(180deg, #F5E6C8 0%, #E8D4A8 100%);
    border: 3px solid #7A1F1F;
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    text-align: center;
}

.game-instruction-title {
    font-size: 22px;
    font-weight: 800;
    color: #7A1F1F;
    margin-bottom: 6px;
}

.game-instruction-text {
    font-size: 20px;
    font-weight: 700;
    color: #2B1A08;
    line-height: 1.4;
    margin-bottom: 10px;
}

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
    "game1_result": None,
    "game2_result": None,
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_visuospatial_score": 0,
    "moca_drawing_score": 0,
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
    "input_reg_1": "",
    "input_reg_2": "",
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

# --- UI COMPONENT FUNCTIONS ---

def render_staff_npc(dialogue_text, staff_type="manager", staff_name="店長阿Ming"):
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


def render_instruction_speaker_component(instruction_text, key_suffix, btn_label="🔊 聽店長語音指引 (Listen)"):
    escaped_text = html.escape(instruction_text).replace("'", "\\'")
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; display:flex; justify-content:center; }}
    button {{ width:100%; max-width:360px; height:48px; font-size:18px; font-weight:bold; color:#FFFFFF !important; background:#FF9800; border:none; border-radius:10px; cursor:pointer; box-shadow:0 3px 6px rgba(0,0,0,0.15); }}
    button:hover {{ background:#E65100; }}
    </style></head><body>
    <button id="inst_btn_{key_suffix}" type="button">{btn_label}</button>

    <script>
    const text = "{escaped_text}";
    const btn = document.getElementById('inst_btn_{key_suffix}');

    if ('speechSynthesis' in window) {{
      window.speechSynthesis.onvoiceschanged = () => {{ window.speechSynthesis.getVoices(); }};
    }}

    function speakInstruction() {{
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-HK';
      utterance.rate = 0.88;

      const voices = window.speechSynthesis.getVoices();
      const hkVoice = voices.find(v => v.lang === 'zh-HK' || v.lang === 'yue-Hant-HK' || v.lang.includes('HK'));
      if (hkVoice) utterance.voice = hkVoice;

      window.speechSynthesis.speak(utterance);
    }}

    btn.onclick = speakInstruction;
    </script></body></html>
    """,
        height=52,
    )


def render_audio_speaker_component(words_list, key_suffix):
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
    is_continuous_js = "true" if continuous_mode else "false"
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#2E7D32; border:none; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#1B5E20; }}
    .status {{ font-size:15px; text-align:center; margin-top:6px; color:#2E7D32; font-weight:bold; }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 按此語音回答 (Speak)</button>
    <div class="status" id="status_{key_suffix}">點擊麥克風說出答案</div>

    <script>
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic_{key_suffix}'), status = document.getElementById('status_{key_suffix}');
    const isContinuous = {is_continuous_js};
    let recognition = null, listening = false;
    let baseText = "";
    let isProgrammaticChange = false;

    function resetToStandby() {{
      listening = false;
      mic.style.background = '#2E7D32';
      mic.textContent = '🎤 按此語音回答 (Speak)';
      status.textContent = '🟢 點擊麥克風說出答案';
    }}

    function getCurrentInputText() {{
      const doc = window.parent.document;
      const inputs = doc.querySelectorAll('input[type="text"], textarea');
      return inputs.length > 0 ? inputs[0].value.trim() : "";
    }}

    function injectValueIntoStreamlitWidget(text) {{
      const doc = window.parent.document;
      const inputs = doc.querySelectorAll('input[type="text"], textarea');
      if (inputs.length > 0) {{
        const target = inputs[0];
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
          window.HTMLInputElement.prototype, "value"
        ) || Object.getOwnPropertyDescriptor(
          window.HTMLTextAreaElement.prototype, "value"
        );
        
        isProgrammaticChange = true;
        if (nativeInputValueSetter && nativeInputValueSetter.set) {{
          nativeInputValueSetter.set.call(target, text);
        }} else {{
          target.value = text;
        }}
        target.dispatchEvent(new Event('input', {{ bubbles: true }}));
        target.dispatchEvent(new Event('change', {{ bubbles: true }}));
        setTimeout(() => {{ isProgrammaticChange = false; }}, 50);
      }}
    }}

    if(SR) {{
      recognition = new SR();
      recognition.lang = 'zh-HK';
      recognition.continuous = isContinuous;
      recognition.interimResults = isContinuous;

      recognition.onstart = () => {{
        listening = true;
        mic.style.background = '#D32F2F';
        mic.textContent = '⏹️ 停止錄音';
        status.textContent = '🔴 正在聆聽您的回答...';
      }};

      recognition.onresult = (event) => {{
        if (isContinuous) {{
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; ++i) {{
            if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
            else interimTranscript += event.results[i][0].transcript;
          }}

          if (finalTranscript) baseText += (baseText ? ' ' : '') + finalTranscript.trim();
          const displayText = baseText + (interimTranscript ? (baseText ? ' ' : '') + interimTranscript : '');
          status.textContent = '🎧 記錄中...';
          injectValueIntoStreamlitWidget(displayText);
        }} else {{
          const text = event.results[0][0].transcript.trim();
          const combined = baseText ? (baseText + ' ' + text) : text;
          status.textContent = '🎧 聽到: ' + text;
          injectValueIntoStreamlitWidget(combined);
        }}
      }};

      recognition.onerror = (event) => {{
        if (event.error !== 'no-speech') status.textContent = '⚠️ 語音問題 (' + event.error + ')';
      }};

      recognition.onend = () => {{
        if (listening && isContinuous) {{
          try {{ recognition.start(); }} catch(e) {{ resetToStandby(); }}
        }} else resetToStandby();
      }};
    }} else {{
      mic.disabled = true;
      status.textContent = '❌ 不支援語音';
    }}

    mic.onclick = () => {{
      if(!recognition) return;
      if(listening) {{ 
        listening = false; 
        recognition.stop(); 
        resetToStandby(); 
        return; 
      }}
      baseText = getCurrentInputText();
      try {{ recognition.start(); }} catch(e) {{}}
    }};
    </script></body></html>
    """,
        height=95,
    )


def evaluate_naming_answer(answer):
    item = NAMING_ITEMS[st.session_state.current_item_index]
    elapsed = round(time.time() - st.session_state.item_start_time, 2) if st.session_state.item_start_time else 0.0
    clean = answer.strip().replace(" ", "").replace("呢個係", "").replace("這是", "").replace("呢隻係", "")
    correct = any(s in answer or s in clean for s in item["acceptable_synonyms"])

    if correct:
        st.session_state.moca_naming_score += item["moca_weight"]

    st.session_state.telemetry_logs.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": "naming",
            "item_id": item["id"],
            "target_name": item["primary_name"],
            "user_response": answer,
            "is_correct": correct,
            "score_awarded": item["moca_weight"] if correct else 0,
            "latency_seconds": elapsed,
            "notes": f"Tier: {item['tier']}",
        }
    )
    return correct


def advance_naming_item():
    if st.session_state.current_item_index + 1 < len(NAMING_ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
    else:
        st.session_state.stage = "delayed_recall_free"
        st.session_state.item_start_time = time.time()


# ==========================================
# GAME FLOW STAGES
# ==========================================

if st.session_state.stage == "intro":
    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:36px; color:#FFFFFF !important;">🛒 超級市場大搜查</h1>
        <p style="margin:5px 0 0 0; font-size:20px; opacity:0.9;">歡迎來到開心超市！今天讓我們一起完成購物任務吧！</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc("早晨！歡迎光臨開心超市！今日超市有好多新鮮貨品，準備好你的購物籃出發吧！", staff_type="manager")

    if st.button("出發 (Start Shopping)"):
        st.session_state.stage = "game1"
        st.rerun()

elif st.session_state.stage == "game1":
    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:32px; color:#FFFFFF !important;">🔌 第一關：街市接線遊戲</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    game1_instruction_text = "請將硬幣與紙幣交錯連接"
    st.markdown(
        f"""
    <div class="game-instruction-card">
        <div class="game-instruction-title">💡 遊戲指引</div>
        <div class="game-instruction-text">
            {game1_instruction_text}<br>
            例如：1 元硬幣 ➔ 10 元紙幣 ➔ 2 元硬幣 ➔ ...
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(
        game1_instruction_text, 
        key_suffix="game1_instruction", 
        btn_label="🔊 聽遊戲指引 (Read Aloud)"
    )

    query_params = st.query_params
    if "game1_result" in query_params:
        try:
            st.session_state.game1_result = json.loads(query_params["game1_result"])
        except Exception:
            st.session_state.game1_result = query_params["game1_result"]

    components.html(GAME1_HTML, height=520, scrolling=False)

    if st.button("➡️ 去下一關"):
        if st.session_state.game1_result:
            res = st.session_state.game1_result
            if isinstance(res, dict):
                score = 1 if res.get("is_correct", False) else 0
                st.session_state.moca_visuospatial_score = score
                st.session_state.telemetry_logs.append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "task": "visuospatial_exec_trail",
                        "item_id": "game1_trail_making",
                        "target_name": "Alternate Trail (1d-10b-2d-20b-5d-50b-10d-100b)",
                        "user_response": " -> ".join(res.get("sequence", [])),
                        "is_correct": res.get("is_correct", False),
                        "score_awarded": score,
                        "latency_seconds": res.get("completion_time_sec", 0.0),
                        "notes": f"Undo Count: {res.get('undo_count', 0)}, Crossing: {res.get('has_crossing', False)}, Order Correct: {res.get('is_order_correct', False)}",
                    }
                )

        st.session_state.stage = "game2"
        st.rerun()

elif st.session_state.stage == "game2":
    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:32px; color:#FFFFFF !important;">🧺 第二關：畫購物籃遊戲</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    game2_instruction_text = "跟住呢個購物籃畫返出嚟，越準確越好！"
    st.markdown(
        f"""
    <div class="game-instruction-card">
        <div class="game-instruction-title">💡 遊戲指引</div>
            <div class="game-instruction-text">
            🧺 阿婆話：「{game2_instruction_text}」
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(
        game2_instruction_text, 
        key_suffix="game2_instruction", 
        btn_label="🔊 聽阿婆語音指引 (Read Aloud)"
    )

    query_params = st.query_params
    if "game2_result" in query_params:
        try:
            st.session_state.game2_result = json.loads(query_params["game2_result"])
        except Exception:
            st.session_state.game2_result = query_params["game2_result"]

    components.html(GAME2_HTML, height=580, scrolling=False)

    if st.button("➡️ 去下一關"):
        if st.session_state.game2_result:
            res = st.session_state.game2_result
            if isinstance(res, dict):
                completed = res.get("completed", False)
                stroke_count = res.get("stroke_count", 0)
                score = 1 if (completed and stroke_count > 0) else 0
                st.session_state.moca_drawing_score = score
                st.session_state.telemetry_logs.append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "task": "visuospatial_cube_copy",
                        "item_id": "game2_basket_drawing",
                        "target_name": "3D Shopping Basket Copy",
                        "user_response": f"Strokes: {stroke_count}, Points: {res.get('total_points', 0)}",
                        "is_correct": completed and stroke_count > 0,
                        "score_awarded": score,
                        "latency_seconds": 0.0,
                        "notes": "Drawing completed via canvas interface",
                    }
                )

        st.session_state.stage = "memory_reg_1"
        st.session_state.current_item_index = 0
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.rerun()

elif st.session_state.stage == "memory_reg_1":
    inst_1 = "請聽清楚超市廣播的 5 個詞語，聽完後講出你記得的。"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">📝 第三站：觀察四周事物 (1/2)</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc(inst_1, staff_type="manager")
    render_instruction_speaker_component(inst_1, "reg_1_inst")

    word_names = [item["name"] for item in MEMORY_ITEMS]

    col_audio, col_mic = st.columns(2)
    with col_audio:
        render_audio_speaker_component(word_names, "reg_1")
    with col_mic:
        render_mic_component("reg_1", continuous_mode=True)

    with st.form(key="form_reg_1"):
        user_answer_input = st.text_input("記得的詞語：", key="input_reg_1")
        if st.form_submit_button("👉 記好了，下一步"):
            val = st.session_state.input_reg_1
            spoken = [w.strip() for w in val.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_1_items = spoken

            st.session_state.telemetry_logs.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "task": "memory_registration_trial_1",
                    "item_id": "memory_reg_1",
                    "target_name": ", ".join(word_names),
                    "user_response": val,
                    "is_correct": None,
                    "score_awarded": 0,
                    "latency_seconds": 0.0,
                    "notes": f"Spoken Items Count: {len(spoken)}",
                }
            )

            st.session_state.stage = "memory_reg_2"
            st.rerun()

elif st.session_state.stage == "memory_reg_2":
    inst_2 = "超市廣播會再播一次，請再次講出記得的東西（包括剛才講過的）。"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">📝 第三站：觀察四周事物 (2/2)</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc(inst_2, staff_type="manager")
    render_instruction_speaker_component(inst_2, "reg_2_inst")

    word_names = [item["name"] for item in MEMORY_ITEMS]

    col_audio, col_mic = st.columns(2)
    with col_audio:
        render_audio_speaker_component(word_names, "reg_2")
    with col_mic:
        render_mic_component("reg_2", continuous_mode=True)

    with st.form(key="form_reg_2"):
        user_answer_input = st.text_input("記得的詞語：", key="input_reg_2")
        if st.form_submit_button("👉 記好了，進入超市"):
            val = st.session_state.input_reg_2
            spoken = [w.strip() for w in val.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_2_items = spoken

            st.session_state.telemetry_logs.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "task": "memory_registration_trial_2",
                    "item_id": "memory_reg_2",
                    "target_name": ", ".join(word_names),
                    "user_response": val,
                    "is_correct": None,
                    "score_awarded": 0,
                    "latency_seconds": 0.0,
                    "notes": f"Spoken Items Count: {len(spoken)}",
                }
            )

            st.session_state.stage = "memory_reg_notice"
            st.rerun()

elif st.session_state.stage == "memory_reg_notice":
    inst_notice = "請緊記剛才這 5 樣東西！稍後去結帳時，需要重覆講出廣播提到的字！"

    st.markdown(
        """
    <div class="market-banner" style="background: linear-gradient(135deg, #FF9800 0%, #E65100 100%);">
        <h1 style="margin:0; font-size:32px; color:#FFFFFF !important;">📌 店長特別提醒</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc("請緊記剛才這 5 樣東西！稍後去結帳時，需要重覆講出廣播提到的字！", staff_type="manager")
    render_instruction_speaker_component(inst_notice, "notice_inst")

    if st.button("👉 明白，開始逛超市！"):
        st.session_state.stage = "naming"
        st.session_state.current_item_index = 0
        st.session_state.item_start_time = time.time()
        st.rerun()

elif st.session_state.stage == "naming":
    index = st.session_state.current_item_index
    item = NAMING_ITEMS[index]
    inst_naming = f"{item['story']}，請問這是什麼？"

    st.markdown(
        f"""
    <div class="market-banner">
        <h1 style="margin:0; font-size:28px; color:#FFFFFF !important;">🔍 第四站：探索超市 ({index+1}/{len(NAMING_ITEMS)})</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc(f"{item['story']}，請問這是什麼？", staff_type="assistant", staff_name="店員小花")
    render_instruction_speaker_component(inst_naming, f"naming_{index}_inst")

    st.markdown(
        f"""
    <div class="market-shelf-card">
        <img src="{item['image_url']}" class="product-image" alt="Supermarket Item">
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_mic_component(f"naming_{index}", continuous_mode=False)

    with st.form(key=f"naming_form_{index}"):
        user_answer = st.text_input("這是...", key=f"user_input_{index}")
        submit_btn = st.form_submit_button("👉 下一步")

        if submit_btn:
            recorded_answer = user_answer.strip() if user_answer.strip() else "跳過"
            evaluate_naming_answer(recorded_answer)
            advance_naming_item()
            st.rerun()

elif st.session_state.stage == "delayed_recall_free":
    inst_free = "歡迎來到結帳處！請講出最開始廣播的 5 樣東西"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">💵 第五站：結帳</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc("歡迎來到結帳處！請講出最開始廣播的 5 樣東西", staff_type="cashier", staff_name="收銀員阿輝")
    render_instruction_speaker_component(inst_free, "free_recall_inst")

    render_mic_component("delayed_free", continuous_mode=True)

    with st.form(key="form_delayed_free"):
        user_answer = st.text_input("講出詞語：", key="input_delayed_free")
        if st.form_submit_button("👉 完成 (Done)"):
            elapsed = round(time.time() - st.session_state.item_start_time, 2)
            recalled = []
            score = 0

            for item in MEMORY_ITEMS:
                if item["name"] in user_answer:
                    recalled.append(item["name"])
                    score += 1

            st.session_state.recalled_free_items = recalled
            st.session_state.moca_memory_score = score

            word_names = [item["name"] for item in MEMORY_ITEMS]
            st.session_state.telemetry_logs.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "task": "delayed_recall_free",
                    "item_id": "delayed_free",
                    "target_name": ", ".join(word_names),
                    "user_response": user_answer,
                    "is_correct": score == 5,
                    "score_awarded": score,
                    "latency_seconds": elapsed,
                    "notes": f"Recalled Items: {', '.join(recalled) if recalled else 'None'}",
                }
            )

            missed = [item for item in MEMORY_ITEMS if item["name"] not in recalled]
            st.session_state.missed_items = missed
            st.session_state.cued_current_index = 0
            st.session_state.cued_sub_step = "category"

            if missed:
                st.session_state.stage = "delayed_recall_cued_step"
            else:
                st.session_state.stage = "complete"
            st.rerun()

elif st.session_state.stage == "delayed_recall_cued_step":
    missed_list = st.session_state.missed_items
    curr_idx = st.session_state.cued_current_index

    if curr_idx >= len(missed_list):
        st.session_state.stage = "complete"
        st.rerun()

    item = missed_list[curr_idx]

    st.markdown(
        """
    <div class="market-banner" style="background: linear-gradient(135deg, #0288D1 0%, #01579B 100%);">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">🔎 超市店員的協助</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.session_state.cued_sub_step == "category":
        inst_cue = f"讓我幫幫你！這東西屬於【{item['category']}】，請問你記得是什麼嗎？"

        render_staff_npc(f"讓我幫幫你！這東西屬於【{item['category']}】，請問你記得是什麼嗎？", staff_type="assistant", staff_name="店員小花")
        render_instruction_speaker_component(inst_cue, f"cue_inst_{item['id']}")
        render_mic_component(f"cue_cat_{item['id']}", continuous_mode=True)

        with st.form(key=f"form_cat_{item['id']}"):
            user_spoken = st.text_input("請講出這樣東西：", key=f"in_cat_{item['id']}")
            if st.form_submit_button("👉 確認"):
                st.session_state.recalled_cued_items[item["name"]] = user_spoken.strip()
                is_correct = item["name"] in user_spoken

                st.session_state.telemetry_logs.append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "task": "delayed_recall_category_cue",
                        "item_id": item["id"],
                        "target_name": item["name"],
                        "user_response": user_spoken,
                        "is_correct": is_correct,
                        "score_awarded": 0,
                        "latency_seconds": 0.0,
                        "notes": f"Category Cue Provided: {item['category']}",
                    }
                )

                if is_correct:
                    st.session_state.cued_current_index += 1
                    st.session_state.cued_sub_step = "category"
                else:
                    st.session_state.cued_sub_step = "choice"
                st.rerun()

    elif st.session_state.cued_sub_step == "choice":
        inst_choice = "這裏有三個選項，請選擇原本廣播的那一個。"

        render_staff_npc("這裏有三個選項，請選擇原本廣播的那一個。", staff_type="assistant", staff_name="店員小花")
        render_instruction_speaker_component(inst_choice, f"choice_inst_{item['id']}")

        with st.form(key=f"form_choice_{item['id']}"):
            selected_option = st.radio(
                "請點選正確選項：",
                options=item["options"],
                key=f"radio_choice_{item['id']}",
            )
            if st.form_submit_button("👉 繼續"):
                st.session_state.recalled_choice_items[item["name"]] = selected_option
                is_correct = selected_option == item["name"]

                st.session_state.telemetry_logs.append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "task": "delayed_recall_multiple_choice",
                        "item_id": item["id"],
                        "target_name": item["name"],
                        "user_response": selected_option,
                        "is_correct": is_correct,
                        "score_awarded": 0,
                        "latency_seconds": 0.0,
                        "notes": f"Options: {', '.join(item['options'])}",
                    }
                )

                st.session_state.cued_current_index += 1
                st.session_state.cued_sub_step = "category"
                st.rerun()

elif st.session_state.stage == "complete":
    st.balloons()

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:36px; color:#FFFFFF !important;">🎉 成功完成購物！</h1>
        <p style="margin:5px 0 0 0; font-size:20px;">多謝惠顧！你已順利買齊所有物品並完成結帳！</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc("恭喜你！買齊所有東西了，歡迎下次再來開心超市購物！", staff_type="manager")

    if st.button("🔄 再玩一次 (Play Again)"):
        st.session_state.stage = "intro"
        st.session_state.game1_result = None
        st.session_state.game2_result = None
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_visuospatial_score = 0
        st.session_state.moca_drawing_score = 0
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.session_state.reg_trial_1_items = []
        st.session_state.reg_trial_2_items = []
        st.session_state.recalled_free_items = []
        st.session_state.missed_items = []
        st.session_state.cued_current_index = 0
        st.session_state.cued_sub_step = "category"
        st.session_state.recalled_cued_items = {}
        st.session_state.recalled_choice_items = {}
        st.session_state.input_reg_1 = ""
        st.session_state.input_reg_2 = ""
        st.rerun()

    with st.expander("🩺 Occupational Therapist / Speech Telemetry Dashboard", expanded=False):
        st.subheader("Game Results Raw Output")
        st.write("**Game 1 (Coin Trail):**", st.session_state.game1_result if st.session_state.game1_result else "No result recorded.")
        st.write("**Game 2 (Basket Drawing):**", st.session_state.game2_result if st.session_state.game2_result else "No result recorded.")

        st.subheader("MoCA Sub-score Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("1. Visuospatial Trail", f"{st.session_state.moca_visuospatial_score} / 1 Pt")
        with col2:
            st.metric("2. Cube/Basket Copy", f"{st.session_state.moca_drawing_score} / 1 Pt")
        with col3:
            st.metric("3. Naming Sub-score", f"{st.session_state.moca_naming_score} / 3 Pts")
        with col4:
            st.metric("4. Delayed Recall", f"{st.session_state.moca_memory_score} / 5 Pts")
        with col5:
            total = (
                st.session_state.moca_visuospatial_score
                + st.session_state.moca_drawing_score
                + st.session_state.moca_naming_score
                + st.session_state.moca_memory_score
            )
            st.metric("Combined MoCA Total", f"{total} / 10 Pts")

        st.subheader("Memory Breakdown")
        st.write(
            f"**Registration Trial 1 Spoken:** {', '.join(st.session_state.reg_trial_1_items) if st.session_state.reg_trial_1_items else 'None'}"
        )
        st.write(
            f"**Registration Trial 2 Spoken:** {', '.join(st.session_state.reg_trial_2_items) if st.session_state.reg_trial_2_items else 'None'}"
        )
        st.write(
            f"**Free Recall (Scored):** {', '.join(st.session_state.recalled_free_items) if st.session_state.recalled_free_items else 'None'}"
        )

        if st.session_state.recalled_cued_items or st.session_state.recalled_choice_items:
            st.write("**Cued / Multiple-Choice Analysis (Encoding vs Retrieval Deficit Analysis):**")
            st.json(
                {
                    "Category_Cues": st.session_state.recalled_cued_items,
                    "Multiple_Choices": st.session_state.recalled_choice_items,
                }
            )

        st.subheader("Complete Clinical Telemetry Log")
        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        if not df.empty:
            st.download_button(
                "📥 Download Clinical Telemetry Log (.CSV)",
                df.to_csv(index=False).encode("utf-8-sig"),
                f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
                "text/csv",
            )
