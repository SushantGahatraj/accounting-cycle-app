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

def get_revenue(df: pd.DataFrame) -> pd.DataFrame:
    '''Filters only Revenue accounts and returns total credit per account.'''
    revenue_df = df[df["account_type"] == "Revenue"].copy()
    revenue_df = revenue_df.groupby("account_name").agg(
        amount=("credit", "sum")
    ).reset_index()
    return revenue_df

def get_expenses(df: pd.DataFrame) -> pd.DataFrame:
    '''Filters only Expense accounts and returns total debit per account.'''
    expense_df = df[df["account_type"] == "Expense"].copy()
    expense_df = expense_df.groupby("account_name").agg(
        amount=("debit", "sum")
    ).reset_index()
    return expense_df

def calculate_net_income(total_revenue: float, total_expenses: float) -> float:
    '''Calculates net income by subtracting total expenses from total revenue.'''
    return total_revenue - total_expenses
    
# ── Page Config ────────────────────────────────────────────────────
st.title("📈 Income Statement")
st.write("Auto-generated from your journal entries. Shows revenues, expenses, and net income.")

# ── Load data ──────────────────────────────────────────────────────
df = load_entries()

if df.empty:
    st.info("📭 No journal entries found. Please add transactions on the Journal Entries page first.")
else:
    # ── Get revenue and expenses ───────────────────────────────────
    revenue_df = get_revenue(df)
    expense_df = get_expenses(df)

    total_revenue = revenue_df["amount"].sum()
    total_expenses = expense_df["amount"].sum()
    net_income = calculate_net_income(total_revenue, total_expenses)

    # ── Display Income Statement ───────────────────────────────────
    st.subheader("📋 Income Statement")
    st.markdown("---")

    # Revenue section
    st.markdown("### 💰 Revenue")
    if revenue_df.empty:
        st.write("No revenue entries found.")
    else:
        for _, row in revenue_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(row["account_name"])
            with col2:
                st.write(f"${row['amount']:,.2f}")

    st.markdown(f"**Total Revenue: ${total_revenue:,.2f}**")
    st.markdown("---")

    # Expenses section
    st.markdown("### 💸 Expenses")
    if expense_df.empty:
        st.write("No expense entries found.")
    else:
        for _, row in expense_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(row["account_name"])
            with col2:
                st.write(f"${row['amount']:,.2f}")

    st.markdown(f"**Total Expenses: ${total_expenses:,.2f}**")
    st.markdown("---")

    # Net income section
    st.markdown("### 🏁 Net Income")
    if net_income >= 0:
        st.success(f"✅ Net Income: ${net_income:,.2f} — Your business is profitable!")
    else:
        st.error(f"❌ Net Loss: ${abs(net_income):,.2f} — Your expenses exceed your revenue.")

    # ── Metrics ───────────────────────────────────────────────────
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        st.metric("Total Expenses", f"${total_expenses:,.2f}")
    with col3:
        st.metric("Net Income", f"${net_income:,.2f}")

    # ── Chart ─────────────────────────────────────────────────────
    st.subheader("📊 Revenue vs Expenses Chart")

    # Combine revenue and expenses for chart
    chart_data = []
    for _, row in revenue_df.iterrows():
        chart_data.append({
            "Account": row["account_name"],
            "Amount": row["amount"],
            "Type": "Revenue"
        })
    for _, row in expense_df.iterrows():
        chart_data.append({
            "Account": row["account_name"],
            "Amount": row["amount"],
            "Type": "Expense"
        })

    chart_df = pd.DataFrame(chart_data)

    if not chart_df.empty:
        fig, ax = plt.subplots(figsize=(10, 5))

        colors = ["#4CAF50" if t == "Revenue" else "#F44336"
                  for t in chart_df["Type"]]

        ax.bar(chart_df["Account"], chart_df["Amount"], color=colors)
        ax.set_xlabel("Account")
        ax.set_ylabel("Amount ($)")
        ax.set_title("Revenue vs Expenses by Account")
        ax.set_xticklabels(chart_df["Account"], rotation=45, ha="right")

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="#4CAF50", label="Revenue"),
            Patch(facecolor="#F44336", label="Expense")
        ]
        ax.legend(handles=legend_elements)
        plt.tight_layout()
        st.pyplot(fig)