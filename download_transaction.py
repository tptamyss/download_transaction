import streamlit as st
import requests
import json
import pandas as pd

st.title("💳 Transaction Downloader (No Selenium)")

# Keep session in Streamlit
if "session" not in st.session_state:
    st.session_state.session = None

# Step 1: Login
st.subheader("🔐 Login")
email = st.text_input("Email")
password = st.text_input("Password (hashed or plain depending on API)", type="password")

if st.button("Login"):
    url = "https://sg.lianlianglobal.com/cb-va-sso-api/login?t=83935"

    payload = {
        "loginName": email,
        "password": password
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://sg.lianlianglobal.com",
        "referer": "https://sg.lianlianglobal.com/login",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        "bizsource": "SG_WALLET",
        "bpentityid": "202202251000001",
        "request-source": "wallet",
        "devicedata": "eyJvc05hbWUiOiJtYWNPUyIsIm9zVmVyc2lvbiI6IjEwLjE1LjciLCJkZXZpY2VNYW51ZmFjdHVyZXIiOiJNaWNyb3NvZnQgRWRnZSIsImRldmljZU1vZGVsIjoiMTM5LjAuMC4wIiwidGltZVpvbmUiOiJBc2lhL1NhaWdvbiIsImRldmljZUlkIjoiNDEzOGEzNTlhYTZhZDFkZmU1NDI5M2IxOTgwYTBjNmQifQ=="
    }

    session = requests.Session()
    resp = session.post(url, headers=headers, data=json.dumps(payload))

    try:
        result = resp.json()
    except Exception:
        st.error("❌ Could not parse server response.")
        st.stop()

    if result.get("success"):
        st.session_state.session = session
        st.success("✅ Login successful!")
    else:
        st.error(f"❌ Login failed: {result}")

# Step 2: Download Transactions
if st.session_state.session:
    st.subheader("📅 Download Transactions")

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Fetch Transactions"):
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

            resp = st.session_state.session.post(url, headers=headers, data=json.dumps(payload))

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
                st.error(f"⚠️ API error: {data}")
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
            st.success(f"✅ Downloaded {len(df)} records")
        else:
            st.warning("⚠️ No transactions found for the selected range.")
