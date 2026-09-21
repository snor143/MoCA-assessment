# Speech Recognition HTML/JS Component
    components.html(
        f"""
        <!DOCTYPE html>
        <!-- Item Index: {st.session_state.current_item_index} -->
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                .mic-btn {{
                    width: 100%;
                    height: 85px;
                    font-size: 24px;
                    font-weight: bold;
                    background-color: #E65100;
                    color: white;
                    border: none;
                    border-radius: 18px;
                    cursor: pointer;
                    box-shadow: 0px 4px 8px rgba(0,0,0,0.15);
                }}
                .mic-btn:active {{ background-color: #BF360C; }}
                .status-text {{ font-size: 20px; font-family: sans-serif; color: #333; text-align: center; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <button class="mic-btn" id="start-btn" onclick="startRecognition()">🎤 按此說話 (Tap & Say "呢個係...")</button>
            <div class="status-text" id="status">點擊上方按鈕並講出名稱</div>

            <script>
                var recognition;
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
                    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.lang = 'zh-HK';
                    recognition.continuous = false;
                    recognition.interimResults = false;

                    recognition.onstart = function() {{
                        document.getElementById('status').innerHTML = "🔴 正在聆聽中，請講話... (Listening...)";
                        document.getElementById('start-btn').style.backgroundColor = "#D32F2F";
                    }};

                    recognition.onresult = function(event) {{
                        var transcript = event.results[0][0].transcript;
                        document.getElementById('status').innerHTML = "✅ 聽到: <b>" + transcript + "</b>";
                        document.getElementById('start-btn').style.backgroundColor = "#388E3C";
                        
                        // Clean history and pass transcript directly to Streamlit via URL
                        setTimeout(function() {{
                            var cleanUrl = window.top.location.pathname + "?speech_result=" + encodeURIComponent(transcript);
                            window.top.history.replaceState(null, '', cleanUrl);
                            window.top.location.href = cleanUrl;
                        }}, 500);
                    }};

                    recognition.onerror = function(event) {{
                        document.getElementById('status').innerHTML = "⚠️ 未能識別，請再試一次 (Error: " + event.error + ")";
                        document.getElementById('start-btn').style.backgroundColor = "#E65100";
                    }};
                }} else {{
                    document.getElementById('status').innerHTML = "❌ 瀏覽器不支援語音功能 (請使用 Chrome 或 Safari)";
                }}

                function startRecognition() {{
                    if (recognition) {{
                        try {{ recognition.start(); }} catch(e) {{ recognition.stop(); recognition.start(); }}
                    }}
                }}
            </script>
        </body>
        </html>
        """,
        height=150
    )
