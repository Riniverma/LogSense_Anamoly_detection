
from pathlib import Path
import base64
import re

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="LogSense | Log Anomaly Discovery",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

NORMALIZED_PATH = RESULTS / "normalized_logs.csv"
BASELINE_PATH = RESULTS / "baseline_results.csv"
ML_PATH = RESULTS / "ml_anomaly_results.csv"

# Optional background image:
# dashboard/assets/operations_center.jpg
BACKGROUND_PATH = Path(__file__).parent / "assets" / "operations_center.jpg"

CHARCOAL = "#252B29"
BUTTON_BG = "#343D38"
INPUT_BG = "#35433B"
GREEN = "#638B73"
DARK_GREEN = "#355C49"
SAGE = "#8EC7A0"
TEXT = "#26312C"
MUTED = "#68746D"


# =========================================================
# THEME
# =========================================================
def background_css():
    if BACKGROUND_PATH.exists():
        encoded = base64.b64encode(
            BACKGROUND_PATH.read_bytes()
        ).decode("utf-8")
        return f"""
        .stApp {{
            background-image:
                linear-gradient(
                    rgba(241,243,241,.94),
                    rgba(241,243,241,.97)
                ),
                url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        """
    return ".stApp { background: #F1F3F1; }"


st.markdown(
    f"""
    <style>
    {background_css()}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {CHARCOAL} !important;
        border-right: 1px solid #414A45;
    }}

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] small {{
        color: #F1F4F1 !important;
    }}

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
        color: #B9C6BD !important;
    }}

    /* Navigation buttons */
    [data-testid="stSidebar"] div.stButton > button {{
        background: {BUTTON_BG} !important;
        background-color: {BUTTON_BG} !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5750 !important;
        border-radius: 8px !important;
        min-height: 44px;
        font-weight: 600;
        box-shadow: none !important;
    }}

    [data-testid="stSidebar"] div.stButton > button p,
    [data-testid="stSidebar"] div.stButton > button span {{
        color: #FFFFFF !important;
    }}

    [data-testid="stSidebar"] div.stButton > button:hover {{
        background: #46574B !important;
        border-color: {SAGE} !important;
        color: #FFFFFF !important;
    }}

    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
        background: #527D62 !important;
        background-color: #527D62 !important;
        color: #FFFFFF !important;
        border: 1px solid {SAGE} !important;
    }}

    /* Dark sage search, date and text inputs */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-baseweb="textarea"] textarea {{
        background: {INPUT_BG} !important;
        background-color: {INPUT_BG} !important;
        color: #F2F5F2 !important;
        -webkit-text-fill-color: #F2F5F2 !important;
        border-color: #596B5E !important;
    }}

    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {{
        color: #B9C6BD !important;
        -webkit-text-fill-color: #B9C6BD !important;
    }}

    /* Dropdowns */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background: {INPUT_BG} !important;
        background-color: {INPUT_BG} !important;
        border-color: #596B5E !important;
        color: #F2F5F2 !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #F2F5F2 !important;
    }}

    /* Selected source tags */
    [data-testid="stSidebar"] [data-baseweb="tag"] {{
        background: #527D62 !important;
        color: #FFFFFF !important;
        border: 1px solid #6D9C7C !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="tag"] span {{
        color: #FFFFFF !important;
    }}

    /* Date picker */
    [data-testid="stSidebar"] [data-testid="stDateInput"] input {{
        background: {INPUT_BG} !important;
        color: #F2F5F2 !important;
        -webkit-text-fill-color: #F2F5F2 !important;
    }}

    /* Green slider thumb and track */
    [data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
        background: {SAGE} !important;
        border-color: {SAGE} !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="slider"] [data-testid="stTickBar"] {{
        background: #53645A !important;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: #414F46 !important;
    }}

    /* Main workspace */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}

    h1, h2, h3 {{
        color: {TEXT};
        letter-spacing: -0.3px;
    }}

    div[data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid #E0E5E1;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(25,40,30,.04);
    }}

    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
    }}

    div[data-testid="stMetricValue"] {{
        color: {DARK_GREEN};
        font-weight: 650;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid #E0E5E1;
        border-radius: 10px;
    }}

    div.stButton > button,
    div[data-testid="stDownloadButton"] button {{
        border-radius: 8px;
        min-height: 40px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(show_spinner="Loading saved project data...")
def load_csv(path_string, modified_time):
    path = Path(path_string)
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as exc:
        st.warning(f"Could not load {path.name}: {exc}")
        return pd.DataFrame()


def read_result(path):
    if path.exists():
        return load_csv(str(path), path.stat().st_mtime)
    return pd.DataFrame()


def find_col(df, candidates):
    exact = {str(c).strip().lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in exact:
            return exact[candidate.lower()]

    normalized = {
        str(c).strip().lower().replace(" ", "_"): c
        for c in df.columns
    }
    for candidate in candidates:
        key = candidate.lower().replace(" ", "_")
        if key in normalized:
            return normalized[key]
    return None


def prepare_logs(df):
    if df.empty:
        return df.copy()

    out = df.copy()

    source_col = find_col(
        out, ["source", "dataset", "log_source", "system", "service"]
    )
    time_col = find_col(
        out, ["timestamp", "datetime", "date", "time",
              "window_start", "start_time"]
    )
    message_col = find_col(
        out, ["message", "log", "content", "log_message", "raw_log"]
    )
    level_col = find_col(
        out, ["level", "severity", "log_level", "loglevel"]
    )

    out["_source"] = (
        out[source_col].fillna("Unknown").astype(str)
        if source_col else "Unknown"
    )

    if time_col:
        out["_time"] = pd.to_datetime(
            out[time_col], errors="coerce", utc=True
        )
    else:
        out["_time"] = pd.Series(
            pd.NaT, index=out.index, dtype="datetime64[ns, UTC]"
        )

    out["_message"] = (
        out[message_col].fillna("").astype(str)
        if message_col else ""
    )
    out["_severity"] = (
        out[level_col].fillna("UNKNOWN").astype(str).str.upper()
        if level_col else "UNKNOWN"
    )

    return out


def prepare_alerts(df, detector):
    if df.empty:
        return df.copy()

    out = df.copy()

    source_col = find_col(
        out, ["source", "dataset", "log_source", "system", "service"]
    )
    time_col = find_col(
        out, ["window_start", "timestamp", "start_time",
              "datetime", "date", "time"]
    )
    error_col = find_col(
        out, ["error_rate", "error rate", "error_ratio"]
    )
    score_col = find_col(
        out, ["anomaly_score", "anomaly score", "score",
              "decision_score", "ml_score"]
    )
    flag_col = find_col(
        out, ["is_anomaly", "anomaly", "is_alert", "alert", "prediction"]
    )

    out["_source"] = (
        out[source_col].fillna("Unknown").astype(str)
        if source_col else "Unknown"
    )

    if time_col:
        out["_time"] = pd.to_datetime(
            out[time_col], errors="coerce", utc=True
        )
    else:
        out["_time"] = pd.Series(
            pd.NaT, index=out.index, dtype="datetime64[ns, UTC]"
        )

    out["_error_rate"] = (
        pd.to_numeric(out[error_col], errors="coerce").fillna(0.0)
        if error_col else 0.0
    )
    out["_score"] = (
        pd.to_numeric(out[score_col], errors="coerce").fillna(0.0)
        if score_col else 0.0
    )

    if flag_col:
        values = out[flag_col]
        if pd.api.types.is_numeric_dtype(values):
            out["_alert"] = (
                pd.to_numeric(values, errors="coerce")
                .fillna(0).ne(0)
            )
        else:
            out["_alert"] = values.astype(str).str.lower().isin(
                ["true", "yes", "anomaly", "alert", "1", "-1"]
            )
    else:
        out["_alert"] = True

    out["_detector"] = detector
    return out


logs = prepare_logs(read_result(NORMALIZED_PATH))
baseline = prepare_alerts(
    read_result(BASELINE_PATH), "Keyword Baseline"
)
ml = prepare_alerts(
    read_result(ML_PATH), "Isolation Forest"
)


# =========================================================
# NAVIGATION AND SIDEBAR FILTERS
# =========================================================
PAGES = [
    "Overview",
    "Anomaly Explorer",
    "Analytics",
    "Model Comparison",
    "Investigation",
    "Logs & Reports",
]

if "page" not in st.session_state:
    st.session_state.page = "Overview"

with st.sidebar:
    st.markdown(
         """
        <div style="padding:8px 2px 15px; font-family:Arial,sans-serif;">
        <div style="font-size:29px;font-weight:750;color:#F4F6F4;line-height:1.4;">
        Log<span style="color:#8EC7A0;">Sense</span>
        </div>
        <div style="font-size:12px;font-weight:600;color:#E1E8E2;letter-spacing:1px;margin-top:5px;">
            LOG ANOMALY DISCOVERY
        </div>
        <div style="font-size:12px;color:#B9C8BD;margin-top:8px;">
            Hadoop · OpenStack · Offline analysis
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### WORKSPACE")

    for page_name in PAGES:
        active = st.session_state.page == page_name
        if st.button(
            ("●  " if active else "   ") + page_name,
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("---")
    st.markdown("#### DATA FILTERS")

    source_list = []
    for frame in (logs, baseline, ml):
        if not frame.empty:
            source_list.extend(
                frame["_source"].dropna().astype(str).unique()
            )

    sources = sorted(set(source_list))
    selected_sources = st.multiselect(
        "Log sources", sources, default=sources
    )

    all_times = []
    for frame in (logs, baseline, ml):
        if not frame.empty:
            all_times.extend(frame["_time"].dropna().tolist())

    date_start = None
    date_end = None

    if all_times:
        min_date = min(all_times).date()
        max_date = max(all_times).date()

        date_range = st.date_input(
            "Date range (UTC)",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            date_start, date_end = date_range
        else:
            date_start = date_end = date_range
    else:
        st.caption("No usable timestamps found.")

    st.markdown("---")
    st.markdown("#### DETECTION CONTROLS")

    error_threshold = st.slider(
        "Keyword error-rate threshold",
        0.0, 1.0, 0.01, 0.01,
    )

    score_threshold = st.slider(
        "ML anomaly-score threshold",
        0.0, 1.0, 0.50, 0.05,
        help="Filters saved scores; it does not retrain Isolation Forest.",
    )

    top_k = st.slider("Top suspicious windows", 5, 50, 10, 5)

    search_text = st.text_input(
        "Search source or message",
        placeholder="timeout, Hadoop, OpenStack...",
    )

    st.caption("Offline analysis of saved CSV files")


# =========================================================
# GLOBAL FILTERS
# =========================================================
def apply_filters(df):
    if df.empty:
        return df.copy()

    out = df.copy()

    if "_source" in out.columns:
        out = out[
            out["_source"].astype(str).isin(selected_sources)
        ]

    if (
        date_start is not None
        and date_end is not None
        and "_time" in out.columns
    ):
        start = pd.Timestamp(date_start).tz_localize("UTC")
        end = (
            pd.Timestamp(date_end) + pd.Timedelta(days=1)
        ).tz_localize("UTC")

        out = out[
            out["_time"].isna()
            | ((out["_time"] >= start) & (out["_time"] < end))
        ]

    if search_text.strip():
        query = search_text.strip().lower()

        columns = [
            c for c in ["_source", "_message"]
            if c in out.columns
        ]
        columns += [
            c for c in out.columns if not c.startswith("_")
        ]

        if columns:
            searchable = (
                out[columns].astype(str)
                .agg(" ".join, axis=1).str.lower()
            )
            out = out[
                searchable.str.contains(re.escape(query), na=False)
            ]

    return out


filtered_logs = apply_filters(logs)
filtered_baseline = apply_filters(baseline)
filtered_ml = apply_filters(ml)

if not filtered_baseline.empty:
    filtered_baseline = filtered_baseline[
        filtered_baseline["_alert"]
        & (filtered_baseline["_error_rate"] >= error_threshold)
    ]

if not filtered_ml.empty:
    filtered_ml = filtered_ml[
        filtered_ml["_alert"]
        & (filtered_ml["_score"] >= score_threshold)
    ]

filtered_alerts = pd.concat(
    [filtered_baseline, filtered_ml],
    ignore_index=True,
    sort=False,
)

if not filtered_alerts.empty:
    filtered_alerts = filtered_alerts.sort_values(
        "_score", ascending=False, na_position="last"
    )


# =========================================================
# COMMON DISPLAY HELPERS
# =========================================================
def page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)


def show_empty(message):
    st.info(message)


def alert_table(df):
    if df.empty:
        return pd.DataFrame()

    return pd.DataFrame({
        "Source": df["_source"].astype(str),
        "Detector": df["_detector"].astype(str),
        "Window Start (UTC)": df["_time"].astype(str),
        "Error Rate": df["_error_rate"],
        "Anomaly Score": df["_score"],
    })


def download_csv(df, filename):
    if df.empty:
        st.caption("No data available to download.")
    else:
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
        )


def bar_chart(df, x, y, title):
    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        color_discrete_sequence=[GREEN, "#91A69A", "#C18B42"],
    )

    fig.update_layout(
        template="plotly_white",
        margin=dict(l=15, r=15, t=55, b=15),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color=TEXT),
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================================================
# PAGE 1: OVERVIEW
# =========================================================
def render_overview():
    page_header(
        "LogSense Overview",
        "Summary of saved Hadoop and OpenStack log analysis.",
    )

    cols = st.columns(4)
    cols[0].metric("Log lines in view", f"{len(filtered_logs):,}")
    cols[1].metric("Alert records", f"{len(filtered_alerts):,}")
    cols[2].metric("Keyword baseline alerts", f"{len(filtered_baseline):,}")
    cols[3].metric("Isolation Forest alerts", f"{len(filtered_ml):,}")

    st.markdown("### Detection snapshot")
    left, right = st.columns(2)

    with left:
        if filtered_alerts.empty:
            show_empty("No alert candidates match these filters.")
        else:
            counts = (
                filtered_alerts.groupby("_source")
                .size().reset_index(name="Alert records")
            )
            bar_chart(
                counts, "_source", "Alert records",
                "Alert records by source"
            )

    with right:
        if filtered_alerts.empty:
            show_empty("No detector results to summarize.")
        else:
            counts = (
                filtered_alerts.groupby("_detector")
                .size().reset_index(name="Alert records")
            )
            fig = px.pie(
                counts,
                names="_detector",
                values="Alert records",
                hole=0.58,
                title="Alert records by detector",
                color_discrete_sequence=[GREEN, "#91A69A"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Highest-scoring candidates")

    if filtered_alerts.empty:
        show_empty("Try widening the date range or adjusting thresholds.")
    else:
        display = alert_table(filtered_alerts.head(top_k))
        st.dataframe(display, use_container_width=True, hide_index=True)
        download_csv(display, "logsense_top_alerts.csv")

    st.caption(
        "Counts depend on filters and are not verified model-accuracy metrics."
    )


# =========================================================
# PAGE 2: ANOMALY EXPLORER
# =========================================================
def render_explorer():
    page_header(
        "Anomaly Explorer",
        "Search suspicious windows and inspect saved detector outputs.",
    )

    detector = st.radio(
        "Choose detector",
        ["Both", "Keyword Baseline", "Isolation Forest"],
        horizontal=True,
    )

    if detector == "Keyword Baseline":
        view = filtered_baseline.copy()
    elif detector == "Isolation Forest":
        view = filtered_ml.copy()
    else:
        view = filtered_alerts.copy()

    if view.empty:
        show_empty("No candidates match the selected filters.")
        return

    fig = px.scatter(
        view,
        x="_error_rate",
        y="_score",
        color="_detector",
        hover_data=["_source", "_time"],
        labels={
            "_error_rate": "Error rate",
            "_score": "Saved anomaly score",
        },
        title="Error rate vs saved anomaly score",
        color_discrete_sequence=[GREEN, "#91A69A"],
    )
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Candidate windows")
    display = alert_table(view.head(500))
    st.dataframe(display, use_container_width=True, hide_index=True)
    download_csv(display, "logsense_anomaly_candidates.csv")

    st.markdown("### Inspect one candidate")
    chosen = st.selectbox(
        "Select candidate",
        list(view.index),
        format_func=lambda i: (
            f"{view.loc[i, '_source']} | {view.loc[i, '_time']} | "
            f"{view.loc[i, '_detector']}"
        ),
    )

    record = view.loc[chosen]
    a, b, c = st.columns(3)
    a.metric("Source", str(record["_source"]))
    b.metric("Error rate", f"{record['_error_rate']:.4f}")
    c.metric("Saved score", f"{record['_score']:.4f}")

    with st.expander("Show original candidate fields"):
        st.json({
            str(k): str(v)
            for k, v in record.to_dict().items()
            if not str(k).startswith("_")
        })

    if st.button("Open candidate in Investigation", type="primary"):
        st.session_state["investigation_source"] = str(record["_source"])
        st.session_state["investigation_time"] = str(record["_time"])
        st.session_state.page = "Investigation"
        st.rerun()


# =========================================================
# PAGE 3: ANALYTICS
# =========================================================
def render_analytics():
    page_header(
        "Analytics",
        "Log-volume trends, source distribution and detector outputs.",
    )

    if filtered_logs.empty:
        show_empty("No normalized logs match the selected filters.")
    else:
        timed = filtered_logs.dropna(subset=["_time"]).copy()

        if timed.empty:
            show_empty("No parseable timestamps found.")
        else:
            interval = st.selectbox(
                "Time aggregation",
                ["Hour", "Day", "Week", "Month"],
                index=1,
            )

            if interval == "Hour":
                timed["_period"] = timed["_time"].dt.floor("h")
            elif interval == "Day":
                timed["_period"] = timed["_time"].dt.floor("D")
            elif interval == "Week":
                timed["_period"] = (
                    timed["_time"].dt.tz_localize(None)
                    .dt.to_period("W").dt.start_time
                )
            else:
                timed["_period"] = (
                    timed["_time"].dt.tz_localize(None)
                    .dt.to_period("M").dt.start_time
                )

            volume = (
                timed.groupby(["_period", "_source"])
                .size().reset_index(name="Log lines")
            )

            fig = px.line(
                volume,
                x="_period",
                y="Log lines",
                color="_source",
                title=f"Log volume by {interval.lower()}",
                color_discrete_sequence=[GREEN, "#91A69A", "#C18B42"],
            )
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            left, right = st.columns(2)

            with left:
                counts = (
                    filtered_logs.groupby("_source")
                    .size().reset_index(name="Log lines")
                )
                bar_chart(
                    counts, "_source", "Log lines", "Log lines by source"
                )

            with right:
                counts = (
                    filtered_logs.groupby("_severity")
                    .size().reset_index(name="Log lines")
                )
                bar_chart(
                    counts, "_severity", "Log lines",
                    "Severity distribution (if available)"
                )

    st.markdown("### Detector output")
    counts = pd.DataFrame({
        "Detector": ["Keyword Baseline", "Isolation Forest"],
        "Flagged rows in view": [
            len(filtered_baseline), len(filtered_ml)
        ],
    })
    bar_chart(
        counts, "Detector", "Flagged rows in view",
        "Flagged rows by detector"
    )

    st.caption("Counts depend on filters and are not verified accuracy metrics.")


# =========================================================
# PAGE 4: MODEL COMPARISON
# =========================================================
def render_comparison():
    page_header(
        "Model Comparison",
        "Compare saved keyword-baseline and Isolation Forest candidates.",
    )

    left, right = st.columns(2)
    left.metric("Keyword baseline rows", f"{len(filtered_baseline):,}")
    right.metric("Isolation Forest rows", f"{len(filtered_ml):,}")

    counts = pd.DataFrame({
        "Detector": ["Keyword Baseline", "Isolation Forest"],
        "Candidate rows": [
            len(filtered_baseline), len(filtered_ml)
        ],
    })
    bar_chart(
        counts, "Detector", "Candidate rows",
        "Candidate count by detector"
    )

    st.markdown("### Shared source/time keys")

    if not filtered_baseline.empty and not filtered_ml.empty:
        baseline_keys = set(zip(
            filtered_baseline["_source"].astype(str),
            filtered_baseline["_time"].astype(str),
        ))
        ml_keys = set(zip(
            filtered_ml["_source"].astype(str),
            filtered_ml["_time"].astype(str),
        ))

        shared = baseline_keys & ml_keys
        union = baseline_keys | ml_keys

        a, b, c = st.columns(3)
        a.metric("Shared keys", f"{len(shared):,}")
        b.metric("Unique keys", f"{len(union):,}")
        c.metric(
            "Jaccard overlap",
            f"{len(shared) / len(union):.1%}" if union else "N/A",
        )
    else:
        st.info("Both detectors need candidate rows to calculate overlap.")

    st.warning(
        "Candidate counts and overlap do not establish accuracy. Precision, "
        "recall, false-alarm rate and lead time require validated incident "
        "labels and timestamps."
    )

    with st.expander("Keyword baseline candidates"):
        st.dataframe(
            alert_table(filtered_baseline.head(top_k)),
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("Isolation Forest candidates"):
        st.dataframe(
            alert_table(filtered_ml.head(top_k)),
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# PAGE 5: INVESTIGATION
# =========================================================
def render_investigation():
    page_header(
        "Investigation",
        "Select a suspicious window and inspect nearby normalized logs.",
    )

    if filtered_alerts.empty:
        show_empty("No candidates available with these filters.")
        return

    options = list(filtered_alerts.index)
    saved_source = st.session_state.get("investigation_source")
    saved_time = st.session_state.get("investigation_time")
    default_index = 0

    for position, idx in enumerate(options):
        row = filtered_alerts.loc[idx]
        if (
            saved_source is not None
            and str(row["_source"]) == saved_source
            and str(row["_time"]) == saved_time
        ):
            default_index = position
            break

    chosen = st.selectbox(
        "Suspicious window",
        options,
        index=default_index,
        format_func=lambda i: (
            f"{filtered_alerts.loc[i, '_source']} | "
            f"{filtered_alerts.loc[i, '_time']} | "
            f"{filtered_alerts.loc[i, '_detector']}"
        ),
    )

    record = filtered_alerts.loc[chosen]
    a, b, c = st.columns(3)
    a.metric("Source", str(record["_source"]))
    b.metric("Error rate", f"{record['_error_rate']:.4f}")
    c.metric("Saved score", f"{record['_score']:.4f}")

    minutes = st.select_slider(
        "Time window around candidate",
        options=[1, 5, 10, 15, 30, 60],
        value=5,
        format_func=lambda x: f"±{x} minutes",
    )

    timestamp = record["_time"]
    source = str(record["_source"])

    if pd.isna(timestamp):
        st.warning("This candidate has no parseable timestamp.")
        return

    nearby = filtered_logs[
        (filtered_logs["_source"].astype(str) == source)
        & filtered_logs["_time"].notna()
        & (
            filtered_logs["_time"]
            >= timestamp - pd.Timedelta(minutes=minutes)
        )
        & (
            filtered_logs["_time"]
            <= timestamp + pd.Timedelta(minutes=minutes)
        )
    ].copy()

    st.caption(f"Matching normalized log lines: {len(nearby):,}")

    if nearby.empty:
        st.info(
            "No normalized records found near this candidate. Try a wider "
            "date range or verify timestamps."
        )
    else:
        display = nearby[
            ["_time", "_source", "_severity", "_message"]
        ].rename(columns={
            "_time": "Timestamp (UTC)",
            "_source": "Source",
            "_severity": "Severity",
            "_message": "Message",
        })

        st.dataframe(display, use_container_width=True, hide_index=True)
        download_csv(display, "logsense_investigation_logs.csv")

    with st.expander("Candidate row fields"):
        st.json({
            str(k): str(v)
            for k, v in record.to_dict().items()
            if not str(k).startswith("_")
        })


# =========================================================
# PAGE 6: LOGS & REPORTS
# =========================================================
def render_reports():
    page_header(
        "Logs & Reports",
        "Browse normalized logs and download existing result files.",
    )

    st.markdown("### Normalized log records")

    if filtered_logs.empty:
        show_empty("No log records match the current filters.")
    else:
        levels = sorted(
            filtered_logs["_severity"].dropna().astype(str).unique()
        )

        selected_levels = st.multiselect(
            "Severity", levels, default=levels
        )

        view = filtered_logs[
            filtered_logs["_severity"].astype(str).isin(selected_levels)
        ].copy()

        display = view[
            ["_time", "_source", "_severity", "_message"]
        ].rename(columns={
            "_time": "Timestamp (UTC)",
            "_source": "Source",
            "_severity": "Severity",
            "_message": "Message",
        })

        st.caption(
            f"{len(display):,} matching records; showing up to 5,000."
        )
        st.dataframe(
            display.head(5000),
            use_container_width=True,
            hide_index=True,
        )
        download_csv(display, "logsense_filtered_logs.csv")

    st.markdown("### Existing result files")

    result_files = [
        NORMALIZED_PATH,
        RESULTS / "window_features.csv",
        BASELINE_PATH,
        ML_PATH,
        RESULTS / "model_comparison.csv",
        RESULTS / "evaluation_metrics.csv",
        RESULTS / "openstack_incident_matches.csv",
    ]

    for path in result_files:
        if path.exists():
            with st.expander(path.name):
                st.caption(f"File size: {path.stat().st_size:,} bytes")
                st.download_button(
                    f"Download {path.name}",
                    data=path.read_bytes(),
                    file_name=path.name,
                    mime="text/csv",
                    key=f"download_{path.name}",
                )

    st.caption(
        "Only existing files are listed; no new evaluation metrics are fabricated."
    )


# =========================================================
# ROUTER: ONE PAGE AT A TIME
# =========================================================
page = st.session_state.page

if page == "Overview":
    render_overview()
elif page == "Anomaly Explorer":
    render_explorer()
elif page == "Analytics":
    render_analytics()
elif page == "Model Comparison":
    render_comparison()
elif page == "Investigation":
    render_investigation()
elif page == "Logs & Reports":
    render_reports()
else:
    st.session_state.page = "Overview"
    st.rerun()

st.markdown("---")
st.caption(
    "LogSense · Offline analysis of saved CSVs · Hadoop and OpenStack · "
    "Not a live monitoring service"
)






