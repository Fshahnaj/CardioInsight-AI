<!-- APPLY CALIBRI FONT & SIZE -->
<style>
    body, p, li, td {
        font-family: Calibri, Arial, sans-serif;
        font-size: 12px;
    }
    h1, h2, h3, h4 {
        font-family: Calibri, Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
    }
    code {
        font-size: 12px;
    }
</style>

<h1>CardioInsight-AI: Cardiovascular Risk Analytics Platform 🩺📊</h1>

<p><b>Enterprise-grade healthcare analytics platform</b> for cardiovascular risk assessment, built on a Kaggle dataset of ~70,000 patient records.</p>

<p>CardioInsight-AI delivers full-stack analytics:</p>

<ul>
<li>HIPAA-style de-identification & clinical feature engineering</li>
<li>20+ automated data quality checks (JSON + HTML reports)</li>
<li>dbt + DuckDB star schema & marts</li>
<li>ML pipeline (Logistic Regression + Random Forest) — <b>ROC-AUC ≈ 0.79</b></li>
<li>Power BI dashboard with population insights & patient-level drilldown</li>
</ul>

<p>This mirrors workflows used in real healthcare analytics teams (Duke Health, UNC Health, CVS Health/Optum, Mayo Clinic).</p>

<hr>

<h2>1. Project Overview</h2>

<h3>Business Question</h3>
<p><i>Can we build an end-to-end platform that turns raw cardiovascular measurements into high-quality, explainable insights for clinicians?</i></p>

<p>CardioInsight-AI accomplishes this by:</p>

<ul>
<li>De-identifying & preparing raw clinical data</li>
<li>Validating & transforming it into a dbt-managed star schema</li>
<li>Training ML models for cardiovascular event prediction</li>
<li>Delivering insights through a dual-page Power BI dashboard</li>
</ul>

<hr>

<h2>2. Architecture</h2>

<h3>Raw Data → De-Identification (Python)</h3>
<ul>
<li>Removes identifiers</li>
<li>Creates: patient_id, age_years, age_band, bmi, bmi_band</li>
<li>Engineers features (pulse pressure, cholesterol category, hypertension flag)</li>
<li>Output → <code>data/lake/cardio_deid_data.csv</code></li>
</ul>

<h3>Data Quality Validation</h3>
<p>Checks include:</p>
<ul>
<li>Missingness</li>
<li>Clinical ranges</li>
<li>Logical consistency</li>
<li>Uniqueness of patient_id</li>
</ul>

Outputs:
<ul>
<li><code>dq_report.json</code></li>
<li><code>dq_report.html</code></li>
</ul>

<h3>Analytics Warehouse (dbt + DuckDB)</h3>
<ul>
<li>Staging: <code>stg_cardioinsight.sql</code></li>
<li>Mart: <code>mart_cardio_risk.sql</code></li>
<li>dbt tests: not_null, unique, accepted_values</li>
</ul>

<h3>Machine Learning</h3>
<ul>
<li>Runs in <code>ml_pipeline.py</code></li>
<li>Models: Logistic Regression, Random Forest</li>
<li>ROC-AUC: <b>0.79</b></li>
</ul>

<h3>Power BI Layer</h3>
<p>Consumes <code>mart_cardio_risk.csv</code> and powers:</p>
<ul>
<li>KPI tiles</li>
<li>CVD funnel</li>
<li>Segment analysis</li>
<li>Patient-level ML risk explorer</li>
</ul>

<hr>

<h2>3. System Architecture Diagram</h2>

┌─────────────────────────────────────────────────────────────────────┐
│ DATA PIPELINE FLOW │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ Raw CSV Data │ Kaggle dataset (70K)
└────────┬─────────┘
│ HIPAA De-ID + Feature Engineering
┌────────▼────────┐
│ Data Lake │ De-identified, cleaned data
└────────┬────────┘
│ dbt (staging + marts)
┌────────▼────────┐
│ DuckDB Warehouse│ Star schema
└────────┬────────┘
│ ML training + BI export
┌────────▼────────┐
│ ML Models │ Logistic + RF classifiers
└────────┬────────┘
│ Power BI reports
┌────────▼────────┐
│ Insights Layer │ KPIs, funnel, patient explorer
└─────────────────┘

php-template
Copy code

<hr>

<h2>4. Tech Stack</h2>

<b>Languages & Tools</b>
<ul>
<li>Python (pandas, numpy, scikit-learn, duckdb)</li>
<li>dbt-core + dbt-duckdb</li>
<li>Power BI (DAX, M)</li>
</ul>

<b>Key Concepts</b>
<ul>
<li>HIPAA de-identification</li>
<li>Data quality automation</li>
<li>Star schema modeling</li>
<li>ML classification modeling</li>
<li>BI storytelling</li>
</ul>

<hr>

<h2>5. Repository Structure</h2>

CardioInsight-AI/
├─ etl/
│ ├─ hipaa_de_identification.py
│ ├─ build_warehouse.py
├─ data/
│ ├─ raw/
│ ├─ lake/
│ ├─ warehouse/
│ └─ exports/export_mart_to_csv.py
├─ data_quality/
│ ├─ dq_validators.py
│ └─ quality_reports/
├─ cardioinsight_dbt/
│ ├─ dbt_project.yml
│ ├─ models/staging/
│ ├─ models/marts/
├─ ml/models/
│ ├─ ml_pipeline.py
│ └─ artifacts/
├─ dashboards/
│ └─ CardioInsight-AI.pbix

php-template
Copy code

<hr>

<h2>6. How to Run the Project Locally</h2>

<b>Prerequisites</b>
<ul>
<li>Python 3.10+</li>
<li>pip or conda</li>
<li>Power BI Desktop</li>
</ul>

<b>Setup</b>

```bash
git clone https://github.com/<your-username>/CardioInsight-AI.git
cd CardioInsight-AI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Download data:

bash
Copy code
data/raw/cardio_raw_data.csv
<b>Run ETL + Data Quality</b>

bash
Copy code
python etl/hipaa_de_identification.py
python etl/build_warehouse.py
python data_quality/dq_validators.py
<b>Run dbt</b>

bash
Copy code
cd cardioinsight_dbt
dbt debug
dbt build --full-refresh
<b>Train ML Models</b>

bash
Copy code
python ml/models/ml_pipeline.py
<b>Export for Power BI</b>

bash
Copy code
python data/export_mart_to_csv.py
<hr> <h2>7. Machine Learning Results</h2> <ul> <li>Logistic Regression ROC-AUC: <b>0.79</b></li> <li>Random Forest ROC-AUC: <b>0.77</b></li> <li>Integrated into Power BI</li> </ul> <hr> <h2>8. Power BI Dashboard</h2> <p><b>Page 1: Population Insights</b></p> <ul> <li>KPI tiles</li> <li>CVD funnel</li> <li>BMI & Age distributions</li> <li>Cholesterol & glucose analysis</li> </ul> <p><b>Page 2: Patient Risk Explorer</b></p> <ul> <li>Patient selector</li> <li>ML probability gauge</li> <li>BP & BMI comparisons</li> </ul> <hr> <h2>9. Why This Project Matters</h2> <ul> <li>Healthcare-grade data engineering</li> <li>ML-driven risk prediction</li> <li>Clinical decision support analytics</li> <li>End-to-end architecture</li> </ul> <hr> <h2>10. Contact</h2> <p><b>Fujaila Shahnaj</b><br> MS Computer Science — Clemson University<br> Raleigh–Durham–Cary (NC)<br> <b>Skills:</b> Power BI • Data Engineering • ML/NLP • Python • dbt • DuckDB</p> ```
