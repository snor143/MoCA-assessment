import html
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="HK Market Voice MoCA Explorer",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom High-Contrast Styling for Elderly Accessibility
st.markdown(
    """
<style>
.main { background-color: #FFFDF9; }
.instruction-card { 
    background: #F0F7F4; 
    padding: 20px; 
    border-radius: 16px; 
    border-left: 8px solid #2E7D32; 
    margin-bottom: 20px; 
}
div.stButton > button {
    width: 100% !important;
    height: 64px !important;
    font-size: 22px !important;
    font-weight: bold !important;
    border-radius: 14px !important;
    border: 0 !important;
    background-color: #2E7D32 !important;
    color: white !important;
    margin-bottom: 10px !important;
}
div.stButton > button:hover {
    background-color: #1B5E20 !important;
}
.secondary-btn div.stButton > button {
    background-color: #607D8B !important;
}
.secondary-btn div.stButton > button:hover {
    background-color: #455A64 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# 1. Initialize Session State
for key, value in {
    "stage": "intro",
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "last_transcript": "",
    "evaluated_item_ids": set(),
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Test Items (MoCA Cantonese Naming Equivalents)
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


def evaluate_and_submit(user_spoken_text):
    """Evaluates the spoken answer and guarantees EXACTLY ONE score evaluation per item."""
    index = st.session_state.current_item_index
    item = ITEMS[index]

    # Guard: Prevent double-scoring if already evaluated
    if item["id"] in st.session_state.evaluated_item_ids:
        return

    st.session_state.evaluated_item_ids.add(item["id"])

    # Calculate response latency
    elapsed = (
        round(time.time() - st.session_state.item_start_time, 2)
        if st.session_state.item_start_time
        else 0.0
    )

    # Normalize Cantonese input
    clean_text = (
        user_spoken_text.strip()
        .replace(" ", "")
        .replace("呢個係", "")
        .replace("這是", "")
        .replace("呢隻係", "")
        .replace("嗰隻係", "")
    )

    is_skip = user_spoken_text == "跳過"
    is_correct = (
        not is_skip
        and any(
            syn in user_spoken_text or syn in clean_text
            for syn in item["acceptable_synonyms"]
        )
    )

    # Increment MoCA Score
    if is_correct:
        st.session_state.moca_naming_score += item["moca_weight"]

    # Log telemetry
    st.session_state.telemetry_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_id": item["id"],
        "target_name": item["primary_name"],
        "user_spoken_raw": user_spoken_text,
        "is_correct": is_correct,
        "speech_latency_seconds": elapsed,
    })

    # Advance to next question or complete stage
    if st.session_state.current_item_index + 1 < len(ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
        st.session_state.last_transcript = ""
    else:
        st.session_state.stage = "complete"


# -----------------------------------------------------------------------------
# STAGE 1: INTRO SCREEN
# -----------------------------------------------------------------------------
if st.session_state.stage == "intro":
    st.title("🛒 香港街市語音買菜 (HK Market Voice MoCA)")
    st.markdown(
        """
    <div class="instruction-card">
        <h2>婆婆/伯伯，今日我們要去街市買菜！</h2>
        <p style="font-size:22px; margin-top:10px;">請睇睇螢幕上的動物，<b>點擊橙色按鈕並用廣東話講出它的名字</b>。</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("🚀 開始測試 (Start Assessment)"):
        st.session_state.stage = "gameplay"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.last_transcript = ""
        st.session_state.evaluated_item_ids = set()
        st.session_state.item_start_time = time.time()
        st.query_params.clear()
        st.rerun()

# -----------------------------------------------------------------------------
# STAGE 2: GAMEPLAY (VOICE NAMING)
# -----------------------------------------------------------------------------
elif st.session_state.stage == "gameplay":
    index = st.session_state.current_item_index
    item = ITEMS[index]

    # Handle incoming voice response from query params
    spoken_param = st.query_params.get("spoken_response")
    skip_param = st.query_params.get("skip_response")

    if spoken_param is not None or skip_param is not None:
        answer_text = "跳過" if skip_param is not None else str(spoken_param)
        st.query_params.clear()
        evaluate_and_submit(answer_text)
        st.rerun()

    # Progress Header
    st.markdown(
        f"<p style='font-size:22px;text-align:center;color:#555;'>進度: <b>{index+1} / {len(ITEMS)}</b></p>",
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

    # Large Animal Emoji Display
    st.markdown(
        f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>",
        unsafe_allow_html=True,
    )

    # Clean Embedded Voice Input Component
    components.html(
        f"""
    <!-- item_id_{item['id']} -->
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:transparent; }}
    button {{ width:100%; height:75px; font-size:24px; font-weight:bold; color:white; border:0; border-radius:16px; cursor:pointer; margin-bottom:12px; transition:0.2s; }}
    #mic {{ background:#E65100; box-shadow:0 4px 10px rgba(230,81,0,0.3); }}
    #mic:active {{ transform:scale(0.98); }}
    .status {{ font-size:20px; text-align:center; font-weight:bold; min-height:32px; margin:8px 0; color:#333; }}
    .result-box {{ background:#E8F5E9; padding:14px; border-radius:12px; font-size:22px; font-weight:bold; color:#1B5E20; text-align:center; margin:10px 0; border:2px solid #A5D6A7; }}
    </style></head><body>

    <button id="mic" type="button">🎤 按此說話 (Tap & Say)</button>
    <div class="status" id="status">點擊上方按鈕並講出名稱</div>
    <div class="result-box">🎤 聽到語音：<span id="display">未有結果</span></div>

    <script>
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic');
    const status = document.getElementById('status');
    const display = document.getElementById('display');
    let recognition = null, listening = false;

    function sendToStreamlit(key, value) {{
      let targetUrl;
      try {{ targetUrl = new URL(window.top.location.href); }}
      catch(e) {{ targetUrl = new URL(window.location.href); }}
      
      targetUrl.search = '';
      targetUrl.searchParams.set(key, value);
      targetUrl.searchParams.set('item_idx', '{index}');
      
      try {{ window.top.location.href = targetUrl.toString(); }}
      catch(e) {{ window.location.href = targetUrl.toString(); }}
    }}

    function setReady(msg) {{
      listening = false;
      mic.disabled = false;
      mic.style.background = '#E65100';
      mic.textContent = '🎤 按此說話 (Tap & Say)';
      if(msg) status.textContent = msg;
    }}

    if (SR) {{
      recognition = new SR();
      recognition.lang = 'zh-HK';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {{
        listening = true;
        mic.style.background = '#D32F2F';
        mic.textContent = '⏹️ 正在聆聽中... (Listening)';
        status.textContent = '🔴 請大聲講出動物名稱...';
      }};

      recognition.onresult = (event) => {{
        const text = event.results[0][0].transcript.trim();
        if (!text) {{
          setReady('⚠️ 沒有聽到內容 — 請再試一次');
          return;
        }}
        display.textContent = text;
        status.textContent = '✅ 成功識別："' + text + '"';
        mic.style.background = '#2E7D32';
        mic.disabled = true;
        
        // Submit response cleanly
        setTimeout(() => {{ sendToStreamlit('spoken_response', text); }}, 600);
      }};

      recognition.onerror = (event) => {{
        setReady('⚠️ 未能識別 (' + event.error + ') — 請再試一次');
      }};

      recognition.onend = () => {{
        if (listening) setReady();
      }};
    }} else {{
      mic.disabled = true;
      status.textContent = '❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)';
    }}

    mic.onclick = () => {{
      if (!recognition) return;
      if (listening) {{
        recognition.stop();
        return;
      }}
      try {{ recognition.start(); }} 
      catch(e) {{ setReady('⚠️ 麥克風未能啟動 — 請再試一次'); }}
    }};
    </script></body></html>
    """,
        height=220,
    )

    # Native Streamlit Skip Button
    st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
    if st.button("⏭️ 唔識答 / 跳過 (Skip Question)"):
        evaluate_and_submit("跳過")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# STAGE 3: CLINICAL REPORT & AI RECOMMENDATION PAYLOAD
# -----------------------------------------------------------------------------
elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 完成測試！ (Assessment Complete)")

    df_telemetry = pd.DataFrame(st.session_state.telemetry_logs)
    avg_latency = (
        round(df_telemetry["speech_latency_seconds"].mean(), 2)
        if not df_telemetry.empty
        else 0.0
    )

    # Score Metrics Summary
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "MoCA Naming Sub-score",
            f"{st.session_state.moca_naming_score} / {len(ITEMS)} Points",
        )
    with col2:
        st.metric("Avg. Response Latency", f"{avg_latency} sec")

    st.subheader("📋 Itemized Assessment Telemetry")
    st.dataframe(df_telemetry, use_container_width=True)

    # AI Cognitive Analysis Payload Generator
    st.subheader("🤖 AI Cognitive Analysis & Game Recommender Payload")
    st.caption(
        "Pass this JSON payload into an LLM to analyze cognitive deficits and auto-recommend targeted training games:"
    )

    ai_payload = {
        "assessment_type": "Gamified MoCA Confrontation Naming (Cantonese)",
        "patient_metrics": {
            "total_score": st.session_state.moca_naming_score,
            "max_score": len(ITEMS),
            "accuracy_percentage": f"{round((st.session_state.moca_naming_score / len(ITEMS)) * 100, 1)}%",
            "average_speech_latency_seconds": avg_latency,
        },
        "item_breakdown": st.session_state.telemetry_logs,
        "cognitive_domains_assessed": [
            "Semantic Memory",
            "Visual Object Recognition",
            "Lexical Retrieval & Cantonese Speech Production",
        ],
    }

    st.json(ai_payload)

    # Download Telemetry Log CSV
    if not df_telemetry.empty:
        st.download_button(
            "📥 Download Telemetry Log (.CSV)",
            df_telemetry.to_csv(index=False).encode("utf-8"),
            f"moca_voice_telemetry_{int(time.time())}.csv",
            "text/csv",
        )

    # Restart Test Button
    if st.button("🔄 重新開始 (Restart Test)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.last_transcript = ""
        st.session_state.evaluated_item_ids = set()
        st.query_params.clear()
        st.rerun()
