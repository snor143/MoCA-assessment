import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="HK Market Voice MoCA Explorer",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
.main { background-color:#FFFDF9; }
.instruction-card { background:#F0F7F4; padding:24px; border-radius:16px; border-left:8px solid #2E7D32; margin-bottom:24px; }
div.stButton > button {
    width: 100% !important;
    height: 60px !important;
    font-size: 20px !important;
    font-weight: bold !important;
    border-radius: 14px !important;
    border: 0 !important;
    background-color: #607D8B !important;
    color: white !important;
}
div.stButton > button:hover { background-color: #455A64 !important; }
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
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

ITEMS = [
    {
        "id": "item_1",
        "tier": "High Familiarity (Warmup)",
        "emoji": "🦋",
        "primary_name": "蝴蝶",
        "acceptable_synonyms": ["蝴蝶", "呢個係蝴蝶", "這是蝴蝶", "呢隻係蝴蝶"],
        "moca_weight": 1,
    },
    {
        "id": "item_2",
        "tier": "Moderate Familiarity",
        "emoji": "🐙",
        "primary_name": "八爪魚",
        "acceptable_synonyms": ["八爪魚", "呢個係八爪魚", "這是八爪魚", "呢隻係八爪魚"],
        "moca_weight": 1,
    },
    {
        "id": "item_3",
        "tier": "Low Familiarity (MoCA Rhino Equivalent)",
        "emoji": "🦥",
        "primary_name": "樹懶",
        "acceptable_synonyms": ["樹懶", "呢個係樹懶", "這是樹懶", "呢隻係樹懶"],
        "moca_weight": 1,
    },
]


def evaluate_and_advance(spoken_text):
    item = ITEMS[st.session_state.current_item_index]
    elapsed = (
        round(time.time() - st.session_state.item_start_time, 2)
        if st.session_state.item_start_time
        else 0.0
    )

    clean = (
        spoken_text.strip()
        .replace(" ", "")
        .replace("呢個係", "")
        .replace("這是", "")
        .replace("呢隻係", "")
    )
    is_skip = spoken_text == "跳過"
    is_correct = (
        not is_skip
        and any(s in spoken_text or s in clean for s in item["acceptable_synonyms"])
    )

    if is_correct:
        st.session_state.moca_naming_score += item["moca_weight"]

    st.session_state.telemetry_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_id": item["id"],
        "target_name": item["primary_name"],
        "user_spoken_raw": spoken_text,
        "is_correct": is_correct,
        "speech_latency_seconds": elapsed,
    })

    if st.session_state.current_item_index + 1 < len(ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
    else:
        st.session_state.stage = "complete"


# STAGE 1: INTRO SCREEN
if st.session_state.stage == "intro":
    st.title("🛒 香港街市語音買菜 (HK Market Voice Assessment)")
    st.markdown(
        """
    <div class="instruction-card">
        <h2>婆婆/伯伯，今日我們要去街市買菜！</h2>
        <p style="font-size:22px;">請睇睇螢幕上的動物，<b>點擊麥克風並用廣東話講出它的名字</b>。</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("開始測試 (Start Voice Assessment)"):
        st.session_state.stage = "gameplay"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.item_start_time = time.time()
        st.query_params.clear()
        st.rerun()

# STAGE 2: GAMEPLAY (PURE VOICE INTERACTION)
elif st.session_state.stage == "gameplay":
    index = st.session_state.current_item_index

    # Process incoming spoken voice input from query parameters
    spoken_param = st.query_params.get("spoken_text")
    if spoken_param is not None:
        st.query_params.clear()
        evaluate_and_advance(str(spoken_param))
        st.rerun()

    item = ITEMS[index]

    st.markdown(
        f"<p style='font-size:22px;text-align:center;color:#666;'>進度: {index+1} / {len(ITEMS)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align:center;'>請大聲講出，這是什麼動物？</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;font-size:18px;color:#2E7D32;'>💡 提示：按下方按鈕後說<b>「呢個係...」</b></p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:140px;text-align:center;margin:10px 0;'>{item['emoji']}</div>",
        unsafe_allow_html=True,
    )

    # Simplified HTML Voice Component (Auto-submits as soon as spoken)
    components.html(
        """
    <!doctype html><html><head><meta charset="utf-8"><style>
    body { margin:0; font-family:sans-serif; }
    #mic { width:100%; height:85px; font-size:26px; font-weight:bold; color:white; border:0; border-radius:20px; cursor:pointer; background:#2E7D32; box-shadow:0 4px 10px rgba(0,0,0,0.15); }
    #mic:active { transform: scale(0.98); }
    .status { font-size:20px; text-align:center; margin-top:12px; color:#333; font-weight:500; }
    </style></head><body>
    <button id="mic" type="button">🎤 按此說話 (Tap & Say)</button>
    <div class="status" id="status">點擊上方按鈕並講出名稱</div>

    <script>
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic'), status = document.getElementById('status');
    let recognition = null, listening = false;

    function sendResult(text) {
        const search = '?spoken_text=' + encodeURIComponent(text);
        try { window.top.location.search = search; }
        catch(e1) {
            try { window.parent.location.search = search; }
            catch(e2) { window.location.search = search; }
        }
    }

    if(SR) {
        recognition = new SR();
        recognition.lang = 'zh-HK';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            listening = true;
            mic.style.background = '#D32F2F';
            mic.textContent = '⏹️ 正在聆聽中... (Listening)';
            status.textContent = '🔴 請大聲講出名稱...';
        };

        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript.trim();
            if(!text) {
                status.textContent = '⚠️ 沒有聽到內容 — 請再試一次';
                mic.style.background = '#2E7D32';
                mic.textContent = '🎤 按此說話 (Tap & Say)';
                listening = false;
                return;
            }
            status.textContent = '✅ 聽到: "' + text + '" (正在核對...)';
            mic.style.background = '#388E3C';
            sendResult(text);
        };

        recognition.onerror = (event) => {
            listening = false;
            mic.style.background = '#2E7D32';
            mic.textContent = '🎤 按此說話 (Tap & Say)';
            status.textContent = '⚠️ 未能識別 (' + event.error + ') — 請再試一次';
        };

        recognition.onend = () => {
            if(listening) {
                listening = false;
                mic.style.background = '#2E7D32';
                mic.textContent = '🎤 按此說話 (Tap & Say)';
            }
        };
    } else {
        mic.disabled = true;
        status.textContent = '❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)';
    }

    mic.onclick = () => {
        if(!recognition) return;
        if(listening) {
            recognition.stop();
        } else {
            try { recognition.start(); } catch(e) { recognition.stop(); recognition.start(); }
        }
    };
    </script></body></html>
    """,
        height=140,
    )

    # Secondary Native Skip Button (If patient cannot name the animal)
    if st.button("⏭️ 唔識答 / 跳過 (Skip)"):
        evaluate_and_advance("跳過")
        st.rerun()

# STAGE 3: REPORT & AI PROMPT GENERATOR
elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 完成測試！ (Assessment Complete)")

    df = pd.DataFrame(st.session_state.telemetry_logs)
    avg_latency = (
        round(df["speech_latency_seconds"].mean(), 2) if not df.empty else 0
    )

    # Performance Summary Cards
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "MoCA Naming Sub-score",
            f"{st.session_state.moca_naming_score} / {len(ITEMS)} Points",
        )
    with col2:
        st.metric("Avg. Response Latency", f"{avg_latency} sec")

    st.subheader("📋 Itemized Telemetry Summary")
    st.dataframe(df, use_container_width=True)

    # AI Cognitive Analysis Payload Generator
    st.subheader("🤖 AI Cognitive Recommendation Payload")
    st.caption(
        "This JSON structure can be passed directly to an LLM to generate targeted cognitive training recommendations:"
    )

    ai_payload = {
        "assessment_type": "Gamified MoCA Confrontation Naming (Cantonese)",
        "patient_metrics": {
            "total_score": st.session_state.moca_naming_score,
            "max_score": len(ITEMS),
            "average_latency_seconds": avg_latency,
            "accuracy_rate": f"{round((st.session_state.moca_naming_score / len(ITEMS)) * 100, 1)}%",
        },
        "item_breakdown": st.session_state.telemetry_logs,
        "cognitive_domains_assessed": [
            "Semantic Memory",
            "Visual Object Recognition",
            "Lexical Retrieval & Speech Production",
        ],
    }

    st.json(ai_payload)

    st.download_button(
        "📥 Download Telemetry Log (.CSV)",
        df.to_csv(index=False).encode("utf-8"),
        f"moca_voice_telemetry_{int(time.time())}.csv",
        "text/csv",
    )

    if st.button("🔄 重新開始 (Restart Assessment)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.query_params.clear()
        st.rerun()
