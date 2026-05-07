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