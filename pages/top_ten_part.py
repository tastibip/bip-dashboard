# pages/top_ten_part.py
import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from config import load_excel, SHEET_NAME_TOPPART
from ui.tables import df_to_plain_html
import altair as alt

def format_trend(v):
    if pd.isna(v):
        return ""

    try:
        v = float(v)
    except Exception:
        return ""

    pct = v * 100 if abs(v) < 1.5 else v
    pct = int(round(pct))

    if pct > 0:
        return f"🔺 {pct}%"
    elif pct < 0:
        return f"🔻 {abs(pct)}%"
    else:
        return "0%"
    
def format_trend_html(v):
    if pd.isna(v):
        return ""

    try:
        v = float(v)
    except Exception:
        return ""

    pct = int(round(v * 100))

    if pct > 0:
        return f"<span style='color:#1a7f37;font-weight:600'>🔺 {pct}%</span>"
    elif pct < 0:
        return f"<span style='color:#c62828;font-weight:600'>🔻 {abs(pct)}%</span>"
    else:
        return "<span>0%</span>"
    
def style_trend(val):
    if not isinstance(val, str):
        return ""

    if "🔺" in val:
        return "color: #1a7f37; font-weight: 600;"   # hijau
    if "🔻" in val:
        return "color: #c62828; font-weight: 600;"   # merah
    return ""


@st.cache_data(show_spinner="Loading Top Ten Part Number...")
def load_topten_part():
    df_top_raw = load_excel(
        sheet_name=SHEET_NAME_TOPPART,
        skiprows=5
    )

    cols_to_drop = [1] + list(range(43, 48))
    df_top = df_top_raw.drop(
        df_top_raw.columns[cols_to_drop],
        axis=1,
        errors="ignore"
    )

    df_top = df_top.loc[:, ~df_top.columns.astype(str).str.startswith("Unnamed")]
    df_top.columns = [str(c).strip() for c in df_top.columns]
    df_top = df_top.dropna(how="all")

    col_map = {}
    for c in df_top.columns:
        cl = c.lower()
        if "part" in cl:
            col_map[c] = "Part Number"
        elif "customer no" in cl or "cust no" in cl:
            col_map[c] = "Customer No"
        elif "cust name" in cl:
            col_map[c] = "Customer Name"   # ⬅️ PENTING
        elif cl == "customer":
            col_map[c] = "Customer"
        elif "branch" in cl:
            col_map[c] = "Branch"
        elif "trend" in cl or "tren" in cl:
            col_map[c] = "Trend"
            
    # 1️⃣ RENAME DULU
    if col_map:
        df_top = df_top.rename(columns=col_map)

    # ===============================
    # Customer FINAL = Customer Name
    # ===============================
    if "Customer Name" in df_top.columns:
        s = df_top["Customer Name"]

        # pastikan 1 dimensi
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]

        df_top["Customer"] = s
        df_top = df_top.drop(columns=["Customer Name"])

    df_top = df_top.loc[:, ~df_top.columns.duplicated()]

    # ===============================
    # Excel-style fill-down (AMAN dari duplicate column)
    # ===============================
    for c in ["Customer No", "Customer", "Branch"]:
        if c in df_top.columns:
            s = df_top[c]

            # jika duplicate column → ambil kolom pertama
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]

            df_top[c] = (
                s
                .replace("", np.nan)
                .where(s.astype(str).str.upper() != "GRAND TOTAL", np.nan)
                .ffill()
            )

    # ===============================
    # ID Code = Customer No (AMAN)
    # ===============================
    if "Customer No" in df_top.columns:
        s = df_top["Customer No"]

        # PASTIIN 1 DIMENSI
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]

        df_top.insert(0, "ID Code", s)
        df_top = df_top.drop(columns=["Customer No"])

    # fill-down hanya untuk kolom identitas, TAPI hentikan di Grand Total
    for c in ["ID Code", "Customer", "Branch"]:
        if c in df_top.columns:
            s = df_top[c]

            # aman dari duplicate column
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]

            df_top[c] = (
                s
                .replace("", np.nan)
                .astype(str)                      # ⬅️ INI WAJIB
                .where(lambda x: x.str.upper() != "GRAND TOTAL")
                .ffill()
            )

    # ===============================
    # Final column order (rapi & konsisten)
    # ===============================
    preferred_order = [
        "Branch",
        "ID Code",
        "Customer",
        "Part Number"        
    ]

    existing = [c for c in preferred_order if c in df_top.columns]
    others = [c for c in df_top.columns if c not in existing]

    df_top = df_top[existing + others]

    # ===============================
    # FORCE numeric untuk semua kolom bulan & total
    # ===============================
    MONTH_PREFIXES = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
        "Grand Total"
    ]

    for c in df_top.columns:
        if any(c.startswith(m) for m in MONTH_PREFIXES):
            df_top[c] = pd.to_numeric(df_top[c], errors="coerce")

    # ===============================
    # Pindahkan Trend ke paling kanan
    # ===============================
    if "Trend" in df_top.columns:
        cols = [c for c in df_top.columns if c != "Trend"]
        df_top = df_top[cols + ["Trend"]]

    return df_top

MONTH_COLS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November",
    "Grand Total"
]

def get_numeric_value_cols(df):
    """
    Ambil semua kolom numeric (bulan + total) untuk diformat jadi whole number
    """
    return [
        c for c in df.columns
        if (
            c not in ["ID Code", "Customer", "Part Number", "Branch", "Trend"]
            and pd.api.types.is_numeric_dtype(df[c])
        )
    ]

def format_whole_number(x):
    if pd.isna(x) or x == "":
        return ""
    try:
        return f"{int(round(float(x))):,}"
    except Exception:
        return x
    
def render():
    st.title("🏆 Top Ten Part Number")

    df = load_topten_part()

    if df.empty:
        st.warning("Data kosong")
        return
     
    # ================= YEAR FILTER (REAL FIX) =================
    YEAR_MAP = {
        "2023": "",
        "2024": ".1",
        "2025": ".2"
    }

    BASE_MONTHS = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # ================= FILTER BAR =================
    idcode_opts = ["ALL"] + sorted(df["ID Code"].dropna().unique().tolist())

    st.markdown("### 🔎 Filter")

    col_year, col_branch, col_id, col_cust, col_top = st.columns([2, 3, 3, 4, 1])

    with col_year:
        selected_year = st.selectbox(
            "Year",
            ["ALL", "2023", "2024", "2025"],
            index=1
        )

    with col_branch:
        branch_opts = ["ALL"] + sorted(df["Branch"].dropna().unique().tolist())
        selected_branch = st.selectbox("Branch", branch_opts, index=0)

    # branch filter
    df_branch = df if selected_branch == "ALL" else df[df["Branch"] == selected_branch]

    with col_id:
        idcode_opts = ["ALL"] + sorted(df_branch["ID Code"].dropna().unique().tolist())
        selected_id = st.selectbox("ID Code", idcode_opts, index=0)

    # id filter
    df_id = df_branch if selected_id == "ALL" else df_branch[df_branch["ID Code"] == selected_id]

    with col_cust:
        cust_opts = ["ALL"] + sorted(df_id["Customer"].dropna().unique().tolist())
        selected_cust = st.selectbox("Customer", cust_opts)

    with col_top:
        top_n = st.selectbox("Top N", [5, 10, 15, 20], index=1)

    # ===============================
    # CUSTOMER FILTER (FINAL & AMAN)
    # ===============================
    if selected_cust != "ALL":
        df = df_id[df_id["Customer"] == selected_cust]
    else:
        df = df_id.copy()

    # ================= MODE TOGGLE =================
    mode = st.radio(
        "Mode Tampilan",
        ["📋 Table", "📈 Graph"],
        horizontal=True
    )

    BASE_MONTHS = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # ================= TABLE MODE =================
    if mode == "📋 Table":

        # =============================
        # 1. Tentukan suffix tahun
        # =============================
        suffix = "" if selected_year == "ALL" else YEAR_MAP[selected_year]

        # =============================
        # 2. Tentukan kolom bulan SESUAI tahun
        # =============================
        month_cols = []
        for m in BASE_MONTHS:
            col = f"{m}{suffix}"
            if col in df.columns:
                month_cols.append(col)

        # =============================
        # 3. Kolom FINAL yang ditampilkan
        # =============================
        base_cols = ["Branch", "ID Code", "Customer", "Part Number"]

        display_cols = base_cols + month_cols

        # ⬇️ Trend PALING KANAN
        if "Trend" in df.columns:
            display_cols = display_cols + ["Trend"]

        # =============================
        # 4. Bentuk df_show (SATU-SATUNYA)
        # =============================
        df_show = (
            df[display_cols]
            .sort_values(["Customer", "Part Number"])
            .groupby("Customer", group_keys=False)
            .head(top_n)
        )

        # =============================
        # FORMAT TREND (emoji + warna)
        # =============================
        if "Trend" in df_show.columns:
            df_show["Trend"] = df_show["Trend"].apply(format_trend)

        # =============================
        # 5. Rename bulan → Januari–Desember
        # =============================
        df_show = df_show.rename(columns={
            f"{m}{suffix}": m for m in BASE_MONTHS
        })

        # =============================
        # 6. FORCE whole number
        # =============================
        for c in df_show.columns:
            if c not in ["Branch", "ID Code", "Customer", "Part Number", "Trend"]:
                if pd.api.types.is_numeric_dtype(df_show[c]):
                    df_show[c] = df_show[c].round(0).astype("Int64")

        # =============================
        # 7. Render
        # =============================
        st.subheader("📋 Detail Top Part")
        components.html(
            df_to_plain_html(df_show),
            height=600,
            scrolling=True
        )

    # ================= GRAPH MODE =================
    elif mode == "📈 Graph":

        if df.empty:
            st.warning("Data kosong")
            return

        part_opts = sorted(df["Part Number"].dropna().unique().tolist())
        selected_part = st.selectbox("Part Number", part_opts)

        df_part = df[df["Part Number"] == selected_part]

        if df_part.empty:
            st.warning("Data part kosong")
            return
        
        # ===============================
        # BUILD MONTH LIST BASED ON YEAR
        # ===============================
        MONTHS_FULL = [
            ("2023", "January", "Jan", ""),
            ("2024", "January", "Jan", ".1"),
            ("2025", "January", "Jan", ".2"),
        ]

        BASE_MONTHS = [
            ("January", "Jan"),
            ("February", "Feb"),
            ("March", "Mar"),
            ("April", "Apr"),
            ("May", "May"),
            ("June", "Jun"),
            ("July", "Jul"),
            ("August", "Aug"),
            ("September", "Sep"),
            ("October", "Oct"),
            ("November", "Nov"),
            ("December", "Dec"),
        ]

        month_rows = []

        for year, suffix in YEAR_MAP.items():
            if selected_year != "ALL" and selected_year != year:
                continue

            for m_full, m_short in BASE_MONTHS:
                col = f"{m_full}{suffix}"

                if col in df_part.columns:
                    val = df_part.iloc[0][col]
                    value = 0 if pd.isna(val) else val
                else:
                    value = 0   # ⬅️ PAKSA ADA MESKI KOLOM TIDAK ADA

                month_rows.append({
                    "Year": year,
                    "Month": m_short,
                    "MonthLabel": f"{m_short}-{year[-2:]}",
                    "Value": value
                })

        chart_df = pd.DataFrame(month_rows)

        # ===============================
        # ADD NUMERIC INDEX (INTERNAL ONLY)
        # ===============================
        chart_df["Idx"] = range(1, len(chart_df) + 1)

        # 🔑 MAP Idx → MonthLabel (UNTUK AXIS LABEL)
        month_labels = dict(zip(chart_df["Idx"], chart_df["MonthLabel"]))

        idx_domain = [chart_df["Idx"].min(), chart_df["Idx"].max()]

        # ===============================
        # ANNUAL LINEAR TREND (MATCH EXCEL)
        # ===============================
        annual_df = (
            chart_df
            .groupby("Year", as_index=False)["Value"]
            .sum()
        )

        # pastikan numeric year
        annual_df["YearNum"] = annual_df["Year"].astype(int)

        x = annual_df["YearNum"].values
        y = annual_df["Value"].values

        if len(x) >= 2 and y.mean() != 0:
            coef = np.polyfit(x, y, 1)
            slope = coef[0]
            avg_y = y.mean()
            trend_pct = slope / avg_y
        else:
            coef = None
            trend_pct = 0

        # buat garis trend tahunan → dipetakan ke bulanan (visual saja)
        trend_df = chart_df.copy()

        # ===============================
        # BUILD CONTINUOUS TIME INDEX
        # ===============================
        # representasikan waktu bulanan sebagai tahun desimal
        trend_df = chart_df.copy()

        # posisi bulan di dalam tahun (0..11)
        trend_df["MonthPos"] = trend_df.groupby("Year").cumcount()

        # YearNum kontinu tapi tetap di domain tahunan
        trend_df["YearNum"] = (
            trend_df["Year"].astype(int)
            + trend_df["MonthPos"] / 12.0
        )

        # evaluasi regresi tahunan di timeline bulanan
        if coef is not None:
            # ===============================
            # ANCHOR TRENDLINE TO ACTUAL DATA
            # ===============================
            x_idx = np.arange(len(trend_df))

            y_start = chart_df["Value"].iloc[0]
            y_end   = chart_df["Value"].iloc[-1]

            trend_df["TrendValue"] = np.linspace(y_start, y_end, len(trend_df))
        else:
            # fallback: garis datar di rata-rata nilai
            trend_df["TrendValue"] = trend_df["Value"].mean()

        # ===============================
        # SHARED Y SCALE (LOCK AXIS)
        # ===============================
        y_min = min(chart_df["Value"].min(), trend_df["TrendValue"].min())
        y_max = max(chart_df["Value"].max(), trend_df["TrendValue"].max())

        y_scale = alt.Scale(
            domain=[y_min * 0.9, y_max * 1.1]
        )

        # ===============================
        # EXPONENTIAL TREND (y = A * e^(k*x))
        # ===============================
        exp_df = chart_df.copy()

        # hanya pakai value > 0 untuk fitting
        mask = exp_df["Value"] > 0
        x_exp = exp_df.loc[mask, "Idx"].values
        y_exp = exp_df.loc[mask, "Value"].values

        if len(x_exp) >= 2:
            # log transform
            log_y = np.log(y_exp)

            k, log_A = np.polyfit(x_exp, log_y, 1)
            A = np.exp(log_A)

            exp_df["ExpTrendValue"] = A * np.exp(k * exp_df["Idx"])
        else:
            exp_df["ExpTrendValue"] = np.nan

        # ===============================
        # EXPONENTIAL % CHANGE
        # ===============================
        exp_start = exp_df["ExpTrendValue"].iloc[0]
        exp_end   = exp_df["ExpTrendValue"].iloc[-1]

        if exp_start == 0 or pd.isna(exp_start):
            exp_pct_change = 0
        else:
            exp_pct_change = ((exp_end - exp_start) / abs(exp_start)) * 100

        exp_label = f"Trend {exp_pct_change:+.1f}%"

        # ===============================
        # LABEL DATAFRAME (EXPONENTIAL)
        # ===============================
        exp_label_df = pd.DataFrame({
            "Idx": [
                exp_df["Idx"].iloc[0],
                exp_df["Idx"].iloc[-1]
            ],
            "Value": [
                exp_start,
                exp_end
            ],
            "Label": [
                "Start",
                exp_label
            ]
        })

        # ===============================
        # EXPONENTIAL CHART (FINAL & AMAN)
        # ===============================
        bar_exp = alt.Chart(chart_df).mark_bar(
            color="#93c5fd"
        ).encode(
            x=alt.X(
                "MonthLabel:N",
                sort=alt.SortField("Idx", order="ascending"),
                title="Month",
                axis=alt.Axis(
                    labelAngle=0,        # ⬅️ horizontal
                    labelOverlap="greedy"
                )
            ),
            y=alt.Y(
                "Value:Q",
                title="Actual Value",
                scale=alt.Scale(zero=False)
            ),
            tooltip=["MonthLabel", "Value"]
        )

        exp_line = alt.Chart(exp_df).mark_line(
            color="#f59e0b",
            strokeWidth=3
        ).encode(
            x=alt.X(
                "MonthLabel:N",
                sort=alt.SortField("Idx", order="ascending"),
                axis=None        # ⬅️ INI KUNCINYA
            ),
            y=alt.Y(
                "ExpTrendValue:Q",
                title="Exponential Trend",
                scale=alt.Scale(zero=False)
            ),
            tooltip=[
                "MonthLabel",
                alt.Tooltip("ExpTrendValue:Q", format=",.0f")
            ]
        )

        # ===============================
        # EXPONENTIAL LABELS
        # ===============================
        exp_labels = alt.Chart(exp_label_df).mark_text(
            align="left",
            dx=6,
            dy=-6,
            fontSize=12,
            fontWeight="bold",
            color="#f59e0b"
        ).encode(
            x=alt.X("Idx:Q", axis=None),   # 🔑 PAKAI Idx
            y="Value:Q",
            text="Label:N"
        )

        exp_chart = (bar_exp + exp_line + exp_labels).properties(
            title=f"{selected_part} – Exponential Trend (with Actual Values)",
            height=300
        )

        # ===============================
        # TREND START & END %
        # ===============================
        Label = f"Trend {trend_pct * 100:+.1f}%"

        label_df = pd.DataFrame({
            "Idx": [chart_df.iloc[0]["Idx"], chart_df.iloc[-1]["Idx"]],
            "Value": [
                trend_df.iloc[0]["TrendValue"],
                trend_df.iloc[-1]["TrendValue"]
            ],
            "Label": [
                "Start",
                Label
            ]
        })

        # ===============================
        # BAR CHART (WAJIB ADA)
        # ===============================
        bar = alt.Chart(chart_df).mark_bar().encode(
            x=alt.X(
                "MonthLabel:N",
                sort=alt.SortField("Idx", order="ascending"),
                axis=alt.Axis(
                    title=None,
                    labelAngle=0,
                    labelOverlap="greedy"
                )
            ),
            y=alt.Y("Value:Q", title="Value", scale=y_scale),
            tooltip=["Year", "Month", "Value"]
        )

        # ===============================
        # TRENDLINE (Idx only, hidden)
        # ===============================
        trend = alt.Chart(trend_df).mark_line(
            color="red",
            strokeWidth=3
        ).encode(
            x=alt.X(
                "MonthLabel:N",
                sort=alt.SortField("Idx", order="ascending"),
                axis=None
            ),
            y=alt.Y("TrendValue:Q", scale=y_scale)
        )

        # ===============================
        # EXPONENTIAL TRENDLINE
        # ===============================
        exp_trend = alt.Chart(exp_df).mark_line(
            color="#f59e0b",          # oranye
            strokeDash=[6, 4],        # dashed
            strokeWidth=2
        ).encode(
            x=alt.X(
                "MonthLabel:N",
                sort=alt.SortField("Idx", order="ascending"),
                axis=None
            ),
            y="ExpTrendValue:Q"
        )

        # ===============================
        # LABEL START & END
        # ===============================
        labels = alt.Chart(label_df).mark_text(
            align="left",
            dx=6,
            dy=-6,
            fontSize=12,
            fontWeight="bold",
            color="red"
        ).encode(
            x=alt.X("Idx:Q", axis=None),   # ⬅️ INI PALING PENTING
            y="Value:Q",
            text="Label:N"
        )

        chart_main = (bar + trend + labels).properties(
            title=f"{selected_part} – {selected_cust} (Linear Trend)",
            height=420,
            padding={"bottom": 20}
        )

        st.subheader("📈 Linear Trend")
        st.altair_chart(chart_main, use_container_width=True)
        st.subheader("📉 Exponential Trend")
        st.altair_chart(exp_chart, use_container_width=True)
