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
