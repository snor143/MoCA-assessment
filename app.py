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
.stButton>button { width:100%; height:70px; font-size:22px !important; font-weight:bold; border-radius:16px; background:#2E7D32; color:white; border:0; margin-bottom:12px; }
.stButton>button:hover { background:#1B5E20; }
.instruction-card { background:#F0F7F4; padding:24px; border-radius:16px; border-left:8px solid #2E7D32; margin-bottom:24px; }
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
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 2. State Recovery: Recover progress after query param reload
if any(
    k in st.query_params
    for k in ["answer_submission", "skip_item", "speech_result"]
):
    st.session_state.stage = "gameplay"
    if "item_idx" in st.query_params:
        try:
            st.session_state.current_item_index = int(
                st.query_params["item_idx"]
            )
        except ValueError:
            pass

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
    transcript = st.query_params.get("speech_result")
    submission = st.query_params.get("answer_submission")
    skip = st.query_params.get("skip_item")

    if transcript is not None:
        st.session_state.last_transcript = str(transcript)
        st.query_params.clear()
        st.rerun()

    if submission is not None or skip is not None:
        answer = "跳過" if skip is not None else str(submission)
        correct = evaluate_answer(answer)
        st.query_params.clear()
        if correct:
            st.success("✅ 正確！ (Correct!)", icon="✅")
            time.sleep(0.8)
        advance_item()
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
        "<p style='text-align:center;font-size:18px;color:#2E7D32;'>💡 提示：可以說<b>「呢個係...」</b>（例如：「呢個係蝴蝶」）</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='font-size:130px;text-align:center;margin:10px 0;'>{item['emoji']}</div>",
        unsafe_allow_html=True,
    )

    components.html(
        f"""
    <!-- item_id_{index} -->
    <!doctype html><html><head><meta charset="utf-8"><style>
    body{{margin:0;font-family:sans-serif}}
    button{{width:100%;height:70px;font-size:22px;font-weight:bold;color:white;border:0;border-radius:16px;cursor:pointer;margin-bottom:10px}}
    #mic{{background:#E65100}}
    #submit{{background:#2E7D32}}
    #skip{{background:#607D8B}}
    button:disabled{{opacity:.65;cursor:wait}}
    .status{{font-size:20px;text-align:center;min-height:30px;margin:8px 0}}
    label{{display:block;font-size:18px;margin:10px 0 6px}}
    textarea{{box-sizing:border-box;width:100%;min-height:70px;padding:12px;font-size:22px;border:2px solid #4CAF50;border-radius:12px;resize:vertical}}
    .display{{background:#E8F5E9;padding:12px;border-radius:12px;font-size:20px;margin:10px 0}}
    </style></head><body>
    <button id="mic" type="button">🎤 按此說話 (Tap & Say)</button>
    <div class="status" id="status">點擊上方按鈕並講出名稱</div>
    <div class="display">🎤 語音結果：<span id="display">{displayed}</span></div>
    <label for="answer">答案（可修改或手動輸入）：</label>
    <textarea id="answer" placeholder="語音結果會顯示在這裡；也可以手動輸入">{initial}</textarea>
    <button id="submit" type="button">👉 提交答案 / 下一題</button>
    <button id="skip" type="button">⏭️ 跳過</button>
    <script>
    const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    const mic=document.getElementById('mic'), status=document.getElementById('status'), answer=document.getElementById('answer'), display=document.getElementById('display');
    let recognition=null, listening=false, navigating=false;

    function go(name,value) {{
      let urlStr = window.location.href;
      try {{ urlStr = window.top.location.href; }} catch(e) {{}}
      const url = new URL(urlStr);
      url.search = '';
      url.searchParams.set(name, value);
      url.searchParams.set('item_idx', '{index}');
      try {{ window.top.location.href = url.toString(); }} 
      catch(e) {{ window.location.href = url.toString(); }}
    }}

    function ready(message) {{
      listening=false;
      mic.disabled=false;
      mic.style.background='#E65100';
      mic.textContent='🎤 按此說話 (Tap & Say)';
      status.textContent=message||'點擊上方按鈕並講出名稱';
    }}

    if(SR) {{
      recognition=new SR();
      recognition.lang='zh-HK';
      recognition.continuous=false;
      recognition.interimResults=false;

      recognition.onstart=()=>{{
        listening=true;
        mic.style.background='#D32F2F';
        mic.textContent='⏹️ 停止聆聽 (Stop)';
        status.textContent='🔴 正在聆聽中，請講話...';
      }};

      recognition.onresult=(event)=>{{
        const text=event.results[0][0].transcript.trim();
        if(!text){{ ready('⚠️ 沒有聽到內容 — 請再試一次'); return; }}
        listening=false;
        navigating=true;
        answer.value=text;
        display.textContent=text;
        status.textContent='✅ 聽到: '+text;
        mic.style.background='#388E3C';
        go('speech_result',text);
      }};

      recognition.onerror=(event)=>{{
        navigating=false;
        ready('⚠️ 未能識別 ('+event.error+') — 請再試一次');
      }};

      recognition.onend=()=>{{
        if(!navigating) ready();
      }};
    }} else {{
      mic.disabled=true;
      status.textContent='❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)';
    }}

    mic.onclick=()=>{{
      if(!recognition) return;
      if(listening){{ recognition.stop(); return; }}
      navigating=false;
      ready();
      try{{ recognition.start(); }}catch(e){{ ready('⚠️ 麥克風未能啟動 — 請再試一次'); }}
    }};

    document.getElementById('submit').onclick=()=>{{ go('answer_submission',answer.value); }};
    document.getElementById('skip').onclick=()=>{{ go('skip_item','1'); }};
    </script></body></html>
    """,
        height=470,
    )

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
