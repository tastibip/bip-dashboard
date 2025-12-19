import streamlit as st
import pandas as pd
from config import FILE_PATH


def render():
    st.title("📑 Sheet Explorer")

    try:
        xls = pd.ExcelFile(FILE_PATH)
        sheet_names = xls.sheet_names
    except Exception as e:
        st.error(f"Gagal membaca file Excel: {e}")
        return

    # pilih sheet
    selected_sheet = st.selectbox(
        "Pilih Sheet Excel:",
        sheet_names
    )

    if not selected_sheet:
        st.info("Silakan pilih sheet terlebih dahulu")
        return

    try:
        df = pd.read_excel(FILE_PATH, sheet_name=selected_sheet)
    except Exception as e:
        st.error(f"Gagal membaca sheet {selected_sheet}: {e}")
        return

    st.caption(
        f"Sheet: **{selected_sheet}** | "
        f"Rows: **{df.shape[0]}** | "
        f"Columns: **{df.shape[1]}**"
    )

    st.dataframe(
        df,
        use_container_width=True,
        height=600
    )
