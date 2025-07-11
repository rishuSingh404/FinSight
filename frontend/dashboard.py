import streamlit as st
import requests
import pandas as pd
import numpy as np
from pathlib import Path

# --- CONFIG ---
API_BASE_URL = "http://localhost:8000/api/v1"
APP_TITLE = "Financial Analytics Dashboard"
LOGO_PATH = "https://upload.wikimedia.org/wikipedia/commons/6/6b/Bitmap_Icon_Finance.png"  # Replace with your logo if needed

# --- PAGE CONFIG ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MINIMALIST CSS ---
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*='css']  {
        font-family: 'Inter', sans-serif !important;
        background: #f7f8fa;
    }
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        background: #fff;
        color: #232946;
        padding: 1.2rem 2.5rem 1.2rem 2.5rem;
        border-bottom: 1px solid #ececec;
        margin-bottom: 2rem;
        box-shadow: none;
    }
    .top-bar .logo {
        height: 48px;
        margin-right: 1.5rem;
    }
    .top-bar .title {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .section-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #232946;
        margin-bottom: 1.5rem;
        margin-top: 0.5rem;
    }
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-top: 2rem;
        padding: 1rem 0 0.5rem 0;
        background: none;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ICONS (SVG as HTML) ---
ICONS = {
    "dashboard": "<svg width='20' height='20' fill='none' stroke='#2563eb' stroke-width='2' viewBox='0 0 24 24'><rect x='3' y='3' width='7' height='7'/><rect x='14' y='3' width='7' height='7'/><rect x='14' y='14' width='7' height='7'/><rect x='3' y='14' width='7' height='7'/></svg>",
    "upload": "<svg width='20' height='20' fill='none' stroke='#2563eb' stroke-width='2' viewBox='0 0 24 24'><path d='M12 19V6M5 12l7-7 7 7'/></svg>",
    "analysis": "<svg width='20' height='20' fill='none' stroke='#2563eb' stroke-width='2' viewBox='0 0 24 24'><path d='M3 17v2a2 2 0 002 2h14a2 2 0 002-2v-2M16 11V7a4 4 0 00-8 0v4M5 11h14'/></svg>",
    "predict": "<svg width='20' height='20' fill='none' stroke='#2563eb' stroke-width='2' viewBox='0 0 24 24'><circle cx='12' cy='12' r='10'/><path d='M12 6v6l4 2'/></svg>",
    "results": "<svg width='20' height='20' fill='none' stroke='#2563eb' stroke-width='2' viewBox='0 0 24 24'><path d='M3 3h18v18H3V3z'/><path d='M9 9h6v6H9V9z'/></svg>",
    "settings": "<svg width='20' height='20' fill='none' stroke='#2563eb' stroke-width='2' viewBox='0 0 24 24'><circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09a1.65 1.65 0 00-1-1.51 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09a1.65 1.65 0 001.51-1 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06a1.65 1.65 0 001.82.33h.09a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51h.09a1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82v.09a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z'/></svg>",
    "help": "<svg width='20' height='20' fill='none' stroke='#2563eb' stroke-width='2' viewBox='0 0 24 24'><circle cx='12' cy='12' r='10'/><path d='M9.09 9a3 3 0 115.82 0c0 1.5-1.5 2.25-2.25 2.25S12 13.5 12 15'/></svg>",
}

NAV_ITEMS = [
    ("Dashboard", "dashboard"),
    ("Upload", "upload"),
    ("Analysis", "analysis"),
    ("Prediction", "predict"),
    ("Results", "results"),
    ("Settings", "settings"),
    ("Help", "help"),
]

def check_api_health():
    try:
        r = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

# --- MAIN APP ---
def main():
    load_css()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("## Navigation")
        sidebar_tab = st.radio(
            "",
            ["Home", "Profile", "Settings", "Help"],
            key="sidebar_tab",
            label_visibility="collapsed"
        )

    # --- TOP BAR ---
    st.markdown(f"""
    <div class='top-bar'>
        <img src='https://cdn-icons-png.flaticon.com/512/10438/10438392.png' class='logo' alt='Logo' />
        <span class='title'>{APP_TITLE}</span>
    </div>
    """, unsafe_allow_html=True)

    # --- API Status ---
    api_ok = check_api_health()
    st.markdown(f"""
    <div class='api-status'>
        <span class='api-dot{' down' if not api_ok else ''}'></span>
        API Status: <span style='color: {'#4caf50' if api_ok else '#e53935'};'>{'Connected' if api_ok else 'Disconnected'}</span>
    </div>
    """, unsafe_allow_html=True)
    if not api_ok:
        st.error("Backend API is not reachable. Please start the backend server.")
        st.stop()

    # --- MAIN PAGE LOGIC ---
    if sidebar_tab == "Home":
        st.markdown("#### Welcome to the Financial Analytics Dashboard.")
        st.write("Use the workflow below: Upload your data, analyze it, predict risk, and view results.")

        # --- Upload Section ---
        st.markdown("### Upload Financial Data")
        uploaded_file = st.file_uploader(
            "Select a file to upload",
            type=["csv", "txt", "pdf", "xlsx", "xls"],
            help="Supported formats: CSV, TXT, PDF, Excel (XLSX/XLS). Max size: 200MB."
        )
        st.caption("Supported formats: CSV, TXT, PDF, Excel (XLSX/XLS). Max size: 200MB.")
        if uploaded_file:
            st.success(f"File '{uploaded_file.name}' uploaded successfully.")
            st.session_state['file_id'] = uploaded_file.name  # For demo, use filename as ID

            # --- Analysis Section ---
            st.markdown("### Analysis")
            st.write("Analysis options and results would appear here.")
            if st.button("Continue to Prediction", key="to_predict", use_container_width=True):
                st.session_state['show_prediction'] = True

            # --- Prediction Section ---
            if st.session_state.get('show_prediction'):
                st.markdown("### Prediction")
                st.write("Prediction options and results would appear here.")
                if st.button("Continue to Results", key="to_results", use_container_width=True):
                    st.session_state['show_results'] = True

            # --- Results Section ---
            if st.session_state.get('show_results'):
                st.markdown("### Results")
                st.write("Results and visualizations would appear here.")
                if st.button("Start New Analysis", key="to_upload", use_container_width=True):
                    st.session_state['file_id'] = None
                    st.session_state['show_prediction'] = False
                    st.session_state['show_results'] = False

    elif sidebar_tab == "Profile":
        st.markdown("### Profile")
        st.write("User profile and preferences will be here.")

    elif sidebar_tab == "Settings":
        st.markdown("### Settings")
        st.write("Theme, profile, and preferences will be here.")

    elif sidebar_tab == "Help":
        st.markdown("### Help & Support")
        st.write("FAQ, contact, and documentation links will be here.")

    # --- Footer ---
    st.markdown("<div class='footer'>© 2024 Financial Analytics Dashboard | All rights reserved.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 