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

DOWNLOAD_URL = (
    "https://drive.usercontent.google.com/download"
)

TMP_DIR = Path(tempfile.gettempdir())
CLOUD_PATH = TMP_DIR / "New BIP Dash 2.4.xlsx"

# ===============================
# DOWNLOAD FOR CLOUD ONLY
# ===============================
@st.cache_resource
def download_excel_cloud():
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    if CLOUD_PATH.exists() and CLOUD_PATH.stat().st_size > 1_000_000:
        return CLOUD_PATH

    with st.spinner("📥 Downloading Excel from Google Drive..."):
        r = requests.get(
            DOWNLOAD_URL,
            params={
                "id": FILE_ID,
                "export": "download",
                "confirm": "t"
            },
            stream=True,
            timeout=120
        )

        if r.status_code != 200:
            raise RuntimeError(f"Download failed ({r.status_code})")

        # 🔥 VALIDASI MIME TYPE
        content_type = r.headers.get("Content-Type", "")
        if "text/html" in content_type.lower():
            raise RuntimeError(
                "Google Drive returned HTML, not Excel. "
                "Check sharing permission (must be Anyone with link → Viewer)"
            )

        with open(CLOUD_PATH, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
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
