import html
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="HK Supermarket Explorer - Voice Naming",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# FIXED CSS: Ensures ALL Streamlit buttons have solid backgrounds
st.markdown(
    """
<style>
.main { background-color:#FFFDF9; }
.instruction-card { background:#F0F7F4; padding:24px; border-radius:16px; border-left:8px solid #2E7D32; margin-bottom:24px; }

/* Default styling for ALL Streamlit buttons (Start, Play Again, Submit) */
div.stButton > button {
    width: 100% !important;
    height: 65px !important;
    font-size: 22px !important;
    font-weight: bold !important;
    border-radius: 16px !important;
    border: 0 !important;
    background-color: #2E7D32 !important;
    color: white !important;
    margin-top: 10px !important;
}

div.stButton > button:hover {
    background-color: #1B5E20 !important;
    color: white !important;
}

/* Specific styling for Skip Button (Column 2) */
div[data-testid="stColumn"]:nth-child(2) div.stButton > button {
    background-color: #607D8B !important;
}
div[data-testid="stColumn"]:nth-child(2) div.stButton > button:hover {
    background-color: #455A64 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Session State Initialization
for key, value in {
    "stage": "intro",
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "last_transcript": "",
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


def evaluate_answer(answer):
    item = ITEMS[st.session_state.current_item_index]
    elapsed = (
        round(time.time() - st.session_state.item_start_time, 2)
        if st.session_state.item_start_time
        else 0.0
    )
    clean = (
        answer.strip()
        .replace(" ", "")
        .replace("呢個係", "")
        .replace("這是", "")
        .replace("呢隻係", "")
        .replace("嗰位是", "")
    )
    correct = any(s in answer or s in clean for s in item["acceptable_synonyms"])
    if correct:
        st.session_state.moca_naming_score += item["moca_weight"]
    st.session_state.telemetry_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_id": item["id"],
        "target_name": item["primary_name"],
        "user_spoken_raw": answer,
        "is_correct": correct,
        "speech_latency_seconds": elapsed,
    })
    return correct


def advance_item():
    if st.session_state.current_item_index + 1 < len(ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
        st.session_state.last_transcript = ""
    else:
        st.session_state.stage = "complete"


# STAGE 1: INTRO
if st.session_state.stage == "intro":
    st.title("🛒 香港街市語音買菜 (HK Market Voice Explorer)")
    st.markdown(
        """
    <div class="instruction-card">
        <h2>婆婆/伯伯，今日我們要去街市買菜！</h2>
        <p style="font-size:22px;">請睇睇螢幕上的動物，<b>用廣東話講出它的名字</b>。</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("開始買菜 (Start Voice Assessment)"):
        st.session_state.stage = "gameplay"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.last_transcript = ""
        st.session_state.item_start_time = time.time()
        st.query_params.clear()
        st.rerun()

# STAGE 2: GAMEPLAY
elif st.session_state.stage == "gameplay":
    index = st.session_state.current_item_index

    # Check for speech recognition or input updates from iframe
    if "speech_result" in st.query_params:
        transcript = str(st.query_params["speech_result"])
        st.query_params.clear()
        st.session_state.last_transcript = transcript
        st.rerun()

    item = ITEMS[index]
    initial = html.escape(st.session_state.last_transcript, quote=True)
    displayed = html.escape(st.session_state.last_transcript or "尚未有語音結果")

    st.markdown(
        f"<p style='font-size:22px;text-align:center;color:#666;'>進度: {index+1} / {len(ITEMS)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align:center;'>請大聲講出，這是什麼動物？</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:18px;text-align:center;color:#2E7D32;'>💡 提示：可以說<b>「呢個係...」</b>（例如：「呢個係蝴蝶」）</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>",
        unsafe_allow_html=True,
    )

    # HTML Component: Voice Recognition + Auto-sync Textarea
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body{{margin:0;font-family:sans-serif}}
    button{{width:100%;height:65px;font-size:22px;font-weight:bold;color:white;border:0;border-radius:16px;cursor:pointer;background:#2E7D32}}
    button:disabled{{opacity:.65;cursor:wait}}
    .status{{font-size:20px;text-align:center;margin:8px 0;color:#333}}
    label{{display:block;font-size:18px;margin:10px 0 6px}}
    textarea{{box-sizing:border-box;width:100%;min-height:75px;padding:12px;font-size:22px;border:2px solid #4CAF50;border-radius:12px;resize:vertical}}
    .display{{background:#E8F5E9;padding:12px;border-radius:12px;font-size:20px;margin:10px 0}}
    </style></head><body>
    <button id="mic" type="button">🎤 按此說話 (Tap & Say)</button>
    <div class="status" id="status">點擊上方按鈕並講出名稱</div>
    <div class="display">🎤 語音結果：<span id="display">{displayed}</span></div>
    <label for="answer">答案（可修改或手動輸入）：</label>
    <textarea id="answer" placeholder="語音結果會顯示在這裡；也可以手動輸入">{initial}</textarea>

    <script>
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic'), status = document.getElementById('status'), answer = document.getElementById('answer');
    let recognition = null, listening = false;

    // Send data to main window URL to reload Streamlit Python state
    function syncText(text) {{
        const param = '?speech_result=' + encodeURIComponent(text);
        try {{
            window.parent.location.search = param;
        }} catch(e) {{
            window.location.search = param;
        }}
    }}

    // Sync manual text changes when user finishes editing
    answer.onchange = () => {{
        syncText(answer.value);
    }};

    if(SR) {{
        recognition = new SR();
        recognition.lang = 'zh-HK';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {{
            listening = true;
            mic.style.background = '#D32F2F';
            mic.textContent = '⏹️ 正在聆聽中... (Listening)';
            status.textContent = '🔴 正在聆聽中，請講話...';
        }};

        recognition.onresult = (event) => {{
            const text = event.results[0][0].transcript.trim();
            if(!text) {{
                status.textContent = '⚠️ 沒有聽到內容 — 請再試一次';
                listening = false;
                mic.style.background = '#2E7D32';
                mic.textContent = '🎤 按此說話 (Tap & Say)';
                return;
            }}
            status.textContent = '✅ 聽到: ' + text;
            mic.style.background = '#388E3C';
            syncText(text);
        }};

        recognition.onerror = (event) => {{
            listening = false;
            mic.style.background = '#2E7D32';
            mic.textContent = '🎤 按此說話 (Tap & Say)';
            status.textContent = '⚠️ 未能識別 (' + event.error + ') — 請再試一次';
        }};

        recognition.onend = () => {{
            if(listening) {{
                listening = false;
                mic.style.background = '#2E7D32';
                mic.textContent = '🎤 按此說話 (Tap & Say)';
            }}
        }};
    }} else {{
        mic.disabled = true;
        status.textContent = '❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)';
    }}

    mic.onclick = () => {{
        if(!recognition) return;
        if(listening) {{
            recognition.stop();
        }} else {{
            try {{ recognition.start(); }} catch(e) {{ recognition.stop(); recognition.start(); }}
        }}
    }};
    </script></body></html>
    """,
        height=310,
    )

    # Native Streamlit Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👉 提交答案 / 下一題", key=f"sub_{index}"):
            ans = (
                st.session_state.last_transcript.strip()
                if st.session_state.last_transcript.strip()
                else "未有說話"
            )
            correct = evaluate_answer(ans)
            if correct:
                st.success("✅ 正確！ (Correct!)", icon="✅")
                time.sleep(0.8)
            advance_item()
            st.rerun()

    with col2:
        if st.button("⏭️ 跳過", key=f"skip_{index}"):
            evaluate_answer("跳過")
            advance_item()
            st.rerun()

# STAGE 3: COMPLETE
elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 完成任務！感謝您的幫忙！")
    st.markdown(
        "<p style='font-size:24px;'>您已經成功分辨所有動物。</p>",
        unsafe_allow_html=True,
    )
    if st.button("再玩一次 (Play Again)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.last_transcript = ""
        st.query_params.clear()
        st.rerun()

    with st.expander(
        "🩺 Occupational Therapist / Speech Telemetry Dashboard", expanded=True
    ):
        st.subheader("MoCA Naming Sub-score (Spontaneous Confrontation)")
        c1, c2 = st.columns(2)
        with c1:
            st.metric(
                "MoCA Proxy Naming Sub-score",
                f"{st.session_state.moca_naming_score} / 3 Points",
            )
        with c2:
            if st.session_state.telemetry_logs:
                avg = pd.DataFrame(st.session_state.telemetry_logs)[
                    "speech_latency_seconds"
                ].mean()
                st.metric("Avg. Speech Latency", f"{round(avg, 2)} seconds")
            else:
                st.metric("Avg. Speech Latency", "N/A")
        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        if not df.empty:
            st.download_button(
                "📥 Download Speech Telemetry Log (.CSV)",
                df.to_csv(index=False).encode("utf-8"),
                f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
                "text/csv",
            )
