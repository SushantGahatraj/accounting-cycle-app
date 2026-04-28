import os
from datetime import date, datetime
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


def get_data_path(filename: str) -> str:
    """Return the absolute path to a data file inside src/data.

    We locate the repo `src` directory by taking the parent directory of
    this file (which lives in src/pages) and joining with `data`.
    """
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(src_dir, "data")
    # Ensure the data directory exists when saving later
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename)


def load_journal_entries(csv_path: str) -> pd.DataFrame:
    """Load journal entries from CSV if it exists, otherwise return an empty DataFrame.

    The returned DataFrame always has the expected columns so downstream code
    can rely on them.
    """
    columns = [
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
        # Return an empty DataFrame with correct columns and dtypes
        df = pd.DataFrame(columns=columns)
        # set dtypes for clarity
        df["entry_id"] = df["entry_id"].astype("Int64")
        df["debit"] = df["debit"].astype(float)
        df["credit"] = df["credit"].astype(float)
        return df

    df = pd.read_csv(csv_path)
    # If file exists but missing columns, try to adapt safely
    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA

    # Ensure types are sensible
    try:
        df["debit"] = df["debit"].fillna(0).astype(float)
        df["credit"] = df["credit"].fillna(0).astype(float)
    except Exception:
        # If conversion fails, coerce and replace invalids with 0.0
        df["debit"] = pd.to_numeric(df.get("debit", 0), errors="coerce").fillna(0.0)
        df["credit"] = pd.to_numeric(df.get("credit", 0), errors="coerce").fillna(0.0)

    return df[columns]


def save_journal_entries(df: pd.DataFrame, csv_path: str) -> None:
    """Save the provided DataFrame to CSV at csv_path.

    Overwrites any existing file. We don't include the pandas index in file.
    """
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)


def get_next_entry_id(df: pd.DataFrame) -> int:
    """Return the next integer entry_id to use when appending new rows.

    If the DataFrame is empty, start at 1.
    """
    if df.empty:
        return 1
    try:
        max_id = int(pd.to_numeric(df["entry_id"], errors="coerce").max())
        return max_id + 1
    except Exception:
        return 1


def append_entries(new_rows: List[Dict], csv_path: str) -> pd.DataFrame:
    """Append new_rows (list of dicts) to existing CSV and return the combined DataFrame.

    This function assigns increasing `entry_id` values to each new row.
    """
    existing = load_journal_entries(csv_path)
    next_id = get_next_entry_id(existing)

    # Create DataFrame for new rows and assign ids
    new_df = pd.DataFrame(new_rows)
    if new_df.empty:
        return existing

    new_df = new_df.copy()
    new_df["debit"] = pd.to_numeric(new_df.get("debit", 0), errors="coerce").fillna(0.0)
    new_df["credit"] = pd.to_numeric(new_df.get("credit", 0), errors="coerce").fillna(0.0)

    ids = list(range(next_id, next_id + len(new_df)))
    new_df["entry_id"] = ids

    combined = pd.concat([existing, new_df], ignore_index=True, sort=False)
    # Save back to CSV
    save_journal_entries(combined, csv_path)
    return combined


def create_transaction_id() -> str:
    """Create a readable transaction id using the current timestamp.

    Example: TX-2026-04-28T15:20:30
    """
    return f"TX-{datetime.now().isoformat(timespec='seconds')}"


def add_line_to_session(line: Dict) -> None:
    """Add a single journal line (dict) to Streamlit session_state temporary list.

    Initializes session_state['transaction_lines'] when needed.
    """
    if "transaction_lines" not in st.session_state:
        st.session_state["transaction_lines"] = []
    st.session_state["transaction_lines"].append(line)


def validate_transaction_lines(lines: List[Dict]) -> Tuple[bool, str]:
    """Validate a list of journal lines for one transaction.

    Rules implemented:
    - At least one line
    - Each line must have exactly one of debit or credit > 0
    - Debit and credit must be non-negative
    - Total debits must equal total credits within a small tolerance

    Returns (is_valid, message). Message is empty when valid.
    """
    if not lines:
        return False, "No lines in the transaction. Add at least one line."

    total_debit = 0.0
    total_credit = 0.0

    for i, line in enumerate(lines, start=1):
        try:
            debit = float(line.get("debit", 0) or 0)
            credit = float(line.get("credit", 0) or 0)
        except Exception:
            return False, f"Line {i}: Debit and Credit must be numbers."

        if debit < 0 or credit < 0:
            return False, f"Line {i}: Debit and Credit must be non-negative."

        # Exactly one should be positive
        if not ((debit > 0 and credit == 0) or (credit > 0 and debit == 0)):
            return False, f"Line {i}: Exactly one of Debit or Credit must be greater than 0."

        total_debit += debit
        total_credit += credit

    # Use a small tolerance for floating point rounding
    if abs(total_debit - total_credit) > 0.01:
        return False, f"Transaction not balanced: Debits = {total_debit:.2f}, Credits = {total_credit:.2f}."

    return True, ""


def delete_entries_by_ids(df: pd.DataFrame, ids: List[int], csv_path: str) -> pd.DataFrame:
    """Delete rows whose entry_id is in ids, save CSV, and return updated DataFrame.
    """
    if not ids:
        return df
    # Ensure entry_id column numeric for comparison
    df = df.copy()
    df["entry_id"] = pd.to_numeric(df["entry_id"], errors="coerce").astype(pd.Int64Dtype())
    remaining = df[~df["entry_id"].isin(ids)].reset_index(drop=True)
    save_journal_entries(remaining, csv_path)
    return remaining


### Streamlit page layout and interaction

st.title("📝 Journal Entries")
st.write("Create and manage journal entry lines. Transactions must balance (total debits = total credits).")

CSV_PATH = get_data_path("journal_entries.csv")


def _show_saved_entries_section():
    """Show saved journal entries and provide a delete interface."""
    df = load_journal_entries(CSV_PATH)

    if df.empty:
        st.info("No journal entries saved yet. Add some using the form on the left.")
        return df

    st.subheader("Saved Journal Entries")
    # Display a friendly dataframe view
    display_df = df.copy()
    # Format numeric columns
    display_df["debit"] = display_df["debit"].map(lambda x: f"{x:.2f}")
    display_df["credit"] = display_df["credit"].map(lambda x: f"{x:.2f}")

    st.dataframe(display_df)

    # Allow user to select entry_ids to delete
    try:
        entry_ids = list(pd.to_numeric(df["entry_id"], errors="coerce").dropna().astype(int))
    except Exception:
        entry_ids = []

    selected = st.multiselect("Select entries to delete (by entry_id)", options=entry_ids)
    if selected:
        if st.button("Delete selected entries"):
            remaining = delete_entries_by_ids(df, selected, CSV_PATH)
            st.success(f"Deleted {len(selected)} entries.")
            st.experimental_rerun()

    return df


def _show_transaction_form():
    """Show form to build a single transaction made of multiple journal lines."""
    st.subheader("Build a Transaction")

    # Initialize session state container for temporary lines
    if "transaction_lines" not in st.session_state:
        st.session_state["transaction_lines"] = []

    # Layout: left column small for form controls
    with st.form(key="line_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            tx_date = st.date_input("Date", value=date.today())
            # Use a multi-line text area for the description so the user has more room
            # to enter longer journal entry descriptions. Height is in pixels.
            description = st.text_area("Description", value="", height=120)

        with col2:
            account_name = st.text_input("Account name", value="Cash")
            account_type = st.selectbox(
                "Account type",
                options=["Asset", "Liability", "Equity", "Revenue", "Expense"],
            )

        debit = st.number_input("Debit", min_value=0.0, value=0.0, format="%.2f")
        credit = st.number_input("Credit", min_value=0.0, value=0.0, format="%.2f")

        add_line = st.form_submit_button("Add line to current transaction")

    if add_line:
        # Validate the single line before appending to temp transaction
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

    # Show current temporary transaction lines
    st.markdown("**Current transaction lines (unsaved)**")
    temp_lines = st.session_state.get("transaction_lines", [])
    if temp_lines:
        temp_df = pd.DataFrame(temp_lines)
        # Show formatted numbers
        temp_df["debit"] = temp_df["debit"].map(lambda x: f"{float(x):.2f}")
        temp_df["credit"] = temp_df["credit"].map(lambda x: f"{float(x):.2f}")
        st.table(temp_df)
    else:
        st.write("No lines added yet.")

    # Show totals and save/cancel buttons
    total_debit = sum(float(l.get("debit", 0) or 0) for l in temp_lines)
    total_credit = sum(float(l.get("credit", 0) or 0) for l in temp_lines)

    st.write(f"Total debits: {total_debit:.2f} — Total credits: {total_credit:.2f}")

    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("Save transaction"):
            ok, message = validate_transaction_lines(temp_lines)
            if not ok:
                st.error(message)
            else:
                tx_id = create_transaction_id()
                # Attach transaction_id to each line and append
                rows_to_save = []
                for line in temp_lines:
                    row = {
                        "transaction_id": tx_id,
                        "date": line.get("date"),
                        "description": line.get("description"),
                        "account_name": line.get("account_name"),
                        "account_type": line.get("account_type"),
                        "debit": float(line.get("debit", 0) or 0),
                        "credit": float(line.get("credit", 0) or 0),
                    }
                    rows_to_save.append(row)

                combined = append_entries(rows_to_save, CSV_PATH)
                st.success(f"Transaction saved with id {tx_id}. {len(rows_to_save)} lines added.")
                # Clear temporary lines and refresh page to show saved table
                st.session_state["transaction_lines"] = []
                st.experimental_rerun()

    with col_cancel:
        if st.button("Clear current transaction"):
            st.session_state["transaction_lines"] = []
            st.info("Cleared the current unsaved transaction lines.")


def main():
    """Main function to render the page sections."""
    left_col, right_col = st.columns([2, 3])

    with left_col:
        _show_transaction_form()

    with right_col:
        _show_saved_entries_section()


if __name__ == "__main__":
    # When run directly, call main() so we can also test the file outside Streamlit
    main()
