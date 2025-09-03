import streamlit as st
import requests
import pandas as pd
import json
import hashlib

st.title("💳 Transaction Downloader (No Selenium)")

# --- Step 1: User login ---
st.subheader("Login")
email = st.text_input("Email", value="Sliner.int@gmail.com")
password = st.text_input("Password", type="password")

if st.button("Login"):
    # Hash the password (MD5)
    password_hash = hashlib.md5(password.encode()).hexdigest()

    login_url = "https://sg.lianlianglobal.com/cb-va-sso-api/login?t=73189"
    payload = {"loginName": email, "password": password_hash}
    headers = {"Content-Type": "application/json"}

    resp = requests.post(login_url, headers=headers, data=json.dumps(payload))
    if resp.status_code == 200:
        data = resp.json()
        if data.get("success") and "data" in data:
            st.session_state.token = data["data"]["token"]
            st.success("✅ Logged in successfully!")
        else:
            st.error(f"❌ Login failed: {data}")
    else:
        st.error(f"⚠️ Request failed: {resp.status_code}")

# --- Step 2: Date range selection ---
st.subheader("Select Date Range")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

# --- Step 3: Download transactions ---
if st.button("Download Transactions"):
    if "token" not in st.session_state:
        st.error("⚠️ Please login first!")
    else:
        url = "https://sg.lianlianglobal.com/cb-ew-biz-gateway/transaction/search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": st.session_state.token,  # 👈 use token here
        }

        all_records = []
        page = 1
        page_size = 500

        while True:
            payload = {
                "pageNo": page,
                "pageSize": page_size,
                "startDate": str(start_date),
                "endDate": str(end_date),
            }

            resp = requests.post(url, headers=headers, data=json.dumps(payload))
            if resp.status_code != 200:
                st.error(f"Request failed: {resp.status_code} → {resp.text}")
                break

            data = resp.json()

            if data.get("success") and "model" in data and "resultList" in data["model"]:
                records = data["model"]["resultList"]
                if not records:
                    break
                all_records.extend(records)

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
