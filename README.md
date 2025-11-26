# CardioInsight-AI: Cardiovascular Risk Analytics Platform 🩺📊

**Enterprise-grade healthcare analytics platform** for cardiovascular risk assessment, built on a Kaggle dataset of ~70,000 patient records.

CardioInsight-AI showcases **production-style data engineering, data quality, ML modeling, and BI dashboarding** in one cohesive, end-to-end project:

- ✅ HIPAA-style **de-identification** and clinical feature engineering  
- ✅ **20+ data quality checks** with JSON + HTML reports  
- ✅ **dbt + DuckDB** star schema and marts for analytics  
- ✅ **ML pipeline** (Logistic Regression + Random Forest) — **ROC-AUC ≈ 0.79**  
- ✅ **Power BI dashboard** with population insights & patient-level risk drilldown  

This system mirrors real workflows used in **hospital analytics teams** (e.g., Duke Health, UNC Health, CVS Health/Optum, Mayo Clinic).

---

## 1. Project Overview

### 1.1 Business Question

> **Can we build an end-to-end platform that turns raw cardiovascular measurements into high-quality, explainable risk insights for clinicians and decision makers?**

### 1.2 Solution

CardioInsight-AI answers this by:

- Ingesting and **de-identifying** a publicly available cardiovascular dataset  
- Cleaning, validating, and transforming it into a **star schema analytics mart**  
- Training **ML models** to predict cardiovascular events  
- Delivering insights through a **two-page Power BI report**:
  - **Page 1:** Population Risk Overview & Segment Analysis  
  - **Page 2:** Patient Risk Explorer & Clinical Drilldown  

---

## 2. Architecture (Narrative)

### 2.1 Raw Data → De-identification (Python)

- Read `cardio_train.csv` (~70K rows)  
- Remove direct identifiers  
- Create `patient_id`, `age_years`, `age_band`, `bmi`, `bmi_band`  
- Engineer clinical features:
  - Pulse pressure  
  - Hypertension flag  
  - Cholesterol/glucose categories  
- Output → `data/lake/cardio_deid_data.csv`  

### 2.2 Data Quality & Validation

Script: `data_quality/dq_validators.py`  

Performs:

- Missingness checks  
- Clinical range checks (age, BP, BMI, height, weight)  
- Logical consistency (e.g., `ap_hi ≥ ap_lo`)  
- Uniqueness of `patient_id`  

Outputs:

- `data/quality_reports/dq_report.json`  
- `data/quality_reports/dq_report.html`  

### 2.3 Analytics Warehouse (dbt + DuckDB)

- Warehouse file: `cardio_warehouse.duckdb`  
- dbt models:
  - **Staging model:** `stg_cardioinsight`  
  - **Mart:** `mart_cardio_risk`  

dbt tests enforce:

- Not-null constraints  
- Accepted values  
- Uniqueness of `patient_id`  

### 2.4 Machine Learning Layer

Script: `ml/models/ml_pipeline.py`  

- Loads `mart_cardio_risk`  
- Performs train/test split  
- Trains two models:
  - Logistic Regression  
  - Random Forest  
- Achieves **Logistic Regression ROC-AUC ≈ 0.79**  
- Saves artifacts to `ml/models/artifacts/`  

### 2.5 Analytics & BI Layer

Script: `data/exports/export_mart_to_csv.py`  

- Exports BI-ready file: `data/processed/mart_cardio_risk.csv`  

Power BI consumes this CSV to power:

- KPI tiles  
- CVD risk funnel  
- Segment analyses  
- ML-integrated **patient risk explorer**  

---

## 3. System Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE FLOW                         │
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
│ DuckDB Warehouse│  Star schema
└────────┬────────┘
         │  ML training + BI export
┌────────▼────────┐
│   ML Models     │  Logistic + RF classifiers
└────────┬────────┘
         │  Power BI reports
┌────────▼────────┐
│  Insights Layer │  KPIs, funnel, patient explorer
└─────────────────┘
