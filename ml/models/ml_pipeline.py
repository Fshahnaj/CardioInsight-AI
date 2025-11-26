"""
ML Pipeline for CardioInsight-AI
Loads data from the dbt mart `mart_cardio_risk`,
performs preprocessing, trains baseline models,
evaluates performance, and saves outputs.
"""

import os
import duckdb
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import joblib


# ---------------------------
# Load Data from DuckDB Mart
# ---------------------------

def load_data() -> pd.DataFrame:
    """
    Connects to the DuckDB warehouse (dev.duckdb) and loads mart_cardio_risk.
    """
    DB_PATH = r"C:/Users/fujai/CardioInsight-AI/cardioinsight_dbt/dev.duckdb"  

    con = duckdb.connect(DB_PATH)
    df = con.execute("SELECT * FROM main.mart_cardio_risk").df()
    con.close()

    print(f"[ML] Loaded mart_cardio_risk: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


# ---------------------------
# Build & Train Models
# ---------------------------

def build_and_train(df: pd.DataFrame):
    target = "cardiovascular_event"

    # Separate features and target
    X = df.drop(columns=["patient_id", target])
    y = df[target]

    # Identify numeric and categorical columns
    numeric = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical = X.select_dtypes(include=["object", "bool"]).columns.tolist()

    print("[ML] Numeric features:", numeric)
    print("[ML] Categorical features:", categorical)

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ]
    )

    # Models
    log_reg = LogisticRegression(max_iter=1000)
    rf = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Pipelines
    log_pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", log_reg),
        ]
    )

    rf_pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", rf),
        ]
    )

    # Fit models
    print("[ML] Training Logistic Regression...")
    log_pipeline.fit(X_train, y_train)

    print("[ML] Training Random Forest...")
    rf_pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred_proba_log = log_pipeline.predict_proba(X_test)[:, 1]
    y_pred_log = log_pipeline.predict(X_test)
    auc_log = roc_auc_score(y_test, y_pred_proba_log)

    y_pred_proba_rf = rf_pipeline.predict_proba(X_test)[:, 1]
    y_pred_rf = rf_pipeline.predict(X_test)
    auc_rf = roc_auc_score(y_test, y_pred_proba_rf)

    print("\n==== MODEL PERFORMANCE ====")
    print("Logistic Regression ROC-AUC:", round(auc_log, 3))
    print("Random Forest ROC-AUC:     ", round(auc_rf, 3))
    print("\nClassification Report (Random Forest):")
    print(classification_report(y_test, y_pred_rf))

    return log_pipeline, rf_pipeline, auc_log, auc_rf


# ---------------------------
# Save Models
# ---------------------------

def save_models(log_model, rf_model):
    os.makedirs("ml/models", exist_ok=True)
    joblib.dump(log_model, "ml/models/log_reg.pkl")
    joblib.dump(rf_model, "ml/models/random_forest.pkl")
    print("[ML] Saved models to ml/models/")


# ---------------------------
# Main
# ---------------------------

def main():
    df = load_data()
    log_model, rf_model, auc_log, auc_rf = build_and_train(df)
    save_models(log_model, rf_model)


if __name__ == "__main__":
    main()
