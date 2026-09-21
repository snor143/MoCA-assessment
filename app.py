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
.stButton>button { width:100%; height:70px; font-size:22px !important; font-weight:bold; border-radius:16px; background:#2E7D32; color:white; border:0; margin-bottom:12px; }
.stButton>button:hover { background:#1B5E20; }
.instruction-card { background:#F0F7F4; padding:24px; border-radius:16px; border-left:8px solid #2E7D32; margin-bottom:24px; }
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
    "manual_answer": "",
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


def reset_answer_state():
    st.session_state.manual_answer = ""


def advance_item():
    if st.session_state.current_item_index + 1 < len(ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
        reset_answer_state()
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
    <div class="instruction-card"><h2>婆婆/伯伯，今日我們要去街市買菜！</h2><p style="font-size:22px;">請睇睇螢幕上的動物，<b>用廣東話講出它的名字</b>。
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
        st.rerun()

elif st.session_state.stage == "gameplay":
    index = st.session_state.current_item_index
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
        f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "請先按下方按鈕，再按手機／平板鍵盤上的 🎙️ 麥克風，直接說出答案。"
    )
    answer_input = st.text_area(
        "答案（可修改或手動輸入）：",
        height=100,
        key="manual_answer",
        placeholder="按「開啟鍵盤麥克風」後，使用鍵盤的 🎙️ 說出答案",
    )

    # This button only focuses the Streamlit text area. The operating system's
    # keyboard microphone must be activated by the user; browsers do not allow
    # a webpage to turn on the device microphone or keyboard dictation silently.
    components.html(
        """
        <button id="focus-answer" type="button">🎙️ 開啟鍵盤麥克風 (Use Keyboard Mic)</button>
        <div id="focus-status" style="font:18px sans-serif;text-align:center;margin-top:8px;color:#555;">
          按鍵盤上的 🎙️，然後直接說出答案
        </div>
        <script>
        const button = document.getElementById('focus-answer');
        const status = document.getElementById('focus-status');
        button.style.cssText = 'width:100%;height:70px;font-size:22px;font-weight:bold;color:white;background:#E65100;border:0;border-radius:16px;cursor:pointer;';
        button.onclick = () => {
          const parent = window.parent.document;
          const textarea = parent.querySelector('textarea[aria-label="答案（可修改或手動輸入）："]') || parent.querySelector('textarea');
          if (textarea) {
            textarea.focus();
            textarea.click();
            status.textContent = '✅ 已選取答案欄位，請按鍵盤上的 🎙️ 並說話';
          } else {
            status.textContent = '請按一下答案欄位，再按鍵盤上的 🎙️';
          }
        };
        </script>
        """,
        height=115,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👉 提交答案 / 下一題"):
            finish_answer(answer_input)
    with col2:
        if st.button("⏭️ 跳過"):
            finish_answer("跳過")

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
        st.rerun()
