import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#  Path helper 
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

def get_total(df: pd.DataFrame, account_type: str, amount_col: str) -> float:
    '''Returns the total amount for a given account type and column.'''
    filtered = df[df["account_type"] == account_type]
    return filtered[amount_col].sum()

def get_indicator(value: float, good: float, okay: float, higher_is_better: bool = True) -> str:
    '''Returns a color indicator based on the value and thresholds.'''
    if higher_is_better:
        if value >= good:
            return "🟢 Good"
        elif value >= okay:
            return "🟡 Okay"
        else:
            return "🔴 Poor"
    else:
        if value <= good:
            return "🟢 Good"
        elif value <= okay:
            return "🟡 Okay"
        else:
            return "🔴 Poor"
        
#  Page Configuration
st.title("Financial Ratio Dashboard")
st.write("Auto-calculated from your journal entries. Shows the financial health of your business.")

#  Load data 
df = load_entries()

if df.empty:
    st.info("No journal entries found. Please add transactions on the Journal Entries page first.")
else:
    #  Calculate base values 
    total_assets = get_total(df, "Asset", "debit") - get_total(df, "Asset", "credit")
    total_liabilities = get_total(df, "Liability", "credit") - get_total(df, "Liability", "debit")
    total_equity = get_total(df, "Equity", "credit") - get_total(df, "Equity", "debit")
    total_revenue = get_total(df, "Revenue", "credit")
    total_expenses = get_total(df, "Expense", "debit")
    net_income = total_revenue - total_expenses

    #  Calculate ratios 
    # Current Ratio
    current_ratio = (total_assets / total_liabilities
                     if total_liabilities != 0 else 0)

    # Net Profit Margin
    net_profit_margin = (net_income / total_revenue * 100
                         if total_revenue != 0 else 0)

    # Return on Assets
    return_on_assets = (net_income / total_assets * 100
                        if total_assets != 0 else 0)

    # Debt to Equity
    debt_to_equity = (total_liabilities / total_equity
                      if total_equity != 0 else 0)

    #  Display Ratios
    st.subheader("Financial Ratios")
    st.markdown("---")

    # Current Ratio
    st.markdown("### 1️⃣ Current Ratio")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Ratio", f"{current_ratio:.2f}")
    with col2:
        st.write(get_indicator(current_ratio, 2, 1))
    with col3:
        st.write("**What it means:** Above 2 is great. Above 1 means you can pay your bills. Below 1 is risky.")
    st.markdown("---")

    # Net Profit Margin
    st.markdown("### 2️⃣ Net Profit Margin")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Net Profit Margin", f"{net_profit_margin:.1f}%")
    with col2:
        st.write(get_indicator(net_profit_margin, 20, 10))
    with col3:
        st.write("**What it means:** Shows what % of revenue is actual profit. Higher is better.")
    st.markdown("---")

    # Return on Assets
    st.markdown("### 3️⃣ Return on Assets")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Return on Assets", f"{return_on_assets:.1f}%")
    with col2:
        st.write(get_indicator(return_on_assets, 10, 5))
    with col3:
        st.write("**What it means:** Shows how efficiently you use assets to generate profit.")
    st.markdown("---")

    # Debt to Equity
    st.markdown("### 4️⃣ Debt to Equity Ratio")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Debt to Equity", f"{debt_to_equity:.2f}")
    with col2:
        st.write(get_indicator(debt_to_equity, 1, 2, higher_is_better=False))
    with col3:
        st.write("**What it means:** Below 1 is great. Above 2 means too much debt compared to equity.")
    st.markdown("---")

    #  Summary Chart 
    st.subheader("Business Health Overview")

    fig, ax = plt.subplots(figsize=(10, 5))

    ratios = ["Current Ratio", "Net Profit Margin %", "Return on Assets %", "Debt to Equity"]
    values = [current_ratio, net_profit_margin, return_on_assets, debt_to_equity]
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]

    ax.bar(ratios, values, color=colors)
    ax.set_ylabel("Value")
    ax.set_title("Financial Ratios Overview")
    ax.set_xticklabels(ratios, rotation=15, ha="right")
    plt.tight_layout()
    st.pyplot(fig)

    #  Raw numbers used for calculations
    with st.expander("📂 See raw numbers used for calculations"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Total Assets: ${total_assets:,.2f}")
            st.write(f"Total Liabilities: ${total_liabilities:,.2f}")
            st.write(f"Total Equity: ${total_equity:,.2f}")
        with col2:
            st.write(f"Total Revenue: ${total_revenue:,.2f}")
            st.write(f"Total Expenses: ${total_expenses:,.2f}")
            st.write(f"Net Income: ${net_income:,.2f}")