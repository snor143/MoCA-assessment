def render_mic_component(key_suffix, continuous_mode=False):
    """Web Speech API Mic component supporting continuous mode, manual edits mid-session, and multi-session appending."""
    is_continuous_js = "true" if continuous_mode else "false"
    components.html(
        f"""
    <!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:sans-serif; }}
    button {{ width:100%; height:55px; font-size:18px; font-weight:bold; color:white; background:#2E7D32; border:0; border-radius:12px; cursor:pointer; transition: background 0.3s; }}
    .status {{ font-size:16px; text-align:center; margin:6px 0; min-height:22px; }}
    </style></head><body>
    <button id="mic_{key_suffix}" type="button">🎤 開啟麥克風 Speak</button>
    <div class="status" id="status_{key_suffix}">點擊上方按鈕開始語音輸入</div>

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
        
        isProgrammaticChange = true; // Flag to ignore our own speech injections
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

    // Attach real-time listener to capture mid-session manual typing/deletions
    function attachManualEditListener() {{
      const doc = window.parent.document;
      const inputs = doc.querySelectorAll('input[type="text"], textarea');
      if (inputs.length > 0) {{
        const target = inputs[0];
        
        const handleManualEdit = () => {{
          if (!isProgrammaticChange && listening) {{
            // Patient/Clinician deleted or changed text manually mid-session
            baseText = target.value.trim();
            // Restart recognition to wipe browser's internal transcript buffer
            try {{
              recognition.stop(); 
            }} catch(e) {{}}
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
        mic.textContent = '⏹️ 停止麥克風 (麥克風持續開啟中)';
        status.textContent = isContinuous ? '🔴 麥克風開啟中，可以邊想邊講...' : '🔴 正在聆聽中，請講話...';
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
        // Auto-restart if active, maintaining updated baseText baseline
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
        height=100,
    )
