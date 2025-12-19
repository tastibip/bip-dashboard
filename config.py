import streamlit as st
import pandas as pd

# ===============================
# LOCAL EXCEL PATH
# ===============================
EXCEL_PATH = r"D:\Business Improvement Project 2025\New BIP Dash 2.4.xlsx"

# ===============================
# GLOBAL EXCEL LOADER (CACHED)
# ===============================
@st.cache_data(ttl=600)  # refresh tiap 10 menit
def load_excel(sheet_name=None, **kwargs):
    return pd.read_excel(
        EXCEL_PATH,
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
