import os
import re
import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BENCHMARK_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "benchmark",
    "detailed_field_results.csv",
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "benchmark",
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# EXACT BENCHMARK FIELDS
# ============================================================

BENCHMARK_FIELDS = [
    "Invoice Number",
    "Invoice Date",
    "Seller Tax ID",
    "Client Tax ID",
    "Seller IBAN",
    "Net Worth",
    "VAT",
    "Gross Worth",
]


# ============================================================
# COLUMN DETECTION
# ============================================================

def find_column(df, candidates):
    """
    Find a column using case-insensitive matching and common
    naming variations.
    """
    normalized = {
        re.sub(r"[^a-z0-9]", "", str(col).lower()): col
        for col in df.columns
    }

    for candidate in candidates:
        key = re.sub(
            r"[^a-z0-9]",
            "",
            candidate.lower(),
        )

        if key in normalized:
            return normalized[key]

    return None


def locate_columns(df):
    """
    Locate the benchmark CSV's key columns without assuming
    one exact capitalization/spelling.
    """

    method_col = find_column(
        df,
        [
            "method",
            "preprocessing_method",
            "preprocessing",
        ],
    )

    field_col = find_column(
        df,
        [
            "field",
            "field_name",
        ],
    )

    gt_col = find_column(
        df,
        [
            "ground_truth",
            "groundtruth",
            "expected",
            "actual",
            "true_value",
        ],
    )

    pred_col = find_column(
        df,
        [
            "predicted",
            "prediction",
            "extracted_value",
            "ocr_value",
        ],
    )

    image_col = find_column(
        df,
        [
            "image",
            "filename",
            "invoice",
            "file",
        ],
    )

    return {
        "method": method_col,
        "field": field_col,
        "ground_truth": gt_col,
        "predicted": pred_col,
        "image": image_col,
    }


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_value(field, value):
    if pd.isna(value):
        return ""

    value = str(value).strip()

    if not value:
        return ""

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    # --------------------------------------------------------
    # Identifier fields
    # --------------------------------------------------------

    if field in {
        "Invoice Number",
        "Seller Tax ID",
        "Client Tax ID",
        "Seller IBAN",
    }:
        return re.sub(
            r"[^A-Za-z0-9]",
            "",
            value,
        ).upper()

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    if field == "Invoice Date":
        return value.replace(
            "-",
            "/",
        ).upper()

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    if field in {
        "Net Worth",
        "VAT",
        "Gross Worth",
    }:

        cleaned = (
            value
            .replace("$", "")
            .replace("€", "")
            .replace("₹", "")
            .replace("Rs.", "")
            .replace("Rs", "")
            .replace(" ", "")
        )

        if "," in cleaned and "." in cleaned:

            if cleaned.rfind(",") > cleaned.rfind("."):
                cleaned = (
                    cleaned
                    .replace(".", "")
                    .replace(",", ".")
                )
            else:
                cleaned = cleaned.replace(
                    ",",
                    "",
                )

        elif "," in cleaned:
            cleaned = cleaned.replace(
                ",",
                ".",
            )

        try:
            return f"{float(cleaned):.2f}"

        except ValueError:
            return cleaned.upper()

    return value.upper()


# ============================================================
# ERROR CLASSIFICATION
# ============================================================

def classify_error(field, ground_truth, predicted):

    predicted_norm = normalize_value(
        field,
        predicted,
    )

    if not predicted_norm:
        return "Missing Extraction"

    if field == "Invoice Date":
        return "Date Error"

    if field in {
        "Net Worth",
        "VAT",
        "Gross Worth",
    }:
        return "Numeric / Amount Error"

    if field in {
        "Invoice Number",
        "Seller Tax ID",
        "Client Tax ID",
        "Seller IBAN",
    }:
        return "Character / Identifier Error"

    return "Other Field Mismatch"


# ============================================================
# MAIN
# ============================================================

def run_error_analysis():

    print("=" * 68)
    print("OCR ERROR-CATEGORY ANALYSIS")
    print("=" * 68)

    if not os.path.exists(BENCHMARK_FILE):

        print()
        print("ERROR: Benchmark result file not found:")
        print(BENCHMARK_FILE)
        print()
        print(
            "Run benchmark_evaluation.py first."
        )

        return

    print()
    print(
        "Reading existing benchmark results..."
    )

    df = pd.read_csv(
        BENCHMARK_FILE,
        dtype=str,
    ).fillna("")

    print(
        f"Rows loaded: {len(df)}"
    )

    columns = locate_columns(df)

    missing_columns = [
        name
        for name, column in columns.items()
        if column is None
        and name != "image"
    ]

    if missing_columns:

        print()
        print(
            "ERROR: Could not identify required columns:"
        )

        for name in missing_columns:
            print(
                f"  - {name}"
            )

        print()
        print(
            "Available columns:"
        )

        for column in df.columns:
            print(
                f"  - {column}"
            )

        return

    print()
    print("Detected benchmark columns:")

    for name, column in columns.items():
        if column is not None:
            print(
                f"  {name}: {column}"
            )

    # --------------------------------------------------------
    # Keep ONLY the 8 fields evaluated by benchmark.
    # --------------------------------------------------------

    field_col = columns["field"]

    df[field_col] = (
        df[field_col]
        .astype(str)
        .str.strip()
    )

    df = df[
        df[field_col].isin(
            BENCHMARK_FIELDS
        )
    ].copy()

    print()
    print(
        f"Benchmark field rows retained: {len(df)}"
    )

    # --------------------------------------------------------
    # Compare ground truth and prediction.
    # --------------------------------------------------------

    errors = []

    for _, row in df.iterrows():

        field = str(
            row[columns["field"]]
        ).strip()

        ground_truth = row[
            columns["ground_truth"]
        ]

        predicted = row[
            columns["predicted"]
        ]

        gt_norm = normalize_value(
            field,
            ground_truth,
        )

        pred_norm = normalize_value(
            field,
            predicted,
        )

        # Correct match.
        if (
            gt_norm
            and gt_norm == pred_norm
        ):
            continue

        if columns["image"] is not None:
            image = row[
                columns["image"]
            ]
        else:
            image = ""

        method = row[
            columns["method"]
        ]

        errors.append(
            {
                "image": image,
                "method": method,
                "field": field,
                "ground_truth": ground_truth,
                "predicted": predicted,
                "error_category": classify_error(
                    field,
                    ground_truth,
                    predicted,
                ),
            }
        )

    # --------------------------------------------------------
    # No errors.
    # --------------------------------------------------------

    if not errors:

        print()
        print("=" * 68)
        print("NO ERRORS FOUND")
        print("=" * 68)

        return

    errors_df = pd.DataFrame(
        errors
    )

    # ========================================================
    # 1. DETAILED ERROR FILE
    # ========================================================

    details_file = os.path.join(
        OUTPUT_DIR,
        "error_details.csv",
    )

    errors_df.to_csv(
        details_file,
        index=False,
    )

    # ========================================================
    # 2. CATEGORY SUMMARY
    # ========================================================

    category_summary = (
        errors_df
        .groupby(
            [
                "method",
                "error_category",
            ]
        )
        .size()
        .reset_index(
            name="error_count"
        )
    )

    totals = (
        category_summary
        .groupby("method")[
            "error_count"
        ]
        .sum()
        .rename("total_errors")
        .reset_index()
    )

    category_summary = category_summary.merge(
        totals,
        on="method",
    )

    category_summary[
        "percentage_of_errors"
    ] = (
        category_summary["error_count"]
        / category_summary["total_errors"]
        * 100
    ).round(2)

    category_file = os.path.join(
        OUTPUT_DIR,
        "error_category_summary.csv",
    )

    category_summary.to_csv(
        category_file,
        index=False,
    )

    # ========================================================
    # 3. FIELD ERROR SUMMARY
    # ========================================================

    field_summary = (
        errors_df
        .groupby(
            [
                "method",
                "field",
            ]
        )
        .size()
        .reset_index(
            name="error_count"
        )
        .sort_values(
            [
                "method",
                "error_count",
            ],
            ascending=[
                True,
                False,
            ],
        )
    )

    field_file = os.path.join(
        OUTPUT_DIR,
        "field_error_summary.csv",
    )

    field_summary.to_csv(
        field_file,
        index=False,
    )

    # ========================================================
    # 4. GRAPH
    # ========================================================

    pivot = (
        category_summary
        .pivot(
            index="method",
            columns="error_category",
            values="error_count",
        )
        .fillna(0)
    )

    ax = pivot.plot(
        kind="bar",
        figsize=(12, 6),
    )

    ax.set_title(
        "OCR Error Categories Across Preprocessing Methods"
    )

    ax.set_xlabel(
        "Preprocessing Method"
    )

    ax.set_ylabel(
        "Number of Incorrect / Missing Fields"
    )

    ax.legend(
        title="Error Category",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )

    plt.tight_layout()

    graph_file = os.path.join(
        OUTPUT_DIR,
        "error_category_comparison.png",
    )

    plt.savefig(
        graph_file,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    # ========================================================
    # REPORT
    # ========================================================

    print()
    print("=" * 68)
    print("ERROR-CATEGORY SUMMARY")
    print("=" * 68)

    print(
        category_summary.to_string(
            index=False
        )
    )

    print()
    print("=" * 68)
    print("FILES GENERATED")
    print("=" * 68)

    print(
        f"Detailed errors      : {details_file}"
    )

    print(
        f"Category summary     : {category_file}"
    )

    print(
        f"Field error summary  : {field_file}"
    )

    print(
        f"Error-category graph : {graph_file}"
    )

    print()
    print(
        "No OCR was rerun."
    )

    print(
        "Analysis is based directly on "
        "detailed_field_results.csv."
    )

    print()
    print(
        "OCR ERROR-CATEGORY ANALYSIS COMPLETED"
    )


if __name__ == "__main__":
    run_error_analysis()