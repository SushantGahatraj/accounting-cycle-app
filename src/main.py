import streamlit as st
import pandas as pd
import os


APP_PATH = os.path.dirname(os.path.abspath(__file__))


def get_data_path(filename: str) -> str:
    '''Returns the path to an asset file, given its filename.'''
    return os.path.join(APP_PATH, "data", filename)

st.set_page_config(
    page_title="Accounting Cycle Simulator",
    page_icon="📊",
    layout="wide"
)

# ── Home Page ─────────────────────────────────────────────────────
st.title("📊 Accounting Cycle Simulator")
st.subheader("A financial tool for small businesses and accounting students")

st.markdown("""
### What can this app do?
- 📝 **Journal Entries** — Record your daily transactions
- ⚖️ **Trial Balance** — Auto-generated from your entries
- 📈 **Income Statement** — See your profits and losses
- 🏦 **Balance Sheet** — View your assets, liabilities, and equity
- 💵 **Cash Flow Statement** — Track your cash movements
- 📊 **Financial Ratio Dashboard** — Instant health check of your business
""")

st.info("👈 Use the sidebar to navigate between pages")