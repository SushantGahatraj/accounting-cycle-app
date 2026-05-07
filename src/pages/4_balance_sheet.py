mport os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#Path helper
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

def get_section(df: pd.DataFrame, account_type: str) -> pd.DataFrame:
    '''Filters entries by account type and returns net balance per account.'''
    section_df = df[df["account_type"] == account_type].copy()
    section_df = section_df.groupby("account_name").agg(
        debit=("debit", "sum"),
        credit=("credit", "sum")
    ).reset_index()
    section_df["net_balance"] = section_df["debit"] - section_df["credit"]
    return section_df

def display_section(title: str, df: pd.DataFrame, emoji: str):
    '''Displays a section of the balance sheet with a title and total.'''
    st.markdown(f"### {emoji} {title}")
    if df.empty:
        st.write(f"No {title.lower()} entries found.")
        return 0
    for _, row in df.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(row["account_name"])
        with col2:
            st.write(f"${abs(row['net_balance']):,.2f}")
    total = df["net_balance"].sum()
    st.markdown(f"**Total {title}: ${abs(total):,.2f}**")
    st.markdown("---")
    return total

# Page Config 
st.title("🏦 Balance Sheet")
st.write("Auto-generated from your journal entries. Shows assets, liabilities, and equity.")

#  Load data 
df = load_entries()

if df.empty:
    st.info("📭 No journal entries found. Please add transactions on the Journal Entries page first.")
else:
    # Get each section 
    assets_df = get_section(df, "Asset")
    liabilities_df = get_section(df, "Liability")
    equity_df = get_section(df, "Equity")

    #  Display Balance Sheet 
    st.subheader("📋 Balance Sheet")
    st.markdown("---")

    total_assets = display_section("Assets", assets_df, "💰")
    total_liabilities = display_section("Liabilities", liabilities_df, "💳")
    total_equity = display_section("Equity", equity_df, "👤")

    # Check if balanced 
    st.markdown("### ⚖️ Balance Check")
    total_liabilities_equity = total_liabilities + total_equity

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Assets", f"${abs(total_assets):,.2f}")
    with col2:
        st.metric("Total Liabilities + Equity",
                  f"${abs(total_liabilities_equity):,.2f}")
    with col3:
        difference = abs(total_assets) - abs(total_liabilities_equity)
        st.metric("Difference", f"${difference:,.2f}")

    if abs(difference) < 0.01:
        st.success("✅ Balance Sheet is balanced! Assets = Liabilities + Equity")
    else:
        st.warning("⚠️ Balance Sheet is not balanced. Check your journal entries.")

    #  Chart 
    st.subheader("📊 Balance Sheet Chart")

    labels = ["Assets", "Liabilities", "Equity"]
    values = [
        abs(total_assets),
        abs(total_liabilities),
        abs(total_equity)
    ]
    colors = ["#4CAF50", "#F44336", "#2196F3"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("Amount ($)")
    ax.set_title("Assets vs Liabilities vs Equity")
    plt.tight_layout()
    st.pyplot(fig)