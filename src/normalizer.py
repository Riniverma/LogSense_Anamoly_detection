import os
import re
import pandas as pd


# ============================================================
# PATHS
# ============================================================

OPENSTACK_DIR = "dataset/OpenStack_log/OpenStack_log"
HADOOP_DIR = "dataset/Hadoop_log/Hadoop_log"

OUTPUT_DIR = "results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "normalized_logs.csv")


# ============================================================
# COMMON LOG PARSER
# ============================================================

def create_record(timestamp, source, severity, component, message):
    """
    Creates one common representation for every log line.
    """

    severity = severity.upper()

    is_error = 1 if severity in ["ERROR", "FATAL", "CRITICAL"] else 0

    return {
        "timestamp": timestamp,
        "source": source,
        "severity": severity,
        "component": component,
        "message": message.strip(),
        "is_error": is_error
    }


# ============================================================
# OPENSTACK PARSER
# ============================================================

def parse_openstack_line(line):
    """
    Parses an OpenStack log line.
    """

    pattern = re.compile(
        r"^(.*?)\s+"
        r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)\s+"
        r"(\d+)\s+"
        r"(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL)\s+"
        r"(.*)$"
    )

    match = pattern.match(line)

    if not match:
        return None

    source = match.group(1).strip()
    timestamp = match.group(2)
    process_id = match.group(3)
    severity = match.group(4)
    message = match.group(5)

    component = f"{source} PID:{process_id}"

    return create_record(
        timestamp=timestamp,
        source="OpenStack",
        severity=severity,
        component=component,
        message=message
    )


# ============================================================
# HADOOP PARSER
# ============================================================

def parse_hadoop_line(line):
    """
    Parses a Hadoop container log line.
    """

    pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2}\s+"
        r"\d{2}:\d{2}:\d{2},\d+)\s+"
        r"(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|TRACE)\s+"
        r"\[([^\]]+)\]\s+"
        r"([^:]+):\s*(.*)$"
    )

    match = pattern.match(line)

    if not match:
        return None

    timestamp = match.group(1)
    severity = match.group(2)
    thread = match.group(3)
    component = match.group(4).strip()
    message = match.group(5)

    component = f"{component} [{thread}]"

    return create_record(
        timestamp=timestamp,
        source="Hadoop",
        severity=severity,
        component=component,
        message=message
    )


# ============================================================
# PROCESS OPENSTACK
# ============================================================

def process_openstack():
    records = []

    files = [
        "openstack_normal1.log",
        "openstack_normal2.log",
        "openstack_abnormal.log"
    ]

    for filename in files:

        filepath = os.path.join(OPENSTACK_DIR, filename)

        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue

        print(f"Processing OpenStack: {filename}")

        with open(filepath, "r", encoding="utf-8", errors="ignore") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                record = parse_openstack_line(line)

                if record:
                    records.append(record)

    return records


# ============================================================
# PROCESS HADOOP
# ============================================================

def process_hadoop():

    records = []

    if not os.path.exists(HADOOP_DIR):
        print(f"Hadoop directory not found: {HADOOP_DIR}")
        return records

    # Walk through all application/container folders
    for root, dirs, files in os.walk(HADOOP_DIR):

        for filename in files:

            filepath = os.path.join(root, filename)

            print(f"Processing Hadoop: {filename}")

            try:

                with open(
                    filepath,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    for line in file:

                        line = line.strip()

                        if not line:
                            continue

                        record = parse_hadoop_line(line)

                        if record:
                            records.append(record)

            except Exception as e:

                print(f"Could not read {filepath}: {e}")

    return records


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n==============================")
    print("LOG NORMALIZATION STARTED")
    print("==============================\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Process datasets
    openstack_records = process_openstack()
    hadoop_records = process_hadoop()

    print("\n------------------------------")
    print(f"OpenStack records: {len(openstack_records)}")
    print(f"Hadoop records:    {len(hadoop_records)}")
    print("------------------------------")

    # Combine both sources
    all_records = openstack_records + hadoop_records

    if not all_records:
        print("\nNo records were parsed.")
        print("Please check dataset paths and log formats.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(all_records)

    # Convert timestamps
    df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    format="mixed",
    errors="coerce"
    )

    # Remove invalid timestamps
    df = df.dropna(subset=["timestamp"])

    # Sort chronologically
    df = df.sort_values("timestamp")

    # Reset index
    df = df.reset_index(drop=True)

    # Save
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n==============================")
    print("NORMALIZATION COMPLETED")
    print("==============================")

    print(f"\nTotal records: {len(df)}")

    print(f"\nSaved to:")
    print(OUTPUT_FILE)

    print("\nColumns:")
    print(list(df.columns))

    print("\nSource distribution:")
    print(df["source"].value_counts())

    print("\nSeverity distribution:")
    print(df["severity"].value_counts())


if __name__ == "__main__":
    main()