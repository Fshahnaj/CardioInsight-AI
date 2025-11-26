import duckdb
import pandas as pd
import joblib
import os

WAREHOUSE = "C:/Users/fujai/CardioInsight-AI/cardioinsight_dbt/dev.duckdb"
MODEL_PATH = "C:/Users/fujai/CardioInsight-AI/ml/models/random_forest.pkl"
OUTPUT = "C:/Users/fujai/CardioInsight-AI/ml/models/ml_predictions.csv"

def load_data():
    con = duckdb.connect(WAREHOUSE)
    df = con.execute("SELECT * FROM mart_cardio_risk").df()
    return df

def main():
    print("[ML-EXPORT] Loading mart_cardio_risk...")
    df = load_data()

    print("[ML-EXPORT] Loading trained model...")
    model = joblib.load(MODEL_PATH)

    target = "cardiovascular_event"
    X = df.drop(columns=["patient_id", target])

    print("[ML-EXPORT] Generating predictions...")
    pred_prob = model.predict_proba(X)[:, 1]
    pred_label = model.predict(X)

    export_df = pd.DataFrame({
        "patient_id": df["patient_id"],
        "predicted_prob": pred_prob,
        "predicted_label": pred_label
    })

    os.makedirs("data", exist_ok=True)
    export_df.to_csv(OUTPUT, index=False)

    print(f"[ML-EXPORT] Saved predictions to {OUTPUT}")
    print(export_df.head())

if __name__ == "__main__":
    main()
