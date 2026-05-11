import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ── Path helper ────────────────────────────────────────────────────
APP_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_path(filename: str) -> str:
    '''Returns the path to a data file given its filename.'''
    return os.path.join(APP_PATH, "..", "data", filename)

def load_entries() -> pd.DataFrame:
    '''Loads journal entries from CSV. Returns empty DataFrame if file does not exist.'''
    filepath = get_data_path("journal_entries.csv")
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return pd.DataFrame()

# ── Page Config ────────────────────────────────────────────────────
st.title("🏦 Balance Sheet")
st.write("Auto-generated from your journal entries.")

# ── Load data ──────────────────────────────────────────────────────
df = load_entries()

if df.empty:
    st.info("📭 No journal entries found. Please add transactions first.")
else:
    # ── Calculate each section directly ────────────────────────────
    # Assets: debit increases assets, credit decreases assets
    assets = df[df["account_type"] == "Asset"]
    total_assets = assets["debit"].sum() - assets["credit"].sum()

    # Liabilities: credit increases liabilities, debit decreases
    liabilities = df[df["account_type"] == "Liability"]
    total_liabilities = liabilities["credit"].sum() - liabilities["debit"].sum()

    # Equity: credit increases equity, debit decreases
    equity = df[df["account_type"] == "Equity"]
    total_equity_base = equity["credit"].sum() - equity["debit"].sum()

    # Revenue increases equity
    total_revenue = df[df["account_type"] == "Revenue"]["credit"].sum()

    # Expenses decrease equity
    total_expenses = df[df["account_type"] == "Expense"]["debit"].sum()

    # Net income is part of equity
    net_income = total_revenue - total_expenses

    # Total equity = owner equity + net income
    total_equity = total_equity_base + net_income

    # ── Display Balance Sheet ──────────────────────────────────────
    st.subheader("📋 Balance Sheet")
    st.markdown("---")

    # Assets
    st.markdown("### 💰 Assets")
    asset_summary = assets.groupby("account_name").agg(
        debit=("debit", "sum"),
        credit=("credit", "sum")
    ).reset_index()
    asset_summary["balance"] = asset_summary["debit"] - asset_summary["credit"]
    for _, row in asset_summary.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(row["account_name"])
        with col2:
            st.write(f"${row['balance']:,.2f}")
    st.markdown(f"**Total Assets: ${total_assets:,.2f}**")
    st.markdown("---")

    # Liabilities
    st.markdown("### 💳 Liabilities")
    liab_summary = liabilities.groupby("account_name").agg(
        debit=("debit", "sum"),
        credit=("credit", "sum")
    ).reset_index()
    liab_summary["balance"] = liab_summary["credit"] - liab_summary["debit"]
    for _, row in liab_summary.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(row["account_name"])
        with col2:
            st.write(f"${row['balance']:,.2f}")
    st.markdown(f"**Total Liabilities: ${total_liabilities:,.2f}**")
    st.markdown("---")

    # Equity
    st.markdown("### 👤 Equity")
    equity_summary = equity.groupby("account_name").agg(
        debit=("debit", "sum"),
        credit=("credit", "sum")
    ).reset_index()
    equity_summary["balance"] = equity_summary["credit"] - equity_summary["debit"]
    for _, row in equity_summary.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(row["account_name"])
        with col2:
            st.write(f"${row['balance']:,.2f}")

    # Show net income as retained earnings inside equity
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("Retained Earnings (Net Income)")
    with col2:
        st.write(f"${net_income:,.2f}")
    st.markdown(f"**Total Equity: ${total_equity:,.2f}**")
    st.markdown("---")

    # ── Balance Check ──────────────────────────────────────────────
    st.markdown("### ⚖️ Balance Check")
    total_liabilities_and_equity = total_liabilities + total_equity
    difference = total_assets - total_liabilities_and_equity

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Assets", f"${total_assets:,.2f}")
    with col2:
        st.metric("Total Liabilities + Equity", f"${total_liabilities_and_equity:,.2f}")
    with col3:
        st.metric("Difference", f"${difference:,.2f}")

    if abs(difference) < 0.01:
        st.success("✅ Balance Sheet is balanced! Assets = Liabilities + Equity")
    else:
        st.warning("⚠️ Balance Sheet is not balanced. Check your journal entries.")

    # ── Chart ──────────────────────────────────────────────────────
    st.subheader("📊 Balance Sheet Chart")
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["Assets", "Liabilities", "Equity"]
    values = [total_assets, total_liabilities, total_equity]
    colors = ["#4CAF50", "#F44336", "#2196F3"]
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("Amount ($)")
    ax.set_title("Assets vs Liabilities vs Equity")
    plt.tight_layout()
    st.pyplot(fig)