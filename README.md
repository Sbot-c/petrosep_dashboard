# PetroSep Investor Data Room

A Streamlit dashboard that backs the PetroSep pitch deck's pricing and market
claims with the underlying cost model and a 1,200-respondent synthetic market
survey — now with a custom design system and an interactive scenario-modeling
tool on top of the original four data views.

## What's inside

| Page | What it shows |
|---|---|
| **Overview** (`app.py`) | Hero banner, headline KPI cards, pricing snapshot, purchase intent by price point, market-pain stat strip, quick-nav cards |
| **Pricing & Cost** | BOM waterfall, cost-by-category donut, margin by pricing scenario, a live margin calculator (price + cost-inflation sliders vs. a margin curve), payment structure cards |
| **TCO & Payback** | PetroSep vs. PTFE/Viton vs. additive-route cost over 24 months, an interactive breakeven slider, and a "suggest from vehicle type" button that pulls a monthly-spend-adjusted assumption straight from the survey panel |
| **Survey Explorer** | Full 1,200-respondent panel with live filters (city tier, region, vehicle type, price point, income, E20 compatibility), active-filter pills, price/demographics/pain/payment tabs, a **cross-tab builder** (pick any two dimensions + a metric → heatmap + pivot table), raw data + CSV export |
| **Scenario Modeling** *(new)* | Combines the cost model with a survey-derived conversion curve (top-2-box "would likely buy" rate at each tested price) to project units, revenue, and gross profit at any price / addressable-market / cost-inflation assumption, plus revenue- and profit-maximizing price markers |

Data lives as plain CSVs in `data/`, generated from:
- `PetroSep_Pricing_Model.xlsx` (cost build-up, pricing scenarios, TCO)
- `PetroSep_Synthetic_Survey.xlsx` (1,200-row respondent panel)

All figures are illustrative and pre-diligence, as noted throughout the app.

## Design system

`utils/styling.py` centralizes the look and feel used by every page:
- A shared color palette (deep teal-blue primary, amber accent) and `Inter` typeface
- `inject_css()` — one call per page for the hero banner, metric-card, and chart styling
- `hero()`, `section_header()`, `metric_card()`, `stat_strip()` — reusable HTML builders instead of bare `st.metric`
- `apply_chart_theme()` — applies a consistent Plotly template, fonts, gridlines, and legend placement to every chart

## Run it locally

```bash
git clone https://github.com/<your-username>/petrosep-dashboard.git
cd petrosep-dashboard
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Push to GitHub

```bash
cd petrosep-dashboard
git init
git add .
git commit -m "Initial commit: PetroSep investor dashboard"
git branch -M main
git remote add origin https://github.com/<your-username>/petrosep-dashboard.git
git push -u origin main
```

## Deploy for free on Streamlit Community Cloud

1. Push the repo to GitHub (above).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, pick this repo/branch, and set the main file to `app.py`.
4. Click **Deploy**. Streamlit Cloud installs `requirements.txt` automatically and
   the CSVs in `data/` ship with the repo, so no extra configuration is needed.

Any push to `main` auto-redeploys the app.

## Updating the data

If the pricing model or survey changes, regenerate the CSVs and commit them:

```python
import pandas as pd

survey = pd.read_excel("PetroSep_Synthetic_Survey.xlsx", sheet_name="Survey Data")
survey.to_csv("data/survey_data.csv", index=False)
# ...repeat for the other sheets/CSVs as needed
```

## Project structure

```
petrosep-dashboard/
├── app.py                          # Overview page (Streamlit entry point)
├── pages/
│   ├── 1_Pricing_and_Cost.py
│   ├── 2_TCO_and_Payback.py
│   ├── 3_Survey_Explorer.py
│   └── 4_Scenario_Modeling.py      # NEW — interactive price/volume/margin what-if tool
├── utils/
│   ├── __init__.py
│   └── styling.py                  # NEW — shared design system (CSS, colors, chart theme, card builders)
├── data/
│   ├── cost_buildup.csv
│   ├── pricing_scenarios.csv
│   ├── tco_payback.csv
│   ├── payment_structures.csv
│   └── survey_data.csv
├── .streamlit/
│   └── config.toml                 # PetroSep color theme
├── requirements.txt
└── README.md
```
