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
    return 

