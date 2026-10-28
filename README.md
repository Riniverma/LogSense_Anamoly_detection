# 🔍 LogSense — Intelligent Log Anomaly Detection

### Discover suspicious patterns in Hadoop and OpenStack logs using Machine Learning.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Machine%20Learning-Isolation%20Forest-purple" alt="Machine Learning"/>
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Analysis-Offline-orange" alt="Offline Analysis"/>
</p>

## 🚀 Overview

**LogSense** is a log anomaly detection project designed to identify potentially suspicious patterns in heterogeneous enterprise logs. It analyses log data from **Hadoop and OpenStack**, helping users explore unusual activity without manually examining thousands of log records.

The system combines a keyword-based error-rate baseline with **Isolation Forest**, an unsupervised machine learning algorithm. An interactive Streamlit dashboard brings the analysis results together and helps users explore suspicious windows, compare detection methods, and investigate log activity.

## ✨ Key Features

- 📂 **Multi-Source Log Analysis:** Analyse Hadoop and OpenStack log datasets in one workflow.
- 🧹 **Log Normalization:** Convert records into a common format for analysis.
- ⚙️ **Feature Engineering:** Group records into time windows and extract numerical features.
- 🧠 **Unsupervised Anomaly Detection:** Apply Isolation Forest to identify unusual patterns.
- 📊 **Baseline Comparison:** Compare machine learning results with a keyword-based error-rate threshold method.
- 📈 **Interactive Dashboard:** Explore log activity, suspicious windows, and detection trends.
- 🔎 **Anomaly Investigation:** Filter results and inspect potentially suspicious log records.
- 📥 **CSV Export:** Download analysis results for further investigation.

## 📊 Project Highlights

| Project Component | Current Result |
|---|---|
| Log sources | Hadoop and OpenStack |
| Processed log records | 388,716 |
| Extracted time windows | 452 |
| Detection approaches | Keyword Baseline and Isolation Forest |
| Dashboard | Interactive Streamlit application |
| Analysis mode | Offline, using saved log data |

*Note: These are the current processed-data and dashboard results. Detected anomaly candidates are not confirmed system failures.*

## 🛠️ Tech Stack

- **Language:** Python
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **Visualization:** Plotly Express
- **Dashboard:** Streamlit
- **Development Environment:** Visual Studio Code

## 🔄 How It Works

```text
Hadoop Logs + OpenStack Logs
             |
             v
      Log Normalization
             |
             v
    Time-Window Features
             |
       +-----+-----+
       |           |
       v           v
Keyword Baseline  Isolation Forest
       |           |
       +-----+-----+
             |
             v
     Detection Results
             |
             v
   Streamlit Dashboard
             |
             v
 Explore, Compare and Investigate
```

## 📁 Project Structure

```text
LogSense_Anamoly_detection/
├── src/
│   ├── normalizer.py
│   ├── window_features.py
│   ├── baseline.py
│   ├── anomaly_detector.py
│   ├── inspect_incidents.py
│   └── evaluate_models.py
├── dashboard/
│   └── dashboard.py
├── results/
│   ├── normalized_logs.csv
│   ├── window_features.csv
│   ├── baseline_results.csv
│   ├── ml_anomaly_results.csv
│   ├── model_comparison.csv
│   └── evaluation_metrics.csv
├── README.md
└── requirements.txt
```

*The tree lists the main project files; adjust it if your repository has a different structure.*

## 💻 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Riniverma/LogSense_Anamoly_detection.git
cd LogSense_Anamoly_detection
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

If `requirements.txt` is available and complete:

```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard

Ensure the required processed CSV files are present in the `results/` folder, then run:

```bash
streamlit run dashboard/dashboard.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## 📌 Limitations

- The current implementation analyses saved log data; it does not provide live monitoring.
- Anomaly candidates may include normal but unusual activity.
- Verified incident labels are needed to establish detection accuracy reliably.
- Dashboard alert counts alone do not establish that one detection method is better than the other.

## 🔮 Future Improvements

- Real-time log ingestion and monitoring.
- Evaluation using verified incident labels.
- Precision, recall, F1-score, and confusion matrix analysis.
- Improved feature engineering and threshold tuning.
- Enhanced incident investigation and root-cause analysis.

## 🎯 Project Goal

To make heterogeneous log analysis more accessible by combining data preprocessing, unsupervised machine learning, and interactive visualization in one workflow.

---

**Developed as an academic machine learning project.**
