import streamlit as st
import pandas as pd
from config import load_excel


def render():
    st.title("📑 Sheet Explorer")

    # =========================
    # LOAD ALL SHEETS (DICT)
    # =========================
    try:
        sheets = load_excel(sheet_name=None)
        sheet_names = list(sheets.keys())
    except Exception as e:
        st.error(f"Gagal membaca daftar sheet Excel: {e}")
        return

    selected_sheet = st.selectbox("Pilih Sheet Excel:", sheet_names)

    if not selected_sheet:
        return

    df = sheets[selected_sheet]

    st.caption(
        f"Sheet: **{selected_sheet}** | "
        f"Rows: **{df.shape[0]}** | "
        f"Columns: **{df.shape[1]}**"
    )

    MAX_ROWS = 3000
    st.info(f"Menampilkan {min(len(df), MAX_ROWS)} dari {len(df)} baris")

    df = df.copy()
    df.columns = df.columns.astype(str)

    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str)

    st.dataframe(
        df.head(MAX_ROWS),
        use_container_width=True,
        height=600
    )
