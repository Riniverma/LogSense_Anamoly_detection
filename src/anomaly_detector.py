
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

INPUT_FILE = "results/window_features.csv"
OUTPUT_FILE = "results/ml_anomaly_results.csv"

FEATURES = [
    "total_logs",
    "error_count",
    "warning_count",
    "critical_count",
    "fatal_count",
    "unique_components",
    "error_rate",
    "warning_rate"
]


def main():
    if not os.path.exists(INPUT_FILE):
        print("Error: window_features.csv not found.")
        return

    df = pd.read_csv(INPUT_FILE)

    # Keep only rows with valid feature values
    df[FEATURES] = df[FEATURES].apply(
        pd.to_numeric, errors="coerce"
    )
    df = df.dropna(subset=FEATURES).copy()

    if len(df) < 2:
        print("Not enough windows to train the model.")
        return

    # Scale features
    scaler = StandardScaler()
    X = scaler.fit_transform(df[FEATURES])

    # Train unsupervised anomaly detector
    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42
    )

    model.fit(X)

    # Higher score = more suspicious
    df["anomaly_score"] = -model.score_samples(X)

    # -1 means anomaly, 1 means normal
    df["ml_anomaly"] = (
        model.predict(X) == -1
    ).astype(int)

    # Rank most suspicious windows first
    df = df.sort_values(
        "anomaly_score", ascending=False
    ).reset_index(drop=True)

    df["rank"] = range(1, len(df) + 1)

    os.makedirs("results", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n===== ISOLATION FOREST COMPLETED =====")
    print("Windows analyzed:", len(df))
    print("Flagged as anomalies:", int(df["ml_anomaly"].sum()))

    print("\nAnomalies by source:")
    print(df.groupby("source")["ml_anomaly"].sum())

    print("\nTop 10 suspicious windows:")
    print(
        df[
            [
                "source",
                "window_start",
                "total_logs",
                "error_count",
                "error_rate",
                "anomaly_score",
                "ml_anomaly",
                "rank"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
