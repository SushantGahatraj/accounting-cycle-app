import os
import streamlit as st
import pandas as pd

# Simple, robust Income Statement page.
# Uses Streamlit native charts (st.bar_chart) to avoid matplotlib import/time issues.

APP_PATH = os.path.dirname(os.path.abspath(__file__))


def get_data_path(filename: str) -> str:
    return os.path.join(APP_PATH, "..", "data", filename)


def load_entries() -> pd.DataFrame:
    fp = get_data_path("journal_entries.csv")
    if os.path.exists(fp):
        df = pd.read_csv(fp)
        # Ensure numeric columns exist
        for col in ["debit", "credit"]:
            if col not in df.columns:
                df[col] = 0.0
        return df
    return pd.DataFrame()


def summarize_by_type(df: pd.DataFrame, account_type: str) -> pd.DataFrame:
    sub = df[df["account_type"] == account_type].copy()
    if sub.empty:
        return pd.DataFrame(columns=["account_name", "amount"])
    if account_type == "Revenue":
        grouped = sub.groupby("account_name").agg(amount=("credit", "sum")).reset_index()
    else:
        grouped = sub.groupby("account_name").agg(amount=("debit", "sum")).reset_index()
    return grouped


st.title("📈 Income Statement")
st.write("Auto-generated from your journal entries. Shows revenues, expenses, and net income.")

df = load_entries()

if df.empty:
    st.info("📭 No journal entries found. Please add transactions on the Journal Entries page first.")
else:
    revenue_df = summarize_by_type(df, "Revenue")
    expense_df = summarize_by_type(df, "Expense")

    total_revenue = float(revenue_df["amount"].sum()) if not revenue_df.empty else 0.0
    total_expenses = float(expense_df["amount"].sum()) if not expense_df.empty else 0.0
    net_income = total_revenue - total_expenses

    st.subheader("📋 Income Statement")
    st.markdown("---")

    st.markdown("### 💰 Revenue")
    if revenue_df.empty:
        st.write("No revenue entries found.")
    else:
        for _, r in revenue_df.iterrows():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(r["account_name"])
            with c2:
                st.write(f"${r['amount']:,.2f}")

    st.markdown(f"**Total Revenue: ${total_revenue:,.2f}**")
    st.markdown("---")

    st.markdown("### 💸 Expenses")
    if expense_df.empty:
        st.write("No expense entries found.")
    else:
        for _, r in expense_df.iterrows():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(r["account_name"])
            with c2:
                st.write(f"${r['amount']:,.2f}")

    st.markdown(f"**Total Expenses: ${total_expenses:,.2f}**")
    st.markdown("---")

    st.markdown("### 🏁 Net Income")
    if net_income >= 0:
        st.success(f"✅ Net Income: ${net_income:,.2f} — Your business is profitable!")
    else:
        st.error(f"❌ Net Loss: ${abs(net_income):,.2f} — Your expenses exceed your revenue.")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${total_revenue:,.2f}")
    c2.metric("Total Expenses", f"${total_expenses:,.2f}")
    c3.metric("Net Income", f"${net_income:,.2f}")

    # Chart: combine revenue & expenses and use Streamlit's charting
    st.subheader("📊 Revenue vs Expenses by Account")
    chart_rows = []
    for _, r in revenue_df.iterrows():
        chart_rows.append({"Account": r["account_name"], "Revenue": r["amount"], "Expense": 0.0})
    for _, r in expense_df.iterrows():
        # if account already present, add to Expense column
        found = next((row for row in chart_rows if row["Account"] == r["account_name"]), None)
        if found:
            found["Expense"] = r["amount"]
        else:
            chart_rows.append({"Account": r["account_name"], "Revenue": 0.0, "Expense": r["amount"]})

    chart_df = pd.DataFrame(chart_rows)
    if not chart_df.empty:
        chart_df = chart_df.set_index("Account")
        st.bar_chart(chart_df)