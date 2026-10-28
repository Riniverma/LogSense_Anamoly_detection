import pandas as pd
import os


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = "results/normalized_logs.csv"
OUTPUT_FILE = "results/window_features.csv"


# ============================================================
# SETTINGS
# ============================================================

WINDOW_SIZE = "5min"


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n======================================")
    print("TIME WINDOW & FEATURE GENERATION")
    print("======================================\n")

    # --------------------------------------------------------
    # Load normalized logs
    # --------------------------------------------------------

    if not os.path.exists(INPUT_FILE):
        print(f"Input file not found: {INPUT_FILE}")
        return

    print("Loading normalized logs...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Total log records: {len(df)}")

    # --------------------------------------------------------
    # Convert timestamp
    # --------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Remove invalid timestamps
    df = df.dropna(subset=["timestamp"])

    # --------------------------------------------------------
    # Normalize severity
    # --------------------------------------------------------

    df["severity"] = df["severity"].astype(str).str.upper()

    # --------------------------------------------------------
    # Create helper columns
    # --------------------------------------------------------

    df["is_warning"] = df["severity"].isin(
        ["WARN", "WARNING"]
    ).astype(int)

    df["is_critical"] = (
        df["severity"] == "CRITICAL"
    ).astype(int)

    df["is_fatal"] = (
        df["severity"] == "FATAL"
    ).astype(int)

    # --------------------------------------------------------
    # Create time window
    # --------------------------------------------------------

    df["window_start"] = df["timestamp"].dt.floor(WINDOW_SIZE)

    # --------------------------------------------------------
    # Group by SOURCE + TIME WINDOW
    # --------------------------------------------------------

    grouped = df.groupby(
        ["source", "window_start"],
        dropna=False
    )

    # --------------------------------------------------------
    # Generate features
    # --------------------------------------------------------

    features = grouped.agg(
        total_logs=("message", "count"),

        error_count=("is_error", "sum"),

        warning_count=("is_warning", "sum"),

        critical_count=("is_critical", "sum"),

        fatal_count=("is_fatal", "sum"),

        unique_components=("component", "nunique")
    ).reset_index()

    # --------------------------------------------------------
    # Calculate rates
    # --------------------------------------------------------

    features["error_rate"] = (
        features["error_count"]
        / features["total_logs"]
    )

    features["warning_rate"] = (
        features["warning_count"]
        / features["total_logs"]
    )

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    features = features.sort_values(
        ["source", "window_start"]
    )

    features = features.reset_index(drop=True)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    features.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print("\n======================================")
    print("FEATURE GENERATION COMPLETED")
    print("======================================")

    print(f"\nTotal windows: {len(features)}")

    print("\nColumns:")
    print(list(features.columns))

    print("\nWindows by source:")

    print(
        features["source"].value_counts()
    )

    print("\nFirst 10 windows:")

    print(
        features.head(10).to_string(
            index=False
        )
    )

    print("\nSaved to:")

    print(OUTPUT_FILE)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()