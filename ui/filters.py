import streamlit as st
import pandas as pd
import re


# ===============================
# SAFE SESSION KEY
# ===============================
def _safe_key(prefix, value):
    value = "" if value is None else str(value)
    safe = re.sub(r"[^0-9a-zA-Z]", "_", value)
    return f"filter_{prefix}_{safe}"


# ===============================
# SELECT ALL HANDLER
# ===============================
def _on_all_changed(prefix, options, all_key):
    master = st.session_state.get(all_key, False)
    for opt in options:
        st.session_state[_safe_key(prefix, opt)] = master


def _on_clear(prefix, options, all_key):
    for opt in options:
        st.session_state[_safe_key(prefix, opt)] = False
    st.session_state[all_key] = False


# ===============================
# CHECKBOX GROUP (NO BLANK)
# ===============================
def checkbox_group_no_blank(
    prefix: str,
    label: str,
    options: list,
    default_all: bool = True,
    expanded: bool = True,
):
    # buang blank & Grand Total
    opts = [o for o in options if str(o).strip() not in ("", "<blank>", "Grand Total")]

    # urutan khusus Pulau
    if prefix.lower() == "pulau":
        order = ["SUMATERA", "JAWA", "BALI NT", "KALIMANTAN", "SULAWESI"]
        mapping = {str(o).upper(): o for o in opts}
        ordered = [mapping[o] for o in order if o in mapping]
        others = [o for o in opts if str(o).upper() not in order]
        opts = ordered + sorted(others, key=lambda x: str(x))
    else:
        opts = sorted(opts, key=lambda x: str(x))

    all_key = f"filter_{prefix}_ALL"
    if all_key not in st.session_state:
        st.session_state[all_key] = default_all

    for opt in opts:
        k = _safe_key(prefix, opt)
        if k not in st.session_state:
            st.session_state[k] = default_all

    box = st.sidebar.expander(label, expanded=expanded)

    box.checkbox(
        "All" if prefix != "pulau" else "All Island",
        key=all_key,
        value=st.session_state[all_key],
        on_change=_on_all_changed,
        args=(prefix, opts, all_key),
    )

    selected = []
    for opt in opts:
        k = _safe_key(prefix, opt)
        if box.checkbox(str(opt), key=k):
            selected.append(opt)

    box.button(
        f"Clear {label}",
        on_click=_on_clear,
        args=(prefix, opts, all_key),
    )

    return selected


# ===============================
# APPLY FILTERS (GENERAL)
# ===============================
def apply_filters_general(df, pulau_sel=None, prov_sel=None, route_sel=None):
    if df is None or df.empty:
        return df

    res = df.copy()

    if pulau_sel and "Pulau" in res.columns:
        res = res[res["Pulau"].isin(pulau_sel)]

    if prov_sel and "Provinsi" in res.columns:
        res = res[res["Provinsi"].isin(prov_sel)]

    if route_sel and "Route" in res.columns:
        res = res[res["Route"].isin(route_sel)]

    return res
