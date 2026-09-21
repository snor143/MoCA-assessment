!pip install streamlit

import streamlit as st
import time
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="HK Supermarket Explorer",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

#Custom geriatric UI CSS (Large text, high contrast, warm colors)
st.markdown("""
    <style>
    .main {
        background-color: #FFFDF9;
    }
    .stButton>button {
        width: 100%;
        height: 80px;
        font-size: 24px !important;
        font-weight: bold;
        border-radius: 16px;
        background-color: #4CAF50;
        color: white;
        border: none;
        margin-bottom: 12px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .instruction-card {
        background-color: #F0F7F4;
        padding: 24px;
        border-radius: 16px;
        border-left: 8px solid #2E7D32;
        margin-bottom: 24px;
    }
    .item-title {
        font-size: 32px;
        font-weight: bold;
        color: #1B5E20;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

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
        "emoji": "🍊",
        "correct_name": "Fresh Orange (鮮橙)",
        "options": ["Fresh Orange (鮮橙)", "Apple (蘋果)", "Mango (芒果)", "Lemon (檸檬)"],
        "moca_weight": 1
    },
    {
        "id": "item_2",
        "tier": "Moderate Familiarity",
        "emoji": "🥒",
        "correct_name": "Bitter Gourd (苦瓜)",
        "options": ["Cucumber (青瓜)", "Bitter Gourd (苦瓜)", "Luffa (絲瓜)", "Zucchini (翠玉瓜)"],
        "moca_weight": 1
    },
    {
        "id": "item_3",
        "tier": "Low Familiarity (MoCA Rhino Equivalent)",
        "emoji": "⭐",
        "correct_name": "Starfruit (楊桃)",
        "options": ["Guava (番石榴)", "Dragon Fruit (火龍果)", "Starfruit (楊桃)", "Wax Apple (蓮霧)"],
        "moca_weight": 1
    }
]

def record_response(selected_option):
    # Calculate reaction latency
    elapsed_time = round(time.time() - st.session_state.item_start_time, 2)
    current_item = ITEMS[st.session_state.current_item_index]
    
    is_correct = (selected_option == current_item["correct_name"])
    if is_correct:
        st.session_state.moca_naming_score += current_item["moca_weight"]
        
    # Log raw telemetry data silently
    st.session_state.telemetry_logs.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item_id": current_item["id"],
        "familiarity_tier": current_item["tier"],
        "correct_answer": current_item["correct_name"],
        "user_selected": selected_option,
        "is_correct": is_correct,
        "reaction_latency_seconds": elapsed_time
    })
    
    # Progress to next item or conclude assessment
    if st.session_state.current_item_index + 1 < len(ITEMS):
        st.session_state.current_item_index += 1
        st.session_state.item_start_time = time.time()
    else:
        st.session_state.stage = "complete"

# --- STAGE 1: COVERATION INTRO SCREEN ---
if st.session_state.stage == "intro":
    st.title("🛒 歡迎來到香港街市 Supermarket Explorer")
    
    st.markdown("""
        <div class="instruction-card">
            <h2>婆婆/伯伯，今日我們要去超級市場買菜！</h2>
            <p style="font-size: 22px;">請看看貨架上的新鮮食材，並點擊正確的名稱放入購物車。</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("開始逛街買菜 (Start Supermarket Visit)"):
        st.session_state.stage = "gameplay"
        st.session_state.item_start_time = time.time()
        st.rerun()

        # --- STAGE 2: GAMEPLAY (COVERT MOCA NAMING) ---
elif st.session_state.stage == "gameplay":
    current_item = ITEMS[st.session_state.current_item_index]
    
    st.markdown(f"<p style='font-size: 24px; text-align: center;'>進度 Progress: {st.session_state.current_item_index + 1} / {len(ITEMS)}</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>請告訴婆婆，這是什麼新鮮食材？</h2>", unsafe_allow_html=True)
    
    # Display item visual target (Large central graphic)
    st.markdown(f"<div style='font-size: 140px; text-align: center; margin: 20px 0;'>{current_item['emoji']}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Render answer choices as large touch targets
    cols = st.columns(2)
    for index, option in enumerate(current_item["options"]):
        col = cols[index % 2]
        with col:
            if st.button(option, key=f"btn_{index}_{st.session_state.current_item_index}"):
                record_response(option)
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

    # --- HIDDEN THERAPIST TELEMETRY DASHBOARD ---
    st.markdown("---")
    with st.expander("🩺 Occupational Therapist / Researcher Telemetry Dashboard", expanded=True):
        st.subheader("Converted MoCA Naming Assessment Result")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("MoCA Proxy Naming Sub-score", f"{st.session_state.moca_naming_score} / 3 Points")
        with col2:
            avg_latency = pd.DataFrame(st.session_state.telemetry_logs)["reaction_latency_seconds"].mean()
            st.metric("Avg. Response Latency", f"{round(avg_latency, 2)} seconds")
            
        st.subheader("Raw Touch Telemetry Stream (.csv)")
        df = pd.DataFrame(st.session_state.telemetry_logs)
        st.dataframe(df)
        
        # CSV Export for clinical record-keeping
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Telemetry Log (.CSV)",
            data=csv,
            file_name=f"moca_naming_telemetry_{int(time.time())}.csv",
            mime="text/csv"
        )
