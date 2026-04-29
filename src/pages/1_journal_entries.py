"""Journal Entries Streamlit page.

Clean, single-page implementation. Streamlit imports page modules and runs
their top-level code — so we call `main()` at import time (no __main__ guard).
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


def _show_transaction_form():
    st.subheader("Build a Transaction")
    if "transaction_lines" not in st.session_state:
        st.session_state["transaction_lines"] = []
    with st.form(key="line_form"):
        col1, col2 = st.columns([4, 1])
        with col1:
            tx_date = st.date_input("Date", value=date.today())
            description = st.text_area("Description", value="", height=220)
        with col2:
            account_name = st.text_input("Account name", value="Cash")
            account_type = st.selectbox("Account type", ["Asset", "Liability", "Equity", "Revenue", "Expense"])
        debit = st.number_input("Debit", min_value=0.0, value=0.0, format="%.2f")
        credit = st.number_input("Credit", min_value=0.0, value=0.0, format="%.2f")
        add_line = st.form_submit_button("Add line to current transaction")
    if add_line:
        line = {
            "date": tx_date.isoformat(),
            "description": description,
            "account_name": account_name.strip(),
            "account_type": account_type,
            "debit": float(debit),
            "credit": float(credit),
        }
        ok, message = validate_transaction_lines([line])
        if not ok:
            st.error(message)
        else:
            add_line_to_session(line)
            st.success("Line added to the transaction (not yet saved).")
    st.markdown("**Current transaction lines (unsaved)**")
    temp_lines = st.session_state.get("transaction_lines", [])
    if temp_lines:
        tdf = pd.DataFrame(temp_lines)
        tdf["debit"] = tdf["debit"].map(lambda x: f"{float(x):.2f}")
        tdf["credit"] = tdf["credit"].map(lambda x: f"{float(x):.2f}")
        st.dataframe(tdf, use_container_width=True)
    else:
        st.write("No lines added yet.")
    total_d = sum(float(l.get("debit", 0) or 0) for l in temp_lines)
    total_c = sum(float(l.get("credit", 0) or 0) for l in temp_lines)
    st.write(f"Total debits: {total_d:.2f} — Total credits: {total_c:.2f}")
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save transaction"):
            ok, message = validate_transaction_lines(temp_lines)
            if not ok:
                st.error(message)
            else:
                tx_id = create_transaction_id()
                rows = []
                for ln in temp_lines:
                    rows.append({
                        "transaction_id": tx_id,
                        "date": ln.get("date"),
                        "description": ln.get("description"),
                        "account_name": ln.get("account_name"),
                        "account_type": ln.get("account_type"),
                        "debit": float(ln.get("debit", 0) or 0),
                        "credit": float(ln.get("credit", 0) or 0),
                    })
                append_entries(rows, CSV_PATH)
                st.success(f"Transaction saved with id {tx_id}. {len(rows)} lines added.")
                st.session_state["transaction_lines"] = []
                st.experimental_rerun()
    with col_cancel:
        if st.button("Clear current transaction"):
            st.session_state["transaction_lines"] = []
            st.info("Cleared the current unsaved transaction lines.")


def _show_saved_entries_section():
    df = load_journal_entries(CSV_PATH)
    if df.empty:
        st.info("No journal entries saved yet. Add some using the form on the left.")
        return df
    st.subheader("Saved Journal Entries")
    disp = df.copy()
    disp["debit"] = disp["debit"].map(lambda x: f"{x:.2f}")
    disp["credit"] = disp["credit"].map(lambda x: f"{x:.2f}")
    st.dataframe(disp, use_container_width=True)
    try:
        ids = list(pd.to_numeric(df["entry_id"], errors="coerce").dropna().astype(int))
    except Exception:
        ids = []
    selected = st.multiselect("Select entries to delete (by entry_id)", options=ids)
    if selected and st.button("Delete selected entries"):
        remaining = delete_entries_by_ids(df, selected, CSV_PATH)
        st.success(f"Deleted {len(selected)} entries.")
        st.experimental_rerun()
    return df


def main():
    st.title("📝 Journal Entries")
    st.write("Create and manage journal entry lines. Transactions must balance (total debits = total credits).")
    left_col, right_col = st.columns([4, 2])
    with left_col:
        _show_transaction_form()
    with right_col:
        _show_saved_entries_section()


# Run at import time so Streamlit will render this page when it imports the module.
main()