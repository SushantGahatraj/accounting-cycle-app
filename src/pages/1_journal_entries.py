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

def save_journal_entries(df: pd.DataFrame, csv_path: str) -> None:
   os.makedirs(os.path.dirname(csv_path), exist_ok=True)
   df.to_csv(csv_path, index=False)

def _next_entry_id(df: pd.DataFrame) -> int:
   if df.empty:
       return 1
   v = pd.to_numeric(df["entry_id"], errors="coerce").max()
   if pd.isna(v):
       return 1
   return int(v) + 1

def append_entries(new_rows: List[Dict], csv_path: str) -> pd.DataFrame:
   existing = load_journal_entries(csv_path)
   nid = _next_entry_id(existing)
   new_df = pd.DataFrame(new_rows)
   if new_df.empty:
       return existing
   new_df = new_df.copy()
   new_df["debit"] = pd.to_numeric(new_df.get("debit", 0), errors="coerce").fillna(0.0)
   new_df["credit"] = pd.to_numeric(new_df.get("credit", 0), errors="coerce").fillna(0.0)
   new_df["entry_id"] = list(range(nid, nid + len(new_df)))
   combined = pd.concat([existing, new_df], ignore_index=True, sort=False)
   save_journal_entries(combined, csv_path)
   return combined


