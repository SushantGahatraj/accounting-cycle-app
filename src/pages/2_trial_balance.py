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

def build_trial_balance(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Groups all journal entries by account name and account type.
    Sums up total debits and total credits for each account.
    Returns a trial balance DataFrame.
    '''
    # Group by account name and type, sum debits and credits
    trial_balance = df.groupby(
        ["account_name", "account_type"]
    ).agg(
        total_debit=("debit", "sum"),
        total_credit=("credit", "sum")
    ).reset_index()

    # Calculate net balance per account
    trial_balance["net_balance"] = (
        trial_balance["total_debit"] - trial_balance["total_credit"]
    )

    # Sort by account type for clean display
    type_order = ["Asset", "Liability", "Equity", "Revenue", "Expense"]
    trial_balance["account_type"] = pd.Categorical(
        trial_balance["account_type"],
        categories=type_order,
        ordered=True
    )
    trial_balance = trial_balance.sort_values("account_type")

    return trial_balance

def check_balance(df: pd.DataFrame) -> tuple:
    '''
    Checks if total debits equal total credits.
    Returns a tuple of (is_balanced, total_debits, total_credits).
    '''
    total_debits = df["debit"].sum()
    total_credits = df["credit"].sum()
    is_balanced = round(total_debits, 2) == round(total_credits, 2)
    return is_balanced, total_debits, total_credits

# ── Page Config ────────────────────────────────────────────────────
st.title("⚖️ Trial Balance")
st.write("Auto-generated from your journal entries. Shows total debits and credits per account.")

# ── Load data ──────────────────────────────────────────────────────
df = load_entries()

if df.empty:
    st.info("📭 No journal entries found. Please add transactions on the Journal Entries page first.")
else:
    # ── Check if balanced ──────────────────────────────────────────
    is_balanced, total_debits, total_credits = check_balance(df)

    if is_balanced:
        st.success(f"✅ The books are balanced! Total Debits = Total Credits = ${total_debits:,.2f}")
    else:
        st.error(f"❌ Not balanced! Total Debits: ${total_debits:,.2f} | Total Credits: ${total_credits:,.2f}")

    # ── Build and display trial balance ────────────────────────────
    trial_balance = build_trial_balance(df)

    st.subheader("📋 Trial Balance Table")

    # Format numbers as currency for display
    display_df = trial_balance.copy()
    display_df["total_debit"] = display_df["total_debit"].map(lambda x: f"${x:,.2f}")
    display_df["total_credit"] = display_df["total_credit"].map(lambda x: f"${x:,.2f}")
    display_df["net_balance"] = display_df["net_balance"].map(lambda x: f"${x:,.2f}")

    # Rename columns for clean display
    display_df.columns = ["Account Name", "Account Type", "Total Debit", "Total Credit", "Net Balance"]

    st.dataframe(display_df, use_container_width=True)

    # ── Totals row ─────────────────────────────────────────────────
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Debits", f"${total_debits:,.2f}")
    with col2:
        st.metric("Total Credits", f"${total_credits:,.2f}")
    with col3:
        difference = total_debits - total_credits
        st.metric("Difference", f"${difference:,.2f}")

      # ── Chart ──────────────────────────────────────────────────────
    st.subheader("📊 Debits vs Credits by Account")

    fig, ax = plt.subplots(figsize=(10, 5))

    accounts = trial_balance["account_name"]
    x = range(len(accounts))
    width = 0.35

    # Plot debit and credit bars side by side
    bars1 = ax.bar(
        [i - width/2 for i in x],
        trial_balance["total_debit"],
        width,
        label="Debit",
        color="#4CAF50"
    )
    bars2 = ax.bar(
        [i + width/2 for i in x],
        trial_balance["total_credit"],
        width,
        label="Credit",
        color="#2196F3"
    )

    ax.set_xlabel("Account")
    ax.set_ylabel("Amount ($)")
    ax.set_title("Trial Balance — Debits vs Credits per Account")
    ax.set_xticks(list(x))
    ax.set_xticklabels(accounts, rotation=45, ha="right")
    ax.legend()
    plt.tight_layout()

    st.pyplot(fig)