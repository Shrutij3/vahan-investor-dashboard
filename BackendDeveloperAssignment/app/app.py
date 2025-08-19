"""
app/app.py
Streamlit dashboard showing registrations, YoY and QoQ for categories and manufacturers.
"""
from __future__ import annotations
import os, sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Try to use the sample generator if processed data missing
try:
    from etl.make_sample_data import ensure_sample_data
except Exception:
    ensure_sample_data = None

st.set_page_config(page_title="Vahan Investor Dashboard", layout="wide")
st.title("Vehicle Registrations — Investor Dashboard")

@st.cache_data
def load_data():
    proc = os.path.join(ROOT, "data", "processed", "registrations_tidy.csv")
    if not os.path.exists(proc):
        if ensure_sample_data is not None:
            ensure_sample_data()
        else:
            st.error("No processed dataset found. Place CSVs in data/raw/ and run etl/process_data.py")
            st.stop()
    df = pd.read_csv(proc, parse_dates=["date"])
    df["category"] = df["category"].astype("category")
    df["manufacturer"] = df["manufacturer"].astype("string").replace({"nan": None})
    return df

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")
min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.date_input("Date range (month granularity)", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
if isinstance(date_range, tuple):
    d0, d1 = date_range
else:
    d0 = date_range
    d1 = date_range
# convert to month-end timestamps for filtering
d0 = pd.to_datetime(d0).to_period("M").to_timestamp("M")
d1 = pd.to_datetime(d1).to_period("M").to_timestamp("M")

cats = st.sidebar.multiselect("Vehicle category", options=sorted(df["category"].dropna().unique()))
mfrs = st.sidebar.multiselect("Manufacturer", options=sorted(df["manufacturer"].dropna().unique()))

mask = (df["date"].between(d0, d1))
if cats:
    mask &= df["category"].isin(cats)
if mfrs:
    mask &= df["manufacturer"].isin(mfrs)

view = df[mask].copy()

def add_growth(df_in: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    df = df_in.copy()
    df = df.groupby(group_cols + ["date"], as_index=False)["registrations"].sum()
    # previous year
    prev_y = df.copy()
    prev_y["date"] = prev_y["date"] + pd.DateOffset(years=1)
    prev_y = prev_y.rename(columns={"registrations": "registrations_prev_y"})
    df = df.merge(prev_y[group_cols + ["date", "registrations_prev_y"]], on=group_cols + ["date"], how="left")
    # previous quarter (3 months)
    prev_q = df.copy()
    prev_q["date"] = prev_q["date"] + pd.DateOffset(months=3)
    prev_q = prev_q.rename(columns={"registrations": "registrations_prev_q"})
    df = df.merge(prev_q[group_cols + ["date", "registrations_prev_q"]], on=group_cols + ["date"], how="left")
    # compute percent changes safely
    df["YoY %"] = np.where(df["registrations_prev_y"].fillna(0) == 0, np.nan,
                           (df["registrations"] - df["registrations_prev_y"]) / df["registrations_prev_y"] * 100.0)
    df["QoQ %"] = np.where(df["registrations_prev_q"].fillna(0) == 0, np.nan,
                           (df["registrations"] - df["registrations_prev_q"]) / df["registrations_prev_q"] * 100.0)
    return df

# --- KPI snapshot (latest selected month) ---
st.subheader("Overview (latest selected month)")
if view.empty:
    st.info("No data for selected filters/date range.")
else:
    latest = view["date"].max()
    curr_total = int(view[view["date"] == latest]["registrations"].sum())
    prev_y_total = int(view[view["date"] == (latest - pd.DateOffset(years=1))]["registrations"].sum()) \
        if not view[view["date"] == (latest - pd.DateOffset(years=1))].empty else None
    prev_q_total = int(view[view["date"] == (latest - pd.DateOffset(months=3))]["registrations"].sum()) \
        if not view[view["date"] == (latest - pd.DateOffset(months=3))].empty else None

    def pct(curr, prev):
        if prev in (None, 0, np.nan):
            return None
        return (curr - prev) / prev * 100.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total registrations (latest)", f"{curr_total:,}",
              f"{pct(curr_total, prev_y_total):.1f}% YoY" if pct(curr_total, prev_y_total) is not None else "—")
    c2.metric("YoY change", f"{pct(curr_total, prev_y_total):.1f}%" if pct(curr_total, prev_y_total) is not None else "—")
    c3.metric("QoQ change", f"{pct(curr_total, prev_q_total):.1f}%" if pct(curr_total, prev_q_total) is not None else "—")

# --- Trends ---
st.divider()
st.subheader("Trends")

st.markdown("**By Category**")
cat_series = view.groupby(["date", "category"], as_index=False)["registrations"].sum()
if not cat_series.empty:
    fig_cat = px.line(cat_series, x="date", y="registrations", color="category", markers=True,
                      title="Monthly registrations by category")
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("No category data for selected filters/date range.")

st.markdown("**By Manufacturer**")
mfr_series = view.dropna(subset=["manufacturer"]).groupby(["date", "manufacturer"], as_index=False)["registrations"].sum()
if not mfr_series.empty:
    fig_mfr = px.line(mfr_series, x="date", y="registrations", color="manufacturer", markers=True,
                      title="Monthly registrations by manufacturer")
    st.plotly_chart(fig_mfr, use_container_width=True)
else:
    st.info("No manufacturer data for selected filters/date range.")

# --- League table: Latest month per-manufacturer with YoY & QoQ ---
st.divider()
st.subheader("Manufacturers — Latest month (registrations, YoY %, QoQ %)")
if view.dropna(subset=["manufacturer"]).empty:
    st.info("No manufacturer-level data in selection.")
else:
    grow = add_growth(view.dropna(subset=["manufacturer"]), ["manufacturer"])
    latest_table = grow[grow["date"] == grow["date"].max()].copy()
    latest_table = latest_table[["manufacturer", "registrations", "YoY %", "QoQ %"]]
    latest_table = latest_table.sort_values("registrations", ascending=False)
    st.dataframe(latest_table.round(1), use_container_width=True)

st.caption("Tip: adjust the sidebar date range and filters to explore trends & growth metrics.")





# # create virtual env
# python -m venv .venv

# # activate (Windows PowerShell / Git Bash)
# .venv/Scripts/activate

# # install dependencies
# pip install -r requirements.txt

# # run app
# streamlit run app/app.py



# Connection error
# Is Streamlit still running? If you accidentally stopped Streamlit, just restart it in your terminal:

# streamlit run yourscript.py

# for run
