"""
build_warehouse.py

Builds star-schema style warehouse tables from the de-identified
cardiovascular dataset produced by hipaa_de_identification.py.

Outputs:
- data/warehouse/dim_patient.csv
- data/warehouse/dim_time.csv
- data/warehouse/dim_lab.csv
- data/warehouse/fact_clinical_metrics.csv
"""

from pathlib import Path
import pandas as pd

LAKE_PATH = Path("data/lake/cardio_deid_data.csv")
WH_PATH = Path("data/warehouse")


def bp_to_band(ap_hi: float) -> str:
    """Rough blood pressure category based on systolic (ap_hi)."""
    if ap_hi < 120:
        return "normal"
    elif ap_hi < 130:
        return "elevated"
    elif ap_hi < 140:
        return "stage1"
    elif ap_hi < 180:
        return "stage2"
    else:
        return "hypertensive_crisis"


def build_dim_patient(df: pd.DataFrame) -> pd.DataFrame:
    base = (
        df[["patient_id", "gender", "age_band", "bmi_band", "smoke", "alcohol", "active"]]
        .drop_duplicates()
        .copy()
    )

    base = base.rename(
        columns={
            "smoke": "smoker_flag",
            "alcohol": "alcohol_flag",
            "active": "active_flag",
        }
    )

    base.insert(0, "patient_key", range(1, len(base) + 1))
    return base


def build_dim_time(df: pd.DataFrame) -> pd.DataFrame:
    # Use measure_month as the grain (coarser, privacy-friendly)
    base = (
        df[["measure_month"]]
        .drop_duplicates()
        .copy()
    )
    base = base.rename(columns={"measure_month": "date"})

    base["year"] = base["date"].dt.year
    base["month"] = base["date"].dt.month
    base["quarter"] = base["date"].dt.quarter

    base.insert(0, "date_key", range(1, len(base) + 1))
    return base


def build_dim_lab(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["bp_band"] = tmp["ap_hi"].apply(bp_to_band)

    base = (
        tmp[["cholesterol_level", "glucose_level", "bp_band"]]
        .drop_duplicates()
        .copy()
    )

    base.insert(0, "lab_key", range(1, len(base) + 1))
    return base


def build_fact_clinical_metrics(
    df: pd.DataFrame,
    dim_patient: pd.DataFrame,
    dim_time: pd.DataFrame,
    dim_lab: pd.DataFrame,
) -> pd.DataFrame:
    tmp = df.copy()
    tmp["bp_band"] = tmp["ap_hi"].apply(bp_to_band)

    # Join to get foreign keys
    fact = tmp.merge(
        dim_patient[["patient_key", "patient_id"]],
        on="patient_id",
        how="left",
    ).merge(
        dim_time[["date_key", "date"]],
        left_on="measure_month",
        right_on="date",
        how="left",
    ).merge(
        dim_lab[["lab_key", "cholesterol_level", "glucose_level", "bp_band"]],
        on=["cholesterol_level", "glucose_level", "bp_band"],
        how="left",
    )

    # Keep only keys + key clinical measures + target
    fact_final = fact[
        [
            "patient_key",
            "date_key",
            "lab_key",
            "bmi",
            "ap_hi",
            "ap_lo",
            "bp_diff",
            "cholesterol_level",
            "glucose_level",
            "target_cvd",
        ]
    ].copy()

    return fact_final


def main():
    print("[WAREHOUSE] Reading de-identified lake data...")
    df = pd.read_csv(LAKE_PATH, parse_dates=["measure_date", "measure_month"])

    print(f"[WAREHOUSE] Lake shape: {df.shape}")

    print("[WAREHOUSE] Building dim_patient...")
    dim_patient = build_dim_patient(df)

    print("[WAREHOUSE] Building dim_time...")
    dim_time = build_dim_time(df)

    print("[WAREHOUSE] Building dim_lab...")
    dim_lab = build_dim_lab(df)

    print("[WAREHOUSE] Building fact_clinical_metrics...")
    fact_clinical = build_fact_clinical_metrics(df, dim_patient, dim_time, dim_lab)

    WH_PATH.mkdir(parents=True, exist_ok=True)

    dim_patient.to_csv(WH_PATH / "dim_patient.csv", index=False)
    dim_time.to_csv(WH_PATH / "dim_time.csv", index=False)
    dim_lab.to_csv(WH_PATH / "dim_lab.csv", index=False)
    fact_clinical.to_csv(WH_PATH / "fact_clinical_metrics.csv", index=False)

    print(f"[WAREHOUSE] dim_patient: {dim_patient.shape}")
    print(f"[WAREHOUSE] dim_time: {dim_time.shape}")
    print(f"[WAREHOUSE] dim_lab: {dim_lab.shape}")
    print(f"[WAREHOUSE] fact_clinical_metrics: {fact_clinical.shape}")
    print("[WAREHOUSE] Warehouse build completed.")


if __name__ == "__main__":
    main()
