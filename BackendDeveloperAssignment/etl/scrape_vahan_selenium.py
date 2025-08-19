"""
etl/scrape_vahan_selenium.py
Selenium skeleton to capture tables from the Vahan dashboard.
You MUST inspect the page and adapt selectors. Prefer reverse-engineering XHR/JSON endpoints instead.
"""
from __future__ import annotations
import os, time, argparse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"

def start_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    return webdriver.Chrome(options=opts)

def scrape_months(start_month: str, end_month: str):
    driver = start_driver(headless=True)
    try:
        driver.get(URL)
        # TODO: use DevTools to find JSON endpoints (preferred). Otherwise:
        # - locate start/end date controls
        # - set them for each month
        # - click 'Search' and parse result table with pandas.read_html
        months = pd.period_range(start_month, end_month, freq="M")
        all_rows = []
        for p in months:
            # Implement interactions using driver.find_element(...)
            # Example placeholder (you must fill actual selectors):
            time.sleep(1.0)
            tables = driver.find_elements(By.TAG_NAME, "table")
            if not tables:
                continue
            html = tables[0].get_attribute("outerHTML")
            df = pd.read_html(html)[0]
            # TODO normalize df columns -> date, category, manufacturer, registrations
            # df['date'] = p.to_timestamp('M')
            # all_rows.append(df_normalized)
            time.sleep(0.5)
        if all_rows:
            return pd.concat(all_rows, ignore_index=True)
        return pd.DataFrame(columns=["date", "category", "manufacturer", "registrations"])
    finally:
        driver.quit()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2023-01")
    ap.add_argument("--end", default=pd.Timestamp.today().strftime("%Y-%m"))
    ap.add_argument("--out", default=os.path.join("data", "raw", "manufacturer_monthly.csv"))
    args = ap.parse_args()
    df = scrape_months(args.start, args.end)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"Wrote {args.out} with {len(df):,} rows.")

if __name__ == "__main__":
    import pandas as pd
    main()
