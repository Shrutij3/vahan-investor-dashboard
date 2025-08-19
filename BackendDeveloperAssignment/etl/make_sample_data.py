"""
etl/make_sample_data.py
Generates realistic synthetic monthly registration data so the app can run out-of-the-box.
"""
from __future__ import annotations
import os, math, random
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(__file__))
PROC = os.path.join(ROOT, "data", "processed")

CATEGORIES = ["2W", "3W", "4W"]
MFR_CATEGORY = {
    "Hero": "2W","Bajaj":"2W","TVS":"2W","Honda":"2W","Suzuki":"2W","Ola":"2W","Ather":"2W",
    "Piaggio":"3W","Mahindra Electric":"3W","YC Electric":"3W","Altigreen":"3W",
    "Maruti":"4W","Hyundai":"4W","Tata":"4W","Mahindra":"4W","Kia":"4W","Toyota":"4W","Honda Cars":"4W"
}

def _seasonal_factor(month: int) -> float:
    return 1.0 + 0.1 * math.sin((month - 1) / 12.0 * 2 * math.pi)

def _trend_factor(t: int) -> float:
    return 1.0 + 0.0025 * t

def _noise() -> float:
    return random.uniform(0.92, 1.08)

def _base_for_category(cat: str) -> int:
    return {"2W": 900_000, "3W": 55_000, "4W": 300_000}[cat]

def generate_sample(start="2023-01", end=None) -> pd.DataFrame:
    if end is None:
        end = pd.Timestamp.today().strftime("%Y-%m")
    months = pd.period_range(start, end, freq="M")
    rows = []
    t = 0
    for p in months:
        for cat in CATEGORIES:
            base = _base_for_category(cat)
            val = base * _seasonal_factor(p.month) * _trend_factor(t) * _noise()
            rows.append({
                "date": p.to_timestamp("M"),
                "state": "India",
                "category": cat,
                "manufacturer": None,
                "registrations": int(max(0, round(val)))
            })
        # allocate per-manufacturer within each category
        for cat in CATEGORIES:
            total_cat = [r for r in rows if r["date"] == p.to_timestamp("M")
                         and r["category"] == cat and r["manufacturer"] is None][0]["registrations"]
            mfrs = [m for m, c in MFR_CATEGORY.items() if c == cat]
            weights = np.abs(np.random.normal(loc=1.0, scale=0.5, size=len(mfrs)))
            weights = weights / weights.sum()
            drift = np.random.uniform(0.95, 1.05, size=len(mfrs))
            weights = weights * drift
            weights = weights / weights.sum()
            alloc = (weights * total_cat).astype(int)
            diff = total_cat - int(alloc.sum())
            if diff != 0:
                alloc[np.argmax(alloc)] += diff
            for mf, val in zip(mfrs, alloc):
                rows.append({
                    "date": p.to_timestamp("M"),
                    "state": "India",
                    "category": cat,
                    "manufacturer": mf,
                    "registrations": int(val)
                })
        t += 1
    df = pd.DataFrame(rows).sort_values(["date", "category", "manufacturer"], na_position="first")
    return df

def ensure_sample_data():
    os.makedirs(PROC, exist_ok=True)
    out_csv = os.path.join(PROC, "registrations_tidy.csv")
    df = generate_sample(end=pd.Timestamp.today().strftime("%Y-%m"))
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} with {len(df):,} rows.")

if __name__ == "__main__":
    ensure_sample_data()
