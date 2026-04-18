# QuickLoan Connect (Streamlit + GitHub)
This project is now implemented in **Streamlit** so you can host a public loan website directly from **GitHub**.
Users fill one loan form, and you receive notifications via webhook.
## Features
- Public loan request form (name, contact, loan type, bank preference, amount, income, notes, consent)
- Server-side lead capture to `data/leads.csv`
- Real-time owner notification via `NOTIFY_WEBHOOK_URL`
- Safe fallback: if webhook fails, lead is still saved locally
## Project files

- `app.py` - Streamlit app
- `requirements.txt` - Python dependencies
- `.streamlit/secrets.toml.example` - example secret config
## Run locally
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml with your real webhook URL
streamlit run app.py
```

## Deploy publicly with GitHub + Streamlit Cloud

1. Push this repo to GitHub.
2. Open [https://share.streamlit.io](https://share.streamlit.io).
3. Click **New app** and select your GitHub repo.
4. Set main file path to `app.py`.
5. In app settings, add secret:

```toml
NOTIFY_WEBHOOK_URL = "https://your-webhook-url"
```
6. Deploy. Your website becomes public with a URL like `https://your-app-name.streamlit.app`.

## Notification options

Use `NOTIFY_WEBHOOK_URL` with:

- Zapier Webhooks → Email/SMS/Slack
- Make.com Webhook → Gmail/Telegram/WhatsApp workflows
- Your own backend endpoint

## Notes

- `data/leads.csv` is local to runtime environment. For production persistence, connect to a database.
- Do not commit `.streamlit/secrets.toml` with real credentials.
