import streamlit as st
import streamlit.components.v1 as components

# --- 1. STREAMLIT PAGE CONFIG & ELDERLY-FRIENDLY ACCESSIBILITY CSS ---
st.set_page_config(
    page_title="Cognitive Test - Delayed Recall", page_icon="🧠", layout="centered"
)

st.markdown(
    """
    <style>
    /* Global accessibility styling for elderly users */
    html, body, [class*="css"] {
        font-size: 20px !important;
    }
    
    /* Enlarge Streamlit text inputs and area labels */
    .stTextInput input, .stTextArea textarea {
        font-size: 24px !important;
        height: 65px !important;
        border-radius: 10px !important;
    }
    .stTextInput label, .stTextArea label, .stRadio label {
        font-size: 22px !important;
        font-weight: 700 !important;
    }
    
    /* Larger, touch-friendly primary buttons */
    .stButton button {
        font-size: 22px !important;
        font-weight: 800 !important;
        min-height: 60px !important;
        border-radius: 12px !important;
        margin-top: 10px;
    }

    /* Custom high-contrast headers */
    .elderly-title {
        font-size: 32px !important;
        font-weight: 900;
        margin-bottom: 20px;
        color: var(--text-color);
    }
    .elderly-prompt {
        font-size: 24px !important;
        line-height: 1.5;
        margin-bottom: 20px;
        padding: 16px;
        border-radius: 12px;
        background-color: rgba(128, 128, 128, 0.1);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- 2. THEME-ADAPTIVE & EDIT-SYNCED MIC COMPONENT ---
def render_mic_component(key_suffix, continuous_mode=False):
    """Web Speech API Mic component that adapts to Light/Dark mode, supports manual edits, and features large UI elements."""
    is_continuous_js = "true" if continuous_mode else "false"
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    :root {{
      color-scheme: light dark;
      --bg-color: transparent;
      --text-color: #212121;
      --status-bg: rgba(128, 128, 128, 0.15);
      --border-color: rgba(128, 128, 128, 0.3);
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --text-color: #FFFFFF;
        --status-bg: rgba(255, 255, 255, 0.1);
        --border-color: rgba(255, 255, 255, 0.25);
      }}
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg-color);
      color: var(--text-color);
    }}
    button {{
      width: 100%;
      height: 65px;
      font-size: 22px;
      font-weight: 800;
      color: #FFFFFF;
      background: #1B5E20;
      border: 2px solid #2E7D32;
      border-radius: 12px;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
      box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }}
    button:active {{
      transform: scale(0.98);
    }}
    .status {{
      font-size: 20px;
      font-weight: 600;
      text-align: center;
      margin-top: 10px;
      padding: 12px 14px;
      border-radius: 10px;
      background-color: var(--status-bg);
      border: 1px solid var(--border-color);
      color: var(--text-color);
      min-height: 28px;
      line-height: 1.4;
      word-break: break-word;
    }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 開啟麥克風 Speak</button>
    <div class="status" id="status_{key_suffix}">🟢 點擊上方按鈕開始語音輸入</div>

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
      mic.textContent = '🎤 開啟麥克風 Speak';
      status.textContent = '🟢 點擊上方按鈕開始語音輸入';
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
        mic.style.background = '#C62828';
        mic.textContent = '⏹️ 停止麥克風 (錄音中)';
        status.textContent = isContinuous ? '🔴 麥克風開啟中，請講話...' : '🔴 正在聆聽中...';
        attachManualEditListener();
      }};

      recognition.onresult = (event) => {{
        if (isContinuous) {{
          let interimTranscript = '';
          let finalTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; ++i) {{
            if (event.results[i].isFinal) {{
              finalTranscript += event.results[i][0].transcript;
            }} else {{
              interimTranscript += event.results[i][0].transcript;
            }}
          }}

          if (finalTranscript) {{
            baseText += (baseText ? ' ' : '') + finalTranscript.trim();
          }}

          const displayText = baseText + (interimTranscript ? (baseText ? ' ' : '') + interimTranscript : '');
          status.textContent = '🎧 正在記錄: ' + displayText;
          injectValueIntoStreamlitWidget(displayText);
        }} else {{
          const text = event.results[0][0].transcript.trim();
          const combined = baseText ? (baseText + ' ' + text) : text;
          status.textContent = '🎧 聽到: ' + text;
          injectValueIntoStreamlitWidget(combined);
        }}
      }};

      recognition.onerror = (event) => {{
        if (event.error !== 'no-speech') {{
          status.textContent = '⚠️ 語音識別問題 (' + event.error + ')，請再試一次';
        }}
      }};

      recognition.onend = () => {{
        if (listening && isContinuous) {{
          try {{ recognition.start(); }} catch(e) {{ resetToStandby(); }}
        }} else {{
          resetToStandby();
        }}
      }};
    }} else {{
      mic.disabled = true;
      status.textContent = '❌ 瀏覽器不支援語音功能';
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
        height=130,
    )


# --- 3. HELPER FUNCTIONS & SESSION INITIALIZATION ---
def check_answer(user_input, target):
    """Checks if target word is present in user's text."""
    if not user_input:
        return False
    return target in user_input.strip()


if "recall_stage" not in st.session_state:
    st.session_state.recall_stage = (
        "spontaneous"  # Options: 'spontaneous', 'category_hint', 'multiple_choice', 'completed'
    )

if "target_words" not in st.session_state:
    st.session_state.target_words = ["紅包", "百合", "教堂"]
    st.session_state.category_hints = {
        "紅包": "一種物品/節慶禮物",
        "百合": "一種花卉",
        "教堂": "一座建築物",
    }
    st.session_state.mc_options = {
        "紅包": ["紅包", "燈籠", "對聯"],
        "百合": ["玫瑰", "百合", "菊花"],
        "教堂": ["學校", "醫院", "教堂"],
    }

if "recalled_words" not in st.session_state:
    st.session_state.recalled_words = set()

if "missing_queue" not in st.session_state:
    st.session_state.missing_queue = []

if "current_queue_index" not in st.session_state:
    st.session_state.current_queue_index = 0


# --- 4. APP FLOW CONTROL ---

# STAGE 1: Spontaneous Free Recall
if st.session_state.recall_stage == "spontaneous":
    st.markdown(
        "<div class='elderly-title'>延遲回憶測試 (Delayed Recall)</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='elderly-prompt'>請講出或輸入您剛才記住的所有詞語：</div>",
        unsafe_allow_html=True,
    )

    user_text = st.text_input("您的回答 Your Answer:", key="spontaneous_input")
    render_mic_component(key_suffix="spontaneous", continuous_mode=True)

    if st.button("提交答案 Submit Answer", use_container_width=True):
        missing_words = []
        for w in st.session_state.target_words:
            if check_answer(user_text, w):
                st.session_state.recalled_words.add(w)
            else:
                missing_words.append(w)

        if len(missing_words) == 0:
            # All correct without hints -> Skip directly to end
            st.session_state.recall_stage = "completed"
            st.rerun()
        else:
            # Move to Hint 1 (Category Hint) for missing words
            st.session_state.missing_queue = missing_words
            st.session_state.current_queue_index = 0
            st.session_state.recall_stage = "category_hint"
            st.rerun()

# STAGE 2: Hint 1 - Category Hint
elif st.session_state.recall_stage == "category_hint":
    current_word = st.session_state.missing_queue[
        st.session_state.current_queue_index
    ]
    hint = st.session_state.category_hints[current_word]

    st.markdown(
        "<div class='elderly-title'>提示 1：類別提示 (Category Hint)</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='elderly-prompt'>其中有一個詞語屬於：<b>【 {hint} 】</b><br>請試著講出這個詞語：</div>",
        unsafe_allow_html=True,
    )

    hint_text = st.text_input("您的答案 Your Answer:", key=f"hint1_{current_word}")
    render_mic_component(
        key_suffix=f"hint1_{st.session_state.current_queue_index}",
        continuous_mode=False,
    )

    if st.button("確認答案 Confirm Answer", use_container_width=True):
        if check_answer(hint_text, current_word):
            st.session_state.recalled_words.add(current_word)
            # Correct! Move to next missing word or complete if done
            st.session_state.current_queue_index += 1
            if (
                st.session_state.current_queue_index
                >= len(st.session_state.missing_queue)
            ):
                st.session_state.recall_stage = "completed"
            st.rerun()
        else:
            # Incorrect -> Fail to Hint 2 (Multiple Choice)
            st.session_state.recall_stage = "multiple_choice"
            st.rerun()

# STAGE 3: Hint 2 - Multiple Choice
elif st.session_state.recall_stage == "multiple_choice":
    current_word = st.session_state.missing_queue[
        st.session_state.current_queue_index
    ]
    options = st.session_state.mc_options[current_word]

    st.markdown(
        "<div class='elderly-title'>提示 2：多項選擇 (Multiple Choice)</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='elderly-prompt'>請從以下選項中選出正確的詞語：</div>",
        unsafe_allow_html=True,
    )

    selected_option = st.radio(
        "請選擇答案 Select One:", options, key=f"mc_{current_word}"
    )

    if st.button("確認選擇 Confirm Choice", use_container_width=True):
        if selected_option == current_word:
            st.session_state.recalled_words.add(current_word)

        # Move to next missing word or complete
        st.session_state.current_queue_index += 1
        if (
            st.session_state.current_queue_index
            >= len(st.session_state.missing_queue)
        ):
            st.session_state.recall_stage = "completed"
        else:
            st.session_state.recall_stage = "category_hint"
        st.rerun()

# STAGE 4: Completed End Screen
elif st.session_state.recall_stage == "completed":
    st.markdown(
        "<div class='elderly-title'>🎉 測試完成 Test Completed</div>",
        unsafe_allow_html=True,
    )
    score = len(st.session_state.recalled_words)
    total = len(st.session_state.target_words)

    st.markdown(
        f"<div class='elderly-prompt'>您成功回憶起：<b>{score} / {total}</b> 個詞語。</div>",
        unsafe_allow_html=True,
    )

    if st.button("重新測試 Restart Test", use_container_width=True):
        st.session_state.recall_stage = "spontaneous"
        st.session_state.recalled_words = set()
        st.session_state.missing_queue = []
        st.session_state.current_queue_index = 0
        st.rerun()
