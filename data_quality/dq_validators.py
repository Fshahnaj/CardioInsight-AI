"""
dq_validators.py

Comprehensive data quality validators for the CardioInsight-AI project.

Runs checks on the de-identified lake dataset and produces:
- Console summary of key data quality indicators
- JSON report written to data/quality_reports/dq_report.json
- HTML report written to data/quality_reports/dq_report.html

Checks include:
- Missing value percentages
- Clinical range checks
- Category validity checks
- Logical consistency rules
- Uniqueness of synthetic patient_id
- Data Quality Scoring (overall + breakdown)
"""

from pathlib import Path
import json
from typing import Dict, Any
from datetime import datetime

import numpy as np
import pandas as pd

LAKE_PATH = Path("data/lake/cardio_deid_data.csv")
REPORT_DIR = Path("data_quality/quality_reports")
JSON_REPORT_PATH = REPORT_DIR / "dq_report.json"
HTML_REPORT_PATH = REPORT_DIR / "dq_report.html"


# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------

def load_lake_dataset(path: Path) -> pd.DataFrame:
    print(f"[DQ] Loading lake dataset from {path} ...")
    df = pd.read_csv(path, parse_dates=["measure_date", "measure_month"])
    print(f"[DQ] Shape: {df.shape}")
    return df


# -----------------------------------------------------------
# CHECKS: Missing Values
# -----------------------------------------------------------

def missing_value_checks(df: pd.DataFrame) -> Dict[str, Any]:
    pct_missing = df.isna().mean() * 100
    percent_missing = {col: float(val) for col, val in pct_missing.items()}
    return {
        "description": "Percentage of missing values per column",
        "percent_missing": percent_missing,
    }


# -----------------------------------------------------------
# CHECKS: Clinical Ranges
# -----------------------------------------------------------

def clinical_range_checks(df: pd.DataFrame) -> Dict[str, Any]:
    def in_range(series, low, high) -> bool:
        return bool(((series >= low) & (series <= high)).all())

    checks = {
        "age_years_18_100": in_range(df["age_years"], 18, 100),
        "height_120_220_cm": in_range(df["height"], 120, 220),
        "weight_35_250_kg": in_range(df["weight"], 35, 250),
        "ap_hi_80_250": in_range(df["ap_hi"], 80, 250),
        "ap_lo_40_160": in_range(df["ap_lo"], 40, 160),
    }

    violations = {
        "age_out_of_range": int((~df["age_years"].between(18, 100)).sum()),
        "height_out_of_range": int((~df["height"].between(120, 220)).sum()),
        "weight_out_of_range": int((~df["weight"].between(35, 250)).sum()),
        "ap_hi_out_of_range": int((~df["ap_hi"].between(80, 250)).sum()),
        "ap_lo_out_of_range": int((~df["ap_lo"].between(40, 160)).sum()),
    }

    return {
        "description": "Clinical range checks for key numeric metrics",
        "all_pass": bool(all(checks.values())),
        "checks": {k: bool(v) for k, v in checks.items()},
        "violations": violations,
    }


# -----------------------------------------------------------
# CHECKS: Category Validity
# -----------------------------------------------------------

def category_validity_checks(df: pd.DataFrame) -> Dict[str, Any]:
    valid_lab_codes = {1, 2, 3}
    valid_age_bands = {"18-29", "30-39", "40-49", "50-59", "60-69", "70+"}
    valid_bmi_bands = {"underweight", "normal", "overweight", "obese"}

    checks = {
        "cholesterol_valid_codes":
            bool(set(df["cholesterol_level"].unique()).issubset(valid_lab_codes)),
        "glucose_valid_codes":
            bool(set(df["glucose_level"].unique()).issubset(valid_lab_codes)),
        "age_band_valid":
            bool(set(df["age_band"].unique()).issubset(valid_age_bands)),
        "bmi_band_valid":
            bool(set(df["bmi_band"].unique()).issubset(valid_bmi_bands)),
    }

    return {
        "description": "Category validity checks for lab codes and banded fields",
        "checks": checks,
    }


# -----------------------------------------------------------
# CHECKS: Logical Consistency
# -----------------------------------------------------------

def logical_consistency_checks(df: pd.DataFrame) -> Dict[str, Any]:
    cond_bp = (df["ap_hi"] >= df["ap_lo"])
    cond_bmi = (df["bmi"] > 0)
    cond_age = (df["age_days"] > 0)

    violations = {
        "bp_logic_violations": int((~cond_bp).sum()),
        "bmi_logic_violations": int((~cond_bmi).sum()),
        "age_days_logic_violations": int((~cond_age).sum())
    }

    checks = {
        "ap_hi_ge_ap_lo": bool(cond_bp.all()),
        "bmi_positive": bool(cond_bmi.all()),
        "age_days_positive": bool(cond_age.all())
    }

    return {
        "description": "Logical rules across related columns",
        "checks": checks,
        "violations": violations,
    }


# -----------------------------------------------------------
# CHECKS: Uniqueness
# -----------------------------------------------------------

def uniqueness_checks(df: pd.DataFrame) -> Dict[str, Any]:
    n_rows = int(len(df))
    n_uniques = int(df["patient_id"].nunique())

    return {
        "description": "Uniqueness checks for synthetic identifiers",
        "patient_id_unique": bool(n_uniques == n_rows),
        "total_rows": n_rows,
        "unique_patient_ids": n_uniques,
        "duplicate_patient_ids": int(n_rows - n_uniques),
    }


# -----------------------------------------------------------
# DATA QUALITY SCORING
# -----------------------------------------------------------

def compute_dq_scores(report: Dict[str, Any]) -> Dict[str, float]:
    n_rows = report["n_rows"]

    # Missingness score
    mv = report["checks"]["missing_values"]["percent_missing"]
    max_missing = max(mv.values()) if mv else 0.0
    missing_score = max(0.0, 100.0 - max_missing)

    # Clinical range score
    cr = report["checks"]["clinical_ranges"]
    total_viol = sum(cr["violations"].values())
    clinical_score = (
        100.0 if total_viol == 0 else max(0.0, 100.0 - min(40.0, 100.0 * (total_viol / n_rows)))
    )

    # Category score
    cv = report["checks"]["category_validity"]["checks"]
    category_score = 100.0 * sum(cv.values()) / len(cv)

    # Logical score
    lc = report["checks"]["logical_consistency"]["checks"]
    logical_score = 100.0 * sum(lc.values()) / len(lc)

    # Uniqueness score
    uq = report["checks"]["uniqueness"]["duplicate_patient_ids"]
    uniqueness_score = 100.0 if uq == 0 else max(
        0.0, 100.0 - min(50.0, 100.0 * (uq / n_rows) * 5)
    )

    # Overall score
    overall_score = (
        missing_score + clinical_score + category_score + logical_score + uniqueness_score
    ) / 5.0

    return {
        "missing_score": round(float(missing_score), 1),
        "clinical_score": round(float(clinical_score), 1),
        "category_score": round(float(category_score), 1),
        "logical_score": round(float(logical_score), 1),
        "uniqueness_score": round(float(uniqueness_score), 1),
        "overall_score": round(float(overall_score), 1),
    }


# -----------------------------------------------------------
# RUN ALL CHECKS
# -----------------------------------------------------------

def run_all_validations() -> Dict[str, Any]:
    df = load_lake_dataset(LAKE_PATH)

    report = {
        "dataset_path": str(LAKE_PATH),
        "n_rows": int(df.shape[0]),
        "n_columns": int(df.shape[1]),
        "checks": {}
    }

    report["checks"]["missing_values"] = missing_value_checks(df)
    report["checks"]["clinical_ranges"] = clinical_range_checks(df)
    report["checks"]["category_validity"] = category_validity_checks(df)
    report["checks"]["logical_consistency"] = logical_consistency_checks(df)
    report["checks"]["uniqueness"] = uniqueness_checks(df)

    # NEW: Add DQ scores
    report["dq_scores"] = compute_dq_scores(report)

    return report


# -----------------------------------------------------------
# SAVE JSON REPORT
# -----------------------------------------------------------

def save_json(report: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[DQ] JSON report written to {path}")


# -----------------------------------------------------------
# PRINT CONSOLE SUMMARY (with scores)
# -----------------------------------------------------------

def print_summary(report: Dict[str, Any]) -> None:
    print("\n============ DATA QUALITY SUMMARY ============\n")

    print(f"Dataset: {report['dataset_path']}")
    print(f"Rows: {report['n_rows']}, Columns: {report['n_columns']}\n")

    # DQ scores
    scores = report["dq_scores"]
    print(f"- Overall Data Quality Score: {scores['overall_score']}%")
    print(f"  • Missingness score:      {scores['missing_score']}%")
    print(f"  • Clinical range score:   {scores['clinical_score']}%")
    print(f"  • Category validity:      {scores['category_score']}%")
    print(f"  • Logical consistency:    {scores['logical_score']}%")
    print(f"  • Uniqueness:             {scores['uniqueness_score']}%\n")

    # Short summary of checks
    print("Checks completed:")
    for section, details in report["checks"].items():
        print(f"  - {section}")

    print("\n==============================================\n")


# -----------------------------------------------------------
# HTML REPORT GENERATION
# -----------------------------------------------------------

def generate_html_report(report: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    scores = report["dq_scores"]
    mv = report["checks"]["missing_values"]
    cr = report["checks"]["clinical_ranges"]
    cv = report["checks"]["category_validity"]
    lc = report["checks"]["logical_consistency"]
    uq = report["checks"]["uniqueness"]

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CardioInsight-AI Data Quality Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 40px;
    background: #f5f5f5;
    color: #333;
}}
.section {{
    background: white;
    padding: 20px;
    margin: 15px 0;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}
.pass {{ color: #2ecc71; font-weight: bold; }}
.fail {{ color: #e74c3c; font-weight: bold; }}
h1, h2 {{ color: #2c3e50; }}
</style>
</head>
<body>

<h1>🏥 CardioInsight-AI Data Quality Report</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<div class="section">
<h2>📊 Executive Summary</h2>
<p><strong>Rows:</strong> {report['n_rows']:,} &nbsp; | &nbsp; <strong>Columns:</strong> {report['n_columns']}</p>
<p><strong>Overall Data Quality Score:</strong> {scores['overall_score']}%</p>
<ul>
    <li>Missingness: {scores['missing_score']}%</li>
    <li>Clinical Ranges: {scores['clinical_score']}%</li>
    <li>Category Validity: {scores['category_score']}%</li>
    <li>Logical Consistency: {scores['logical_score']}%</li>
    <li>Uniqueness: {scores['uniqueness_score']}%</li>
</ul>
</div>

<div class="section">
<h2>1️⃣ Missing Value Checks</h2>
<p>Max Missing: {max(mv['percent_missing'].values()):.2f}%</p>
</div>

<div class="section">
<h2>2️⃣ Clinical Range Violations</h2>
<pre>{json.dumps(cr['violations'], indent=2)}</pre>
</div>

<div class="section">
<h2>3️⃣ Category Validity Checks</h2>
<pre>{json.dumps(cv['checks'], indent=2)}</pre>
</div>

<div class="section">
<h2>4️⃣ Logical Consistency Checks</h2>
<pre>{json.dumps(lc['violations'], indent=2)}</pre>
</div>

<div class="section">
<h2>5️⃣ Uniqueness Checks</h2>
<pre>{json.dumps(uq, indent=2)}</pre>
</div>

</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[DQ] HTML report written to {path}")


# -----------------------------------------------------------
# MAIN
# -----------------------------------------------------------

def main():
    report = run_all_validations()
    print_summary(report)
    save_json(report, JSON_REPORT_PATH)
    generate_html_report(report, HTML_REPORT_PATH)


if __name__ == "__main__":
    main()
