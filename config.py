from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Dashboard Zero48",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
IMAGENS_DIR = BASE_DIR / "imagens"
LOGO = IMAGENS_DIR / "logo.png"
