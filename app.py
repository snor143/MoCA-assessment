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

st.markdown(
    """
<style>
.main { background-color:#FFFDF9; }
.stButton>button {
    width:100%;
    height:70px;
    font-size:22px !important;
    font-weight:bold;
    border-radius:16px;
    background:#2E7D32;
    color:white;
    border:0;
    margin-bottom:12px;
}
.stButton>button:hover { background:#1B5E20; }
.instruction-card {
    background:#F0F7F4;
    padding:24px;
    border-radius:16px;
    border-left:8px solid #2E7D32;
    margin-bottom:24px;
}
</style>
""",
    unsafe_allow_html=True,
)

for key, value in {
    "stage": "intro",
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "last_transcript": "",
    "answer_box": "",
    "voice_ready": False,
    "pending_answer_reset": False,
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
        if st.session_state.item_start_time is not None
        else 0.0
    )
    answer = str(answer).strip()
    clean = (
        answer.replace(" ", "")
        .replace("呢個係", "")
        .replace("這是", "")
        .replace("呢隻係", "")
        .replace("嗰位是", "")
    )
    target = item["primary_name"]
    correct = target in answer or target in clean
    if correct:
        st.session_state.moca_naming_score += item["moca_weight"]

    st.session_state.telemetry_logs.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "item_id": item["id"],
            "target_name": target,
            "user_spoken_raw": answer,
            "is_correct": correct,
            "speech_latency_seconds": elapsed,
        }
    )
    return correct


def record_skip():
    item = ITEMS[st.session_state.current_item_index]
    elapsed = (
        round(time.time() - st.session_state.item_start_time, 2)
        if st.session_state.item_start_time is not None
        else 0.0
    )
    st.session_state.telemetry_logs.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "item_id": item["id"],
            "target_name": item["primary_name"],
            "user_spoken_raw": "",
            "is_correct": False,
            "speech_latency_seconds": elapsed,
        }
    )


def reset_answer_state():
    st.session_state.answer_box = ""
    st.session_state.last_transcript = ""
    st.session_state.voice_ready = False
    st.session_state.pending_answer_reset = False


def advance_item():
    if st.session_state.current_item_index + 1 < len(ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
        st.session_state.pending_answer_reset = True
    else:
        st.session_state.stage = "complete"


def finish_answer(answer):
    correct = evaluate_answer(answer)
    if correct:
        st.success("✅ 正確！ (Correct!)", icon="✅")
        time.sleep(0.8)
    advance_item()
    st.rerun()


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
        st.session_state.item_start_time = time.time()
        reset_answer_state()
        st.query_params.clear()
        st.rerun()

elif st.session_state.stage == "gameplay":
    if st.session_state.pending_answer_reset:
        reset_answer_state()

    voice_result = st.query_params.get("voice_answer")
    if voice_result is not None:
        transcript_text = str(voice_result).strip()
        st.session_state.last_transcript = transcript_text
        st.session_state.answer_box = transcript_text
        st.session_state.voice_ready = bool(transcript_text)
        st.query_params.clear()
        st.rerun()

    index = st.session_state.current_item_index
    item = ITEMS[index]
    displayed = html.escape(st.session_state.last_transcript or "尚未有語音結果")

    st.markdown(
        f"<p style='font-size:22px;text-align:center;color:#666;'>進度: {index + 1} / {len(ITEMS)}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align:center;'>請大聲講出，這是什麼動物？</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>",
        unsafe_allow_html=True,
    )

    components.html(
        f"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8">
            <style>
              body {{ margin:0; font-family:sans-serif; }}
              button {{ width:100%; height:70px; font-size:22px; font-weight:bold; color:white; border:0; border-radius:16px; cursor:pointer; margin-bottom:10px; }}
              #mic {{ background:#E65100; }}
              .status, .display {{ font-size:18px; text-align:center; margin:8px 0; color:#555; }}
            </style>
          </head>
          <body>
            <button id="mic" type="button">🎙️ 按此啟用 Google 語音 (Start Microphone)</button>
            <div class="status" id="status">按一下按鈕，允許麥克風，然後說出答案</div>
            <div class="display">語音結果：<span id="display">{displayed}</span></div>
            <script>
              const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
              const mic = document.getElementById('mic');
              const status = document.getElementById('status');
              const display = document.getElementById('display');
              let recognition = null;
              let listening = false;

              function sendTranscript(text) {{
                const url = new URL(window.parent.location.href);
                url.search = '';
                url.searchParams.set('voice_answer', text);
                window.parent.location.assign(url.toString());
              }}

              function resetButton(message) {{
                listening = false;
                mic.disabled = false;
                mic.style.background = '#E65100';
                mic.textContent = '🎙️ 按此啟用 Google 語音 (Start Microphone)';
                status.textContent = message || '按一下按鈕，然後說出答案';
              }}

              if (SpeechRecognition) {{
                recognition = new SpeechRecognition();
                recognition.lang = 'zh-HK';
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;

                recognition.onstart = () => {{
                  listening = true;
                  mic.style.background = '#D32F2F';
                  mic.textContent = '⏹️ 正在聆聽...';
                  status.textContent = '🔴 請說出動物名稱';
                }};

                recognition.onresult = (event) => {{
                  const text = event.results[0][0].transcript.trim();
                  if (!text) {{ resetButton('⚠️ 沒有聽到內容，請再試一次'); return; }}
                  display.textContent = text;
                  status.textContent = '✅ 已轉換成文字，正在填入答案欄...';
                  sendTranscript(text);
                }};

                recognition.onerror = (event) => {{
                  const message = event.error === 'not-allowed'
                    ? '⚠️ 請在瀏覽器允許此網站使用麥克風'
                    : '⚠️ 語音辨識失敗（' + event.error + '），請再試一次';
                  resetButton(message);
                }};

                recognition.onend = () => {{
                  if (!listening) resetButton();
                }};
              }} else {{
                mic.disabled = true;
                status.textContent = '❌ 請使用最新版 Chrome 或 Safari';
              }}

              mic.onclick = () => {{
                if (!recognition) return;
                if (listening) {{ recognition.stop(); return; }}
                try {{ recognition.start(); }}
                catch (error) {{ resetButton('⚠️ 麥克風未能啟動，請再試一次'); }}
              }};
            </script>
          </body>
        </html>
        """,
        height=230,
    )

    answer_input = st.text_area(
        "答案（語音文字可修改）：",
        key="answer_box",
        height=100,
        placeholder="按上方按鈕說話，文字會顯示在這裡",
    )

    st.session_state.last_transcript = st.session_state.answer_box
    if st.session_state.voice_ready:
        st.success("已將語音轉成文字並填入答案欄，請提交或按下一題。")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ 提交答案"):
            finish_answer(st.session_state.answer_box)
    with col2:
        if st.button("➡️ 下一題"):
            finish_answer(st.session_state.answer_box)
    with col3:
        if st.button("⏭️ 跳過"):
            record_skip()
            advance_item()
            st.rerun()

elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 完成任務！感謝您的幫忙！")
    st.markdown(
        "<p style='font-size:24px;'>您已經完成全部三項命名測試。</p>",
        unsafe_allow_html=True,
    )
    st.subheader("MoCA Naming Result Report")
    st.metric("MoCA Naming Score", f"{st.session_state.moca_naming_score} / {len(ITEMS)}")

    df = pd.DataFrame(st.session_state.telemetry_logs)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        avg = df["speech_latency_seconds"].mean()
        st.metric("Average Speech Latency", f"{round(avg, 2)} seconds")
        st.download_button(
            "📥 Download Speech Telemetry Log (.CSV)",
            df.to_csv(index=False).encode("utf-8"),
            f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
            "text/csv",
        )

    if st.button("再玩一次 (Play Again)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.item_start_time = time.time()
        reset_answer_state()
        st.query_params.clear()
        st.rerun()
