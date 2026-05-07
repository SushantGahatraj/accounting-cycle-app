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