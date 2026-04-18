from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import streamlit as st

st.set_page_config(page_title="QuickLoan Connect", page_icon="💳", layout="centered")

st.title("💳 QuickLoan Connect")
st.caption("Public loan request portal for multiple banks.")

st.markdown(
    """
Use this form to request a loan. After submission, the owner receives a notification
(via webhook) when configured.
"""
)

LOAN_TYPES = [
    "Personal Loan",
    "Home Loan",
    "Business Loan",
    "Car Loan",
    "Education Loan",
]

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
LEADS_FILE = DATA_DIR / "leads.csv"


def get_secret(name: str, default: str = "") -> str:
    return str(st.secrets.get(name, default)).strip()


def send_webhook(payload: dict[str, Any]) -> tuple[bool, str]:
    webhook_url = get_secret("NOTIFY_WEBHOOK_URL")
    if not webhook_url:
        return False, "NOTIFY_WEBHOOK_URL is not set in Streamlit secrets."

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if 200 <= response.status_code < 300:
            return True, "Webhook notification sent successfully."
        return False, f"Webhook returned HTTP {response.status_code}."
    except requests.RequestException as exc:
        return False, f"Webhook call failed: {exc}"


def persist_lead(payload: dict[str, Any]) -> None:
    headers = list(payload.keys())
    file_exists = LEADS_FILE.exists()

    with LEADS_FILE.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(payload)


with st.form("loan_form", clear_on_submit=True):
    full_name = st.text_input("Full Name *")

    col1, col2 = st.columns(2)
    with col1:
        phone = st.text_input("Phone Number *")
    with col2:
        email = st.text_input("Email *")

    col3, col4 = st.columns(2)
    with col3:
        loan_type = st.selectbox("Loan Type *", options=[""] + LOAN_TYPES)
    with col4:
        preferred_bank = st.text_input("Preferred Bank", placeholder="Any bank / specific bank")

    col5, col6 = st.columns(2)
    with col5:
        loan_amount = st.number_input("Loan Amount (USD) *", min_value=1000, step=100)
    with col6:
        monthly_income = st.number_input("Monthly Income (USD) *", min_value=0, step=100)

    notes = st.text_area("Notes", placeholder="Share any details useful for your loan request")
    consent = st.checkbox("I agree to be contacted regarding this loan request.")

    submitted = st.form_submit_button("Submit Request")

if submitted:
    required_errors = []
    if not full_name.strip():
        required_errors.append("Full Name")
    if not phone.strip():
        required_errors.append("Phone Number")
    if not email.strip():
        required_errors.append("Email")
    if not loan_type:
        required_errors.append("Loan Type")
    if not consent:
        required_errors.append("Consent")

    if required_errors:
        st.error(f"Please complete required fields: {', '.join(required_errors)}")
    else:
        payload = {
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "full_name": full_name.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "loan_type": loan_type,
            "preferred_bank": preferred_bank.strip() or "Any",
            "loan_amount": int(loan_amount),
            "monthly_income": int(monthly_income),
            "notes": notes.strip(),
            "consent": consent,
        }

        persist_lead(payload)
        ok, message = send_webhook(payload)

        if ok:
            st.success("Request submitted. Owner notification sent successfully.")
        else:
            st.warning(
                "Request submitted and saved locally, but live notification is not configured/failed. "
                f"Details: {message}"
            )

        with st.expander("View submitted payload"):
            st.code(json.dumps(payload, indent=2), language="json")

st.divider()
st.markdown(
    """
### Owner setup (required for notifications)
1. Add `NOTIFY_WEBHOOK_URL` in `.streamlit/secrets.toml`.
2. Connect that webhook to Zapier / Make / your backend.
3. Deploy this app from GitHub on Streamlit Community Cloud.
"""
)
