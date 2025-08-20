🚗 Vahan Investor Dashboard

🔹 Overview

Interactive Streamlit dashboard to explore monthly vehicle registration trends.
Covers categories: 2W, 3W, 4W and individual manufacturers.
Includes a full ETL pipeline:
     Generate synthetic sample data.
     Normalize official Vahan CSV exports.
Selenium scraper skeleton (for advanced users).
Automatically falls back to synthetic data if no processed dataset is available → runs out-of-the-box.

📂 Repository Structure

etl/

make_sample_data.py → generates mock registration data.

process_data.py → normalizes raw Vahan CSV exports.

scrape_vahan_selenium.py → Selenium scraper template (requires customization).

app/

app.py → launches the Streamlit dashboard.

data/

raw/ → place Vahan CSV exports here.

processed/ → processed tidy dataset is written here.

requirements.txt → project dependencies.

⚙️ Setup Instructions

1.Create and activate a virtual environment

python -m venv venv
venv\Scripts\activate      # Windows


2.Install dependencies

pip install -r requirements.txt


▶️ Usage
Option A: Run with synthetic data
streamlit run app/app.py


📊 Dashboard Features

Sidebar filters: date range, category, manufacturer.

KPIs: total registrations with YoY % and QoQ %.

Interactive charts:

Line chart by category.

Line chart by manufacturer.

League table: manufacturers ranked by registrations with YoY/QoQ growth for the latest month.
