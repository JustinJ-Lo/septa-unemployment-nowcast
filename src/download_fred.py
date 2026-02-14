"""
Download unemployment data from FRED for use in the nowcasting pipeline.

This script fetches a single macro series and writes a raw CSV
that downstream steps can build on.
"""

from pathlib import Path
import pandas as pd
from pandas_datareader import data as web


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Placeholder series used to validate the pipeline end-to-end.
# This will be replaced with the Philadelphia MSA unemployment series.
FRED_SERIES_ID = "PHIL942UR"


# ---------------------------------------------------------------------
# Data access
# ---------------------------------------------------------------------

def fetch_fred_series(series_id: str, start_date: str) -> pd.DataFrame:
    """
    Fetch a single time series from FRED and return a tidy DataFrame.
    """
    df = web.DataReader(series_id, "fred", start_date)
    df = df.reset_index()
    df.columns = ["date", "value"]
    return df


# ---------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------

def main() -> None:
    start_date = "2000-01-01"

    df = fetch_fred_series(
        series_id=FRED_SERIES_ID,
        start_date=start_date,
    )

    out_path = RAW_DIR / f"fred_{FRED_SERIES_ID.lower()}.csv"
    df.to_csv(out_path, index=False)

    print(f"Wrote FRED series '{FRED_SERIES_ID}' to {out_path}")


if __name__ == "__main__":
    main()
