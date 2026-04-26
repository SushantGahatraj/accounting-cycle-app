import streamlit as st
import pandas as pd


def main():
    st.title("Accounting Cycle App — Demo")
    st.write("This is a minimal Streamlit app to verify Streamlit + pandas are working in this project.")

    df = pd.DataFrame(
        {
            "Account": ["Cash", "Revenue", "Expenses"],
            "Amount": [1000, 500, 200],
        }
    )

    st.subheader("Sample accounts table")
    st.table(df)


if __name__ == "__main__":
    main()