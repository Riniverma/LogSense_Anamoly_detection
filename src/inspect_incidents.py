
import os
import re
import pandas as pd

# Dataset paths
LABEL_FILE = "dataset/OpenStack_log/OpenStack_log/anomaly_labels.txt"
ABNORMAL_FILE = "dataset/OpenStack_log/OpenStack_log/openstack_abnormal.log"
OUTPUT_FILE = "results/openstack_incident_matches.csv"

# OpenStack log timestamp format:
# 2017-05-14 19:39:01.445
TIMESTAMP_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+)"
)


def main():
    if not os.path.exists(LABEL_FILE):
        print("Label file not found:", LABEL_FILE)
        return

    if not os.path.exists(ABNORMAL_FILE):
        print("Abnormal log file not found:", ABNORMAL_FILE)
        return

    # Read the four labeled VM IDs
    with open(LABEL_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    vm_ids = re.findall(
        r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b",
        text
    )

    vm_ids = sorted(set(vm_ids))

    if not vm_ids:
        print("No VM IDs found in the label file.")
        return

    print("VM IDs found:", len(vm_ids))

    records = []
    match_counts = {vm_id: 0 for vm_id in vm_ids}

    # Search the abnormal log line by line
    with open(
        ABNORMAL_FILE,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        for line_number, line in enumerate(f, start=1):
            matched_ids = [
                vm_id for vm_id in vm_ids
                if vm_id in line
            ]

            if not matched_ids:
                continue

            timestamp_match = TIMESTAMP_PATTERN.search(line)
            timestamp = (
                timestamp_match.group(1)
                if timestamp_match
                else None
            )

            for vm_id in matched_ids:
                match_counts[vm_id] += 1

                records.append({
                    "vm_id": vm_id,
                    "timestamp": timestamp,
                    "line_number": line_number,
                    "message": line.strip()
                })

    # Save matching lines
    os.makedirs("results", exist_ok=True)

    columns = ["vm_id", "timestamp", "line_number", "message"]
    df = pd.DataFrame(records, columns=columns)

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], errors="coerce"
        )
        df = df.sort_values(
            ["vm_id", "timestamp", "line_number"],
            na_position="last"
        )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\n===== INCIDENT LABEL INSPECTION =====")
    print("VM IDs in label file:", len(vm_ids))
    print("Total matching log lines:", len(records))

    print("\nMatches per VM:")
    for vm_id, count in match_counts.items():
        print(f"{vm_id}: {count}")

    if not df.empty:
        print("\nFirst 10 matching records:")
        print(df.head(10).to_string(index=False))
    else:
        print("\nNo matching log lines found.")

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
