import pandas as pd
import numpy as np
import re

# =====================================================
# Helper: recover hierarchy from Excel-style grouped rows
# =====================================================
def recover_hierarchy_from_rows(df):
    if df is None or df.empty:
        return df

    cur_pulau = None
    cur_prov = None

    for i in range(len(df)):
        row = df.iloc[i]

        filled_cells = [
            c for c in df.columns
            if isinstance(row[c], str) and row[c].strip() != ""
        ]

        # Baris header grup (biasanya hanya 1 sel terisi)
        if len(filled_cells) == 1:
            val = row[filled_cells[0]].strip().upper()

            if val in ("SUMATERA", "JAWA", "KALIMANTAN", "SULAWESI", "BALI NT"):
                cur_pulau = val
                cur_prov = None
                continue
            else:
                cur_prov = val
                continue

        # Baris data
        if cur_pulau:
            df.at[i, "Pulau"] = cur_pulau
        if cur_prov:
            df.at[i, "Provinsi"] = cur_prov

    return df


# =====================================================
# MAIN LOADER
# =====================================================
def load_clean_revbykab(file_path, sheet_name="RevbyKab"):
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # --- percentage table ---
    raw_pct = raw.iloc[:358].copy()
    header = raw_pct.iloc[3].fillna("").astype(str).tolist()

    df_pct = raw_pct.iloc[4:].copy().reset_index(drop=True)
    df_pct.columns = header

    # normalize column names
    df_pct.columns = [str(c).strip() for c in df_pct.columns]

    # ensure columns exist
    for c in ("Pulau", "Provinsi", "Kab Kota", "Route"):
        if c not in df_pct.columns:
            df_pct[c] = np.nan

    # 🔑 EXACTLY like app.py original
    for col in ("Pulau", "Provinsi", "Kab Kota"):
        df_pct[col] = (
            df_pct[col]
            .apply(lambda x: x.strip() if isinstance(x, str) and x.strip() != "" else np.nan)
            .ffill()
        )

    # normalize Route
    df_pct["Route"] = df_pct["Route"].apply(
        lambda v: v.strip().upper() if isinstance(v, str) and v.strip() != "" else np.nan
    )

    # parse percentage values
    def parse_pct(v):
        if pd.isna(v):
            return np.nan
        if isinstance(v, (int, float)):
            return v / 100 if v > 1.5 else v
        s = str(v).replace("%", "").replace(",", "")
        try:
            x = float(s)
            return x / 100 if x > 1.5 else x
        except:
            return np.nan

    for c in df_pct.columns:
        if c not in ("Pulau", "Provinsi", "Kab Kota", "Route", "Type"):
            df_pct[c] = df_pct[c].apply(parse_pct)

    return df_pct, None


