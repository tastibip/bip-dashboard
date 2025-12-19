# data/revbynat.py
import numpy as np
from config import SHEET_NAME_REVNAT


def load_revby_nat(load_excel):
    """
    load_excel : function(sheet_name=...) -> DataFrame
    """

    df = load_excel(sheet_name=SHEET_NAME_REVNAT)

    # ===============================
    # Header row (Row Labels)
    # ===============================
    header_row = df[df["Type"] == "Row Labels"].iloc[0]

    quarter_labels, quarter_cols = [], []
    for col in df.columns:
        val = header_row[col]
        if isinstance(val, str) and "-Q" in val:
            quarter_labels.append(val)
            quarter_cols.append(col)

    # ===============================
    # Data rows
    # ===============================
    direct_row = df[df["Type"] == "DIRECT"].iloc[0]
    tasti_row  = df[df["Type"] == "TASTI"].iloc[0]

    quarter_data = {
        q: {
            "DIRECT": float(direct_row[c]),
            "TASTI": float(tasti_row[c])
        }
        for q, c in zip(quarter_labels, quarter_cols)
    }

    # ===============================
    # Aggregate Year & Semester
    # ===============================
    year_map = {"23": "2023", "24": "2024", "25": "2025"}

    yearly, semester = {}, {}

    for q, v in quarter_data.items():
        y, qn = q.split("-Q")
        year = year_map.get(y, "20" + y)
        qn = int(qn)

        yearly.setdefault(year, {"DIRECT": [], "TASTI": []})
        yearly[year]["DIRECT"].append(v["DIRECT"])
        yearly[year]["TASTI"].append(v["TASTI"])

        sem = "S1" if qn <= 2 else "S2"
        k = f"{year}-{sem}"
        semester.setdefault(k, {"DIRECT": [], "TASTI": []})
        semester[k]["DIRECT"].append(v["DIRECT"])
        semester[k]["TASTI"].append(v["TASTI"])

    yearly = {k: {t: np.mean(v[t]) for t in v} for k, v in yearly.items()}
    semester = {k: {t: np.mean(v[t]) for t in v} for k, v in semester.items()}

    return yearly, semester, quarter_data
