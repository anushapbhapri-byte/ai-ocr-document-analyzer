import streamlit as st
import pandas as pd
from pathlib import Path

# ============================================================
# AI OCR DOCUMENT ANALYZER — RECRUITER-FACING DASHBOARD
# ============================================================

st.set_page_config(
    page_title="AI OCR Document Analyzer | Portfolio Dashboard",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).resolve().parent
BENCHMARK_DIR = PROJECT_ROOT / "outputs" / "benchmark"
BATCH_DIR = PROJECT_ROOT / "outputs" / "batch"


# -----------------------------
# Helpers
# -----------------------------
def load_csv(path):
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def find_csv(directory, filename):
    return load_csv(directory / filename)


def pct(value):
    if pd.isna(value):
        return "—"
    return f"{float(value):.2f}%"


# -----------------------------
# Load project outputs
# -----------------------------
method_df = find_csv(BENCHMARK_DIR, "method_comparison.csv")
field_df = find_csv(BENCHMARK_DIR, "field_comparison.csv")
error_df = find_csv(BENCHMARK_DIR, "error_category_summary.csv")
batch_df = find_csv(BATCH_DIR, "batch_invoice_results.csv")


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.45rem;
            font-weight: 750;
            margin-bottom: 0.15rem;
            letter-spacing: -0.02em;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1.02rem;
            margin-bottom: 0.8rem;
        }

        .hero-note {
            color: #9ca3af;
            font-size: 0.88rem;
            margin-bottom: 1.4rem;
        }

        .finding-box {
            border: 1px solid #dbeafe;
            border-radius: 12px;
            padding: 16px 18px;
            background: #eff6ff;
            margin: 1rem 0 1.3rem 0;
        }

        .finding-title {
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .scope-box {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 14px 16px;
            background: #f9fafb;
            margin-top: 0.8rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 650;
            margin-top: 1rem;
            margin-bottom: 0.7rem;
        }

        /* KPI cards: explicitly set dark text so Streamlit's
           global/dark-theme text color cannot make it white-on-white. */
        div[data-testid="stMetric"] {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 16px 15px;
            background: #ffffff !important;
            min-height: 112px;
        }

        div[data-testid="stMetric"] *,
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] *,
        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] * {
            color: #222222 !important;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.88rem;
            color: #555555 !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.85rem;
            color: #222222 !important;
        }

        /* Keep positive/negative delta text readable while retaining
           Streamlit's green/red visual treatment. */
        div[data-testid="stMetricDelta"] {
            color: #16a34a !important;
        }

        /* Light custom information boxes need dark text as well. */
        .finding-box,
        .finding-box *,
        .scope-box,
        .scope-box * {
            color: #222222 !important;
        }

        .finding-title {
            color: #1f2937 !important;
        }

        /* Streamlit alert/info boxes: readable on light backgrounds. */
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span,
        div[data-testid="stAlert"] div {
            color: #222222 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Header
# -----------------------------
st.markdown(
    '<div class="main-title">📄 AI OCR Document Analyzer</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Automated invoice document processing with OCR, preprocessing optimization, "
    "structured extraction, validation, and human-review routing."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-note">'
    "Portfolio demonstration • Controlled noisy-invoice benchmark • Decision-oriented analytics"
    "</div>",
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Dashboard")

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "OCR Benchmark",
        "Field Analysis",
        "Batch Operations",
    ],
)

st.sidebar.divider()

st.sidebar.caption("Dataset")
st.sidebar.write("50 controlled noisy invoices")
st.sidebar.caption("Best preprocessing")
st.sidebar.write("Threshold")

st.sidebar.divider()
st.sidebar.caption(
    "Benchmark accuracy is based on exact normalized field matching. "
    "Tesseract confidence is reported separately."
)


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================
if page == "Executive Overview":

    if method_df is not None and not method_df.empty:
        threshold_row = method_df[
            method_df["method"].astype(str).str.lower() == "threshold"
        ]
        original_row = method_df[
            method_df["method"].astype(str).str.lower() == "original"
        ]

        if not threshold_row.empty:
            best_field = float(threshold_row.iloc[0]["aggregate_field_accuracy"])
            best_char = float(threshold_row.iloc[0]["character_accuracy"])
            best_review = float(threshold_row.iloc[0]["manual_review_proxy_rate"])
        else:
            best_field = None
            best_char = None
            best_review = None

        if not original_row.empty:
            baseline_field = float(
                original_row.iloc[0]["aggregate_field_accuracy"]
            )
            baseline_char = float(original_row.iloc[0]["character_accuracy"])
            baseline_review = float(
                original_row.iloc[0]["manual_review_proxy_rate"]
            )
        else:
            baseline_field = None
            baseline_char = None
            baseline_review = None
    else:
        best_field = best_char = best_review = None
        baseline_field = baseline_char = baseline_review = None

    st.markdown(
        '<div class="section-title">Key Performance Indicators</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Best Field Accuracy",
            pct(best_field),
            f"{best_field - baseline_field:+.2f} pp"
            if best_field is not None and baseline_field is not None
            else None,
        )

    with c2:
        st.metric(
            "Best Character Accuracy",
            pct(best_char),
            f"{best_char - baseline_char:+.2f} pp"
            if best_char is not None and baseline_char is not None
            else None,
        )

    with c3:
        st.metric(
            "Manual Review Proxy",
            pct(best_review),
            f"{best_review - baseline_review:+.2f} pp"
            if best_review is not None and baseline_review is not None
            else None,
            delta_color="inverse",
        )

    if batch_df is not None and not batch_df.empty:
        total = len(batch_df)

        if "status" in batch_df.columns:
            status = batch_df["status"].astype(str).str.lower()
            accepted = int(status.str.contains("accept").sum())
            review = int(status.str.contains("review").sum())
        elif "decision" in batch_df.columns:
            status = batch_df["decision"].astype(str).str.lower()
            accepted = int(status.str.contains("accept").sum())
            review = int(status.str.contains("review").sum())
        else:
            accepted = review = None

        with c4:
            if accepted is not None:
                st.metric(
                    "Batch Straight-Through Rate",
                    pct((accepted / total) * 100),
                    f"{accepted}/{total} accepted",
                )
            else:
                st.metric("Batch Invoices", total)
    else:
        with c4:
            st.metric("Benchmark Invoices", "50")

    st.markdown(
        '<div class="finding-box">'
        '<div class="finding-title">Key finding</div>'
        "Threshold preprocessing delivered the highest measured field accuracy "
        "on the controlled noisy-invoice benchmark, improving field accuracy from "
        "<b>91.25%</b> to <b>94.75%</b>."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="scope-box">'
        "<b>Benchmark scope:</b> 50 controlled noisy invoices • 8 evaluated fields per invoice "
        "• 400 total field evaluations • Ground truth manually verified from clean invoices"
        "</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="section-title">Baseline → Best Method</div>',
            unsafe_allow_html=True,
        )

        overview_data = pd.DataFrame(
            {
                "Metric": [
                    "Field accuracy",
                    "Character accuracy",
                    "Manual-review proxy",
                ],
                "Baseline (Original)": [
                    baseline_field,
                    baseline_char,
                    baseline_review,
                ],
                "Best (Threshold)": [
                    best_field,
                    best_char,
                    best_review,
                ],
            }
        ).set_index("Metric")

        st.dataframe(
            overview_data.style.format("{:.2f}%"),
            use_container_width=True,
        )

    with right:
        st.markdown(
            '<div class="section-title">What the system does</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            **1. Image preprocessing**  
            Tests multiple OpenCV preprocessing strategies.

            **2. OCR extraction**  
            Uses Tesseract to convert invoice images into text.

            **3. Structured field extraction**  
            Identifies invoice number, dates, tax IDs, IBAN and monetary fields.

            **4. Validation & confidence**  
            Applies field-specific validation and separates OCR confidence from factual accuracy.

            **5. Human review decision**  
            Flags uncertain or invalid results instead of blindly accepting them.

            **6. Benchmarking & reporting**  
            Compares preprocessing methods using a verified ground-truth dataset.
            """
        )

    st.divider()

    st.markdown(
        '<div class="section-title">Decision & business interpretation</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Decision: select Threshold as the preferred preprocessing strategy for this "
        "controlled benchmark because it produced the highest measured field accuracy. "
        "The manual-review percentage is a proxy for incorrect/missing fields, not a "
        "measured production labor-time saving."
    )


# ============================================================
# OCR BENCHMARK
# ============================================================
elif page == "OCR Benchmark":

    st.markdown(
        '<div class="section-title">Preprocessing Benchmark</div>',
        unsafe_allow_html=True,
    )

    if method_df is None or method_df.empty:
        st.error(
            "method_comparison.csv was not found. Run benchmark_evaluation.py first."
        )
    else:
        display_cols = [
            col
            for col in [
                "method",
                "invoices_tested",
                "correct_fields",
                "evaluated_fields",
                "aggregate_field_accuracy",
                "character_accuracy",
                "manual_review_proxy_rate",
                "average_tesseract_confidence",
            ]
            if col in method_df.columns
        ]

        st.dataframe(
            method_df[display_cols].sort_values(
                "aggregate_field_accuracy", ascending=False
            ).style.format(
                {
                    col: "{:.2f}%"
                    for col in [
                        "aggregate_field_accuracy",
                        "character_accuracy",
                        "manual_review_proxy_rate",
                    ]
                    if col in method_df.columns
                }
            ),
            use_container_width=True,
        )

        st.markdown(
            '<div class="section-title">Field Accuracy by Preprocessing Method</div>',
            unsafe_allow_html=True,
        )

        chart_df = method_df[["method", "aggregate_field_accuracy"]].copy()
        chart_df = chart_df.set_index("method")
        chart_df.columns = ["Field Accuracy (%)"]

        st.bar_chart(chart_df)

        st.markdown(
            '<div class="section-title">Character Accuracy</div>',
            unsafe_allow_html=True,
        )

        char_df = method_df[["method", "character_accuracy"]].copy()
        char_df = char_df.set_index("method")
        char_df.columns = ["Character Accuracy (%)"]

        st.bar_chart(char_df)

        st.caption(
            "The benchmark contains 50 noisy invoices and 8 evaluated fields per invoice "
            "for a total of 400 field evaluations."
        )


# ============================================================
# FIELD ANALYSIS
# ============================================================
elif page == "Field Analysis":

    st.markdown(
        '<div class="section-title">Field-Level Performance</div>',
        unsafe_allow_html=True,
    )

    if field_df is not None and not field_df.empty:

        st.dataframe(field_df, use_container_width=True)

        # Try to identify a field + accuracy structure.
        possible_field_cols = [
            c for c in field_df.columns
            if c.lower() in ["field", "field_name", "invoice_field"]
        ]

        possible_accuracy_cols = [
            c for c in field_df.columns
            if "accuracy" in c.lower()
        ]

        if possible_field_cols and possible_accuracy_cols:
            field_col = possible_field_cols[0]
            accuracy_col = possible_accuracy_cols[0]

            plot_df = field_df[[field_col, accuracy_col]].copy()
            plot_df[accuracy_col] = pd.to_numeric(
                plot_df[accuracy_col], errors="coerce"
            )
            plot_df = plot_df.dropna()

            if not plot_df.empty:
                st.markdown(
                    '<div class="section-title">Accuracy by Field</div>',
                    unsafe_allow_html=True,
                )

                st.bar_chart(
                    plot_df.set_index(field_col)[accuracy_col]
                )

        # Explicitly highlight the known IBAN limitation when available.
        iban_rows = field_df[
            field_df.astype(str)
            .apply(
                lambda col: col.str.contains("IBAN", case=False, na=False)
            )
            .any(axis=1)
        ]

        if not iban_rows.empty:
            st.warning(
                "Known limitation: Seller IBAN extraction is weaker than the other "
                "invoice fields. This should be presented as a known system limitation, "
                "not hidden from the benchmark."
            )

    else:
        st.warning(
            "field_comparison.csv was not found. Run benchmark_evaluation.py first."
        )

    if error_df is not None and not error_df.empty:
        st.divider()

        st.markdown(
            '<div class="section-title">Error Categories</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(error_df, use_container_width=True)

        category_cols = [
            c
            for c in ["error_category", "error_count"]
            if c in error_df.columns
        ]

        if len(category_cols) == 2:
            error_plot = (
                error_df.groupby("error_category")["error_count"]
                .sum()
                .sort_values(ascending=False)
            )

            st.bar_chart(error_plot)


# ============================================================
# BATCH OPERATIONS
# ============================================================
elif page == "Batch Operations":

    st.markdown(
        '<div class="section-title">Batch Invoice Processing</div>',
        unsafe_allow_html=True,
    )

    if batch_df is None or batch_df.empty:
        st.warning(
            "batch_invoice_results.csv was not found. Run batch_processor.py first."
        )
    else:
        total = len(batch_df)

        status_column = None
        for candidate in ["status", "decision", "review_status"]:
            if candidate in batch_df.columns:
                status_column = candidate
                break

        if status_column:
            statuses = batch_df[status_column].astype(str).str.lower()
            accepted = int(statuses.str.contains("accept").sum())
            review = int(statuses.str.contains("review").sum())

            processing_errors = int(
                statuses.str.contains("error|failed", regex=True).sum()
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Invoices", total)
            c2.metric(
                "Auto Accepted",
                accepted,
                f"{accepted / total * 100:.2f}%",
            )
            c3.metric(
                "Manual Review",
                review,
                f"{review / total * 100:.2f}%",
            )
            c4.metric("Processing Errors", processing_errors)

        st.markdown(
            '<div class="section-title">Processed Invoice Results</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(batch_df, use_container_width=True)

        if status_column:
            status_counts = batch_df[status_column].astype(str).value_counts()
            st.markdown(
                '<div class="section-title">Operational Outcome</div>',
                unsafe_allow_html=True,
            )
            st.bar_chart(status_counts)


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "AI OCR Document Analyzer • Tesseract + OpenCV + Python • "
    "Benchmark results are specific to the controlled dataset."
)
