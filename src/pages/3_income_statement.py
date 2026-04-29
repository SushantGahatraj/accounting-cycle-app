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
    