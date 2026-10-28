
import os
import re
import pandas as pd

INPUT_FILE = "results/normalized_logs.csv"
OUTPUT_FILE = "results/baseline_results.csv"

ERROR_RATE_THRESHOLD = 0.01

ERROR_SEVERITIES = {"ERROR", "FATAL", "CRITICAL"}
KNOWN_SEVERITIES = {
    "INFO", "WARN", "WARNING", "ERROR",
    "FATAL", "CRITICAL", "DEBUG", "TRACE"
}

ERROR_KEYWORDS = [
    "ERROR", "FATAL", "CRITICAL",
    "EXCEPTION", "FAILED", "FAILURE"
]


def is_keyword_error(row):
    severity = str(row.get("severity", "")).strip().upper()

    # Prefer an explicitly parsed severity
    if severity in KNOWN_SEVERITIES:
        return int(severity in ERROR_SEVERITIES)

    # Fallback only when severity is missing or unrecognized
    message = str(row.get("message", ""))
    pattern = r"\b(?:" + "|".join(
        re.escape(word) for word in ERROR_KEYWORDS
    ) + r")\b"

    return int(
        re.search(pattern, message, re.IGNORECASE) is not None
    )


def main():
    if not os.path.exists(INPUT_FILE):
        print("Input file not found:", INPUT_FILE)
        return

    df = pd.read_csv(INPUT_FILE)

    required = {"timestamp", "source", "severity", "message"}
    missing = required - set(df.columns)

    if missing:
        print("Missing columns:", sorted(missing))
        return

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], errors="coerce"
    )
    df = df.dropna(subset=["timestamp"]).copy()

    df["severity"] = df["severity"].fillna("").astype(str).str.upper()
    df["message"] = df["message"].fillna("").astype(str)

    df["keyword_error"] = df.apply(is_keyword_error, axis=1)

    df["keyword_warning"] = df["severity"].isin(
        ["WARN", "WARNING"]
    ).astype(int)

    df["window_start"] = df["timestamp"].dt.floor("5min")

    features = df.groupby(
        ["source", "window_start"], dropna=False
    ).agg(
        total_logs=("message", "size"),
        keyword_error_count=("keyword_error", "sum"),
        warning_count=("keyword_warning", "sum")
    ).reset_index()

    features["error_rate"] = (
        features["keyword_error_count"] / features["total_logs"]
    )

    features["baseline_anomaly"] = (
        features["error_rate"] > ERROR_RATE_THRESHOLD
    ).astype(int)

    features = features.sort_values(
        "error_rate", ascending=False
    ).reset_index(drop=True)

    features["rank"] = range(1, len(features) + 1)

    os.makedirs("results", exist_ok=True)
    features.to_csv(OUTPUT_FILE, index=False)

    print("\n===== KEYWORD BASELINE COMPLETED =====")
    print("Threshold:", ERROR_RATE_THRESHOLD)
    print("Total windows:", len(features))
    print("Flagged windows:", int(features["baseline_anomaly"].sum()))

    print("\nError severity counts:")
    print(df["severity"].value_counts())

    print("\nFlagged windows by source:")
    print(features.groupby("source")["baseline_anomaly"].sum())

    print("\nTop 10 suspicious windows:")
    print(features[
        [
            "source", "window_start", "total_logs",
            "keyword_error_count", "error_rate",
            "baseline_anomaly", "rank"
        ]
    ].head(10).to_string(index=False))

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

