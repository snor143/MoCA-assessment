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

# --- METHOD 1: VISUAL CSS & SUPERMARKET IMMERSION STYLING ---
st.markdown(
    """
<style>
/* Full Supermarket Store Background Image with Blur Overlay */
.stApp {
    background: linear-gradient(rgba(245, 247, 248, 0.88), rgba(245, 247, 248, 0.88)),
                url('https://images.unsplash.com/photo-1578916171728-46686eac8d58?q=80&w=1600&auto=format&fit=crop');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Supermarket Banner Style */
.market-banner {
    background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
    color: #FFFFFF !important;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}

/* NPC Staff & Speech Bubble Layout */
.npc-container {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 15px;
    margin-bottom: 20px;
}

.npc-avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 4px solid #2E7D32;
    background-color: #E8F5E9;
    object-fit: cover;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    flex-shrink: 0;
}

.speech-bubble {
    position: relative;
    background: #FFFFFF;
    border: 3px solid #2E7D32;
    border-radius: 18px;
    padding: 16px 20px;
    max-width: 450px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    font-size: 20px !important;
    color: #1C3125;
    font-weight: 600;
    line-height: 1.4 !important;
}

.speech-bubble:after {
    content: '';
    position: absolute;
    left: -14px;
    bottom: 25px;
    border-width: 8px 14px 8px 0;
    border-style: solid;
    border-color: transparent #2E7D32 transparent transparent;
    display: block;
    width: 0;
}

/* Supermarket Shelf / Display Card */
.market-shelf-card {
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #81C784;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.product-image {
    width: 220px;
    height: 220px;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid #C8E6C9;
    margin: 10px auto;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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

/* Input & Button Customization */
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
</style>
""",
    unsafe_allow_html=True,
)

# Initialize Session State
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

# --- GAME DATA ---
MEMORY_ITEMS = [
    {"id": "mem_1", "name": "雪櫃", "category": "一種電器", "options": ["雪櫃", "風扇", "電視"]},
    {"id": "mem_2", "name": "郵局", "category": "一種建築物", "options": ["消防局", "郵局", "醫院"]},
    {"id": "mem_3", "name": "榕樹", "category": "一種植物", "options": ["橡樹", "榕樹", "松樹"]},
    {"id": "mem_4", "name": "塑膠", "category": "一種物料", "options": ["紙張", "金屬", "塑膠"]},
    {"id": "mem_5", "name": "藍色", "category": "一種顏色", "options": ["藍色", "紅色", "綠色"]},
]

NAMING_ITEMS = [
    {
        "id": "item_1",
        "tier": "Warmup",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTa95wEIgRD64bergbVn9BgZ_w-Ia6eshD8OhL3ezEV1w&s=10",
        "primary_name": "蝴蝶",
        "acceptable_synonyms": ["蝴蝶", "呢個係蝴蝶", "這是蝴蝶", "呢隻係蝴蝶"],
        "moca_weight": 1,
        "story": "剛剛在超市外面看到這東西",
    },
    {
        "id": "item_2",
        "tier": "Moderate",
        "image_url": "https://cdn.vectorstock.com/i/750p/77/18/a-whimsical-black-and-white-line-drawing-vector-62527718.avif",
        "primary_name": "八爪魚",
        "acceptable_synonyms": ["八爪魚", "呢個係八爪魚", "這是八爪魚", "呢隻係八爪魚", "章魚"],
        "moca_weight": 1,
        "story": "進入超市後，檔主向你展示了這樣東西",
    },
    {
        "id": "item_3",
        "tier": "Low",
        "image_url": "https://www.publicdomainpictures.net/pictures/190000/velka/sloth-drawing.jpg",
        "primary_name": "樹懶",
        "acceptable_synonyms": ["樹懶", "呢個係樹懶", "這是樹懶", "呢隻係樹懶"],
        "moca_weight": 1,
        "story": "貨架上有一張圖片",
    },
]

# --- UI COMPONENT FUNCTIONS ---

def render_staff_npc(dialogue_text, staff_type="manager", staff_name="店長阿Ming"):
    """Renders the Store Staff NPC avatar alongside a retro speech bubble."""
    avatar_urls = {
        "manager": "https://cdn-icons-png.flaticon.com/512/4140/4140047.png",
        "cashier": "https://cdn-icons-png.flaticon.com/512/3052/3052217.png",
        "assistant": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
    }
    avatar_src = avatar_urls.get(staff_type, avatar_urls["manager"])

    st.markdown(
        f"""
    <div class="npc-container">
        <img src="{avatar_src}" class="npc-avatar" alt="{staff_name}">
        <div class="speech-bubble">
            <b>{staff_name}：</b><br>「{dialogue_text}」
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_instruction_speaker_component(instruction_text, key_suffix):
    """Voice speaker component for staff NPC dialogue."""
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
    """Audio broadcaster for store PA shopping list system."""
    words_js_array = str(words_list)
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; text-align:center; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#0D47A1; border:none; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#002171; }}
    .status {{ font-size:15px; margin-top:6px; font-weight:bold; color:#0D47A1; }}
    </style></head><body>
    <button id="speak_btn_{key_suffix}" type="button">📢 聽超市廣播</button>
    <div class="status" id="status_{key_suffix}">點擊收聽</div>

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
          status.textContent = '✅ 廣播完畢';
          isPlaying = false;
          btn.disabled = false;
          btn.style.background = '#0D47A1';
          btn.textContent = '🔄 重播 (Replay)';
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
            status.textContent = '✅ 廣播完畢';
            isPlaying = false;
            btn.disabled = false;
            btn.style.background = '#0D47A1';
            btn.textContent = '🔄 重播 (Replay)';
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
    """Voice speech-to-text recording input component."""
    is_continuous_js = "true" if continuous_mode else "false"
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; background:transparent; }}
    button {{ width:100%; height:62px; font-size:20px; font-weight:bold; color:#FFFFFF !important; background:#2E7D32; border:none; border-radius:12px; cursor:pointer; box-shadow:0 3px 8px rgba(0,0,0,0.15); }}
    button:hover {{ background:#1B5E20; }}
    .status {{ font-size:15px; text-align:center; margin-top:6px; color:#2E7D32; font-weight:bold; }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 按此語音回答 (Speak)</button>
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
      mic.textContent = '🎤 按此語音回答 (Speak)';
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


# ==========================================
# GAME FLOW STAGES WITH IMMERSIVE GRAPHICS
# ==========================================

# --- STAGE 1: GAME WELCOME ---
if st.session_state.stage == "intro":
    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:36px; color:#FFFFFF !important;">🛒 超級市場大搜查</h1>
        <p style="margin:5px 0 0 0; font-size:20px; opacity:0.9;">歡迎來到開心超市！今天讓我們一起完成購物任務吧！</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc("早晨！歡迎光臨開心超市！今日超市有好多新鮮貨品，準備好你的購物籃出發吧！", staff_type="manager")

    if st.button("出發 (Start Shopping)"):
        st.session_state.stage = "memory_reg_1"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.session_state.moca_memory_score = 0
        st.rerun()

# --- STAGE 2: SHOPPING LIST TRIAL 1 ---
elif st.session_state.stage == "memory_reg_1":
    inst_1 = "請聽清楚超市廣播的 5 個詞語，聽完後講出你記得的。"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">📝 第一站：觀察四周事物 (1/2)</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc(inst_1, staff_type="manager")
    render_instruction_speaker_component(inst_1, "reg_1_inst")

    word_names = [item["name"] for item in MEMORY_ITEMS]

    col_audio, col_mic = st.columns(2)
    with col_audio:
        render_audio_speaker_component(word_names, "reg_1")
    with col_mic:
        render_mic_component("reg_1", continuous_mode=True)

    with st.form(key="form_reg_1"):
        user_answer = st.text_input("記得的詞語：", key="input_reg_1")
        if st.form_submit_button("👉 記好了，下一步"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_1_items = spoken
            st.session_state.stage = "memory_reg_2"
            st.rerun()

# --- STAGE 3: SHOPPING LIST TRIAL 2 ---
elif st.session_state.stage == "memory_reg_2":
    inst_2 = "超市廣播會再播一次，請再次講出記得的東西（包括剛才講過的）。"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">📝 第一站：觀察四周事物 (2/2)</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc(inst_2, staff_type="manager")
    render_instruction_speaker_component(inst_2, "reg_2_inst")

    word_names = [item["name"] for item in MEMORY_ITEMS]

    col_audio, col_mic = st.columns(2)
    with col_audio:
        render_audio_speaker_component(word_names, "reg_2")
    with col_mic:
        render_mic_component("reg_2", continuous_mode=True)

    with st.form(key="form_reg_2"):
        user_answer = st.text_input("記得的詞語：", key="input_reg_2")
        if st.form_submit_button("👉 記好了，進入超市"):
            spoken = [w.strip() for w in user_answer.replace("，", ",").replace(" ", ",").split(",") if w.strip()]
            st.session_state.reg_trial_2_items = spoken
            st.session_state.stage = "memory_reg_notice"
            st.rerun()

# --- STAGE 4: SHOPPING MEMO NOTICE PAGE ---
elif st.session_state.stage == "memory_reg_notice":
    inst_notice = "請緊記剛才這 5 樣東西！稍後去結帳時，需要重覆講出廣播提到的字！"

    st.markdown(
        """
    <div class="market-banner" style="background: linear-gradient(135deg, #FF9800 0%, #E65100 100%);">
        <h1 style="margin:0; font-size:32px; color:#FFFFFF !important;">📌 店長特別提醒</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc("請緊記剛才這 5 樣東西！稍後去結帳時，需要重覆講出廣播提到的字！", staff_type="manager")
    render_instruction_speaker_component(inst_notice, "notice_inst")

    if st.button("👉 明白，開始逛超市！"):
        st.session_state.stage = "naming"
        st.session_state.current_item_index = 0
        st.session_state.item_start_time = time.time()
        st.rerun()

# --- STAGE 5: NAMING GAME (EXPLORING MARKET STALLS WITH GRAPHICS) ---
elif st.session_state.stage == "naming":
    index = st.session_state.current_item_index
    item = NAMING_ITEMS[index]
    inst_naming = f"{item['story']}，請問這是什麼？"

    st.markdown(
        f"""
    <div class="market-banner">
        <h1 style="margin:0; font-size:28px; color:#FFFFFF !important;">🔍 第二站：探索超市 ({index+1}/{len(NAMING_ITEMS)})</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 1. Store Staff Speaks to Patient via Avatar & Speech Bubble
    render_staff_npc(f"{item['story']}，請問這是什麼？", staff_type="assistant", staff_name="店員小花")
    render_instruction_speaker_component(inst_naming, f"naming_{index}_inst")

    # 2. Market Shelf Visual Display Container
    st.markdown(
        f"""
    <div class="market-shelf-card">
        <img src="{item['image_url']}" class="product-image" alt="Supermarket Item">
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_mic_component(f"naming_{index}", continuous_mode=False)

    with st.form(key=f"naming_form_{index}"):
        user_answer = st.text_input("這是...", key=f"user_input_{index}")
        submit_btn = st.form_submit_button("👉 下一步")

        if submit_btn:
            recorded_answer = user_answer.strip() if user_answer.strip() else "跳過"
            evaluate_naming_answer(recorded_answer)
            advance_naming_item()
            st.rerun()

# --- STAGE 6: CHECKOUT COUNTER (FREE RECALL) ---
elif st.session_state.stage == "delayed_recall_free":
    inst_free = "歡迎來到結帳處！請講出最開始廣播的 5 樣東西"

    st.markdown(
        """
    <div class="market-banner">
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">💵 第三站：結帳</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    render_staff_npc("歡迎來到結帳處！請講出最開始廣播的 5 樣東西", staff_type="cashier", staff_name="收銀員阿輝")
    render_instruction_speaker_component(inst_free, "free_recall_inst")

    render_mic_component("delayed_free", continuous_mode=True)

    with st.form(key="form_delayed_free"):
        user_answer = st.text_input("講出詞語：", key="input_delayed_free")
        if st.form_submit_button("👉 完成 (Done)"):
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
        <h1 style="margin:0; font-size:30px; color:#FFFFFF !important;">🔎 超市店員的協助</h1>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if st.session_state.cued_sub_step == "category":
        inst_cue = f"讓我幫幫你！這東西屬於【{item['category']}】，請問你記得是什麼嗎？"

        render_staff_npc(f"讓我幫幫你！這東西屬於【{item['category']}】，請問你記得是什麼嗎？", staff_type="assistant", staff_name="店員小花")
        render_instruction_speaker_component(inst_cue, f"cue_inst_{item['id']}")
        render_mic_component(f"cue_cat_{item['id']}", continuous_mode=True)

        with st.form(key=f"form_cat_{item['id']}"):
            user_spoken = st.text_input("請講出這樣東西：", key=f"in_cat_{item['id']}")
            if st.form_submit_button("👉 確認"):
                st.session_state.recalled_cued_items[item["name"]] = user_spoken.strip()
                if item["name"] in user_spoken:
                    st.session_state.cued_current_index += 1
                    st.session_state.cued_sub_step = "category"
                else:
                    st.session_state.cued_sub_step = "choice"
                st.rerun()

    elif st.session_state.cued_sub_step == "choice":
        inst_choice = "這裏有三個選項，請選擇原本廣播的那一個。"

        render_staff_npc("這裏有三個選項，請選擇原本廣播的那一個。", staff_type="assistant", staff_name="店員小花")
        render_instruction_speaker_component(inst_choice, f"choice_inst_{item['id']}")

        with st.form(key=f"form_choice_{item['id']}"):
            selected_option = st.radio(
                "請點選正確選項：",
                options=item["options"],
                key=f"radio_choice_{item['id']}",
            )
            if st.form_submit_button("👉 繼續"):
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

    render_staff_npc("恭喜你！買齊所有東西了，歡迎下次再來開心超市購物！", staff_type="manager")

    if st.button("🔄 再玩一次 (Play Again)"):
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

    # Backend Dashboard for OT/ST Assessment
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
