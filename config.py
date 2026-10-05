# IMPORTANT:
# For GitHub/Streamlit Cloud, do NOT commit a real API key.
# Put the key in Streamlit Secrets instead.
#
# If you insist on local hard-coded configuration, replace the placeholder below.
# The code also reads environment variables so deployment can stay secure.

import os

APP_NAME = "AI CNC Programming Copilot"

# User-requested hard-coded configuration placeholder.
# Replace only locally if you understand the security risk.
API_KEY = os.getenv("GPT_API_KEY", "PASTE_YOUR_API_KEY_HERE")

# GPT-120B-compatible OpenAI-style endpoint.
# Set this to the provider's actual endpoint.
BASE_URL = os.getenv("GPT_BASE_URL", "https://YOUR_PROVIDER/v1")
MODEL_NAME = os.getenv("GPT_MODEL", "gpt-120b")

def get_api_key():
    # Streamlit Secrets takes priority when available.
    try:
        import streamlit as st
        if "GPT_API_KEY" in st.secrets:
            return st.secrets["GPT_API_KEY"]
    except Exception:
        pass
    return API_KEY
