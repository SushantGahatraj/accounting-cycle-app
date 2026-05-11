# 📊 Accounting Cycle Simulator

A data-driven web application built with Python and Streamlit that simulates the full accounting cycle for small businesses and accounting students.



## App Description

The Accounting Cycle Simulator allows users to record financial transactions
as journal entries and automatically generates key financial statements and
ratios. It is designed as both a learning tool for accounting students and a practical bookkeeping tool for small businesses.

##  How to Run

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- pip

### Install dependencies
```bash
pip install streamlit pandas matplotlib
```

### Run the app
streamlit run dist/main.py

## How to Use the App

### Step 1 — Add Journal Entries
- Navigate to the **Journal Entries** page from the sidebar
- Fill in the date and description for your transaction
- Add each line of the transaction (account name, account type, debit or credit amount)
- Click **"Add line to current transaction"** for each line
- Make sure total debits = total credits before saving
- Click **"Save transaction"** to save

### Step 2 — View Financial Statements
All financial statements are automatically generated from your saved journal entries:
- **Trial Balance** — See total debits and credits per account
- **Income Statement** — See your revenues, expenses, and net income
- **Balance Sheet** — See your assets, liabilities, and equity
- **Cash Flow Statement** — See all cash inflows and outflows

### Step 3 — Check Financial Health
- Navigate to the **Financial Ratio Dashboard**
- View automatically calculated ratios with green/yellow/red health indicators

### Account Types
When entering journal entries, use these account types:
| Account Type | Examples |
|-------------|---------|
| Asset | Cash, Equipment, Accounts Receivable |
| Liability | Loans Payable, Accounts Payable |
| Equity | Owner's Equity, Retained Earnings |
| Revenue | Service Revenue, Sales Revenue |
| Expense | Rent Expense, Salary Expense |

### Golden Rule
Total Debits must ALWAYS equal Total Credits



## File Structure
```
accounting-cycle-app/
├── README.md                        # This file
├── demo.mp4                         # App demo video
├── src/                             # Development folder
│   ├── main.py                      # Home page of the app
│   ├── data/                        # Data folder
│   │   └── journal_entries.csv      # Saved journal entries
│   └── pages/                       # App pages
│       ├── 1_journal_entries.py     # Journal entry form
│       ├── 2_trial_balance.py       # Trial balance generator
│       ├── 3_income_statement.py    # Income statement generator
│       ├── 4_balance_sheet.py       # Balance sheet generator
│       ├── 5_cash_flow.py           # Cash flow statement
│       └── 6_ratio_dashboard.py     # Financial ratio dashboard
└── dist/                            # Production folder (graded)
├── main.py                      # Stable version of main.py
├── data/                        # Stable data files
└── pages/                       # Stable versions of all pages

```

## ✨ Features

- **Journal Entry System** — Enter multi-line transactions with
  debit/credit validation
- **Trial Balance** — Auto-generated with balance verification
- **Income Statement** — Revenue vs expenses with net income calculation
- **Balance Sheet** — Assets = Liabilities + Equity verification
- **Cash Flow Statement** — Tracks all cash inflows and outflows
- **Financial Ratio Dashboard** — 4 key ratios with health indicators:
  - Current Ratio
  - Net Profit Margin
  - Return on Assets
  - Debt to Equity Ratio
- **Save/Load** — All data persists in CSV format between sessions
- **Delete Entries** — Remove incorrect entries by ID



## AI Usage Statement

This project used AI (GitHub Copilot and Claude by Anthropic) in the
following ways:
- Helping debug specific errors in the code
- Suggesting improvements to validation logic
- Generating docstrings and comments for functions
- Helping structure the README documentation

