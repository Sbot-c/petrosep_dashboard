# PetroSep Investor Data Room

A Streamlit dashboard that backs the PetroSep pitch deck's pricing and market
claims with the underlying cost model and a 1,200-respondent synthetic market
survey.

## What's inside

| Page | What it shows |
|---|---|
| **Overview** (`app.py`) | Headline metrics, pricing snapshot, purchase intent by price point, top pain-point stats |
| **Pricing & Cost** | BOM waterfall to fully-loaded cost, margin by pricing scenario, alternative payment structures |
| **TCO & Payback** | PetroSep vs. PTFE/Viton vs. additive-route cost over 24 months, plus an interactive breakeven slider |
| **Survey Explorer** | Full 1,200-respondent panel with live filters (city tier, region, vehicle type, price point, income, E20 compatibility) across price sensitivity, demographics, pain points, and payment/motivator tabs; raw data + CSV export |

Data lives as plain CSVs in `data/`, generated from:
- `PetroSep_Pricing_Model.xlsx` (cost build-up, pricing scenarios, TCO)
- `PetroSep_Synthetic_Survey.xlsx` (1,200-row respondent panel)

All figures are illustrative and pre-diligence, as noted in the source workbooks.

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
│   └── 3_Survey_Explorer.py
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
