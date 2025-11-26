<!-- README.md for CardioInsight-AI -->

<h1><strong>CardioInsight-AI:Clinical Risk Analytics & Dashboard Platform🩺📊</strong></h1>

<p><strong>Enterprise-grade healthcare analytics platform</strong> for cardiovascular risk assessment, built on a Kaggle dataset of ~70,000 patient records.</p>

<p><strong>CardioInsight-AI</strong> demonstrates production-style:</p>
<ul>
  <li>Data engineering</li>
  <li>Data quality & validation</li>
  <li>ML modeling</li>
  <li>BI dashboarding</li>
</ul>

<p>All in one cohesive project:</p>
<ul>
  <li>HIPAA-style de-identification and clinical feature engineering</li>
  <li>20+ data quality checks with JSON + HTML reports</li>
  <li>dbt + DuckDB star schema and marts for analytics</li>
  <li>ML pipeline (Logistic Regression + Random Forest) — <strong>ROC-AUC ≈ 0.79</strong></li>
  <li>Power BI dashboard with population insights & patient-level risk drilldown</li>
</ul>

<p>This system mirrors real-world workflows used in hospital analytics teams (Duke Health, UNC Health, CVS Health/Optum, Mayo Clinic, etc.).</p>

<hr />

<h2>1. Project Overview</h2>

<h3>Business Question</h3>

<p><em>Can we build an end-to-end platform that turns raw cardiovascular measurements into high-quality, explainable risk insights for clinicians and decision makers?</em></p>

<p><strong>CardioInsight-AI</strong> answers this by:</p>
<ul>
  <li>Ingesting and de-identifying a publicly available cardiovascular dataset</li>
  <li>Cleaning, validating, and transforming it into a star schema analytics mart</li>
  <li>Training ML models to predict cardiovascular events</li>
  <li>Delivering insights through a two-page Power BI report:
    <ul>
      <li><strong>Page 1:</strong> Population Risk Overview &amp; Segment Analysis</li>
      <li><strong>Page 2:</strong> Patient Risk Explorer &amp; Clinical Drilldown</li>
    </ul>
  </li>
</ul>

<hr />

<h2>2. Architecture (Narrative Details)</h2>

<h3>2.1 Raw Data → De-identification (Python)</h3>
<ul>
  <li>Read <code>cardio_train.csv</code> (~70K rows)</li>
  <li>Remove direct identifiers</li>
  <li>Create <code>patient_id</code>, <code>age_years</code>, <code>age_band</code>, <code>bmi</code>, <code>bmi_band</code></li>
  <li>Engineer features:
    <ul>
      <li>Pulse pressure</li>
      <li>Hypertension flag</li>
      <li>Cholesterol/glucose categories</li>
    </ul>
  </li>
  <li>Output → <code>data/lake/cardio_deid_data.csv</code></li>
</ul>

<h3>2.2 Data Quality &amp; Validation</h3>
<ul>
  <li>Script: <code>data_quality/dq_validators.py</code></li>
  <li>Runs:
    <ul>
      <li>Missingness checks</li>
      <li>Clinical range checks (age, BP, BMI, height, weight)</li>
      <li>Logical consistency (<code>ap_hi ≥ ap_lo</code>)</li>
      <li>Uniqueness of <code>patient_id</code></li>
    </ul>
  </li>
  <li>Outputs:
    <ul>
      <li><code>data/quality_reports/dq_report.json</code></li>
      <li><code>data/quality_reports/dq_report.html</code></li>
    </ul>
  </li>
</ul>

<h3>2.3 Analytics Warehouse (dbt + DuckDB)</h3>
<ul>
  <li>Warehouse: <code>cardio_warehouse.duckdb</code></li>
  <li><strong>dbt models:</strong>
    <ul>
      <li>Staging model → <code>stg_cardioinsight</code></li>
      <li>Mart → <code>mart_cardio_risk</code></li>
    </ul>
  </li>
  <li><strong>dbt tests enforce:</strong>
    <ul>
      <li>Not-null constraints</li>
      <li>Accepted values</li>
      <li>Uniqueness of <code>patient_id</code></li>
    </ul>
  </li>
</ul>

<h3>2.4 Machine Learning Layer</h3>
<ul>
  <li>Script: <code>ml/models/ml_pipeline.py</code></li>
  <li>Loads <code>mart_cardio_risk</code></li>
  <li>Performs train/test split</li>
  <li>Trains two models:
    <ul>
      <li>Logistic Regression</li>
      <li>Random Forest</li>
    </ul>
  </li>
  <li>Logistic Regression <strong>ROC-AUC ≈ 0.79</strong></li>
  <li>Saves model artifacts to <code>ml/models/artifacts/</code></li>
</ul>

<h3>2.5 Analytics &amp; BI Layer</h3>
<ul>
  <li>Script: <code>data/exports/export_mart_to_csv.py</code></li>
  <li>Exports BI-ready file:
    <ul>
      <li><code>data/processed/mart_cardio_risk.csv</code></li>
    </ul>
  </li>
  <li>Power BI consumes this CSV to power:
    <ul>
      <li>KPI tiles</li>
      <li>CVD funnel</li>
      <li>Segment analyses</li>
      <li>ML-integrated patient risk explorer</li>
    </ul>
  </li>
</ul>

<hr />

<h2>3. System Architecture Diagram</h2>

<!-- Custom HTML diagram to avoid distorted ASCII -->

<div align="center">
  <table style="border-collapse: separate; border-spacing: 12px; text-align: center;">
    <tr>
      <td style="border: 1px solid #cccccc; padding: 10px; border-radius: 6px;">
        <strong>Raw CSV Data</strong><br />
        <small>Kaggle dataset (~70K)</small>
      </td>
      <td>➡️</td>
      <td style="border: 1px solid #cccccc; padding: 10px; border-radius: 6px;">
        <strong>Data Lake</strong><br />
        <small>De-identified, cleaned data</small><br />
        <small>(Python ETL)</small>
      </td>
      <td>➡️</td>
      <td style="border: 1px solid #cccccc; padding: 10px; border-radius: 6px;">
        <strong>DuckDB Warehouse</strong><br />
        <small>Star schema marts</small><br />
        <small>(dbt models)</small>
      </td>
      <td>➡️</td>
      <td style="border: 1px solid #cccccc; padding: 10px; border-radius: 6px;">
        <strong>ML Models</strong><br />
        <small>Logistic Regression &amp; Random Forest</small>
      </td>
      <td>➡️</td>
      <td style="border: 1px solid #cccccc; padding: 10px; border-radius: 6px;">
        <strong>Insights Layer</strong><br />
        <small>Power BI KPIs, funnel,<br />patient explorer</small>
      </td>
    </tr>
  </table>
</div>

<hr />

<h2>4. Tech Stack</h2>

<h3>Languages &amp; Tools</h3>
<ul>
  <li>Python (<code>pandas</code>, <code>numpy</code>, <code>scikit-learn</code>, <code>duckdb</code>)</li>
  <li><code>dbt-core</code> + <code>dbt-duckdb</code></li>
  <li>Power BI (DAX, M)</li>
  <li>Git, virtualenv</li>
</ul>

<h3>Key Concepts</h3>
<ul>
  <li>HIPAA de-identification</li>
  <li>Data quality validation</li>
  <li>Star schema modeling</li>
  <li>ML classification modeling</li>
  <li>BI visual analytics (clinical context)</li>
</ul>

<hr />

<h2>5. Repository Structure</h2>

<pre>
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
</pre>

<hr />

<h2>6. How to Run the Project Locally</h2>

<h3>6.1 Prerequisites</h3>
<ul>
  <li>Python 3.10+</li>
  <li><code>pip</code> or <code>conda</code></li>
  <li>Power BI Desktop</li>
  <li>Git (optional)</li>
  <li>(Optional) Conda / virtualenv</li>
</ul>

<h3>6.2 Setup</h3>

<pre>
# Clone the repo
git clone https://github.com/&lt;your-username&gt;/CardioInsight-AI.git
cd CardioInsight-AI

# Create and activate a virtual env (recommended)
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
</pre>

<p>Download the Kaggle dataset and place it as:</p>
<pre>data/raw/cardio_raw_data.csv</pre>

<h3>6.3 Run ETL + Data Quality</h3>

<pre>
python etl/hipaa_de_identification.py
python etl/build_warehouse.py
python data_quality/dq_validators.py
</pre>

<p>After this, check:</p>
<ul>
  <li><code>data/lake/cardio_deid_data.csv</code></li>
  <li><code>data/quality_reports/dq_report.json</code></li>
  <li><code>data/quality_reports/dq_report.html</code></li>
</ul>

<h3>6.4 Run dbt Models</h3>

<pre>
cd cardioinsight_dbt

dbt debug
dbt build --full-refresh

# Or run specific models:
dbt run --select stg_cardioinsight
dbt run --select mart_cardio_risk
</pre>

<h3>6.5 Train ML Models</h3>

<pre>
cd ..
python ml/models/ml_pipeline.py
</pre>

<p>This will:</p>
<ul>
  <li>Load <code>mart_cardio_risk</code></li>
  <li>Train Logistic Regression &amp; Random Forest</li>
  <li>Print ROC-AUC and classification metrics</li>
  <li>Save model artifacts</li>
</ul>

<h3>6.6 Export Data for Power BI</h3>

<pre>
python data/exports/export_mart_to_csv.py
</pre>

<p>This writes the BI-ready file:</p>
<pre>data/processed/mart_cardio_risk.csv</pre>

<hr />

<h2>🧠 Machine Learning Results</h2>

<ul>
  <li><strong>Logistic Regression AUC:</strong> ~0.79</li>
  <li><strong>Random Forest AUC:</strong> ~0.77</li>
  <li>Best model integrated into Power BI</li>
  <li>Patient-level predictions include expected vs actual clinical values</li>
</ul>

<hr />

<h2>📊 CardioInsight-AI — Power BI Dashboard</h2>

<h3>Clinical Analytics &amp; Patient Risk Explorer</h3>

<p>This dashboard visualizes cardiovascular risk insights using:</p>
<ul>
  <li>Cleaned &amp; feature-engineered dataset</li>
  <li>dbt-built clinical risk mart</li>
  <li>Logistic Regression ML model</li>
  <li>Patient-level ML risk drilldown</li>
  <li>Population-level epidemiological patterns</li>
</ul>

<h3>📄 Page 1 — Population Cardiovascular Insights</h3>

<ul>
  <li><strong>KPI Tiles:</strong> Total Patients, CVD Risk %, High-Risk Patients</li>
  <li><strong>CVD Risk Funnel:</strong> Population → CVD Events → Hypertension → High Cholesterol</li>
  <li><strong>BMI Band</strong> distribution</li>
  <li><strong>Age Band</strong> donut</li>
  <li>Cholesterol &amp; Glucose stacked bars</li>
  <li>Hypertension distribution by age</li>
  <li><strong>Filter panel:</strong>
    <ul>
      <li>Age Band</li>
      <li>BMI Band</li>
      <li>Cholesterol Category</li>
      <li>Glucose Category</li>
      <li>Smoking Status</li>
      <li>Alcohol Use</li>
      <li>Activity Level</li>
    </ul>
  </li>
</ul>

<h3>📄 Page 2 — Patient Risk Explorer</h3>

<ul>
  <li>Patient selector (drop-down)</li>
  <li>Patient profile panel</li>
  <li><strong>Clinical indicators:</strong>
    <ul>
      <li>Hypertension Status</li>
      <li>ML Risk Flag</li>
      <li>CVD Observed</li>
      <li>Pulse Pressure</li>
    </ul>
  </li>
  <li><strong>ML Output:</strong>
    <ul>
      <li>Predicted CVD Probability (Gauge)</li>
    </ul>
  </li>
  <li><strong>Patient vs Population Comparisons:</strong>
    <ul>
      <li>Systolic BP</li>
      <li>Diastolic BP</li>
      <li>BMI</li>
    </ul>
  </li>
</ul>

<h3>🧪 ML Integration</h3>

<p>The dashboard uses ML predictions generated by the Python pipeline:</p>
<ul>
  <li>Logistic Regression probability</li>
  <li>High/Low Risk classification</li>
  <li>Combined with clinical thresholds (BP, cholesterol, BMI) → strong, explainable indicators</li>
</ul>

<hr />

<h2>🩺 Why This Project Matters</h2>

<p>This platform demonstrates:</p>
<ul>
  <li><strong>Real-world data engineering</strong></li>
  <li><strong>Healthcare-grade data cleaning &amp; validation</strong></li>
  <li><strong>ML model development &amp; deployment</strong></li>
  <li><strong>BI storytelling with clinical insights</strong></li>
  <li><strong>Full end-to-end architecture</strong></li>
</ul>
<p>Aligned with roles in:</p>
<ul>
  <li>Healthcare Analytics</li>
  <li>Biotech</li>
  <li>Data Engineering</li>
  <li>Machine Learning Engineering</li>
</ul>

<hr />

<h2>📬 Contact</h2>

 <p>
    <strong>Email:</strong>
    <a href="mailto:shahnajfujaila@gmail.com">shahnajfujaila@gmail.com</a><br><br>
    <strong>LinkedIn:</strong>
    <a href="www.linkedin.com/in/fujaila-shahnaj-clemson" target="_blank">
      Fujaila-Shahnaj
    </a><br><br>
    <strong>Location:</strong> Raleigh–Durham–Cary, NC
  </p>

<p><strong>Skills:</strong> Power BI • Data Engineering • ML/NLP • Python • dbt • DuckDB</p>
