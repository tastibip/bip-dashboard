# pages/direct_tasti.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import streamlit.components.v1 as components
import re

from config import SHEET_NAME_REVKAB
from data.revbykab import load_clean_revbykab
from ui.filters import checkbox_group_no_blank, apply_filters_general
from ui.tables import df_to_colored_html, df_to_plain_html

# =========================================================
# MAIN RENDER
# =========================================================
def render(file_path: str):

    st.title("📋 Direct vs TASTI Revenue details")

    # ---------------------------
    # MODE TOGGLE
    # ---------------------------
    mode = st.radio(
        "Mode Tampilan:",
        ["Percentage", "Value", "Graph"],
        index=0,
        horizontal=True
    )

    count_placeholder = st.empty()

    # ---------------------------
    # LOAD DATA (PERCENT + VALUE PARSER)
    # ---------------------------
    df_pct_raw, df_val_raw = load_clean_revbykab(
        file_path,
        sheet_name=SHEET_NAME_REVKAB
    )

    # ---------------------------
    # NORMALIZATION (IDENTIK ORIGINAL)
    # ---------------------------
    def norm_route(v):
        if pd.isna(v):
            return np.nan
        if isinstance(v, str):
            s = v.strip().upper()
            return s if s != "" else np.nan
        return np.nan

    for df in (df_pct_raw, df_val_raw):
        if df is not None:
            if "Route" in df.columns:
                df["Route"] = df["Route"].apply(norm_route)

            for col in ("Pulau", "Provinsi"):
                if col in df.columns:
                    df[col] = (
                        df[col]
                        .apply(lambda x: x.strip() if isinstance(x, str) and x.strip() != "" else np.nan)
                        .ffill()
                    )

    # ---------------------------
    # FILTER SOURCE (PERCENT PRIORITY)
    # ---------------------------
    src = (
        df_pct_raw
        if df_pct_raw is not None and not df_pct_raw.empty
        else df_val_raw
    )

    if src is None or src.empty:
        st.info("Tidak ada data")
        return

    # ---------------------------
    # SIDEBAR FILTERS
    # ---------------------------
    pulau_opts = sorted(src["Pulau"].dropna().unique().tolist())

    sel_pulau = checkbox_group_no_blank(
        "pulau", "Pulau",
        pulau_opts,
        default_all=True,
        expanded=True
    )

    if sel_pulau:
        prov_opts = (
            src[src["Pulau"].isin(sel_pulau)]["Provinsi"]
            .dropna().unique().tolist()
        )
    else:
        prov_opts = src["Provinsi"].dropna().unique().tolist()

    sel_prov = checkbox_group_no_blank(
        "prov", "Provinsi",
        sorted(prov_opts),
        default_all=False,
        expanded=False
    )

    route_opts = sorted(src["Route"].dropna().unique().tolist())

    sel_route = checkbox_group_no_blank(
        "route", "Route",
        route_opts,
        default_all=True,
        expanded=False
    )

    # ---------------------------
    # APPLY FILTERS
    # ---------------------------
    df_pct_f = apply_filters_general(df_pct_raw, sel_pulau, sel_prov, sel_route)
    df_val_f = apply_filters_general(df_val_raw, sel_pulau, sel_prov, sel_route)

    # =========================================================
    # GRAPH MODE
    # =========================================================
    if mode == "Graph":
        if df_pct_f is None or df_pct_f.empty:
            st.info("Tidak ada data untuk grafik")
            return

        pct_cols = []
        for c in df_pct_f.columns:
            if c in ("Pulau", "Provinsi", "Kab Kota", "Route", "Type"):
                continue
            s = pd.to_numeric(df_pct_f[c], errors="coerce")
            if s.notna().sum() > 0 and s.max() <= 1.5:
                pct_cols.append(c)

        if not pct_cols:
            st.info("Tidak ada kolom persentase")
            return

        id_cols = [c for c in ["Kab Kota", "Route"] if c in df_pct_f.columns]

        df_long = (
            df_pct_f[id_cols + pct_cols]
            .melt(id_vars=id_cols, var_name="Month", value_name="Share")
            .dropna(subset=["Share"])
        )

        last_month = pct_cols[-1]

        # Gunakan SEMUA Kab/Kota hasil filter Pulau / Provinsi
        df_plot = df_long.copy()

        df_last = df_plot[df_plot["Month"] == last_month]
        kpi = df_last.groupby("Route")["Share"].mean()

        c1, c2, c3 = st.columns([1, 1, 6])
        c1.metric("Avg TASTI", f"{kpi.get('TASTI', 0) * 100:.1f}%")
        c2.metric("Avg DIRECT", f"{kpi.get('DIRECT', 0) * 100:.1f}%")
        c3.markdown("Stacked bar = pangsa TASTI vs DIRECT per Kab/Kota")

        df_bar = (
            df_last.groupby(["Kab Kota", "Route"], as_index=False)["Share"]
            .mean()
        )

        # 🔒 kunci urutan stack (UNTUK POSISI)
        STACK_ORDER = {"DIRECT": 0, "TASTI": 1}
        df_bar["stack_order"] = df_bar["Route"].map(STACK_ORDER)

        # label
        df_bar["label"] = (
            df_bar["Share"]
            .apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) and x > 0.03 else "")
        )

        # 🔥 TAMBAHKAN INI
        hover = alt.selection_point(
            fields=["Route"],
            on="mouseover",
            clear="mouseout"
        )

        bars = (
            alt.Chart(df_bar)
            .mark_bar()
            .encode(
                x=alt.X(
                    "Kab Kota:N",
                    sort=alt.EncodingSortField(
                        field="Share",
                        op="sum",
                        order="descending"
                    )
                ),
                y=alt.Y(
                    "Share:Q",
                    stack="normalize",
                    axis=alt.Axis(format="%", title="Market Share")
                ),
                color=alt.Color(
                    "Route:N",
                    scale=alt.Scale(
                        domain=["DIRECT", "TASTI"],          # ✅ LIST
                        range=["#16A34A", "#2563EB"]
                    ),
                    legend=alt.Legend(title="Route")
                ),
                order=alt.Order("stack_order:Q")             # ✅ ANGKA
            )
        )

        labels = (
            alt.Chart(df_bar)
            .transform_window(
                cumulative="sum(Share)",
                groupby=["Kab Kota"],
                sort=[alt.SortField("stack_order", order="ascending")]
            )
            .transform_calculate(
                mid="datum.cumulative - datum.Share / 2"
            )
            .mark_text(
                align="center",
                baseline="middle",
                color="white",
                fontSize=11,
                fontWeight="bold"
            )
            .encode(
                x="Kab Kota:N",
                y=alt.Y("mid:Q", stack="normalize"),
                text="label:N"
            )
        )

        chart = (bars + labels).properties(height=420)
        st.altair_chart(chart, use_container_width=True)

        count_placeholder.write(f"Menampilkan **{len(df_plot)}** baris (graph)")
        return

    # =========================================================
    # PERCENTAGE MODE
    # =========================================================
    if mode == "Percentage":
        if df_pct_f is None or df_pct_f.empty:
            st.info("Tidak ada data")
            return

        pct_cols = [
            c for c in df_pct_f.columns
            if c not in ("Pulau", "Provinsi", "Kab Kota", "Route", "Type")
        ]

        df_html = df_pct_f.copy()
        for c in pct_cols:
            df_html[c] = pd.to_numeric(df_html[c], errors="coerce")

        html = df_to_colored_html(df_html, pct_cols)
        components.html(html, height=1100, scrolling=True)

        count_placeholder.write(f"Menampilkan **{len(df_html)}** baris")
        return

    # =========================================================
    # VALUE MODE (100% IDENTIK ORIGINAL)
    # =========================================================
    if mode == "Value":

        # --- STEP 1: READ VALUE TABLE ---
        try:
            df_val_direct = pd.read_excel(
                file_path,
                sheet_name=SHEET_NAME_REVKAB,
                header=364  # Excel row 365
            )
        except Exception:
            df_val_direct = None

        # --- STEP 2: SIMPLE CANONICALIZE ---
        def simple_canonicalize(df):
            if df is None or df.empty:
                return df

            lower_map = {str(c).lower(): c for c in df.columns}
            col_map = {}

            for k, orig in lower_map.items():
                if "pulau" in k:
                    col_map[orig] = "Pulau"
                elif "prov" in k:
                    col_map[orig] = "Provinsi"
                elif "kab" in k or "kota" in k:
                    col_map[orig] = "Kab Kota"
                elif "route" in k:
                    col_map[orig] = "Route"
                elif "type" in k:
                    col_map[orig] = "Type"

            if col_map:
                df = df.rename(columns=col_map)

            for col in ("Pulau", "Provinsi"):
                if col in df.columns:
                    df[col] = (
                        df[col]
                        .apply(lambda x: x.strip() if isinstance(x, str) and x.strip() != "" else np.nan)
                        .ffill()
                    )

            if "Route" in df.columns:
                df["Route"] = df["Route"].apply(
                    lambda v: v.strip().upper()
                    if isinstance(v, str) and v.strip() != ""
                    else np.nan
                )

            return df

        df_val_for_display = None

        if df_val_direct is not None and not df_val_direct.empty:
            df_val_direct = simple_canonicalize(df_val_direct)
            if any(c in df_val_direct.columns for c in ("Pulau", "Provinsi", "Kab Kota", "Route")):
                df_val_for_display = apply_filters_general(
                    df_val_direct, sel_pulau, sel_prov, sel_route
                )

        if (df_val_for_display is None or df_val_for_display.empty) and df_val_f is not None:
            df_val_tmp = simple_canonicalize(df_val_f.copy())
            df_val_for_display = apply_filters_general(
                df_val_tmp, sel_pulau, sel_prov, sel_route
            )

        if df_val_for_display is None:
            df_val_for_display = pd.DataFrame()

        # --- STEP 3: COERCE NUMERIC SAFELY ---
        df_disp = df_val_for_display.copy()
        for c in df_disp.columns:
            try:
                if df_disp[c].dtype == object:
                    df_disp[c] = (
                        df_disp[c]
                        .apply(lambda x: str(x).replace("%", "") if isinstance(x, str) else x)
                    )
                df_disp[c] = pd.to_numeric(df_disp[c], errors="coerce") \
                                .combine_first(df_val_for_display[c])
            except Exception:
                pass

        df_disp = df_disp.replace({np.nan: ""})
        df_disp.columns = [str(c) for c in df_disp.columns]

        # --- STEP 4: RENDER ---
        html = df_to_plain_html(df_disp)
        components.html(html, height=1100, scrolling=True)

        count_placeholder.write(
            f"Menampilkan **{len(df_disp)}** baris"
        )
