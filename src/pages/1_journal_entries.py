"""Journal Entries Streamlit page.
"""

import os
from datetime import date, datetime
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


def _data_path(filename: str) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(root, "data")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, filename)


CSV_PATH = _data_path("journal_entries.csv")


def load_journal_entries(csv_path: str) -> pd.DataFrame:
    cols = [
        "entry_id",
        "transaction_id",
        "date",
        "description",
        "account_name",
        "account_type",
        "debit",
        "credit",
    ]
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=cols)
        df["entry_id"] = df["entry_id"].astype("Int64")
        df["debit"] = df["debit"].astype(float)
        df["credit"] = df["credit"].astype(float)
        return df
    df = pd.read_csv(csv_path)
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    df["debit"] = pd.to_numeric(df.get("debit", 0), errors="coerce").fillna(0.0)
    df["credit"] = pd.to_numeric(df.get("credit", 0), errors="coerce").fillna(0.0)
    return df[cols]



