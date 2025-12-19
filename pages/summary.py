import streamlit as st
import pandas as pd
import altair as alt

from config import (
    FILE_PATH,
    SHEET_NAME_REVNAT,
    SHEET_NAME_REVPROV,
    SHEET_NAME_REVKAB,
    SHEET_NAME_PNVAR,
)

from data.revbynat import load_revby_nat


def render():
    st.title("📊 Summary")

    # =========================
    # Load basic sheets (counter)
    # =========================
    try:
        df_rev_nat = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME_REVNAT)
        df_rev_prov = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME_REVPROV)
        df_rev_kab = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME_REVKAB)
        df_pn_var = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME_PNVAR)
    except Exception as e:
        st.error(f"Gagal load data summary: {e}")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Row RevbyNat", df_rev_nat.shape[0])
    c2.metric("Row RevbyProv", df_rev_prov.shape[0])
    c3.metric("Row RevbyKab", df_rev_kab.shape[0])
    c4.metric("Row PN Varians", df_pn_var.shape[0])

    st.markdown("---")

    # =========================
    # Load computed data
    # =========================
    try:
        yearly, semester, quarter = load_revby_nat(FILE_PATH)
    except Exception as e:
        st.error(f"Gagal hitung RevbyNat: {e}")
        st.stop()

    # =========================
    # YEARLY
    # =========================
    st.subheader("Revenue Direct vs TASTI (Yearly)")

    col_kpi, col_chart = st.columns([2, 1.5])

    with col_kpi:
        years = sorted(yearly.keys())
        cols = st.columns(len(years))
        for i, y in enumerate(years):
            cols[i].metric(f"{y} TASTI", f"{yearly[y]['TASTI']*100:.1f}%")
            cols[i].metric(f"{y} DIRECT", f"{yearly[y]['DIRECT']*100:.1f}%")

    with col_chart:
        df_year = pd.DataFrame(
            {
                "Year": years,
                "DIRECT": [yearly[y]["DIRECT"] for y in years],
                "TASTI": [yearly[y]["TASTI"] for y in years],
            }
        )

        df_long = df_year.melt(
            id_vars="Year",
            value_vars=["DIRECT", "TASTI"],
            var_name="Type",
            value_name="Share",
        )

        df_long["LabelPos"] = df_long.apply(
            lambda r: r["Share"] / 2
            if r["Type"] == "DIRECT"
            else 1 - r["Share"] / 2,
            axis=1,
        )

        bars = (
            alt.Chart(df_long)
            .mark_bar()
            .encode(
                x=alt.X("Year:N", title="Year"),
                y=alt.Y("Share:Q", stack="normalize", axis=alt.Axis(format="%")),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["TASTI", "DIRECT"],
                        range=["#8E44AD", "#1ABC9C"],
                    ),
                ),
                tooltip=[
                    alt.Tooltip("Year:N"),
                    alt.Tooltip("Type:N"),
                    alt.Tooltip("Share:Q", format=".1%"),
                ],
            )
        )

        text = (
            alt.Chart(df_long)
            .mark_text(color="white", size=12, baseline="middle")
            .encode(
                x="Year:N",
                y="LabelPos:Q",
                text=alt.Text("Share:Q", format=".1%"),
                detail="Type:N",
            )
        )

        st.altair_chart((bars + text).properties(height=220), use_container_width=True)

    # =========================
    # SEMESTER
    # =========================
    with st.expander("📌 Semester Breakdown", expanded=False):
        st.subheader("Semester Breakdown (Pivot Format)")

        def sem_sort(k):
            year, sem = k.split("-")
            return int(year), 1 if sem == "S1" else 2

        ordered = sorted(semester.keys(), key=sem_sort)

        df_sem = pd.DataFrame({"Type": ["DIRECT", "TASTI"]})
        labels = []

        for k in ordered:
            year, sem = k.split("-")
            label = f"{sem} {year}"
            labels.append(label)
            df_sem[label] = [
                f"{semester[k]['DIRECT']*100:.1f}%",
                f"{semester[k]['TASTI']*100:.1f}%",
            ]

        rows = []
        for k in ordered:
            year, sem = k.split("-")
            label = f"{sem} {year}"
            for t in ["TASTI", "DIRECT"]:
                rows.append(
                    {
                        "Semester": label,
                        "Type": t,
                        "Share": semester[k][t],
                    }
                )

        df_long = pd.DataFrame(rows)
        df_long["Semester"] = pd.Categorical(df_long["Semester"], categories=labels, ordered=True)
        df_long["LabelPos"] = df_long.apply(
            lambda r: r["Share"] / 2
            if r["Type"] == "DIRECT"
            else 1 - r["Share"] / 2,
            axis=1,
        )

        bars = (
            alt.Chart(df_long)
            .mark_bar()
            .encode(
                x=alt.X("Semester:O", sort=labels),
                y=alt.Y("Share:Q", stack="normalize", axis=alt.Axis(format="%")),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["TASTI", "DIRECT"],
                        range=["#8E44AD", "#1ABC9C"],
                    ),
                ),
            )
        )

        text = (
            alt.Chart(df_long)
            .mark_text(color="white", size=11)
            .encode(
                x=alt.X("Semester:O", sort=labels),
                y="LabelPos:Q",
                text=alt.Text("Share:Q", format=".1%"),
                detail="Type:N",
            )
        )

        st.altair_chart((bars + text).properties(height=260), use_container_width=True)
        st.table(df_sem)

    # =========================
    # QUARTER
    # =========================
    with st.expander("📌 Quarter Breakdown", expanded=False):
        st.subheader("Quarter Breakdown (Pivot Format)")

        def q_sort(q):
            y, qn = q.split("-Q")
            return int("20" + y), int(qn)

        ordered_q = sorted(quarter.keys(), key=q_sort)

        df_q = pd.DataFrame({"Type": ["DIRECT", "TASTI"]})
        labels = []

        for q in ordered_q:
            y, qn = q.split("-Q")
            label = f"Q{qn} 20{y}"
            labels.append(label)
            df_q[label] = [
                f"{quarter[q]['DIRECT']*100:.1f}%",
                f"{quarter[q]['TASTI']*100:.1f}%",
            ]

        rows = []
        for q in ordered_q:
            y, qn = q.split("-Q")
            label = f"Q{qn} 20{y}"
            for t in ["TASTI", "DIRECT"]:
                rows.append(
                    {
                        "Quarter": label,
                        "Type": t,
                        "Share": quarter[q][t],
                    }
                )

        df_long = pd.DataFrame(rows)
        df_long["Quarter"] = pd.Categorical(df_long["Quarter"], categories=labels, ordered=True)
        df_long["LabelPos"] = df_long.apply(
            lambda r: r["Share"] / 2
            if r["Type"] == "DIRECT"
            else 1 - r["Share"] / 2,
            axis=1,
        )

        bars = (
            alt.Chart(df_long)
            .mark_bar()
            .encode(
                x=alt.X("Quarter:O", sort=labels),
                y=alt.Y("Share:Q", stack="normalize", axis=alt.Axis(format="%")),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["TASTI", "DIRECT"],
                        range=["#8E44AD", "#1ABC9C"],
                    ),
                ),
            )
        )

        text = (
            alt.Chart(df_long)
            .mark_text(color="white", size=11)
            .encode(
                x=alt.X("Quarter:O", sort=labels),
                y="LabelPos:Q",
                text=alt.Text("Share:Q", format=".1%"),
                detail="Type:N",
            )
        )

        st.altair_chart((bars + text).properties(height=260), use_container_width=True)
        st.table(df_q)
