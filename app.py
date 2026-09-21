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

st.markdown(
    """
    <style>
    .main { background-color: #FFFDF9; }
    .stButton>button {
        width: 100%; height: 70px; font-size: 22px !important;
        font-weight: bold; border-radius: 16px; background: #2E7D32;
        color: white; border: 0; margin-bottom: 12px;
    }
    .stButton>button:hover { background: #1B5E20; }
    .instruction-card {
        background: #F0F7F4; padding: 24px; border-radius: 16px;
        border-left: 8px solid #2E7D32; margin-bottom: 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Session state
# -----------------------------
for key, default in {
    "stage": "intro",
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "last_transcript": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

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
    """Score and log the submitted answer."""
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
    is_correct = any(
        synonym in answer or synonym in clean
        for synonym in item["acceptable_synonyms"]
    )

    if is_correct:
        st.session_state.moca_naming_score += item["moca_weight"]

    st.session_state.telemetry_logs.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "item_id": item["id"],
            "target_name": item["primary_name"],
            "user_spoken_raw": answer,
            "is_correct": is_correct,
            "speech_latency_seconds": elapsed,
        }
    )
    return is_correct


def advance_item():
    """Move to the next item or show the completion screen."""
    if st.session_state.current_item_index + 1 < len(ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
        st.session_state.last_transcript = ""
    else:
        st.session_state.stage = "complete"


# -----------------------------
# Intro screen
# -----------------------------
if st.session_state.stage == "intro":
    st.title("🛒 香港街市語音買菜 (HK Market Voice Explorer)")
    st.markdown(
        """
        <div class="instruction-card">
            <h2>婆婆/伯伯，今日我們要去街市買菜！</h2>
            <p style="font-size:22px;">請睇睇螢幕上的動物，<b>用廣東話講出它的名字</b>。</p>
            <p style="font-size:18px;color:#555;">(例如說：「呢個係蝴蝶」)</p>
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

# -----------------------------
# Gameplay
# -----------------------------
elif st.session_state.stage == "gameplay":
    index = st.session_state.current_item_index
    current_key = f"answer_{index}"

    # The microphone iframe sends only the transcript. Process it before
    # creating the Streamlit text_input, then rerun once so the input receives
    # the value safely.
    transcript = st.query_params.get("speech_result")
    if transcript is not None:
        st.session_state.last_transcript = str(transcript)
        st.query_params.clear()
        st.session_state[current_key] = st.session_state.last_transcript
        st.rerun()

    # Keep the current transcript in the native Streamlit input. The user can
    # edit it or replace it with a manually typed answer.
    if current_key not in st.session_state:
        st.session_state[current_key] = st.session_state.last_transcript

    item = ITEMS[index]
    st.markdown(
        f"<p style='font-size:22px;text-align:center;color:#666;'>進度: {index + 1} / {len(ITEMS)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align:center;'>請大聲講出，這是什麼動物？</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;font-size:18px;color:#2E7D20;'>💡 提示：可以說<b>「呢個係...」</b></p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>",
        unsafe_allow_html=True,
    )

    # This component contains microphone controls only. Submit and Skip are
    # deliberately NOT inside the iframe because native Streamlit buttons are
    # more reliable and can directly run the Python scoring code.
    components.html(
        """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { margin: 0; font-family: sans-serif; }
                button {
                    width: 100%; height: 85px; font-size: 24px;
                    font-weight: bold; color: white; border: 0;
                    border-radius: 18px; cursor: pointer;
                }
                #mic { background: #E65100; }
                .status {
                    font-size: 20px; text-align: center;
                    min-height: 30px; margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <button id="mic" type="button">🎤 按此說話 (Tap & Say)</button>
            <div class="status" id="status">點擊上方按鈕並講出名稱</div>

            <script>
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const mic = document.getElementById('mic');
                const status = document.getElementById('status');
                let recognition = null;
                let listening = false;
                let navigating = false;

                function ready(message) {
                    listening = false;
                    mic.disabled = false;
                    mic.style.background = '#E65100';
                    mic.textContent = '🎤 按此說話 (Tap & Say)';
                    status.textContent = message || '點擊上方按鈕並講出名稱';
                }

                function sendTranscript(text) {
                    // Navigate the top-level Streamlit page. The Python code
                    // receives this as st.query_params['speech_result'].
                    const url = new URL(window.top.location.href);
                    url.search = '';
                    url.searchParams.set('speech_result', text);
                    window.top.location.href = url.toString();
                }

                if (SpeechRecognition) {
                    recognition = new SpeechRecognition();
                    recognition.lang = 'zh-HK';
                    recognition.continuous = false;
                    recognition.interimResults = false;

                    recognition.onstart = function() {
                        listening = true;
                        mic.style.background = '#D32F2F';
                        mic.textContent = '⏹️ 停止聆聽 (Stop)';
                        status.textContent = '🔴 正在聆聽中，請講話...';
                    };

                    recognition.onresult = function(event) {
                        const text = event.results[0][0].transcript.trim();
                        if (!text) {
                            ready('⚠️ 沒有聽到內容 — 請再試一次');
                            return;
                        }
                        navigating = true;
                        status.textContent = '✅ 聽到: ' + text;
                        mic.style.background = '#388E3C';
                        sendTranscript(text);
                    };

                    recognition.onerror = function(event) {
                        navigating = false;
                        ready('⚠️ 未能識別 (' + event.error + ') — 請再試一次');
                    };

                    recognition.onend = function() {
                        if (!navigating) ready();
                    };
                } else {
                    mic.disabled = true;
                    status.textContent = '❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)';
                }

                mic.onclick = function() {
                    if (!recognition) return;
                    if (listening) {
                        recognition.stop();
                        return;
                    }
                    navigating = false;
                    ready();
                    try {
                        recognition.start();
                    } catch (error) {
                        ready('⚠️ 麥克風未能啟動 — 請再試一次');
                    }
                };
            </script>
        </body>
        </html>
        """,
        height=150,
    )

    st.markdown("---")

    # This is the editable backup input. Speech recognition populates it, and
    # the user can still type or correct the answer manually.
    answer = st.text_input(
        "識別結果 / 手動輸入 (Recognized Text / Manual Input):",
        key=current_key,
        placeholder="語音結果會顯示在這裡；也可以手動輸入",
    )

    # These are native Streamlit buttons, restored from the older working
    # version. Their click events execute directly in Python.
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👉 提交答案 / 下一題 (Submit / Next)", key=f"next_{index}"):
            submitted_answer = answer.strip() or "未有說話"
            correct = evaluate_answer(submitted_answer)
            if correct:
                st.success("✅ 正確！ (Correct!)", icon="✅")
                time.sleep(0.8)
            advance_item()
            st.rerun()

    with col2:
        if st.button("⏭️ 跳過 (Skip Item)", key=f"skip_{index}"):
            # Skip is logged as incorrect and therefore receives zero marks.
            evaluate_answer("跳過")
            advance_item()
            st.rerun()

# -----------------------------
# Complete screen
# -----------------------------
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

    with st.expander("🩺 Occupational Therapist / Speech Telemetry Dashboard", expanded=True):
        st.subheader("MoCA Naming Sub-score (Spontaneous Confrontation)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "MoCA Proxy Naming Sub-score",
                f"{st.session_state.moca_naming_score} / {len(ITEMS)} Points",
            )
        with col2:
            if st.session_state.telemetry_logs:
                average = pd.DataFrame(st.session_state.telemetry_logs)["speech_latency_seconds"].mean()
                st.metric("Avg. Speech Latency", f"{round(average, 2)} seconds")
            else:
                st.metric("Avg. Speech Latency", "N/A")

        st.subheader("Raw Speech Telemetry Stream (.csv)")
        dataframe = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(dataframe)

        if not dataframe.empty:
            st.download_button(
                "📥 Download Speech Telemetry Log (.CSV)",
                dataframe.to_csv(index=False).encode("utf-8"),
                f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
                "text/csv",
            )
