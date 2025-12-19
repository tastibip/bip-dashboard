import streamlit as st
import pandas as pd
from config import EXCEL_PATH, load_excel


def render():
    st.title("📑 Sheet Explorer")

    try:
        xls = pd.ExcelFile(EXCEL_PATH, engine="openpyxl")
        sheet_names = xls.sheet_names
    except Exception as e:
        st.error(f"Gagal membaca file Excel: {e}")
        return

    selected_sheet = st.selectbox("Pilih Sheet Excel:", sheet_names)

    if not selected_sheet:
        return

    try:
        df = load_excel(sheet_name=selected_sheet)
    except Exception as e:
        st.error(f"Gagal membaca sheet {selected_sheet}: {e}")
        return

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

