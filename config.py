import streamlit as st
import pandas as pd
import requests
from pathlib import Path
import platform
import tempfile

# ===============================
# DETECT ENVIRONMENT (FIXED)
# ===============================
IS_CLOUD = platform.system() != "Windows"

# ===============================
# LOCAL WINDOWS PATH (DEV ONLY)
# ===============================
LOCAL_DEV_PATH = Path(
    r"D:\Business Improvement Project 2025\New BIP Dash 2.4.xlsx"
)

# ===============================
# GOOGLE DRIVE CONFIG (CLOUD)
# ===============================
FILE_ID = "1DDmALmveVKWYuu7pVhfafhcmC8rmkzII"
DOWNLOAD_URL = "https://drive.google.com/uc?export=download"
TMP_DIR = Path(tempfile.gettempdir())
CLOUD_PATH = TMP_DIR / "bip_data.xlsx"


# ===============================
# DOWNLOAD FOR CLOUD ONLY
# ===============================
@st.cache_resource
def download_excel_cloud():
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    if CLOUD_PATH.exists() and CLOUD_PATH.stat().st_size > 1_000_000:
        return CLOUD_PATH

    with st.spinner("📥 Downloading Excel from Google Drive..."):
        session = requests.Session()
        response = session.get(DOWNLOAD_URL, params={"id": FILE_ID}, stream=True)

        for k, v in response.cookies.items():
            if k.startswith("download_warning"):
                response = session.get(
                    DOWNLOAD_URL,
                    params={"id": FILE_ID, "confirm": v},
                    stream=True,
                )
                break

        if response.status_code != 200:
            raise RuntimeError("Failed to download file from Google Drive")

        with open(CLOUD_PATH, "wb") as f:
            for chunk in response.iter_content(65536):
                if chunk:
                    f.write(chunk)

    return CLOUD_PATH


# ===============================
# GLOBAL EXCEL LOADER
# ===============================
@st.cache_data(ttl=600)
def load_excel(sheet_name=None, **kwargs):
    if IS_CLOUD:
        path = download_excel_cloud()
    else:
        path = LOCAL_DEV_PATH
        if not path.exists():
            raise FileNotFoundError(f"Local Excel not found: {path}")

    return pd.read_excel(
        path,
        sheet_name=sheet_name,
        engine="openpyxl",
        **kwargs
    )


# ===============================
# SHEET NAMES
# ===============================
SHEET_NAME_REVKAB   = "RevbyKab"
SHEET_NAME_REVNAT   = "RevbyNat"
SHEET_NAME_REVPROV  = "RevbyProv"
SHEET_NAME_PNVAR    = "PN Varians"
SHEET_NAME_TOPPART  = "Top10Part"
