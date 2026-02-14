"""
Build analysis-ready monthly panel:
- Aggregate SEPTA monthly UPT across all modes
- Merge with Philadelphia MSA unemployment
- Output data/processed/panel_monthly.csv
"""

from pathlib import Path
import re
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

NTD_FILE = "December 2025 Complete Monthly Ridership (with adjustments and estimates)_260202.xlsx"
FRED_FILE = "fred_phil942ur.csv"


def load_septa_monthly_upt() -> pd.DataFrame:
    df = pd.read_excel(RAW_DIR / NTD_FILE, sheet_name="UPT")

    # Filter to SEPTA (exact agency label in the NTD file)
    df = df[df["Agency"] == "Southeastern Pennsylvania Transportation Authority"].copy()
    if df.empty:
        raise ValueError("No rows found for SEPTA. Check the exact Agency label in the UPT sheet.")

    # Month columns are named like "1/2002", "12/2025", etc.
    month_re = re.compile(r"^\s*\d{1,2}/\d{4}\s*$")
    month_cols = [c for c in df.columns if month_re.match(str(c))]

    if not month_cols:
        raise ValueError("No month columns found. Expected columns like '1/2002', '12/2025'.")

    # Use all non-month columns as identifiers (robust if FTA adds metadata columns)
    id_vars = [c for c in df.columns if c not in month_cols]

    df_long = df.melt(
        id_vars=id_vars,
        value_vars=month_cols,
        var_name="month",
        value_name="upt",
    )

    df_long["date"] = pd.to_datetime(df_long["month"].astype(str).str.strip(), format="%m/%Y")
    df_long["upt"] = pd.to_numeric(df_long["upt"], errors="coerce")

    # Aggregate across modes/TOS to total monthly ridership
    df_monthly = (
        df_long.groupby("date", as_index=False)["upt"]
        .sum(min_count=1)
        .sort_values("date")
    )

    return df_monthly


def load_unemployment() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / FRED_FILE)
    df["date"] = pd.to_datetime(df["date"])
    df = df.rename(columns={"value": "unemployment_rate"})
    return df


def main() -> None:
    ridership = load_septa_monthly_upt()
    unemployment = load_unemployment()

    panel = ridership.merge(unemployment, on="date", how="inner")
    panel = panel.dropna(subset=["unemployment_rate"]).sort_values("date")

    out_path = PROCESSED_DIR / "panel_monthly.csv"
    panel.to_csv(out_path, index=False)
    print(f"Wrote analysis-ready panel -> {out_path}")


if __name__ == "__main__":
    main()
