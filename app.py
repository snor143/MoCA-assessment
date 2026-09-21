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

st.markdown("""
<style>
.main { background-color: #FFFDF9; }
.stButton>button { width: 100%; height: 70px; font-size: 22px !important; font-weight: bold; border-radius: 16px; background-color: #2E7D32; color: white; border: none; margin-bottom: 12px; }
.stButton>button:hover { background-color: #1B5E20; }
.instruction-card { background-color: #F0F7F4; padding: 24px; border-radius: 16px; border-left: 8px solid #2E7D32; margin-bottom: 24px; }
</style>
""", unsafe_allow_html=True)

for name, default in {
    "stage": "intro",
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "last_transcript": "",
}.items():
    if name not in st.session_state:
        st.session_state[name] = default

ITEMS = [
    {
        "id": "item_1", "tier": "High Familiarity (Warmup)", "emoji": "🐓",
        "primary_name": "雞",
        "acceptable_synonyms": ["雞", "公雞", "母雞", "雞仔", "呢個係雞", "這是雞", "隻係雞"],
        "moca_weight": 1,
    },
    {
        "id": "item_2", "tier": "Moderate Familiarity", "emoji": "🐙",
        "primary_name": "八爪魚",
        "acceptable_synonyms": ["八爪魚", "章魚", "呢個係八爪魚", "這是八爪魚", "隻係八爪魚"],
        "moca_weight": 1,
    },
    {
        "id": "item_3", "tier": "Low Familiarity (MoCA Rhino Equivalent)", "emoji": "🦥",
        "primary_name": "樹懶",
        "acceptable_synonyms": ["樹懶", "呢個係樹懶", "這是樹懶", "隻係樹懶"],
        "moca_weight": 1,
    },
]


def evaluate_answer(answer):
    item = ITEMS[st.session_state.current_item_index]
    elapsed = round(time.time() - st.session_state.item_start_time, 2) if st.session_state.item_start_time else 0.0
    clean = (
        answer.strip().replace(" ", "").replace("呢個係", "")
        .replace("這是", "").replace("隻係", "").replace("個位是", "")
    )
    correct = any(
        synonym in answer or synonym in clean
        for synonym in item["acceptable_synonyms"]
    )
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


def navigate_parent(extra_params):
    """JavaScript helper used inside the speech/answer iframe."""
    params = "&".join(
        f"{key}={value}" for key, value in extra_params.items()
    )
    return f"""
        const url = new URL(window.parent.location.href);
        url.search = '';
        {''.join(f'url.searchParams.set({key!r}, {value!r});' for key, value in extra_params.items())}
        window.parent.location.assign(url.toString());
    """


if st.session_state.stage == "intro":
    st.title("🛒 香港街市語音買菜 (HK Market Voice Explorer)")
    st.markdown("""
    <div class="instruction-card">
      <h2>婆婆/伯伯，今日我們要去街市買菜！</h2>
      <p style="font-size: 22px;">請睇睇螢幕上的食材，<b>用廣東話講出它的名字</b>。</p>
      <p style="font-size: 18px; color: #555;">(例如說：「呢個係雞」或「八爪魚」)</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("開始買菜 (Start Voice Assessment)"):
        st.session_state.stage = "gameplay"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.last_transcript = ""
        st.session_state.item_start_time = time.time()
        st.query_params.clear()
        st.rerun()

elif st.session_state.stage == "gameplay":
    index = st.session_state.current_item_index

    # Voice and textarea actions return through URL parameters. Unlike a
    # Streamlit text_input, the textarea is owned by this HTML component, so
    # JavaScript can both populate it and read any manual edits reliably.
    transcript = st.query_params.get("speech_result")
    submitted = st.query_params.get("answer_submission")
    skipped = st.query_params.get("skip_item")

    if transcript is not None:
        st.session_state.last_transcript = str(transcript)
        st.query_params.clear()
        st.rerun()

    if submitted is not None or skipped is not None:
        answer = "跳過" if skipped is not None else str(submitted)
        correct = evaluate_answer(answer)
        st.query_params.clear()
        if correct:
            st.success("✅ 正確！ (Correct!)", icon="✅")
            time.sleep(0.8)
        advance_item()
        st.rerun()

    item = ITEMS[index]
    initial_answer = html.escape(st.session_state.last_transcript, quote=True)
    visible_transcript = html.escape(st.session_state.last_transcript or "尚未有語音結果", quote=False)

    st.markdown(f"<p style='font-size:22px;text-align:center;color:#666;'>進度: {index + 1} / {len(ITEMS)}</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>請大聲講出，這是什麼食材？</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:18px;color:#2E7D32;'>💡 提示：可以說<b>「呢個係...」</b>（例如：「呢個係雞」）</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>", unsafe_allow_html=True)

    components.html(f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
    body {{ margin: 0; font-family: sans-serif; }}
    .mic-btn, .answer-btn {{ width:100%; height:70px; font-size:22px; font-weight:bold; color:white; border:0; border-radius:16px; cursor:pointer; margin-bottom:10px; }}
    .mic-btn {{ background:#E65100; }}
    .answer-btn {{ background:#2E7D32; }}
    .skip-btn {{ background:#607D8B; }}
    .mic-btn:disabled, .answer-btn:disabled {{ opacity:.65; cursor:wait; }}
    .status-text {{ font-size:20px; color:#333; text-align:center; margin:8px 0; min-height:30px; }}
    label {{ display:block; font-size:18px; margin:10px 0 6px; }}
    textarea {{ box-sizing:border-box; width:100%; min-height:70px; padding:12px; font-size:22px; border:2px solid #4CAF50; border-radius:12px; resize:vertical; }}
    .display {{ background:#E8F5E9; padding:12px; border-radius:12px; font-size:20px; margin:10px 0; }}
    </style></head><body>
    <button class="mic-btn" id="mic" type="button">🎤 按此說話 (Tap & Say)</button>
    <div class="status-text" id="status">點擊上方按鈕並講出名稱</div>
    <div class="display">🎤 語音結果：<span id="display">{visible_transcript}</span></div>
    <label for="answer">答案（可修改或手動輸入）：</label>
    <textarea id="answer" placeholder="語音結果會顯示在這裡；也可以手動輸入">{initial_answer}</textarea>
    <button class="answer-btn" id="submit" type="button">👉 提交答案 / 下一題</button>
    <button class="answer-btn skip-btn" id="skip" type="button">⏭️ 跳過</button>
    <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic');
    const status = document.getElementById('status');
    const answer = document.getElementById('answer');
    const display = document.getElementById('display');
    let recognition = null;
    let listening = false;
    let navigating = false;

    function parentNavigate(name, value) {{
      const url = new URL(window.parent.location.href);
      url.search = '';
      url.searchParams.set(name, value);
      window.parent.location.assign(url.toString());
    }}
    function ready(message) {{
      listening = false;
      mic.disabled = false;
      mic.style.background = '#E65100';
      mic.innerHTML = '🎤 按此說話 (Tap & Say)';
      status.textContent = message || '點擊上方按鈕並講出名稱';
    }}

    if (SpeechRecognition) {{
      recognition = new SpeechRecognition();
      recognition.lang = 'zh-HK';
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.onstart = function() {{
        listening = true;
        mic.style.background = '#D32F2F';
        mic.innerHTML = '⏹️ 停止聆聽 (Stop)';
        status.textContent = '🔴 正在聆聽中，請講話...';
      }};
      recognition.onresult = function(event) {{
        const text = event.results[0][0].transcript.trim();
        if (!text) {{ ready('⚠️ 沒有聽到內容 — 請再試一次'); return; }}
        listening = false;
        navigating = true;
        answer.value = text;
        display.textContent = text;
        mic.style.background = '#388E3C';
        parentNavigate('speech_result', text);
      }};
      recognition.onerror = function(event) {{
        navigating = false;
        ready('⚠️ 未能識別 (' + event.error + ') — 請再試一次');
      }};
      recognition.onend = function() {{
        if (!navigating) ready();
      }};
    }} else {{
      mic.disabled = true;
      status.textContent = '❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)';
    }}

    mic.addEventListener('click', function() {{
      if (!recognition) return;
      if (listening) {{ recognition.stop(); return; }}
      navigating = false;
      ready();
      try {{ recognition.start(); }} catch (error) {{ ready('⚠️ 麥克風未能啟動 — 請再試一次'); }}
    }});
    document.getElementById('submit').addEventListener('click', function() {{
      parentNavigate('answer_submission', answer.value);
    }});
    document.getElementById('skip').addEventListener('click', function() {{
      parentNavigate('skip_item', '1');
    }});
    </script></body></html>
    """, height=470)

elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 買菜完成！感謝您的幫忙！")
    st.markdown("<p style='font-size:24px;'>您已經成功將所有食材放入購物車。</p>", unsafe_allow_html=True)
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
        c1, c2 = st.columns(2)
        with c1:
            st.metric("MoCA Proxy Naming Sub-score", f"{st.session_state.moca_naming_score} / 3 Points")
        with c2:
            if st.session_state.telemetry_logs:
                avg = pd.DataFrame(st.session_state.telemetry_logs)["speech_latency_seconds"].mean()
                st.metric("Avg. Speech Latency", f"{round(avg, 2)} seconds")
            else:
                st.metric("Avg. Speech Latency", "N/A")
        st.subheader("Raw Speech Telemetry Stream (.csv)")
        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        if not df.empty:
            st.download_button(
                "📥 Download Speech Telemetry Log (.CSV)",
                df.to_csv(index=False).encode("utf-8"),
                f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
                "text/csv",
            )
