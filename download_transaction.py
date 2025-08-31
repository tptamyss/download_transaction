import streamlit as st
from selenium import webdriver
import requests
import json
import pandas as pd

st.title("💳 Transaction Downloader")

# Keep driver in Streamlit session state
if "driver" not in st.session_state:
    st.session_state.driver = None

# Step 1: Open login page
if st.button("Open Login Page"):
    st.write("Launching Chrome... Please log in manually.")
    st.session_state.driver = webdriver.Chrome()
    st.session_state.driver.get("https://sg.lianlianglobal.com/login")  # replace with actual login URL
    st.success("Browser launched! Please log in, then return here.")

# Step 2: Date input
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

# Step 3: Download transactions
if st.button("Download Transactions"):
    driver = st.session_state.driver
    if driver is None:
        st.error("⚠️ Please open the login page and log in first!")
    else:
        st.write("Grabbing cookies...")

        # Grab cookies from Selenium
        cookies = driver.get_cookies()
        cookie_dict = {c['name']: c['value'] for c in cookies}

        # Use cookies with requests
        session = requests.Session()
        for name, value in cookie_dict.items():
            session.cookies.set(name, value)

        url = "https://sg.lianlianglobal.com/cb-ew-biz-gateway/transaction/search"
        headers = {"Content-Type": "application/json"}

        all_records = []
        page = 1
        page_size = 500

        while True:
            payload = {
                "pageNo": page,
                "pageSize": page_size,
                "startDate": str(start_date),
                "endDate": str(end_date)
            }

            resp = session.post(url, headers=headers, data=json.dumps(payload))

            if resp.status_code != 200:
                st.error(f"Request failed: {resp.status_code} → {resp.text}")
                break

            data = resp.json()

            if data.get("success", False) and "model" in data and "resultList" in data["model"]:
                records = data["model"]["resultList"]
                if not records:  # no more results
                    break
                all_records.extend(records)

                # if less than page_size → last page
                if len(records) < page_size:
                    break
                page += 1
            else:
                st.error(f"API did not return transactions. Full response: {data}")
                break

        if all_records:
            df = pd.DataFrame(all_records)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"transactions_{start_date}_{end_date}.csv",
                mime="text/csv",
            )
            st.success(f"Downloaded {len(df)} records ✅")
        else:
            st.warning("⚠️ No transactions found for the selected date range.")
