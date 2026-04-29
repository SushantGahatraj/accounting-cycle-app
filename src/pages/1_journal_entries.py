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

def create_transaction_id() -> str:
   return f"TX-{datetime.now().isoformat(timespec='seconds')}"

def add_line_to_session(line: Dict) -> None:
   if "transaction_lines" not in st.session_state:
       st.session_state["transaction_lines"] = []
   st.session_state["transaction_lines"].append(line)

def validate_transaction_lines(lines: List[Dict]) -> Tuple[bool, str]:
   if not lines:
       return False, "No lines in the transaction. Add at least one line."
   total_d = 0.0
   total_c = 0.0
   for i, ln in enumerate(lines, start=1):
       try:
           d = float(ln.get("debit", 0) or 0)
           c = float(ln.get("credit", 0) or 0)
       except Exception:
           return False, f"Line {i}: Debit and Credit must be numbers."
       if d < 0 or c < 0:
           return False, f"Line {i}: Debit and Credit must be non-negative."
       if not ((d > 0 and c == 0) or (c > 0 and d == 0)):
           return False, f"Line {i}: Exactly one of Debit or Credit must be greater than 0."
       total_d += d
       total_c += c
   if abs(total_d - total_c) > 0.01:
       return False, f"Transaction not balanced: Debits = {total_d:.2f}, Credits = {total_c:.2f}."
   return True, ""

def delete_entries_by_ids(df: pd.DataFrame, ids: List[int], csv_path: str) -> pd.DataFrame:
   if not ids:
       return df
   df2 = df.copy()
   df2["entry_id"] = pd.to_numeric(df2["entry_id"], errors="coerce").astype(pd.Int64Dtype())
   remaining = df2[~df2["entry_id"].isin(ids)].reset_index(drop=True)
   save_journal_entries(remaining, csv_path)
   return remaining




