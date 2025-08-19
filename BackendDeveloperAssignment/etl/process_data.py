"""
etl/process_data.py
If you export CSVs from the Vahan dashboard, place them into data/raw/ and this script
normalizes them into data/processed/registrations_tidy.csv
Expected raw file names:
 - data/raw/category_monthly.csv        (date, category, registrations)
 - data/raw/manufacturer_monthly.csv    (date, category, manufacturer, registrations)
"""
from __future__ import annotations
import os, sys
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(ROOT, "data", "raw")
PROC = os.path.join(ROOT, "data", "processed")

def _read_if_exists(path: str):
    return pd.read_csv(path) if os.path.exists(path) else None

def process():
    os.makedirs(PROC, exist_ok=True)
    cat_path = os.path.join(RAW, "category_monthly.csv")
    mfr_path = os.path.join(RAW, "manufacturer_monthly.csv")

    cat = _read_if_exists(cat_path)
    mfr = _read_if_exists(mfr_path)

    if cat is None and mfr is None:
        print("No raw files found in data/raw/. Place CSV exports there and re-run.")
        sys.exit(1)

    frames = []
    if cat is not None:
        cat = cat.rename(columns={c: c.strip().lower() for c in cat.columns})
        expected = {"date", "category", "registrations"}
        if not expected.issubset(set(cat.columns)):
            raise ValueError(f"category_monthly.csv must have columns: {expected}")
        cat["manufacturer"] = None
        frames.append(cat[["date", "category", "manufacturer", "registrations"]])

    if mfr is not None:
        mfr = mfr.rename(columns={c: c.strip().lower() for c in mfr.columns})
        expected = {"date", "category", "manufacturer", "registrations"}
        if not expected.issubset(set(mfr.columns)):
            raise ValueError(f"manufacturer_monthly.csv must have columns: {expected}")
        frames.append(mfr[["date", "category", "manufacturer", "registrations"]])

    df = pd.concat(frames, ignore_index=True)
    # align to month-end so QoQ / YoY line up
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("M").dt.to_timestamp("M")
    df["state"] = "India"
    df = df[["date", "state", "category", "manufacturer", "registrations"]]
    out = os.path.join(PROC, "registrations_tidy.csv")
    df.to_csv(out, index=False)
    print(f"Wrote {out} with {len(df):,} rows.")

if __name__ == "__main__":
    process()
