import streamlit as st
import time
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="HK Supermarket Explorer - Voice Naming", page_icon="🛒", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.main { background-color: #FFFDF9; }
.stButton>button { width: 100%; height: 70px; font-size: 22px !important; font-weight: bold; border-radius: 16px; background-color: #2E7D32; color: white; border: none; margin-bottom: 12px; }
.stButton>button:hover { background-color: #1B5E20; }
.instruction-card { background-color: #F0F7F4; padding: 24px; border-radius: 16px; border-left: 8px solid #2E7D32; margin-bottom: 24px; }
</style>
""", unsafe_allow_html=True)

for name, default in {
    "stage": "intro", "current_item_index": 0, "telemetry_logs": [],
    "item_start_time": None, "moca_naming_score": 0,
    "answer_revision": 0, "last_transcript": "",
}.items():
    if name not in st.session_state:
        st.session_state[name] = default

ITEMS = [
    {"id": "item_1", "tier": "High Familiarity (Warmup)", "emoji": "🐓", "primary_name": "雞", "acceptable_synonyms": ["雞", "公雞", "母雞", "雞仔", "呢個係雞", "這是雞", "隻係雞"], "moca_weight": 1},
    {"id": "item_2", "tier": "Moderate Familiarity", "emoji": "🐙", "primary_name": "八爪魚", "acceptable_synonyms": ["八爪魚", "章魚", "呢個係八爪魚", "這是八爪魚", "隻係八爪魚"], "moca_weight": 1},
    {"id": "item_3", "tier": "Low Familiarity (MoCA Rhino Equivalent)", "emoji": "🦥", "primary_name": "樹懶", "acceptable_synonyms": ["樹懶", "呢個係樹懶", "這是樹懶", "隻係樹懶"], "moca_weight": 1},
]


def evaluate_cantonese_speech(spoken_text):
    item = ITEMS[st.session_state.current_item_index]
    elapsed = round(time.time() - st.session_state.item_start_time, 2) if st.session_state.item_start_time else 0.0
    clean = spoken_text.strip().replace(" ", "").replace("呢個係", "").replace("這是", "").replace("隻係", "").replace("個位是", "")
    correct = any(s in spoken_text or s in clean for s in item["acceptable_synonyms"])
    st.session_state.show_tick_feedback = correct
    if correct:
        st.session_state.moca_naming_score += item["moca_weight"]
    st.session_state.telemetry_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_id": item["id"], "target_name": item["primary_name"],
        "user_spoken_raw": spoken_text, "is_correct": correct,
        "speech_latency_seconds": elapsed,
    })
    st.session_state.pending_advance = True


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
        st.session_state.answer_revision = 0
        st.session_state.last_transcript = ""
        st.session_state.item_start_time = time.time()
        st.query_params.clear()
        st.rerun()

elif st.session_state.stage == "gameplay":
    index = st.session_state.current_item_index

    # A new widget key is deliberately created for every voice result. This
    # prevents Streamlit's already-mounted text_input from restoring its old
    # browser value over the newly received transcript.
    transcript = st.query_params.get("speech_result", "")
    if transcript:
        transcript = str(transcript)
        st.session_state.last_transcript = transcript
        st.session_state.answer_revision += 1
        st.query_params.clear()
        st.rerun()

    current_key = f"manual_in_{index}_{st.session_state.answer_revision}"
    if st.session_state.last_transcript:
        st.session_state[current_key] = st.session_state.last_transcript

    def advance_to_next_item():
        st.session_state.show_tick_feedback = False
        st.session_state.pending_advance = False
        st.session_state.last_transcript = ""
        st.session_state.answer_revision += 1
        st.query_params.clear()
        if index + 1 < len(ITEMS):
            st.session_state.current_item_index += 1
            st.session_state.item_start_time = time.time()
        else:
            st.session_state.stage = "complete"

    if st.session_state.get("pending_advance", False):
        if st.session_state.get("show_tick_feedback", False):
            st.success("✅ 正確！ (Correct!)", icon="✅")
            time.sleep(1.0)
        advance_to_next_item()
        st.rerun()

    item = ITEMS[index]
    st.markdown(f"<p style='font-size:22px;text-align:center;color:#666;'>進度: {index + 1} / {len(ITEMS)}</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>請大聲講出，這是什麼食材？</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:18px;color:#2E7D32;'>💡 提示：可以說<b>「呢個係...」</b>（例如：「呢個係雞」）</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>", unsafe_allow_html=True)

    if st.session_state.last_transcript:
        st.info(f"🎤 語音辨識結果：{st.session_state.last_transcript}")

    components.html(f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"><style>
    .mic-btn {{ width:100%; height:85px; font-size:24px; font-weight:bold; background:#E65100; color:white; border:0; border-radius:18px; cursor:pointer; box-shadow:0 4px 8px rgba(0,0,0,.15); }}
    .mic-btn:disabled {{ opacity: .85; cursor: wait; }}
    .status-text {{ font-size:20px; font-family:sans-serif; color:#333; text-align:center; margin-top:10px; }}
    </style></head><body>
    <button class="mic-btn" id="start-btn" type="button">🎤 按此說話 (Tap & Say "呢個係...")</button>
    <div class="status-text" id="status">點擊上方按鈕並講出名稱</div>
    <script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const button = document.getElementById('start-btn');
    const status = document.getElementById('status');
    let recognition = null;
    let active = false;
    let gotResult = false;
    let navigating = false;

    function ready(message) {{
      active = false;
      gotResult = false;
      button.disabled = false;
      button.style.pointerEvents = 'auto';
      button.style.backgroundColor = '#E65100';
      button.innerHTML = '🎤 按此說話 (Tap & Say "呢個係...")';
      status.textContent = message || '點擊上方按鈕並講出名稱';
    }}

    if (SpeechRecognition) {{
      recognition = new SpeechRecognition();
      recognition.lang = 'zh-HK';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = function() {{
        active = true;
        gotResult = false;
        button.disabled = false;
        button.style.pointerEvents = 'auto';
        button.style.backgroundColor = '#D32F2F';
        button.innerHTML = '⏹️ 停止聆聽 (Stop)';
        status.textContent = '🔴 正在聆聽中，請講話... (Listening...)';
      }};

      recognition.onresult = function(event) {{
        gotResult = true;
        active = false;
        const text = event.results[0][0].transcript.trim();
        status.textContent = text ? '✅ 聽到: ' + text : '⚠️ 沒有聽到內容';
        button.style.backgroundColor = '#388E3C';
        if (!text) {{ ready('⚠️ 沒有聽到內容 — 請再試一次'); return; }}

        // Navigate the parent Streamlit page with the transcript. The Python
        // code consumes this once, creates a fresh input key, and reruns.
        navigating = true;
        const url = new URL(window.parent.location.href);
        url.searchParams.set('speech_result', text);
        window.parent.location.assign(url.toString());
      }};

      recognition.onerror = function(event) {{
        active = false;
        navigating = false;
        ready('⚠️ 未能識別 (' + event.error + ') — 請再試一次');
      }};

      recognition.onend = function() {{
        // No-speech, aborted, and other failed sessions must never remain
        // labelled Listening. Successful results are being navigated.
        if (!gotResult && !navigating) ready();
      }};
    }} else {{
      button.disabled = true;
      status.textContent = '❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)';
    }}

    button.addEventListener('click', function() {{
      if (!recognition) return;
      if (active) {{ recognition.stop(); return; }}
      navigating = false;
      ready();
      try {{ recognition.start(); }}
      catch (error) {{ ready('⚠️ 麥克風未能啟動 — 請再試一次'); }}
    }});
    </script></body></html>
    """, height=150)

    st.markdown("---")
    manual_input = st.text_input(
        "識別結果 / 手動輸入 (Recognized Text / Manual Input):",
        key=current_key,
        placeholder="語音結果會顯示在這裡；也可以手動輸入",
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👉 提交答案 / 下一題 (Submit / Next)", key=f"btn_next_{index}"):
            # The value here comes from either speech recognition or manual entry.
            evaluate_cantonese_speech(manual_input.strip() or "未有說話")
            st.rerun()
    with col2:
        if st.button("⏭️ 跳過 (Skip Item)", key=f"btn_skip_{index}"):
            evaluate_cantonese_speech("跳過")
            st.rerun()

elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 買菜完成！感謝您的幫忙！")
    st.markdown("<p style='font-size:24px;'>您已經成功將所有食材放入購物車。</p>", unsafe_allow_html=True)
    if st.button("再玩一次 (Play Again)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.answer_revision = 0
        st.session_state.last_transcript = ""
        st.query_params.clear()
        st.rerun()
    st.markdown("---")
    with st.expander("🩺 Occupational Therapist / Speech Telemetry Dashboard", expanded=True):
        st.subheader("MoCA Naming Sub-score (Spontaneous Confrontation)")
        c1, c2 = st.columns(2)
        with c1: st.metric("MoCA Proxy Naming Sub-score", f"{st.session_state.moca_naming_score} / 3 Points")
        with c2:
            if st.session_state.telemetry_logs:
                avg = pd.DataFrame(st.session_state.telemetry_logs)["speech_latency_seconds"].mean()
                st.metric("Avg. Speech Latency", f"{round(avg, 2)} seconds")
            else: st.metric("Avg. Speech Latency", "N/A")
        st.subheader("Raw Speech Telemetry Stream (.csv)")
        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        if not df.empty:
            st.download_button("📥 Download Speech Telemetry Log (.CSV)", df.to_csv(index=False).encode("utf-8"), f"moca_cantonese_speech_telemetry_{int(time.time())}.csv", "text/csv")
