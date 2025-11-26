"""
hipaa_de_identification.py

De-identification pipeline for the CardioInsight-AI project.

Implements a HIPAA-inspired approach for transforming the raw
Kaggle cardiovascular dataset into an analytics-ready, de-identified
dataset suitable for modeling and reporting.

Key techniques:
- Age banding instead of exact age
- BMI banding instead of exact BMI
- Synthetic patient_id
- Synthetic measurement dates
- Removal of implausible clinical values
"""

from pathlib import Path
import pandas as pd

# Input / output locations
RAW_PATH = Path("data/raw/cardio_raw_data.csv")
LAKE_PATH = Path("data/lake/cardio_deid_data.csv")


def age_to_band(age_years: int) -> str:
    """Convert exact age in years to coarse age bands."""
    if age_years < 30:
        return "18-29"
    elif age_years < 40:
        return "30-39"
    elif age_years < 50:
        return "40-49"
    elif age_years < 60:
        return "50-59"
    elif age_years < 70:
        return "60-69"
    else:
        return "70+"


def bmi_to_band(bmi: float) -> str:
    """Convert continuous BMI to coarse BMI categories."""
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"


def read_raw_dataset(path: Path) -> pd.DataFrame:
    """Load the raw Kaggle cardiovascular dataset."""
    print(f"[HIPAA-DEID] Reading raw data from {path} ...")
    # Kaggle cardio dataset is semicolon-separated
    df = pd.read_csv(path, sep=";")
    print(f"[HIPAA-DEID] Raw shape: {df.shape}")
    return df


def rename_and_derive_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns and derive core clinical features."""
    df = df.rename(
        columns={
            "age": "age_days",
            "cholesterol": "cholesterol_level",
            "gluc": "glucose_level",
            "alco": "alcohol",
            "cardio": "target_cvd",
        }
    )

    # Age in years
    df["age_years"] = (df["age_days"] / 365.25).round().astype(int)

    # BMI
    df["bmi"] = df["weight"] / ((df["height"] / 100) ** 2)

    # Blood pressure difference
    df["bp_diff"] = df["ap_hi"] - df["ap_lo"]

    return df

import numpy as np
import pandas as pd
def apply_deidentification(df: pd.DataFrame) -> pd.DataFrame:
    """Apply de-identification transformations."""
    # Age & BMI bands
    df["age_band"] = df["age_years"].apply(age_to_band)
    df["bmi_band"] = df["bmi"].apply(bmi_to_band)

    # --- Synthetic measurement date generation ---
    # If measure_date doesn't exist, create a synthetic one
    if "measure_date" not in df.columns:
        # Reproducible random dates between 2010-01-01 and 2015-12-31 (for example)
        rng = np.random.default_rng(42)
        start = pd.to_datetime("2010-01-01")
        end   = pd.to_datetime("2015-12-31")
        n_days = (end - start).days

        random_offsets = rng.integers(0, n_days, size=len(df))
        df["measure_date"] = start + pd.to_timedelta(random_offsets, unit="D")

    # Ensure datetime and clip to a safe range
    df["measure_date"] = pd.to_datetime(df["measure_date"])
    df["measure_date"] = df["measure_date"].clip(
        lower=pd.to_datetime("2010-01-01"),
        upper=pd.to_datetime("2025-12-31"),
    )

    # Month-level coarsening
    df["measure_month"] = df["measure_date"].dt.to_period("M").dt.to_timestamp()

    # Synthetic patient_id (no direct real identifier)
    df["patient_id"] = df.index + 1

    return df


def apply_clinical_sanity_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply basic clinical sanity checks to drop implausible values.
    This is both a data-quality and privacy-friendly step (removes outliers).
    """
    before = df.shape[0]

    df = df[df["age_years"].between(18, 100)]
    df = df[df["height"].between(120, 220)]
    df = df[df["weight"].between(35, 250)]
    df = df[df["ap_hi"].between(80, 250)]
    df = df[df["ap_lo"].between(40, 160)]
    df = df[df["ap_hi"] >= df["ap_lo"]]

    after = df.shape[0]
    print(f"[HIPAA-DEID] Dropped {before - after} records failing sanity checks")
    return df


def write_deidentified_dataset(df: pd.DataFrame, path: Path) -> None:
    """Persist the de-identified dataset to the analytics 'lake' layer."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[HIPAA-DEID] De-identified dataset written to {path} with shape {df.shape}")


def main():
    # Pipeline orchestration
    df = read_raw_dataset(RAW_PATH)
    df = rename_and_derive_columns(df)
    df = apply_deidentification(df)
    df = apply_clinical_sanity_filters(df)
    write_deidentified_dataset(df, LAKE_PATH)


if __name__ == "__main__":
    main()
