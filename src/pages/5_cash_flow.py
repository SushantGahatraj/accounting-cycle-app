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

def get_cash_entries(df: pd.DataFrame) -> pd.DataFrame:
    '''Filters only Cash account entries and calculates net cash flow.'''
    cash_df = df[df["account_name"].str.lower() == "cash"].copy()
    cash_df["net_cash"] = cash_df["debit"] - cash_df["credit"]
    cash_df["flow_type"] = cash_df["net_cash"].apply(
        lambda x: "Inflow" if x > 0 else "Outflow"
    )
    return cash_df
#  Page Configuration
st.title("💵 Cash Flow Statement")
st.write("Auto-generated from your journal entries. Tracks all cash inflows and outflows.")

#  Load data 
df = load_entries()

if df.empty:
    st.info("📭 No journal entries found. Please add transactions on the Journal Entries page first.")
else:
    cash_df = get_cash_entries(df)

    if cash_df.empty:
        st.info("No Cash account entries found. Make sure to use 'Cash' as account name.")
    else:
        #  Split inflows and outflows 
        inflows = cash_df[cash_df["flow_type"] == "Inflow"]
        outflows = cash_df[cash_df["flow_type"] == "Outflow"]

        total_inflows = inflows["net_cash"].sum()
        total_outflows = abs(outflows["net_cash"].sum())
        net_cash = total_inflows - total_outflows

        #  Display Cash Flow Statement 
        st.subheader("📋 Cash Flow Statement")
        st.markdown("---")

        # Inflows
        st.markdown("### 💚 Cash Inflows")
        if inflows.empty:
            st.write("No cash inflows found.")
        else:
            for _, row in inflows.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(row["description"])
                with col2:
                    st.write(f"+${row['net_cash']:,.2f}")
        st.markdown(f"**Total Inflows: ${total_inflows:,.2f}**")
        st.markdown("---")

        # Outflows
        st.markdown("### 🔴 Cash Outflows")
        if outflows.empty:
            st.write("No cash outflows found.")
        else:
            for _, row in outflows.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(row["description"])
                with col2:
                    st.write(f"-${abs(row['net_cash']):,.2f}")
        st.markdown(f"**Total Outflows: ${total_outflows:,.2f}**")
        st.markdown("---")

        # Net cash position
        st.markdown("### 🏁 Net Cash Position")
        if net_cash >= 0:
            st.success(f"✅ Net Cash: ${net_cash:,.2f} — Positive cash position!")
        else:
            st.error(f"❌ Net Cash: ${abs(net_cash):,.2f} — Negative cash position!")

        #  Metrics 
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Inflows", f"${total_inflows:,.2f}")
        with col2:
            st.metric("Total Outflows", f"${total_outflows:,.2f}")
        with col3:
            st.metric("Net Cash", f"${net_cash:,.2f}")

        #  Chart 
        st.subheader("📊 Cash Flow Chart")

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(
            ["Total Inflows", "Total Outflows", "Net Cash"],
            [total_inflows, total_outflows, net_cash],
            color=["#4CAF50", "#F44336",
                   "#4CAF50" if net_cash >= 0 else "#F44336"]
        )
        ax.set_ylabel("Amount ($)")
        ax.set_title("Cash Flow Summary")
        plt.tight_layout()
        st.pyplot(fig)
