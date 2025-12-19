import streamlit as st
from pages import summary
from pages import direct_tasti
from pages import top_ten_part
from pages import sheet_explorer

st.set_page_config(page_title="BIP Dashboard", layout="wide")

# 🔒 SEMBUNYIKAN DEFAULT MULTIPAGE SIDEBAR
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("🧭 Navigasi")
page = st.sidebar.radio(
    "Halaman:",
    [
        "Summary",
        "Direct TASTI Details",
        "Top Ten Part Number",
        "Sheet Explorer"
    ]
)

if page == "Summary":
    summary.render()

elif page == "Direct TASTI Details":
    direct_tasti.render()

elif page == "Top Ten Part Number":
    top_ten_part.render()

elif page == "Sheet Explorer":
    sheet_explorer.render()
