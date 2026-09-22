import html
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="探索香港街市 (Explore HK Market)",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom UI Styling
st.markdown(
    """
<style>
.main { background-color:#FFFDF9; }
.stButton>button { width:100%; height:65px; font-size:20px !important; font-weight:bold; border-radius:16px; background:#2E7D32; color:white; border:0; margin-bottom:12px; }
.stButton>button:hover { background:#1B5E20; }
.instruction-card { background:#F0F7F4; padding:20px; border-radius:16px; border-left:8px solid #2E7D32; margin-bottom:20px; }
.word-card { background:#FFF3E0; border-radius:12px; padding:16px; margin:6px; text-align:center; font-size:26px; font-weight:bold; color:#E65100; display:inline-block; width:18%; }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize global session state
for key, value in {
    "stage": "intro",  # Options: intro, naming, memory_reg_1, memory_reg_2, delayed_recall_free, delayed_recall_cued, complete
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "moca_memory_score": 0,
    "reg_trial_1_items": [],
    "reg_trial_2_items": [],
    "recalled_free_items": [],
    "recalled_cued_items": {},
    "recalled_choice_items": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# GAME 1: NAMING ITEMS
NAMING_ITEMS = [
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

# GAME 2: MEMORY ITEMS (HK MARKET EQUIVALENTS)
MEMORY_ITEMS = [
    {"id": "mem_1", "name": "菜心", "category": "一種蔬菜", "options": ["菜心", "芥蘭", "白菜"]},
    {"id": "mem_2", "name": "石斑", "category": "一種海鮮/魚類", "options": ["石斑", "鯇魚", "三文魚"]},
    {"id": "mem_3", "name": "豆腐", "category": "一種豆製品", "options": ["豆腐", "腐竹", "豆漿"]},
    {"id": "mem_4", "name": "蘋果", "category": "一種水果", "options": ["蘋果", "香蕉", "草莓"]},
    {"id": "mem_5", "name": "雞蛋", "category": "一種蛋類", "options": ["雞蛋", "鴨蛋", "豬肉"]},
]


def render_mic_component(key_suffix):
    """Reusable Web Speech API Mic component with standby reset logic."""
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; }}
    button {{ width:100%; height:55px; font-size:18px; font-weight:bold; color:white; background:#2E7D32; border:0; border-radius:12px; cursor:pointer; width:100%; transition: background 0.3s; }}
    .status {{ font-size:16px; text-align:center; margin:6px 0; min-height:22px; }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 按此說話 (Tap & Say)</button>
    <div class="status" id="status_{key_suffix}">點擊上方按鈕並講出名稱</div>

    <script>
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic_{key_suffix}'), status = document.getElementById('status_{key_suffix}');
    let recognition = null, listening = false;

    function resetToStandby() {{
      listening = false;
      mic.style.background = '#2E7D32';
      mic.textContent = '🎤 按此說話 (Tap & Say)';
      status.textContent = '🟢 點擊上方按鈕並講出名稱';
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
        if (nativeInputValueSetter && nativeInputValueSetter.set) {{
          nativeInputValueSetter.set.call(target, text);
        }} else {{
          target.value = text;
        }}
        target.dispatchEvent(new Event('input', {{ bubbles: true }}));
        target.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }}
    }}

    if(SR) {{
      recognition = new SR();
      recognition.lang = 'zh-HK';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {{
        listening = true;
        mic.style.background = '#D32F2F';
        mic.textContent = '⏹️ 正在聆聽中...';
        status.textContent = '🔴 正在聆聽中，請講話...';
      }};

      recognition.onresult = (event) => {{
        const text = event.results[0][0].transcript.trim();
        status.textContent = '✅ 聽到: ' + text;
        injectValueIntoStreamlitWidget(text);
      }};

      recognition.onerror = (event) => {{
        resetToStandby();
        status.textContent = '⚠️ 未能識別，請再試一次';
      }};

      recognition.onend = () => {{
        if (listening) {{ resetToStandby(); }}
      }};
    }} else {{
      mic.disabled = true;
      status.textContent = '❌ 瀏覽器不支援語音功能';
    }}

    mic.onclick = () => {{
      if(!recognition) return;
      if(listening) {{ recognition.stop(); resetToStandby(); return; }}
      try {{ recognition.start(); }} catch(e) {{}}
    }};
    </script></body></html>
    """,
        height=100,
    )


# Function to evaluate naming answers
def evaluate_naming_answer(answer):
    item = NAMING_ITEMS[st.session_state.current_item_index]
    elapsed = round(time.time() - st.session_state.item_start_time, 2) if st.session_state.item_start_time else 0.0
    clean = answer.strip().replace(" ", "").replace("呢個係", "").replace("這是", "").replace("呢隻係", "")
    correct = any(s in answer or s in clean for s in item["acceptable_synonyms"])
    
    if correct:
        st.session_state.moca_naming_score += item["moca_weight"]
        
    st.session_state.telemetry_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": "naming",
        "item_id": item["id"],
        "target_name": item["primary_name"],
        "user_spoken_raw": answer,
        "is_correct": correct,
        "latency_seconds": elapsed,
    })
    return correct


def advance_naming_item():
    if st.session_state.current_item_index + 1 < len(NAMING_ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
    else:
        # Move seamlessly into Game 2 (Memory Registration)
        st.session_state.stage = "memory_reg_1"
        st.session_state.item_start_time = time.time()


# --- STAGE 1: INTRO ---
if st.session_state.stage == "intro":
    st.title("🛒 探索香港街市 (Explore HK Market)")
    st.markdown(
        """
    <div class="instruction-card">
        <h2>今天我們要去街市買菜！</h2>
        <p style="font-size:20px;">本遊戲共有兩個部分：</p>
        <p style="font-size:18px;">1. <b>動物辨識</b>（大聲講出名稱）</p>
        <p style="font-size:18px;">2. <b>買菜記憶力測試</b>（記住買菜清單）</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("開始 (Start)"):
        st.session_state.stage = "naming"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.session_state.item_start_time = time.time()
        st.rerun()

# --- STAGE 2: GAME 1 - NAMING ---
elif st.session_state.stage == "naming":
    index = st.session_state.current_item_index
    item = NAMING_ITEMS[index]

    st.markdown(f"<p style='font-size:20px;text-align:center;color:#666;'>動物命名: {index+1} / {len(NAMING_ITEMS)}</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>請大聲講出，這是什麼動物？</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:120px;text-align:center;margin:10px 0;'>{item['emoji']}</div>", unsafe_allow_html=True)

    render_mic_component(f"naming_{index}")

    with st.form(key=f"naming_form_{index}"):
        user_answer = st.text_input("答案（語音識別結果會自動填入）：", key=f"user_input_{index}")
        col1, col2 = st.columns(2)
        with col1:
            submit_btn = st.form_submit_button("👉 提交答案 / 下一題")
        with col2:
            skip_btn = st.form_submit_button("⏭️ 跳過")

        if submit_btn:
            evaluate_naming_answer(user_answer if user_answer.strip() else "未有說話")
            advance_naming_item()
            st.rerun()

        if skip_btn:
            evaluate_naming_answer("跳過")
            advance_naming_item()
            st.rerun()

# --- STAGE 3: GAME 2 (PART 1) - MEMORY REGISTRATION TRIAL 1 ---
elif st.session_state.stage == "memory_reg_1":
    st.title("🧠 買菜記性測試 (第一次學習)")
    st.markdown(
        """
    <div class="instruction-card">
        <p style="font-size:22px;">這是一個記憶力測試。請聽清楚及記住以下<b>5個詞語</b>：</p>
        <p style="font-size:18px;color:#D32F2F;">⚠️ 提示：讀完後請盡量講出你記得的詞語（次序並不重要）。<b>此階段不計分</b>。</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    words_html = "".join([f"<div class='word-card'>{item['name']}</div>" for item in MEMORY_ITEMS])
    st.markdown(f"<div style='text-align:center;'>{words_html}</div>", unsafe_allow_html=True)

    render_mic_component("reg_1")

    with st.form(key="form_reg_1"):
        user_answer = st.text_input("請講出剛才的詞語（可以用點擊語音輸入）：", key="input_reg_1")
        if st.form_submit_button("👉 完成第一次嘗試 (Next Trial)"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").split(",") if w.strip()]
            st.session_state.reg_trial_1_items = spoken
            st.session_state.stage = "memory_reg_2"
            st.rerun()

# --- STAGE 4: GAME 2 (PART 1) - MEMORY REGISTRATION TRIAL 2 ---
elif st.session_state.stage == "memory_reg_2":
    st.title("🧠 買菜記性測試 (第二次學習)")
    st.markdown(
        """
    <div class="instruction-card">
        <p style="font-size:22px;">我會重複讀第二次這5個詞語。請嘗試把它們記住並說給我聽，越多越好。</p>
        <p style="font-size:20px;color:#2E7D32;">💡 提示：<b>在整個測試完結時，我會再問你這些詞語！</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    words_html = "".join([f"<div class='word-card'>{item['name']}</div>" for item in MEMORY_ITEMS])
    st.markdown(f"<div style='text-align:center;'>{words_html}</div>", unsafe_allow_html=True)

    render_mic_component("reg_2")

    with st.form(key="form_reg_2"):
        user_answer = st.text_input("請再次講出記得的詞語：", key="input_reg_2")
        if st.form_submit_button("👉 進入延遲回憶測試 (Go to Delayed Recall)"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").split(",") if w.strip()]
            st.session_state.reg_trial_2_items = spoken
            st.session_state.stage = "delayed_recall_free"
            st.session_state.item_start_time = time.time()
            st.rerun()

# --- STAGE 5: GAME 2 (PART 2) - DELAYED RECALL (FREE RECALL) ---
elif st.session_state.stage == "delayed_recall_free":
    st.title("⏳ 延遲記憶測試 (自由回憶)")
    st.markdown(
        """
    <div class="instruction-card">
        <h2>我之前讀了一些買菜詞語給你聽，叫你記住它們。</h2>
        <p style="font-size:22px;"><b>現在請你講出你記得的那些詞語。</b>（每個正確給1分）</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_mic_component("delayed_free")

    with st.form(key="form_delayed_free"):
        user_answer = st.text_input("講出記得的詞語：", key="input_delayed_free")
        if st.form_submit_button("👉 提交自由回憶答案"):
            elapsed = round(time.time() - st.session_state.item_start_time, 2)
            recalled = []
            score = 0

            for item in MEMORY_ITEMS:
                if item["name"] in user_answer:
                    recalled.append(item["name"])
                    score += 1

            st.session_state.recalled_free_items = recalled
            st.session_state.moca_memory_score = score

            st.session_state.telemetry_logs.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "task": "delayed_recall_free",
                "score_awarded": score,
                "recalled_items": recalled,
                "latency_seconds": elapsed,
            })

            missed = [item for item in MEMORY_ITEMS if item["name"] not in recalled]
            if missed:
                st.session_state.stage = "delayed_recall_cued"
            else:
                st.session_state.stage = "complete"
            st.rerun()

# --- STAGE 6: GAME 2 (PART 2) - DELAYED RECALL (CUED & MULTIPLE CHOICE) ---
elif st.session_state.stage == "delayed_recall_cued":
    st.title("💡 延遲記憶測試 (提示回憶 - 臨床參考)")
    st.markdown(
        """
    <div class="instruction-card">
        <p style="font-size:20px;">針對剛才未回想出的詞語，請嘗試根據類目提示或選擇題作答。</p>
        <p style="font-size:18px;color:#D32F2F;">⚠️ 註：提示下答對<b>不獲分數</b>，僅供臨床編碼/檢索障礙分析。</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    missed_items = [item for item in MEMORY_ITEMS if item["name"] not in st.session_state.recalled_free_items]

    with st.form(key="form_cued"):
        cued_results = {}
        choice_results = {}

        for item in missed_items:
            st.subheader(f"項目: {item['category']}")
            c1, c2 = st.columns(2)
            with c1:
                cued_results[item["name"]] = st.text_input(f"類目提示: 「其中一個是{item['category']}」", key=f"cue_{item['id']}")
            with c2:
                choice_results[item["name"]] = st.radio(f"選擇題: 請選擇正確詞語", options=["未選擇"] + item["options"], key=f"choice_{item['id']}")
            st.divider()

        if st.form_submit_button("👉 完成所有測試 (Finish Assessment)"):
            st.session_state.recalled_cued_items = cued_results
            st.session_state.recalled_choice_items = choice_results
            st.session_state.stage = "complete"
            st.rerun()

# --- STAGE 7: COMPLETE & CLINICAL TELEMETRY DASHBOARD ---
elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 完成所有任務！感謝您的參與！")

    if st.button("再玩一次 (Play Again)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.session_state.reg_trial_1_items = []
        st.session_state.reg_trial_2_items = []
        st.session_state.recalled_free_items = []
        st.session_state.recalled_cued_items = {}
        st.session_state.recalled_choice_items = {}
        st.rerun()

    with st.expander("🩺 Occupational Therapist / Speech Telemetry Dashboard", expanded=True):
        st.subheader("MoCA Sub-score Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("1. Naming Sub-score", f"{st.session_state.moca_naming_score} / 3 Points")
        with col2:
            st.metric("2. Delayed Recall (Free)", f"{st.session_state.moca_memory_score} / 5 Points")
        with col3:
            total = st.session_state.moca_naming_score + st.session_state.moca_memory_score
            st.metric("Combined MoCA Sub-total", f"{total} / 8 Points")

        st.subheader("Memory Breakdown")
        st.write(f"**Registration Trial 1 Spoken:** {', '.join(st.session_state.reg_trial_1_items) if st.session_state.reg_trial_1_items else 'None'}")
        st.write(f"**Registration Trial 2 Spoken:** {', '.join(st.session_state.reg_trial_2_items) if st.session_state.reg_trial_2_items else 'None'}")
        st.write(f"**Free Recall (Scored):** {', '.join(st.session_state.recalled_free_items) if st.session_state.recalled_free_items else 'None'}")

        if st.session_state.recalled_cued_items:
            st.write("**Cued / Multiple-Choice Analysis (Encoding vs Retrieval Deficit Analysis):**")
            st.json({"Category_Cues": st.session_state.recalled_cued_items, "Multiple_Choices": st.session_state.recalled_choice_items})

        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        if not df.empty:
            st.download_button(
                "📥 Download Clinical Telemetry Log (.CSV)",
                df.to_csv(index=False).encode("utf-8"),
                f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
                "text/csv",
            )
