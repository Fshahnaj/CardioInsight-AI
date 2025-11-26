CardioInsight-AI: Cardiovascular Risk Analytics Platform 🩺📊

Enterprise-grade healthcare analytics platform for cardiovascular risk assessment, built on a Kaggle dataset of ~70,000 patient records.

CardioInsight-AI demonstrates production-style data engineering, data quality, ML modeling, and BI dashboarding in one cohesive project:

HIPAA-style de-identification and clinical feature engineering

20+ data quality checks with JSON + HTML reports

dbt + DuckDB star schema and marts for analytics

ML pipeline (Logistic Regression + Random Forest) — ROC-AUC ≈ 0.79

Power BI dashboard with population insights & patient-level risk drilldown

This system mirrors real-world workflows used in hospital analytics teams (Duke Health, UNC Health, CVS Health/Optum, Mayo Clinic, etc.).

1. Project Overview
Business Question

Can we build an end-to-end platform that turns raw cardiovascular measurements into high-quality, explainable risk insights for clinicians and decision makers?

CardioInsight-AI answers this by:

Ingesting and de-identifying a publicly available cardiovascular dataset

Cleaning, validating, and transforming it into a star schema analytics mart

Training ML models to predict cardiovascular events

Delivering insights through a two-page Power BI report:

Page 1: Population Risk Overview & Segment Analysis

Page 2: Patient Risk Explorer & Clinical Drilldown

2. Architecture (Narrative Details)
1. Raw Data → De-identification (Python)

Read cardio_train.csv (~70K rows)

Remove direct identifiers

Create patient_id, age_years, age_band, bmi, bmi_band

Engineer features:

Pulse pressure

Hypertension flag

Cholesterol/glucose categories

Output → data/lake/cardio_deid_data.csv

2. Data Quality & Validation

The script data_quality/dq_validators.py runs:

Missingness checks

Clinical range checks (age, BP, BMI, height, weight)

Logical consistency (ap_hi ≥ ap_lo)

Uniqueness of patient_id

Output files:

data/quality_reports/dq_report.json
data/quality_reports/dq_report.html

3. Analytics Warehouse (dbt + DuckDB)

Warehouse file: cardio_warehouse.duckdb

dbt models:

Staging model → stg_cardioinsight

Mart → mart_cardio_risk

dbt tests enforce:

Not-null constraints

Accepted values

Uniqueness of patient_id

4. Machine Learning Layer

ml/models/ml_pipeline.py:

Loads mart_cardio_risk

Train/test split

Trains two models:

Logistic Regression

Random Forest

Logistic Regression ROC-AUC ≈ 0.79

Saves model artifacts to ml/models/artifacts/

5. Analytics & BI Layer

export_mart_to_csv.py exports a BI-ready file:

data/processed/mart_cardio_risk.csv


Power BI consumes this CSV to power:

KPI tiles

CVD funnel

Segment analyses

ML-integrated patient risk explorer

3. System Architecture Diagram
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE FLOW                           │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Raw CSV Data   │  Kaggle dataset (70K)
└────────┬─────────┘
         │  HIPAA De-ID + Feature Engineering
┌────────▼────────┐
│   Data Lake     │  De-identified, cleaned data
└────────┬────────┘
         │  dbt (staging + marts)
┌────────▼────────┐
│  DuckDB Warehouse│  Star schema
└────────┬────────┘
         │  ML training + BI export
┌────────▼────────┐
│  ML Models      │  Logistic + RF classifiers
└────────┬────────┘
         │  Power BI reports
┌────────▼────────┐
│  Insights Layer │  KPIs, funnel, patient explorer
└─────────────────┘

4. Tech Stack
Languages & Tools

Python (pandas, numpy, scikit-learn, duckdb)

dbt-core + dbt-duckdb

Power BI (DAX, M)

Git, virtualenv

Key Concepts

HIPAA de-identification

Data quality validation

Star schema modeling

ML classification modeling

BI visual analytics (clinical context)

5. Repository Structure
CardioInsight-AI/
├─ etl/
│  ├─ hipaa_de_identification.py
│  ├─ build_warehouse.py
│
├─ data/
│  ├─ raw/
│  ├─ lake/
│  ├─ warehouse/
│  └─ exports/export_mart_to_csv.py
│
├─ data_quality/
│  ├─ dq_validators.py
│  └─ quality_reports/
│
├─ cardioinsight_dbt/
│  ├─ dbt_project.yml
│  ├─ models/staging/
│  │   └─ stg_cardioinsight.sql
│  ├─ models/marts/
│  │   └─ mart_cardio_risk.sql
│
├─ ml/models/
│  ├─ ml_pipeline.py
│  └─ artifacts/
│
├─ dashboards/
│  └─ CardioInsight-AI.pbix
│
├─ requirements.txt
└─ README.md

6. How to Run the Project Locally
6.1 Prerequisites

Python 3.10+

pip or conda

Power BI Desktop

Git (optional)

(Optional) Conda / virtualenv

6.2 Setup
# Clone the repo
git clone https://github.com/<your-username>/CardioInsight-AI.git
cd CardioInsight-AI

# Create and activate a virtual env (recommended)
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt


Download the Kaggle dataset and place it as:

data/raw/cardio_raw_data.csv

6.3 Run ETL + Data Quality
python etl/hipaa_de_identification.py
python etl/build_warehouse.py
python data_quality/dq_validators.py


After this, check:

data/lake/cardio_deid_data.csv
data/quality_reports/dq_report.json
data/quality_reports/dq_report.html

6.4 Run dbt Models
cd cardioinsight_dbt

dbt debug
dbt build --full-refresh

# Or run specific models:
dbt run --select stg_cardioinsight
dbt run --select mart_cardio_risk

6.5 Train ML Models
cd ..
python ml/models/ml_pipeline.py


This will:

Load mart_cardio_risk

Train Logistic Regression & Random Forest

Print ROC-AUC and classification metrics

Save model artifacts

6.6 Export Data for Power BI
python data/export_mart_to_csv.py


This writes the BI-ready file:

data/processed/mart_cardio_risk.csv

🧠 Machine Learning Results

Logistic Regression AUC: ~0.79

Random Forest AUC: ~0.77

Best model integrated into Power BI

Patient-level predictions include expected vs actual clinical values

📊 CardioInsight-AI — Power BI Dashboard
Clinical Analytics & Patient Risk Explorer

This dashboard visualizes cardiovascular risk insights using:

Cleaned & feature-engineered dataset

dbt-built clinical risk mart

Logistic Regression ML model

Patient-level ML risk drilldown

Population-level epidemiological patterns

Dashboard Structure
📄 Page 1 — Population Cardiovascular Insights

KPI Tiles: Total Patients, CVD Risk %, High-Risk Patients

CVD Risk Funnel (Population → CVD Events → Hypertension → High Cholesterol)

BMI Band distribution

Age Band donut

Cholesterol & Glucose stacked bars

Hypertension distribution by age

Full filter panel

Age Band

BMI Band

Cholesterol Category

Glucose Category

Smoking Status

Alcohol Use

Activity Level

📄 Page 2 — Patient Risk Explorer

Patient selector (drop-down)

Patient profile panel

Clinical indicators:

Hypertension Status

ML Risk Flag

CVD Observed

Pulse Pressure

ML Output:

Predicted CVD Probability (Gauge)

Patient vs Population Comparisons:

Systolic BP

Diastolic BP

BMI

🧪 ML Integration

The dashboard uses ML predictions generated by the Python pipeline:

Logistic Regression probability

High/Low Risk classification

Combined with clinical thresholds
(BP, cholesterol, BMI) → produces strong, explainable indicators

🩺 Why This Project Matters

This platform demonstrates:

⭐ Real-world data engineering

⭐ Healthcare-grade data cleaning & validation

⭐ ML model development & deployment

⭐ BI storytelling with clinical insights

⭐ Full end-to-end architecture

Aligned with roles in:

Healthcare Analytics

Biotech

Data Engineering

Machine Learning Engineering

📬 Contact

Fujaila Shahnaj
MS Computer Science — Clemson University
Raleigh–Durham–Cary (NC)

Skills: Power BI • Data Engineering • ML/NLP • Python • dbt • DuckDB