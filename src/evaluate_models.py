
import os
import pandas as pd

LOGS_FILE = "results/normalized_logs.csv"
BASELINE_FILE = "results/baseline_results.csv"
ML_FILE = "results/ml_anomaly_results.csv"
OUTPUT_FILE = "results/evaluation_metrics.csv"

TOP_K = 10


def main():
    for path in [LOGS_FILE, BASELINE_FILE, ML_FILE]:
        if not os.path.exists(path):
            print("File not found:", path)
            return

    logs = pd.read_csv(LOGS_FILE)
    baseline = pd.read_csv(BASELINE_FILE)
    ml = pd.read_csv(ML_FILE)

    keys = ["source", "window_start"]

    baseline_needed = keys + [
        "baseline_anomaly", "rank"
    ]
    ml_needed = keys + [
        "ml_anomaly", "anomaly_score", "rank"
    ]

    for name, df, columns in [
        ("Baseline", baseline, baseline_needed),
        ("Isolation Forest", ml, ml_needed)
    ]:
        missing = set(columns) - set(df.columns)
        if missing:
            print(name, "missing columns:", sorted(missing))
            return

    baseline = baseline.rename(
        columns={"rank": "baseline_rank"}
    )
    ml = ml.rename(
        columns={"rank": "ml_rank"}
    )

    merged = baseline.merge(
        ml,
        on=keys,
        how="inner",
        suffixes=("_baseline", "_ml"),
        validate="one_to_one"
    )

    # Count the original log lines for each source.
    line_counts = logs.groupby("source").size().to_dict()

    rows = []

    for model, flag_column, rank_column in [
        ("Keyword Baseline", "baseline_anomaly", "baseline_rank"),
        ("Isolation Forest", "ml_anomaly", "ml_rank")
    ]:
        flagged = merged[merged[flag_column] == 1]
        top_k = merged.nsmallest(
            min(TOP_K, len(merged)), rank_column
        )

        # No verified window-level ground truth is available yet.
        # Therefore precision is deliberately not fabricated.
        for source in sorted(merged["source"].unique()):
            source_flagged = flagged[
                flagged["source"] == source
            ]

            source_lines = line_counts.get(source, 0)

            rows.append({
                "model": model,
                "source": source,
                "total_windows": int(
                    (merged["source"] == source).sum()
                ),
                "flagged_windows": len(source_flagged),
                "total_log_lines": source_lines,
                "alarms_per_1000_lines": (
                    len(source_flagged) / source_lines * 1000
                    if source_lines else None
                ),
                "top_k": min(TOP_K, len(merged)),
                "flagged_in_global_top_k": int(
                    (
                        (top_k["source"] == source) &
                        (top_k[flag_column] == 1)
                    ).sum()
                ),
                "precision_at_k": None,
                "lead_time": None,
                "evaluation_note": (
                    "Precision@K and lead time unavailable "
                    "until verified incident labels/times exist."
                )
            })

    result = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print("\n===== EVALUATION SUMMARY =====")
    print(result.to_string(index=False))
    print("\nSaved to:", OUTPUT_FILE)
    print(
        "\nNote: Alarms per 1000 lines is a rate, "
        "not a verified false-alarm rate."
    )


if __name__ == "__main__":
    main()

