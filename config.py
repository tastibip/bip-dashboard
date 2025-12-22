import streamlit as st
import pandas as pd

EXCEL_URL = (
    "https://tastiid-my.sharepoint.com/personal/"
    "hermanudin_hermanudin_tasti_id/"
    "_layouts/15/download.aspx"
    "?UniqueId=460d1000-8d20-43ee-9c03-e05b587f7d32"
)

@st.cache_data(ttl=600)
def load_excel(sheet_name=None, **kwargs):
    return pd.read_excel(
        EXCEL_URL,
        sheet_name=sheet_name,
        engine="openpyxl",
        **kwargs
    )

SHEET_NAME_REVKAB   = "RevbyKab"
SHEET_NAME_REVNAT   = "RevbyNat"
SHEET_NAME_REVPROV  = "RevbyProv"
SHEET_NAME_PNVAR    = "PN Varians"
SHEET_NAME_TOPPART  = "Top10Part"
