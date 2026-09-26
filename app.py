# Set up environment
import html
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="超級市場大搜查 (Supermarket Shopping Adventure)",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom Themed CSS Styling
st.markdown(
    """
<style>
:root {
    --market-green: #2E7D32;
    --market-accent: #FF9800;
    --card-bg: #F4FBF7;
    --text-main: #1C3125;
}

@media (prefers-color-scheme: dark) {
    :root {
        --card-bg: #1B2921;
        --text-main: #E8F5E9;
    }
}

/* Supermarket Banner & Card Styles */
.market-banner {
    background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
    color: #FFFFFF !important;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}

.market-card {
    background: var(--card-bg);
    border: 2px solid var(--market-green);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}

.market-card p {
    font-size: 22px !important;
    color: var(--text-main) !important;
    margin: 0 !important;
    line-height: 1.5 !important;
}

.item-badge {
    display: inline-block;
    background: #FF9800;
    color: #FFFFFF;
    font-weight: bold;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 18px;
    margin-bottom: 10px;
}

/* Input & Button Refinement */
.stTextInput > div > div > input {
    font-size: 22px !important;
    height: 58px !important;
    border-radius: 12px !important;
}

.stButton>button {
    width: 100% !important;
    height: 60px !important;
    font-size: 22px !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    background-color: #2E7D32 !important;
    color: #FFFFFF !important;
    border: none !important;
    margin-top: 10px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.12) !important;
}

.stButton>button:hover {
    background-color: #1B5E20 !important;
}

.big-emoji {
    font-size: 130px !important;
    text-align: center;
    margin: 10px 0;
    user-select: none;
}
</style>
""",
    unsafe_allow_html=True,
)

# Initialize global session state
for key, value in {
    "stage": "intro",
    "current_item_index": 0,
    "telemetry_logs": [],
    "item_start_time": None,
    "moca_naming_score": 0,
    "moca_memory_score": 0,
    "reg_trial_1_items": [],
    "reg_trial_2_items": [],
    "recalled_free_items": [],
    "missed_items": [],
    "cued_current_index": 0,
    "cued_sub_step": "category",
    "recalled_cued_items": {},
    "recalled_choice_items": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# GAME DATA 1: MEMORY ITEMS (SHOPPING LIST)
MEMORY_ITEMS = [
    {"id": "mem_1", "name": "雪櫃", "category": "一種電器", "options": ["雪櫃", "風扇", "電視"]},
    {"id": "mem_2", "name": "郵局", "category": "一種建築物", "options": ["消防局", "郵局", "醫院"]},
    {"id": "mem_3", "name": "榕樹", "category": "一種植物", "options": ["橡樹", "榕樹", "松樹"]},
    {"id": "mem_4", "name": "塑膠", "category": "一種物料", "options": ["紙張", "金屬", "塑膠"]},
    {"id": "mem_5", "name": "藍色", "category": "一種顏色", "options": ["藍色", "紅色", "綠色"]},
]

# GAME DATA 2: NAMING ITEMS (MARKET COUNTER & MASCOT)
NAMING_ITEMS = [
    {
        "id": "item_1",
        "tier": "Warmup",
        "emoji": "🦋",
        "primary_name": "蝴蝶",
        "acceptable_synonyms": ["蝴蝶", "呢個係蝴蝶", "這是蝴蝶", "呢隻係蝴蝶"],
        "moca_weight": 1,
        "story": "花園角發現了一隻漂亮的昆蟲！",
    },
    {
        "id": "item_2",
        "tier": "Moderate",
        "emoji": "🐙",
        "primary_name": "八爪魚",
        "acceptable_synonyms": ["八爪魚", "呢個係八爪魚", "這是八爪魚", "呢隻係八爪魚"],
        "moca_weight": 1,
        "story": "來到海鮮檔，檔主展示了新鮮進貨的海鮮：",
    },
    {
        "id": "item_3",
        "tier": "Low",
        "emoji": "🦥",
        "primary_name": "樹懶",
        "acceptable_synonyms": ["樹懶", "呢個係樹懶", "這是樹懶", "呢隻係樹懶"],
        "moca_weight": 1,
        "story": "超市入口放置了一個特別的動物吉祥物：",
    },
]


def render_instruction_speaker_component(instruction_text, key_suffix):
    """Voice speaker component for store instructions."""
    escaped_text = html.escape(instruction_text).replace("'", "\\'")
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; display:flex; justify-content:center; }}
    button {{ width:100%; max-width:340px; height:44px; font-size:16px; font-weight:bold; color:#FFFFFF !important; background:#FF9800; border:none; border-radius:8px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.15); }}
    button:hover {{ background:#E65100; }}
    </style></head><body>
    <button id="inst_btn_{key_suffix}" type="button">🔊 聽店長語音指引 (Listen)</button>

    <script>
    const text = "{escaped_text}";
    const btn = document.getElementById('inst_btn_{key_suffix}');

    function speakInstruction() {{
      if (!('speechSynthesis' in window)) return;
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-HK';
      utterance.rate = 0.9;

      const voices = window.speechSynthesis.getVoices();
      const hkVoice = voices.find(v => v.lang === 'zh-HK' || v.lang === 'yue-Hant-HK' || v.lang.includes('HK'));
      if (hkVoice) utterance.voice = hkVoice;

      window.speechSynthesis.speak(utterance);
    }}

    btn.onclick = speakInstruction;
    </script></body></html>
    """,
        height=50,
    )


def render_audio_speaker_component(words_list, key_suffix):
    """Audio broad-caster for shopping list items."""
    words_js_array = str(words_list)
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; text-align:center; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#0D47A1; border:none; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#002171; }}
    .status {{ font-size:15px; margin-top:6px; font-weight:bold; color:#0D47A1; }}
    </style></head><body>
    <button id="speak_btn_{key_suffix}" type="button">📢 聽購物清單 (Listen Shopping List)</button>
    <div class="status" id="status_{key_suffix}">點擊收聽清單</div>

    <script>
    const words = {words_js_array};
    const btn = document.getElementById('speak_btn_{key_suffix}');
    const status = document.getElementById('status_{key_suffix}');
    let isPlaying = false;

    if ('speechSynthesis' in window) {{
      window.speechSynthesis.onvoiceschanged = () => {{ window.speechSynthesis.getVoices(); }};
    }}

    function speakWords() {{
      if (!('speechSynthesis' in window)) {{
        status.textContent = '❌ 不支援語音';
        return;
      }}
      if (isPlaying) return;
      
      window.speechSynthesis.cancel();
      isPlaying = true;
      btn.disabled = true;
      btn.style.background = '#757575';
      status.textContent = '🔊 廣播中...';
      
      let index = 0;

      function speakNext() {{
        if (index >= words.length) {{
          status.textContent = '✅ 清單廣播完畢';
          isPlaying = false;
          btn.disabled = false;
          btn.style.background = '#0D47A1';
          btn.textContent = '🔄 重播購物清單 (Replay)';
          return;
        }}

        const utterance = new SpeechSynthesisUtterance(words[index]);
        utterance.lang = 'zh-HK';
        utterance.rate = 0.85;

        const voices = window.speechSynthesis.getVoices();
        const hkVoice = voices.find(v => v.lang === 'zh-HK' || v.lang === 'yue-Hant-HK' || v.lang.includes('HK'));
        if (hkVoice) utterance.voice = hkVoice;

        utterance.onend = () => {{
          index++;
          if (index < words.length) setTimeout(speakNext, 1000);
          else {{
            status.textContent = '✅ 清單廣播完畢';
            isPlaying = false;
            btn.disabled = false;
            btn.style.background = '#0D47A1';
            btn.textContent = '🔄 重播購物清單 (Replay)';
          }}
        }};

        utterance.onerror = () => {{ index++; setTimeout(speakNext, 1000); }};
        window.speechSynthesis.speak(utterance);
      }}

      speakNext();
    }}

    btn.onclick = speakWords;
    </script></body></html>
    """,
        height=95,
    )


def render_mic_component(key_suffix, continuous_mode=False):
    """Mic component embedded in shopping basket context."""
    is_continuous_js = "true" if continuous_mode else "false"
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#2E7D32; border:none; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#1B5E20; }}
    .status {{ font-size:15px; text-align:center; margin-top:6px; color:#2E7D32; font-weight:bold; }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 按此回答 (Speak)</button>
    <div class="status" id="status_{key_suffix}">點擊麥克風說出答案</div>

    <script>
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic_{key_suffix}'), status = document.getElementById('status_{key_suffix}');
    const isContinuous = {is_continuous_js};
    let recognition = null, listening = false;
    let baseText = "";
    let isProgrammaticChange = false;

    function resetToStandby() {{
      listening = false;
      mic.style.background = '#2E7D32';
      mic.textContent = '🎤 按此回答 (Speak)';
      status.textContent = '🟢 點擊麥克風說出答案';
    }}

    function getCurrentInputText() {{
      const doc = window.parent.document;
      const inputs = doc.querySelectorAll('input[type="text"], textarea');
      return inputs.length > 0 ? inputs[0].value.trim() : "";
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
        
        isProgrammaticChange = true;
        if (nativeInputValueSetter && nativeInputValueSetter.set) {{
          nativeInputValueSetter.set.call(target, text);
        }} else {{
          target.value = text;
        }}
        target.dispatchEvent(new Event('input', {{ bubbles: true }}));
        target.dispatchEvent(new Event('change', {{ bubbles: true }}));
        setTimeout(() => {{ isProgrammaticChange = false; }}, 50);
      }}
    }}

    if(SR) {{
      recognition = new SR();
      recognition.lang = 'zh-HK';
      recognition.continuous = isContinuous;
      recognition.interimResults = isContinuous;

      recognition.onstart = () => {{
        listening = true;
        mic.style.background = '#D32F2F';
        mic.textContent = '⏹️ 停止錄音';
        status.textContent = '🔴 正在聆聽您的回答...';
      }};

      recognition.onresult = (event) => {{
        if (isContinuous) {{
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; ++i) {{
            if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
            else interimTranscript += event.results[i][0].transcript;
          }}

          if (finalTranscript) baseText += (baseText ? ' ' : '') + finalTranscript.trim();
          const displayText = baseText + (interimTranscript ? (baseText ? ' ' : '') + interimTranscript : '');
          status.textContent = '🎧 記錄中...';
          injectValueIntoStreamlitWidget(displayText);
        }} else {{
          const text = event.results[0][0].transcript.trim();
          const combined = baseText ? (baseText + ' ' + text) : text;
          status.textContent = '🎧 聽到: ' + text;
          injectValueIntoStreamlitWidget(combined);
        }}
      }};

      recognition.onerror = (event) => {{
        if (event.error !== 'no-speech') status.textContent = '⚠️ 語音問題 (' + event.error + ')';
      }};

      recognition.onend = () => {{
        if (listening && isContinuous) {{
          try {{ recognition.start(); }} catch(e) {{ resetToStandby(); }}
        }} else resetToStandby();
      }};
    }} else {{
      mic.disabled = true;
      status.textContent = '❌ 不支援語音';
    }}

    mic.onclick = () => {{
      if(!recognition) return;
      if(listening) {{ 
        listening = false; 
        recognition.stop(); 
        resetToStandby(); 
        return; 
      }}
      baseText = getCurrentInputText();
      try {{ recognition.start(); }} catch(e) {{}}
    }};
    </script></body></html>
    """,
        height=95,
    )


def evaluate_naming_answer(answer):
    item = NAMING_ITEMS[st.session_state.current_item_index]
    elapsed = round(time.time() - st.session_state.item_start_time, 2) if st.session_state.item_start_time else 0.0
    clean = answer.strip().replace(" ", "").replace("呢個係", "").replace("這是", "").replace("呢隻係", "")
    correct = any(s in answer or s in clean for s in item["acceptable_synonyms"])

    if correct:
        st.session_state.moca_naming_score += item["moca_weight"]

    st.session_state.telemetry_logs.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task": "naming",
            "item_id": item["id"],
            "target_name": item["primary_name"],
            "user_spoken_raw": answer,
            "is_correct": correct,
            "latency_seconds": elapsed,
        }
    )
    return correct


def advance_naming_item():
    if st.session_state.current_item_index + 1 < len(NAMING_ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
    else:
        st.session_state.stage = "delayed_recall_free"
        st.session_state.item_start_time = time.time()


# --- STAGE 1: GAME WELCOME ---
if st.session_state.stage == "intro":
    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:36px; color:#FFFFFF !important;">🛒 超級市場大搜查</h1>
        <p style="margin:5px 0 0 0; font-size:20px; opacity:0.9;">歡迎來到開心超市！今天讓我們一起完成購物任務吧！</p>
    </div>
    <div class="market-card" style="text-align: center;">
        <div style="font-size: 80px; margin-bottom: 10px;">🏪</div>
        <p><b>店長語錄：</b>「早晨！今日超市有好多新鮮貨品，準備好帶你嘅購物籃出發未？」</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("推購物車出發 (Start Shopping)"):
        st.session_state.stage = "memory_reg_1"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.rerun()

# --- STAGE 2: SHOPPING LIST TRIAL 1 ---
elif st.session_state.stage == "memory_reg_1":
    inst_1 = "請聽清楚店長為你準備的 5 樣購物清單物品，聽完後講出你記得的物品。"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">📝 第一站：準備購物清單 (1/2)</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="market-card">
        <span class="item-badge">任務 1</span>
        <p>{inst_1}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(inst_1, "reg_1_inst")

    word_names = [item["name"] for item in MEMORY_ITEMS]

    col_audio, col_mic = st.columns(2)
    with col_audio:
        render_audio_speaker_component(word_names, "reg_1")
    with col_mic:
        render_mic_component("reg_1", continuous_mode=True)

    with st.form(key="form_reg_1"):
        user_answer = st.text_input("放入購物籃的物品：", key="input_reg_1")
        if st.form_submit_button("👉 記好了，下一步"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_1_items = spoken
            st.session_state.stage = "memory_reg_2"
            st.rerun()

# --- STAGE 3: SHOPPING LIST TRIAL 2 ---
elif st.session_state.stage == "memory_reg_2":
    inst_2 = "店長會再廣播一次購物清單，請再次講出記得的物品（包括剛才講過的）。"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">📝 第一站：確認購物清單 (2/2)</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="market-card">
        <span class="item-badge">任務 2</span>
        <p>{inst_2}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(inst_2, "reg_2_inst")

    word_names = [item["name"] for item in MEMORY_ITEMS]

    col_audio, col_mic = st.columns(2)
    with col_audio:
        render_audio_speaker_component(word_names, "reg_2")
    with col_mic:
        render_mic_component("reg_2", continuous_mode=True)

    with st.form(key="form_reg_2"):
        user_answer = st.text_input("放入購物籃的物品：", key="input_reg_2")
        if st.form_submit_button("👉 記好了，進入超市"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_2_items = spoken
            st.session_state.stage = "memory_reg_notice"
            st.rerun()

# --- STAGE 4: SHOPPING MEMO NOTICE PAGE ---
elif st.session_state.stage == "memory_reg_notice":
    inst_notice = "請緊記這 5 樣購物清單物品！當我們逛完超市結帳時，需要再核對這份清單。"

    st.markdown(
        """
    <div class="market-banner" style="background: linear-gradient(135deg, #FF9800 0%, #E65100 100%);">
        <h1 style="margin:0; font-size:32px; color:#FFFFFF !important;">📌 店長特別提醒</h1>
    </div>
    <div class="market-card" style="text-align: center; border-color: #FF9800;">
        <div style="font-size: 70px; margin-bottom: 10px;">📋</div>
        <p style="font-size: 26px !important; color: #E65100 !important;"><b>請緊記剛才這 5 樣物品！</b></p>
        <p style="margin-top: 10px !important;">稍後去到<b>【自動結帳機】</b>時，需要你講出清單上的所有物品。</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(inst_notice, "notice_inst")

    if st.button("👉 明白，開始逛超市！"):
        st.session_state.stage = "naming"
        st.session_state.current_item_index = 0
        st.session_state.item_start_time = time.time()
        st.rerun()

# --- STAGE 5: NAMING GAME (EXPLORING MARKET STALLS) ---
elif st.session_state.stage == "naming":
    index = st.session_state.current_item_index
    item = NAMING_ITEMS[index]
    inst_naming = f"請大聲講出：{item['story']}這是什麼？"

    st.markdown(
        f"""
    <div class="market-banner">
        <h1 style="margin:0; font-size:28px; color:#FFFFFF !important;">🔍 第二站：超市貨架探索 ({index+1}/{len(NAMING_ITEMS)})</h1>
    </div>
    <div class="market-card">
        <p style="text-align: center;"><b>{item['story']}</b></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(inst_naming, f"naming_{index}_inst")

    st.markdown(f"<div class='big-emoji'>{item['emoji']}</div>", unsafe_allow_html=True)

    render_mic_component(f"naming_{index}", continuous_mode=False)

    with st.form(key=f"naming_form_{index}"):
        user_answer = st.text_input("這物品是：", key=f"user_input_{index}")
        submit_btn = st.form_submit_button("👉 放入購物車 / 下一格貨架")

        if submit_btn:
            recorded_answer = user_answer.strip() if user_answer.strip() else "跳過"
            evaluate_naming_answer(recorded_answer)
            advance_naming_item()
            st.rerun()

# --- STAGE 6: CHECKOUT COUNTER (FREE RECALL) ---
elif st.session_state.stage == "delayed_recall_free":
    inst_free = "歡迎來到自動結帳機！請講出你剛才準備的 5 樣購物清單物品："

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">💳 第三站：超市自動結帳</h1>
    </div>
    <div class="market-card">
        <span class="item-badge">結帳核對</span>
        <p>最開始店長請你記住的 <b>5 樣購物清單物品</b>，現在請你講出來核對：</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(inst_free, "free_recall_inst")

    render_mic_component("delayed_free", continuous_mode=True)

    with st.form(key="form_delayed_free"):
        user_answer = st.text_input("講出清單物品：", key="input_delayed_free")
        if st.form_submit_button("👉 掃瞄完成 (Scan Items)"):
            elapsed = round(time.time() - st.session_state.item_start_time, 2)
            recalled = []
            score = 0

            for item in MEMORY_ITEMS:
                if item["name"] in user_answer:
                    recalled.append(item["name"])
                    score += 1

            st.session_state.recalled_free_items = recalled
            st.session_state.moca_memory_score = score

            st.session_state.telemetry_logs.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "task": "delayed_recall_free",
                    "score_awarded": score,
                    "recalled_items": recalled,
                    "latency_seconds": elapsed,
                }
            )

            missed = [item for item in MEMORY_ITEMS if item["name"] not in recalled]
            st.session_state.missed_items = missed
            st.session_state.cued_current_index = 0
            st.session_state.cued_sub_step = "category"

            if missed:
                st.session_state.stage = "delayed_recall_cued_step"
            else:
                st.session_state.stage = "complete"
            st.rerun()

# --- STAGE 7: AISLE ASSISTANT (CUED RECALL) ---
elif st.session_state.stage == "delayed_recall_cued_step":
    missed_list = st.session_state.missed_items
    curr_idx = st.session_state.cued_current_index

    if curr_idx >= len(missed_list):
        st.session_state.stage = "complete"
        st.rerun()

    item = missed_list[curr_idx]

    st.markdown(
        """
    <div class="market-banner" style="background: linear-gradient(135deg, #0288D1 0%, #01579B 100%);">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">🔎 超市店員尋物協助</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.session_state.cued_sub_step == "category":
        inst_cue = f"店員提示：物品類別是【{item['category']}】，請問這是什麼物品？"

        st.markdown(
            f"""
        <div class="market-card">
            <span class="item-badge" style="background:#0288D1;">分區提示</span>
            <p>店員指著貨架說：<b>「呢樣物品屬於【{item['category']}】」</b></p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        render_instruction_speaker_component(inst_cue, f"cue_inst_{item['id']}")
        render_mic_component(f"cue_cat_{item['id']}", continuous_mode=True)

        with st.form(key=f"form_cat_{item['id']}"):
            user_spoken = st.text_input("請講出這個物品：", key=f"in_cat_{item['id']}")
            if st.form_submit_button("👉 確認物品"):
                st.session_state.recalled_cued_items[item["name"]] = user_spoken.strip()
                if item["name"] in user_spoken:
                    st.session_state.cued_current_index += 1
                    st.session_state.cued_sub_step = "category"
                else:
                    st.session_state.cued_sub_step = "choice"
                st.rerun()

    elif st.session_state.cued_sub_step == "choice":
        inst_choice = "店員拿出了三個物品，請選擇原本清單上的那一個。"

        st.markdown(
            """
        <div class="market-card">
            <span class="item-badge" style="background:#0288D1;">貨架三選一</span>
            <p>店員從貨架拿出了 3 個物品，請選出原本購物清單上的物品：</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        render_instruction_speaker_component(inst_choice, f"choice_inst_{item['id']}")

        with st.form(key=f"form_choice_{item['id']}"):
            selected_option = st.radio(
                "請點選正確物品：",
                options=item["options"],
                key=f"radio_choice_{item['id']}",
            )
            if st.form_submit_button("👉 放入購物車並繼續"):
                st.session_state.recalled_choice_items[item["name"]] = selected_option
                st.session_state.cued_current_index += 1
                st.session_state.cued_sub_step = "category"
                st.rerun()

# --- STAGE 8: GAME COMPLETE & BACKGROUND CLINICAL DASHBOARD ---
elif st.session_state.stage == "complete":
    st.balloons()

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:36px; color:#FFFFFF !important;">🎉 成功完成購物！</h1>
        <p style="margin:5px 0 0 0; font-size:20px;">多謝惠顧！你已順利買齊所有物品並完成結帳！</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 再玩一次超市遊戲 (Play Again)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.session_state.reg_trial_1_items = []
        st.session_state.reg_trial_2_items = []
        st.session_state.recalled_free_items = []
        st.session_state.missed_items = []
        st.session_state.cued_current_index = 0
        st.session_state.cued_sub_step = "category"
        st.session_state.recalled_cued_items = {}
        st.session_state.recalled_choice_items = {}
        st.rerun()

    # Concealed / Professional Backend Telemetry Area for Clinicians
    with st.expander("🩺 Occupational Therapist / Speech Telemetry Dashboard", expanded=False):
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
        st.write(
            f"**Registration Trial 1 Spoken:** {', '.join(st.session_state.reg_trial_1_items) if st.session_state.reg_trial_1_items else 'None'}"
        )
        st.write(
            f"**Registration Trial 2 Spoken:** {', '.join(st.session_state.reg_trial_2_items) if st.session_state.reg_trial_2_items else 'None'}"
        )
        st.write(
            f"**Free Recall (Scored):** {', '.join(st.session_state.recalled_free_items) if st.session_state.recalled_free_items else 'None'}"
        )

        if st.session_state.recalled_cued_items or st.session_state.recalled_choice_items:
            st.write("**Cued / Multiple-Choice Analysis (Encoding vs Retrieval Deficit Analysis):**")
            st.json(
                {
                    "Category_Cues": st.session_state.recalled_cued_items,
                    "Multiple_Choices": st.session_state.recalled_choice_items,
                }
            )

        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        if not df.empty:
            st.download_button(
                "📥 Download Clinical Telemetry Log (.CSV)",
                df.to_csv(index=False).encode("utf-8"),
                f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
                "text/csv",
            )
