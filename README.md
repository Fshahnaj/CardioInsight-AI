# CardioInsight-AI: Cardiovascular Risk Analytics Platform 🩺📊

**Enterprise-grade healthcare analytics platform** for cardiovascular risk assessment, built on a Kaggle dataset of ~70,000 patient records.

CardioInsight-AI delivers full-stack analytics:

- HIPAA-style de-identification & clinical feature engineering  
- 20+ automated data quality checks (JSON + HTML reports)  
- dbt + DuckDB star schema & marts  
- ML pipeline (Logistic Regression + Random Forest) — **ROC-AUC ≈ 0.79**  
- Power BI dashboard with population insights & patient-level drilldown  

This mirrors workflows used in real healthcare analytics teams (Duke Health, UNC Health, CVS Health/Optum, Mayo Clinic).

---

## 1. Project Overview

### Business Question

*Can we build an end-to-end platform that turns raw cardiovascular measurements into high-quality, explainable insights for clinicians?*

CardioInsight-AI accomplishes this by:

- De-identifying & preparing raw clinical data  
- Validating & transforming it into a dbt-managed star schema  
- Training ML models for cardiovascular event prediction  
- Delivering insights through a dual-page Power BI dashboard  

---

## 2. Architecture

### Raw Data → De-Identification (Python)

- Removes identifiers  
- Creates: `patient_id`, `age_years`, `age_band`, `bmi`, `bmi_band`  
- Engineers features (pulse pressure, cholesterol category, hypertension flag)  
- Output → `data/lake/cardio_deid_data.csv`  

### Data Quality Validation

Checks include:

- Missingness  
- Clinical ranges  
- Logical consistency  
- Uniqueness of `patient_id`  

Outputs:

- `data_quality/quality_reports/dq_report.json`  
- `data_quality/quality_reports/dq_report.html`  

### Analytics Warehouse (dbt + DuckDB)

- Staging model: `stg_cardioinsight.sql`  
- Mart model: `mart_cardio_risk.sql`  
- dbt tests: `not_null`, `unique`, `accepted_values`  

### Machine Learning

- Runs in `ml/models/ml_pipeline.py`  
- Models: Logistic Regression, Random Forest  
- ROC-AUC (Logistic Regression): **0.79**  

### Power BI Layer

Consumes `data/warehouse/mart_cardio_risk.csv` and powers:

- KPI tiles  
- CVD funnel  
- Segment analysis (age band, BMI band, cholesterol, glucose)  
- Patient-level ML risk explorer  

---

## 3. System Architecture Diagram

```text
┌──────────────────────────────────────────────────────────────┐
│                     DATA PIPELINE FLOW                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Raw CSV Data   │  ← Kaggle dataset (~70K records)
└────────┬─────────┘
         │  HIPAA De-ID + Feature Engineering (Python)
         ▼
┌──────────────────┐
│    Data Lake     │  ← De-identified, cleaned data
│ (cardio_deid_*)  │
└────────┬─────────┘
         │  dbt (staging + marts) on DuckDB
         ▼
┌──────────────────┐
│ DuckDB Warehouse │  ← Star schema (staging + marts)
└────────┬─────────┘
         │  ML training + export for BI
         ▼
┌──────────────────┐
│    ML Models     │  ← Logistic Regression, Random Forest
└────────┬─────────┘
         │  Power BI import
         ▼
┌──────────────────┐
│  Insights Layer  │  ← KPIs, CVD funnel, cohort & patient views
└──────────────────┘
