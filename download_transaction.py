import streamlit as st
import pandas as pd
import requests as rq
from datetime import datetime

st.title("📥 Transaction Downloader")

# --- User input ---
username = st.text_input("Username")
password = st.text_input("Password", type="password")
start_date = st.date_input("Start date", datetime(2020, 1, 1))
end_date = st.date_input("End date", datetime.today())

if st.button("Download Transactions"):
    try:
        # --- Convert dates to timestamp (ms) ---
        start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
        end_ts = int(datetime.combine(end_date, datetime.max.time()).timestamp() * 1000)

        # --- API endpoints (replace with yours) ---
        login_url = "https://example.com/api/login"
        tx_url = "https://example.com/api/transaction/download"

        # --- Login ---
        session = rq.Session()
        payload = {
            "loginName": username,
            "password": password
        }
        login_res = session.post(login_url, json=payload).json()

        if not login_res.get("success"):
            st.error("❌ Login failed, please check credentials.")
        else:
            # --- Fetch transactions ---
            params = {
                "dateStart": start_ts,
                "dateEnd": end_ts,
                "pageNo": 1,
                "pageSize": 1000
            }
            tx_res = session.post(tx_url, json=params).json()

            if not tx_res.get("success"):
                st.error("❌ Failed to fetch transactions. Please check the date range.")
            else:
                records = tx_res["model"]["resultList"]

                if not records:
                    st.warning("No transactions found for this period.")
                else:
                    # --- Turn into DataFrame ---
                    df = pd.DataFrame(records)
                    st.dataframe(df)

                    # --- Download as CSV ---
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download CSV", csv, "transactions.csv", "text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
