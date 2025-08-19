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

Clone the repository

git clone <your-repo-url>
cd <your-repo>


Create and activate a virtual environment

python -m venv venv
source venv/bin/activate   # macOS/Linux  
venv\Scripts\activate      # Windows


Install dependencies

pip install -r requirements.txt

▶️ Usage
Option A: Run with synthetic data
streamlit run app/app.py


If no processed dataset exists, the app will generate realistic synthetic registrations automatically.

Option B: Run with official Vahan CSV exports

Export and place into data/raw/:

category_monthly.csv

manufacturer_monthly.csv

Process the raw files:

python etl/process_data.py


Launch the dashboard:

streamlit run app/app.py

Option C: Use the Selenium scraper (advanced ⚠️)
python etl/scrape_vahan_selenium.py --start 2023-01 --end 2023-12


Must adapt selectors or reverse-engineer JSON endpoints.

⚠️ Scraping government dashboards may have legal/ethical restrictions. Prefer CSV exports whenever possible.

📊 Dashboard Features

Sidebar filters: date range, category, manufacturer.

KPIs: total registrations with YoY % and QoQ %.

Interactive charts:

Line chart by category.

Line chart by manufacturer.

League table: manufacturers ranked by registrations with YoY/QoQ growth for the latest month.
