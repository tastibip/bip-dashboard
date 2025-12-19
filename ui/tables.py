import numpy as np
import pandas as pd
import re
import html

# =====================================================
# PERCENTAGE TABLE (COLORED)
# =====================================================
def df_to_colored_html(df, pct_cols, thresholds=(0.4, 0.3, 0.2)):
    green_cut, blue_cut, yellow_cut = thresholds

    css = """
    <style>
    .table-wrap { overflow-x: auto; }
    table.custom {
        border-collapse: collapse;
        width:100%;
        font-family: "Segoe UI", Roboto, Arial;
        font-size:13px;
    }
    table.custom th, table.custom td {
        border: 1px solid #e6e6e6;
        padding: 6px 8px;
        text-align: center;
        white-space: nowrap;
    }
    table.custom thead th {
        position: sticky;
        top: 0;
        background: #f7f7f7;
        z-index:2;
        font-weight:600;
    }
    td.left { text-align: left; }
    </style>
    """

    def fmt_pct(v):
        try:
            p = float(v) * 100
            return f"{int(p)}%" if abs(p - round(p)) < 0.01 else f"{p:.1f}%"
        except:
            return ""

    rows = []
    header = "".join(f"<th>{c}</th>" for c in df.columns)
    rows.append(f"<thead><tr>{header}</tr></thead>")

    body = []

    for _, r in df.iterrows():
        cells = []

        route = str(r.get("Route", "")).upper()
        is_tasti = route == "TASTI"

        for c in df.columns:
            v = r[c]

            if c in pct_cols:
                try:
                    val = float(v)
                except:
                    val = None

                if val is None or pd.isna(val):
                    cells.append("<td></td>")
                else:
                    bg = ""
                    color = "#222"

                    if is_tasti:
                        if val > green_cut:
                            bg, color = "#c6efce", "#006100"
                        elif val > blue_cut:
                            bg, color = "#cfe8ff", "#003f7f"
                        elif val > yellow_cut:
                            bg, color = "#fff4cc", "#725800"
                        else:
                            bg, color = "#f8d7da", "#721c24"

                    cells.append(
                        f"<td style='background:{bg};color:{color};'>{fmt_pct(val)}</td>"
                    )
            else:
                cls = "left" if c.lower() not in ("route",) else "left"
                style = ""
                if c.lower() == "route":
                    if route == "TASTI":
                        style = "color:#001f3f;font-weight:600;"
                    elif route == "DIRECT":
                        style = "color:#b30000;font-weight:600;"
                cells.append(
                    f"<td class='{cls}' style='{style}'>{'' if pd.isna(v) else v}</td>"
                )

        body.append("<tr>" + "".join(cells) + "</tr>")

    html = (
        css
        + "<div class='table-wrap'>"
        + "<table class='custom'>"
        + "".join(rows)
        + "<tbody>"
        + "\n".join(body)
        + "</tbody></table></div>"
    )
    return html


# =====================================================
# VALUE TABLE (PLAIN)
# =====================================================
def df_to_plain_html(df):
    import numpy as np
    import pandas as pd

    css = """
    <style>
    .table-wrap { overflow-x: auto; }
    table.tbl {
        border-collapse: collapse;
        width:100%;
        font-family: "Segoe UI", Roboto, Arial;
        font-size:13px;
    }
    table.tbl th, table.tbl td {
        border: 1px solid #e6e6e6;
        padding: 8px 10px;
        text-align: center;
        white-space: nowrap;
    }
    table.tbl thead th {
        position: sticky;
        top: 0;
        background: #f7f7f7;
        z-index:2;
        font-weight:600;
    }
    .num { font-variant-numeric: tabular-nums; }
    </style>
    """

    # HEADER — TANPA ESCAPE
    header = "".join(f"<th>{c}</th>" for c in df.columns)
    thead = f"<thead><tr>{header}</tr></thead>"

    rows = []

    for _, r in df.iterrows():
        cells = []

        for c in df.columns:
            v = r[c]

            # TREND = HTML (emoji / span)
            if c.lower() == "trend":
                if pd.isna(v):
                    disp = ""
                    style = ""
                else:
                    disp = str(v)
                    if "🔺" in disp:
                        style = "color:#1a7f37;font-weight:600;"
                    elif "🔻" in disp:
                        style = "color:#c62828;font-weight:600;"
                    else:
                        style = ""

                cells.append(f"<td class='num' style='{style}'>{disp}</td>")
                continue

            # NUMERIC
            if isinstance(v, (int, float, np.number)) and not pd.isna(v):
                disp = f"{int(round(v)):,}"
            else:
                disp = "" if pd.isna(v) else str(v)

            cells.append(f"<td class='num'>{disp}</td>")

        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        css
        + "<div class='table-wrap'>"
        + "<table class='tbl'>"
        + thead
        + "<tbody>"
        + "\n".join(rows)
        + "</tbody></table></div>"
    )


