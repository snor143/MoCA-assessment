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

# Custom UI Styling (Clean Vertical Layout + High-Contrast Typography)
st.markdown(
    """
<style>
/* Base Typography and Theme Variable Overrides */
:root {
    --card-bg: #F0F7F4;
    --card-border: #2E7D32;
    --notice-bg: #FFF8E1;
    --notice-border: #FFA000;
    --text-primary: #1A1A1A;
    --input-bg: #FFFFFF;
    --input-text: #000000;
}

@media (prefers-color-scheme: dark) {
    :root {
        --card-bg: #1E2D24;
        --card-border: #4CAF50;
        --notice-bg: #3E2723;
        --notice-border: #FFB74D;
        --text-primary: #FFFFFF;
        --input-bg: #2C2C2C;
        --input-text: #FFFFFF;
    }
}

/* Clear Page Flow Headers */
h1 {
    font-size: 32px !important;
    font-weight: bold !important;
    color: var(--text-primary) !important;
    text-align: center;
    margin-bottom: 12px !important;
    padding-top: 0px !important;
}
h2 {
    font-size: 26px !important;
    font-weight: bold !important;
    color: var(--text-primary) !important;
    text-align: center;
    margin-bottom: 10px !important;
}

/* Input Fields */
.stTextInput > div > div > input {
    font-size: 22px !important;
    height: 58px !important;
    background-color: var(--input-bg) !important;
    color: var(--input-text) !important;
    border-radius: 10px !important;
}

.stRadio label, .stRadio div[role="radiogroup"] p {
    font-size: 22px !important;
    font-weight: bold !important;
    color: var(--text-primary) !important;
}

/* Submit Buttons */
.stButton>button {
    width: 100% !important;
    height: 60px !important;
    font-size: 22px !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    background-color: #1B5E20 !important;
    color: #FFFFFF !important;
    border: 2px solid #2E7D32 !important;
    margin-top: 10px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.12) !important;
}
.stButton>button:hover {
    background-color: #003300 !important;
    color: #FFFFFF !important;
}
.stButton>button p, .stButton>button span {
    color: #FFFFFF !important;
}

/* Instruction & Notice Cards */
.instruction-card {
    background: var(--card-bg);
    padding: 16px 20px;
    border-radius: 12px;
    border-left: 8px solid var(--card-border);
    margin-bottom: 15px;
}
.instruction-card p {
    font-size: 22px !important;
    color: var(--text-primary) !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}

.notice-card {
    background: var(--notice-bg);
    border-radius: 16px;
    padding: 25px;
    border-left: 10px solid var(--notice-border);
    text-align: center;
    margin-bottom: 20px;
}

.big-naming-emoji {
    font-size: 140px !important;
    line-height: 1 !important;
    text-align: center;
    margin: 15px 0;
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

# GAME DATA 1: MEMORY ITEMS
MEMORY_ITEMS = [
    {"id": "mem_1", "name": "雪櫃", "category": "一種電器", "options": ["雪櫃", "風扇", "電視"]},
    {"id": "mem_2", "name": "郵局", "category": "一種建築物", "options": ["消防局", "郵局", "醫院"]},
    {"id": "mem_3", "name": "榕樹", "category": "一種植物", "options": ["橡樹", "榕樹", "松樹"]},
    {"id": "mem_4", "name": "塑膠", "category": "一種物料", "options": ["紙張", "金屬", "塑膠"]},
    {"id": "mem_5", "name": "藍色", "category": "一種顏色", "options": ["藍色", "紅色", "綠色"]},
]

# GAME DATA 2: NAMING ITEMS
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


def render_instruction_speaker_component(instruction_text, key_suffix):
    """Compact button to read out question instructions and allow repeating."""
    escaped_text = html.escape(instruction_text).replace("'", "\\'")
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; display:flex; justify-content:center; }}
    button {{ width:100%; max-width:320px; height:42px; font-size:16px; font-weight:bold; color:#FFFFFF !important; background:#43A047; border:1.5px solid #2E7D32; border-radius:8px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.1); }}
    button:hover {{ background:#2E7D32; }}
    </style></head><body>
    <button id="inst_btn_{key_suffix}" type="button">🔊 讀出指引 (Read Instruction)</button>

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
        height=48,
    )


def render_audio_speaker_component(words_list, key_suffix):
    """Cantonese Speech Synthesis component for word list."""
    words_js_array = str(words_list)
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; text-align:center; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#0D47A1; border:2px solid #1565C0; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#002171; }}
    .status {{ font-size:15px; margin-top:6px; font-weight:bold; color:#0D47A1; }}
    </style></head><body>
    <button id="speak_btn_{key_suffix}" type="button">▶️ 播放語音 (Play Words)</button>
    <div class="status" id="status_{key_suffix}">點擊播放</div>

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
      status.textContent = '🔊 正在播放中...';
      
      let index = 0;

      function speakNext() {{
        if (index >= words.length) {{
          status.textContent = '✅ 播放完畢';
          isPlaying = false;
          btn.disabled = false;
          btn.style.background = '#0D47A1';
          btn.textContent = '🔄 重播語音 (Replay Words)';
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
            status.textContent = '✅ 播放完畢';
            isPlaying = false;
            btn.disabled = false;
            btn.style.background = '#0D47A1';
            btn.textContent = '🔄 重播語音 (Replay Words)';
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
    """Web Speech API Mic component."""
    is_continuous_js = "true" if continuous_mode else "false"
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#1B5E20; border:2px solid #2E7D32; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#003300; }}
    .status {{ font-size:15px; text-align:center; margin-top:6px; color:#1B5E20; font-weight:bold; }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 開啟麥克風 (Speak)</button>
    <div class="status" id="status_{key_suffix}">點擊開始語音</div>

    <script>
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const mic = document.getElementById('mic_{key_suffix}'), status = document.getElementById('status_{key_suffix}');
    const isContinuous = {is_continuous_js};
    let recognition = null, listening = false;
    let baseText = "";
    let isProgrammaticChange = false;

    function resetToStandby() {{
      listening = false;
      mic.style.background = '#1B5E20';
      mic.textContent = '🎤 開啟麥克風 (Speak)';
      status.textContent = '🟢 點擊開始語音';
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

    function attachManualEditListener() {{
      const doc = window.parent.document;
      const inputs = doc.querySelectorAll('input[type="text"], textarea');
      if (inputs.length > 0) {{
        const target = inputs[0];
        const handleManualEdit = () => {{
          if (!isProgrammaticChange && listening) {{
            baseText = target.value.trim();
            try {{ recognition.stop(); }} catch(e) {{}}
          }}
        }};
        target.removeEventListener('input', handleManualEdit);
        target.addEventListener('input', handleManualEdit);
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
        mic.textContent = '⏹️ 停止麥克風';
        status.textContent = isContinuous ? '🔴 麥克風開啟中...' : '🔴 正在聆聽...';
        attachManualEditListener();
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
        st.session_state.stage = "delayed_recall_free"
        st.session_state.item_start_time = time.time()


# --- STAGE 1: INTRO ---
if st.session_state.stage == "intro":
    st.title("🛒 探索香港街市 (Explore HK Market)")
    st.markdown(
        """
    <div class="instruction-card">
        <h2 style="font-size: 28px !important; text-align: center;">今天我們去超市吧！</h2>
        <p style="text-align: center;">馬上開始遊戲</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("開始 (Start)"):
        st.session_state.stage = "memory_reg_1"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.rerun()

# --- STAGE 2: MEMORY REGISTRATION TRIAL 1 ---
elif st.session_state.stage == "memory_reg_1":
    inst_1 = "請聽清楚並記住 5 個詞語，完畢後說出你記得的，次序不限。"

    st.title("🧠 記憶力遊戲 1")

    st.markdown(
        f"""
    <div class="instruction-card">
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
        user_answer = st.text_input("記得的詞語：", key="input_reg_1")
        if st.form_submit_button("👉 完成 (Finish)"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_1_items = spoken
            st.session_state.stage = "memory_reg_2"
            st.rerun()

# --- STAGE 3: MEMORY REGISTRATION TRIAL 2 ---
elif st.session_state.stage == "memory_reg_2":
    inst_2 = "詞語會再播放一次，請再次講出記得的，包括剛才說過的。"

    st.title("🧠 記憶力遊戲 2")

    st.markdown(
        f"""
    <div class="instruction-card">
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
        user_answer = st.text_input("記得的詞語：", key="input_reg_2")
        if st.form_submit_button("👉 完成 (Finish)"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_2_items = spoken
            st.session_state.stage = "memory_reg_notice"
            st.rerun()

# --- STAGE 4: MEMORY REMINDER NOTICE PAGE ---
elif st.session_state.stage == "memory_reg_notice":
    inst_notice = "請緊記這 5 個詞語！在整個測試完結時，會再問你那些詞語。"

    st.title("📌 重要提示 (Important Notice)")

    st.markdown(
        """
    <div class="notice-card">
        <h1 style="color:#D84315; font-size: 38px !important; margin-bottom: 15px !important;">請緊記這 5 個詞語！</h1>
        <p style="font-size: 26px !important; margin: 0;">
            <b>在整個測試完結時，會再問你那些詞語。</b>
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(inst_notice, "notice_inst")

    if st.button("👉 我明白了"):
        st.session_state.stage = "naming"
        st.session_state.current_item_index = 0
        st.session_state.item_start_time = time.time()
        st.rerun()

# --- STAGE 5: NAMING GAME ---
elif st.session_state.stage == "naming":
    index = st.session_state.current_item_index
    item = NAMING_ITEMS[index]
    inst_naming = "請大聲講出，這是什麼動物？"

    st.markdown(f"<p style='font-size: 20px; text-align: center; margin: 0;'>動物命名: {index+1} / {len(NAMING_ITEMS)}</p>", unsafe_allow_html=True)
    st.markdown("<h2>請大聲講出，這是什麼動物？</h2>", unsafe_allow_html=True)

    render_instruction_speaker_component(inst_naming, f"naming_{index}_inst")

    st.markdown(f"<div class='big-naming-emoji'>{item['emoji']}</div>", unsafe_allow_html=True)

    render_mic_component(f"naming_{index}", continuous_mode=False)

    with st.form(key=f"naming_form_{index}"):
        user_answer = st.text_input("答案：", key=f"user_input_{index}")
        submit_btn = st.form_submit_button("👉 提交答案 / 下一題")

        if submit_btn:
            recorded_answer = user_answer.strip() if user_answer.strip() else "跳過"
            evaluate_naming_answer(recorded_answer)
            advance_naming_item()
            st.rerun()

# --- STAGE 6: DELAYED RECALL (FREE RECALL) ---
elif st.session_state.stage == "delayed_recall_free":
    inst_free = "最開始播放了一些詞語給你聽並請你記住它們，現在請你講出你記得的那些詞語："

    st.title("⏳ 延遲記憶遊戲")

    st.markdown(
        f"""
    <div class="instruction-card">
        <p>{inst_free}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_instruction_speaker_component(inst_free, "free_recall_inst")

    render_mic_component("delayed_free", continuous_mode=True)

    with st.form(key="form_delayed_free"):
        user_answer = st.text_input("講出記得的詞語：", key="input_delayed_free")
        if st.form_submit_button("👉 完成 (Finish)"):
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
            st.session_state.missed_items = missed
            st.session_state.cued_current_index = 0
            st.session_state.cued_sub_step = "category"

            if missed:
                st.session_state.stage = "delayed_recall_cued_step"
            else:
                st.session_state.stage = "complete"
            st.rerun()

# --- STAGE 7: CUED RECALL ---
elif st.session_state.stage == "delayed_recall_cued_step":
    missed_list = st.session_state.missed_items
    curr_idx = st.session_state.cued_current_index

    if curr_idx >= len(missed_list):
        st.session_state.stage = "complete"
        st.rerun()

    item = missed_list[curr_idx]
    st.title("💡 延遲記憶遊戲 (提示)")

    if st.session_state.cued_sub_step == "category":
        inst_cue = f"提示類別為：{item['category']}，請講出這個詞語。"

        st.subheader(f"提示: 「{item['category']}」")
        render_instruction_speaker_component(inst_cue, f"cue_inst_{item['id']}")
        render_mic_component(f"cue_cat_{item['id']}", continuous_mode=True)

        with st.form(key=f"form_cat_{item['id']}"):
            user_spoken = st.text_input("請講出這個詞語：", key=f"in_cat_{item['id']}")
            if st.form_submit_button("👉 完成 (Finish)"):
                st.session_state.recalled_cued_items[item["name"]] = user_spoken.strip()
                if item["name"] in user_spoken:
                    st.session_state.cued_current_index += 1
                    st.session_state.cued_sub_step = "category"
                else:
                    st.session_state.cued_sub_step = "choice"
                st.rerun()

    elif st.session_state.cued_sub_step == "choice":
        inst_choice = "請在以下選項中選擇正確的詞語。"

        render_instruction_speaker_component(inst_choice, f"choice_inst_{item['id']}")

        with st.form(key=f"form_choice_{item['id']}"):
            selected_option = st.radio(
                "請在以下選項中選擇正確的詞語：",
                options=item["options"],
                key=f"radio_choice_{item['id']}",
            )
            if st.form_submit_button("👉 確定選擇並繼續"):
                st.session_state.recalled_choice_items[item["name"]] = selected_option
                st.session_state.cued_current_index += 1
                st.session_state.cued_sub_step = "category"
                st.rerun()

# --- STAGE 8: COMPLETE & CLINICAL REPORT ---
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
        st.session_state.missed_items = []
        st.session_state.cued_current_index = 0
        st.session_state.cued_sub_step = "category"
        st.session_state.recalled_cued_items = {}
        st.session_state.recalled_choice_items = {}
        st.rerun()

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
        st.write(f"**Registration Trial 1 Spoken:** {', '.join(st.session_state.reg_trial_1_items) if st.session_state.reg_trial_1_items else 'None'}")
        st.write(f"**Registration Trial 2 Spoken:** {', '.join(st.session_state.reg_trial_2_items) if st.session_state.reg_trial_2_items else 'None'}")
        st.write(f"**Free Recall (Scored):** {', '.join(st.session_state.recalled_free_items) if st.session_state.recalled_free_items else 'None'}")

        if st.session_state.recalled_cued_items or st.session_state.recalled_choice_items:
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
