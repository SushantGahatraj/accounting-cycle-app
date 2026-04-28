# accounting-cycle-app
A Streamlit app for accounting cycle simulation and financial statement generation
=================

Accounting Cycle Simulator
--------------------------

This is a small Streamlit app built for a college accounting class project. It lets you enter journal entries and view derived financial statements.

Running the app
---------------

1. Install dependencies (recommended to use a virtual environment):

```bash
python3 -m pip install --user -r requirements.txt
```

2. Run the Streamlit app:

```bash
streamlit run src/main.py
```

Pages
-----
- `1_journal_entries.py` — Form for entering journal entries and saving them to `src/data/journal_entries.csv`.

Notes
-----
- The project stores data as CSV files in `src/data/` so you can open and inspect them.
