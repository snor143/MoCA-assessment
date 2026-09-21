import streamlit as st
import time
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(
    page_title="HK Supermarket Explorer - Voice Naming",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom geriatric UI CSS
st.markdown("""
    <style>
    .main {
        background-color: #FFFDF9;
    }
    .stButton>button {
        width: 100%;
        height: 70px;
        font-size: 22px !important;
        font-weight: bold;
        border-radius: 16px;
        background-color: #2E7D32;
        color: white;
        border: none;
        margin-bottom: 12px;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
    }
    .instruction-card {
        background-color: #F0F7F4;
        padding: 24px;
        border-radius: 16px;
        border-left: 8px solid #2E7D32;
        margin-bottom: 24px;
    }
    .voice-box {
        background-color: #E8F5E9;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        border: 2px dashed #4CAF50;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "stage" not in st.session_state:
    st.session_state.stage = "intro"

if "current_item_index" not in st.session_state:
    st.session_state.current_item_index = 0

if "telemetry_logs" not in st.session_state:
    st.session_state.telemetry_logs = []

if "item_start_time" not in st.session_state:
    st.session_state.item_start_time = None

if "moca_naming_score" not in st.session_state:
    st.session_state.moca_naming_score = 0

# Grade 1 = High familiarity, Grade 2 = Medium, Grade 3 = Low (MoCA Rhino equivalent)
ITEMS = [
    {
        "id": "item_1",
        "tier": "High Familiarity (Warmup)",
        "emoji": "🐓",
        "primary_name": "雞",
        "acceptable_synonyms": ["雞", "公雞", "母雞", "雞仔"],
        "moca_weight": 1
    },
    {
        "id": "item_2",
        "tier": "Moderate Familiarity",
        "emoji": "🐙",
        "primary_name": "八爪魚",
        "acceptable_synonyms": ["八爪魚"],
        "moca_weight": 1
    },
    {
        "id": "item_3",
        "tier": "Low Familiarity (MoCA Rhino Equivalent)",
        "emoji": "🦥",
        "primary_name": "樹懶",
        "acceptable_synonyms": ["樹懶"],
        "moca_weight": 1
    }
]

def evaluate_cantonese_speech(spoken_text):
    """Evaluates Cantonese speech, provides positive tick feedback for correct answers, and advances smoothly."""
    current_item = ITEMS[st.session_state.current_item_index]
    
    # Calculate latency
    if st.session_state.item_start_time:
        elapsed_time = round(time.time() - st.session_state.item_start_time, 2)
    else:
        elapsed_time = 0.0
    
    clean_text = spoken_text.strip().replace(" ", "").replace("呢個係", "").replace("這是", "").replace("個位是", "")
    
    # Check if any synonym exists in spoken sentence or clean text
    is_correct = any(synonym in spoken_text or synonym in clean_text for synonym in current_item["acceptable_synonyms"])
    
    if is_correct:
        st.session_state.moca_naming_score += current_item["moca_weight"]
        st.session_state.show_tick_feedback = True
    else:
        st.session_state.show_tick_feedback = False

    # Log telemetry
    st.session_state.telemetry_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_id": current_item["id"],
        "target_name": current_item["primary_name"],
        "user_spoken_raw": spoken_text,
        "is_correct": is_correct,
        "speech_latency_seconds": elapsed_time
    })

    # Prepare for next item
    st.session_state.pending_advance = True
    
# --- STAGE 1: INTRO SCREEN ---
if st.session_state.stage == "intro":
    st.title("🛒 香港街市語音買菜 (HK Market Voice Explorer)")
    
    st.markdown("""
        <div class="instruction-card">
            <h2>婆婆/伯伯，今日我們要去街市買菜！</h2>
            <p style="font-size: 22px;">請睇睇螢幕上的食材，<b>用廣東話講出它的名字</b>。</p>
            <p style="font-size: 18px; color: #555;">(例如說：「這是鮮橙」或「苦瓜」)</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("開始買菜 (Start Voice Assessment)"):
        st.session_state.stage = "gameplay"
        st.session_state.item_start_time = time.time()
        st.rerun()

# --- STAGE 2: GAMEPLAY (CANTONESE VOICE RECOGNITION) ---
elif st.session_state.stage == "gameplay":
    # 1. Listen for voice recognition results passed from JS via URL parameters
    if "speech_result" in st.query_params:
        spoken_transcript = st.query_params["speech_result"]
        # Clear URL parameter
        del st.query_params["speech_result"]
        # Evaluate speech and update state
        evaluate_cantonese_speech(spoken_transcript)
        st.rerun()

    # Helper to advance to next item safely
    def advance_to_next_item():
        st.session_state.show_tick_feedback = False
        st.session_state.pending_advance = False
        if st.session_state.current_item_index + 1 < len(ITEMS):
            st.session_state.current_item_index += 1
            st.session_state.item_start_time = time.time()
        else:
            st.session_state.stage = "complete"

    # Handle pending advance state (displays tick if correct, then advances)
    if st.session_state.get("pending_advance", False):
        if st.session_state.get("show_tick_feedback", False):
            st.success("✅ 正確！ (Correct!)", icon="✅")
            time.sleep(1.0)  # Brief visual tick feedback
        advance_to_next_item()
        st.rerun()

    current_item = ITEMS[st.session_state.current_item_index]

    # Display progress
    st.markdown(f"<p style='font-size: 22px; text-align: center; color: #666;'>進度: {st.session_state.current_item_index + 1} / {len(ITEMS)}</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>請大聲講出，這是什麼食材？</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #2E7D32;'>💡 提示：可以說<b>「呢個係...」</b>（例如：「呢個係苦瓜」）</p>", unsafe_allow_html=True)

    # Visual stimulus
    st.markdown(f"<div style='font-size: 130px; text-align: center; margin: 10px 0;'>{current_item['emoji']}</div>", unsafe_allow_html=True)

    # Speech Recognition HTML/JS Component
    components.html(
        f"""
        <!DOCTYPE html>
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
                        
                        // Pass Cantonese speech transcript directly to Streamlit Python via URL
                        setTimeout(function() {{
                            window.top.location.href = window.top.location.pathname + "?speech_result=" + encodeURIComponent(transcript);
                        }}, 600);
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

    st.markdown("---")
    
    # Manual text input backup
    manual_input = st.text_input(
        "手動輸入 / 備用答案 (Manual Backup Input):", 
        key=f"manual_in_{st.session_state.current_item_index}"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👉 提交手動答案 (Submit Manual Text)", key=f"btn_next_{st.session_state.current_item_index}"):
            ans = manual_input if manual_input else "未有說話"
            evaluate_cantonese_speech(ans)
            st.rerun()

    with col2:
        if st.button("⏭️ 跳過 (Skip Item)", key=f"btn_skip_{st.session_state.current_item_index}"):
            evaluate_cantonese_speech("跳過")
            st.rerun()

# --- STAGE 3: ASSESSMENT COMPLETE & THERAPIST DASHBOARD ---
elif st.session_state.stage == "complete":
    st.balloons()
    st.title("🎉 買菜完成！感謝您的幫忙！")
    st.markdown("<p style='font-size: 24px;'>您已經成功將所有食材放入購物車。</p>", unsafe_allow_html=True)
    
    if st.button("再玩一次 (Play Again)"):
        st.session_state.stage = "intro"
        st.session_state.current_item_index = 0
        st.session_state.telemetry_logs = []
        st.session_state.moca_naming_score = 0
        st.rerun()

    # --- THERAPIST TELEMETRY DASHBOARD ---
    st.markdown("---")
    with st.expander("🩺 Occupational Therapist / Speech Telemetry Dashboard", expanded=True):
        st.subheader("MoCA Naming Sub-score (Spontaneous Confrontation)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("MoCA Proxy Naming Sub-score", f"{st.session_state.moca_naming_score} / 3 Points")
        with col2:
            avg_latency = pd.DataFrame(st.session_state.telemetry_logs)["speech_latency_seconds"].mean()
            st.metric("Avg. Speech Latency", f"{round(avg_latency, 2)} seconds")
            
        st.subheader("Raw Speech Telemetry Stream (.csv)")
        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        
        # CSV Export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Speech Telemetry Log (.CSV)",
            data=csv,
            file_name=f"moca_cantonese_speech_telemetry_{int(time.time())}.csv",
            mime="text/csv"
        )
