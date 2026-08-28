import os
import re
import cv2
import pandas as pd
import matplotlib.pyplot as plt

from ocr_engine import (
    create_ocr_variants,
    ocr_with_word_confidence,
)

from data_extractor import extract_invoice_data


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NOISY_IMAGE_DIR = os.path.join(
    BASE_DIR,
    "data",
    "benchmark",
    "noisy_images",
)

GROUND_TRUTH_FILE = os.path.join(
    BASE_DIR,
    "data",
    "benchmark",
    "ground_truth.csv",
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "benchmark",
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# These are the 8 fields in the verified benchmark dataset.
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

AMOUNT_FIELDS = {
    "Net Worth",
    "VAT",
    "Gross Worth",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_value(field, value):
    """
    Normalize values for comparison only.

    The original OCR output is preserved in detailed_results.csv.
    """

    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    value = re.sub(r"\s+", " ", value)

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

    if field == "Invoice Date":
        return (
            value
            .replace("-", "/")
            .replace(".", "/")
            .upper()
        )

    if field in AMOUNT_FIELDS:

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
                cleaned = cleaned.replace(",", "")

        elif "," in cleaned:
            cleaned = cleaned.replace(",", ".")

        try:
            return f"{float(cleaned):.2f}"
        except ValueError:
            return cleaned.upper()

    return value.upper()


# ============================================================
# CHARACTER SIMILARITY
# ============================================================

def levenshtein_distance(a, b):
    """
    Calculate Levenshtein edit distance without external
    dependencies.
    """

    if a == b:
        return 0

    if not a:
        return len(b)

    if not b:
        return len(a)

    previous = list(range(len(b) + 1))

    for i, char_a in enumerate(a, start=1):

        current = [i]

        for j, char_b in enumerate(b, start=1):

            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            substitution = previous[j - 1] + (
                0 if char_a == char_b else 1
            )

            current.append(
                min(
                    insertion,
                    deletion,
                    substitution,
                )
            )

        previous = current

    return previous[-1]


def character_accuracy(field, predicted, actual):
    """
    Character-level accuracy based on normalized edit distance.

    Formula:

        1 - edit_distance / max(len(actual), len(predicted))

    Result is bounded between 0 and 100.
    """

    predicted = normalize_value(
        field,
        predicted,
    )

    actual = normalize_value(
        field,
        actual,
    )

    if not actual:
        return None

    if predicted == actual:
        return 100.0

    if not predicted:
        return 0.0

    distance = levenshtein_distance(
        predicted,
        actual,
    )

    denominator = max(
        len(predicted),
        len(actual),
    )

    if denominator == 0:
        return 100.0

    score = (
        1.0
        - distance / denominator
    ) * 100.0

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


# ============================================================
# EXACT FIELD MATCH
# ============================================================

def field_matches(field, predicted, actual):

    predicted = normalize_value(
        field,
        predicted,
    )

    actual = normalize_value(
        field,
        actual,
    )

    if not actual:
        return None

    return bool(
        predicted
        and predicted == actual
    )


# ============================================================
# TESSERACT CONFIDENCE
# ============================================================

def average_tesseract_confidence(words):

    values = []

    for item in words or []:

        try:
            confidence = float(
                item.get("confidence", -1)
            )
        except (TypeError, ValueError):
            confidence = -1

        if confidence >= 0:
            values.append(confidence)

    if not values:
        return None

    return round(
        sum(values) / len(values),
        2,
    )


# ============================================================
# EVALUATE ONE IMAGE
# ============================================================

def evaluate_image(image_path, ground_truth):

    image = cv2.imread(image_path)

    if image is None:
        print(
            f"WARNING: Could not read {image_path}"
        )
        return []

    variants = create_ocr_variants(
        image
    )

    results = []

    for method_name, processed_image in variants.items():

        text, words = ocr_with_word_confidence(
            processed_image,
            psm=6,
        )

        extracted = extract_invoice_data(
            text,
            processed_image,
        )

        field_results = {}

        correct_fields = 0
        evaluated_fields = 0
        total_character_accuracy = 0.0
        character_fields = 0

        for field in BENCHMARK_FIELDS:

            actual = ground_truth.get(
                field,
                "",
            )

            predicted = extracted.get(
                field,
                "",
            )

            exact_match = field_matches(
                field,
                predicted,
                actual,
            )

            char_score = character_accuracy(
                field,
                predicted,
                actual,
            )

            if exact_match is None:
                continue

            evaluated_fields += 1

            if exact_match:
                correct_fields += 1

            if char_score is not None:
                total_character_accuracy += char_score
                character_fields += 1

            field_results[field] = {
                "actual": actual,
                "predicted": predicted,
                "exact_match": bool(exact_match),
                "character_accuracy": char_score,
            }

        field_accuracy = (
            correct_fields
            / evaluated_fields
            * 100
            if evaluated_fields
            else 0.0
        )

        average_character_accuracy = (
            total_character_accuracy
            / character_fields
            if character_fields
            else 0.0
        )

        incorrect_or_missing = (
            evaluated_fields
            - correct_fields
        )

        manual_review_proxy = (
            incorrect_or_missing
            / evaluated_fields
            * 100
            if evaluated_fields
            else 0.0
        )

        results.append({
            "image": os.path.basename(image_path),
            "method": method_name,
            "ocr_confidence": average_tesseract_confidence(
                words
            ),
            "field_accuracy": round(
                field_accuracy,
                2,
            ),
            "character_accuracy": round(
                average_character_accuracy,
                2,
            ),
            "correct_fields": correct_fields,
            "evaluated_fields": evaluated_fields,
            "incorrect_or_missing_fields": incorrect_or_missing,
            "manual_review_proxy_rate": round(
                manual_review_proxy,
                2,
            ),
            "field_results": field_results,
        })

    return results


# ============================================================
# MAIN BENCHMARK
# ============================================================

def run_benchmark():

    print()
    print("=" * 70)
    print("BASELINE VS IMPROVED OCR DATASET EVALUATION")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Check required files
    # --------------------------------------------------------

    if not os.path.isdir(NOISY_IMAGE_DIR):

        print(
            "ERROR: Noisy invoice folder found at:"
        )
        print(NOISY_IMAGE_DIR)
        return

    if not os.path.exists(GROUND_TRUTH_FILE):

        print(
            "ERROR: ground_truth.csv not found at:"
        )
        print(GROUND_TRUTH_FILE)
        return

    # --------------------------------------------------------
    # Load ground truth
    # --------------------------------------------------------

    ground_truth_df = pd.read_csv(
        GROUND_TRUTH_FILE,
        dtype=str,
    ).fillna("")

    required_columns = [
        "image",
        *BENCHMARK_FIELDS,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in ground_truth_df.columns
    ]

    if missing_columns:

        print(
            "ERROR: ground_truth.csv is missing:"
        )

        for column in missing_columns:
            print(
                f"  - {column}"
            )

        print()
        print(
            "Available columns:"
        )
        print(
            list(ground_truth_df.columns)
        )

        return

    # --------------------------------------------------------
    # Find noisy images
    # --------------------------------------------------------

    noisy_images = sorted(
        file
        for file in os.listdir(
            NOISY_IMAGE_DIR
        )
        if file.lower().endswith(
            (
                ".jpg",
                ".jpeg",
                ".png",
                ".bmp",
                ".tif",
                ".tiff",
            )
        )
    )

    print(
        f"Found {len(noisy_images)} noisy invoice images."
    )

    print(
        f"Found {len(ground_truth_df)} ground-truth rows."
    )

    # --------------------------------------------------------
    # Evaluate
    # --------------------------------------------------------

    all_results = []
    tested_images = set()

    for _, row in ground_truth_df.iterrows():

        image_name = str(
            row["image"]
        ).strip()

        if not image_name:
            continue

        image_path = os.path.join(
            NOISY_IMAGE_DIR,
            image_name,
        )

        if not os.path.exists(image_path):

            print(
                f"WARNING: No noisy image for {image_name}"
            )

            continue

        ground_truth = {
            field: str(
                row[field]
            ).strip()
            for field in BENCHMARK_FIELDS
        }

        print(
            f"Evaluating: {image_name}"
        )

        results = evaluate_image(
            image_path,
            ground_truth,
        )

        if results:

            tested_images.add(
                image_name
            )

            all_results.extend(
                results
            )

    # --------------------------------------------------------
    # Coverage
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("BENCHMARK COVERAGE")
    print("=" * 70)

    print(
        f"Ground-truth invoices : "
        f"{len(ground_truth_df)}"
    )

    print(
        f"Noisy images found    : "
        f"{len(noisy_images)}"
    )

    print(
        f"Invoices evaluated    : "
        f"{len(tested_images)}"
    )

    if not all_results:

        print(
            "\nERROR: No benchmark results generated."
        )

        return

    # ========================================================
    # DETAILED RESULTS
    # ========================================================

    detailed_rows = []

    for result in all_results:

        base = {
            "image": result["image"],
            "method": result["method"],
            "ocr_confidence": result[
                "ocr_confidence"
            ],
        }

        for field in BENCHMARK_FIELDS:

            field_result = result[
                "field_results"
            ].get(
                field,
                {},
            )

            detailed_rows.append({
                **base,
                "field": field,
                "actual": field_result.get(
                    "actual",
                    "",
                ),
                "predicted": field_result.get(
                    "predicted",
                    "",
                ),
                "exact_match": field_result.get(
                    "exact_match",
                    False,
                ),
                "character_accuracy": field_result.get(
                    "character_accuracy",
                    0,
                ),
            })

    detailed_df = pd.DataFrame(
        detailed_rows
    )

    detailed_file = os.path.join(
        OUTPUT_DIR,
        "detailed_field_results.csv",
    )

    detailed_df.to_csv(
        detailed_file,
        index=False,
    )

    # ========================================================
    # FIELD-LEVEL SUMMARY
    # ========================================================

    field_summary_rows = []

    for method in sorted(
        detailed_df["method"].unique()
    ):

        method_df = detailed_df[
            detailed_df["method"] == method
        ]

        for field in BENCHMARK_FIELDS:

            field_df = method_df[
                method_df["field"] == field
            ]

            evaluated = len(
                field_df
            )

            correct = int(
                field_df[
                    "exact_match"
                ].sum()
            )

            exact_accuracy = (
                correct
                / evaluated
                * 100
                if evaluated
                else 0
            )

            char_accuracy = (
                field_df[
                    "character_accuracy"
                ].mean()
                if evaluated
                else 0
            )

            field_summary_rows.append({
                "method": method,
                "field": field,
                "correct": correct,
                "evaluated": evaluated,
                "exact_field_accuracy": round(
                    exact_accuracy,
                    2,
                ),
                "character_accuracy": round(
                    char_accuracy,
                    2,
                ),
            })

    field_summary_df = pd.DataFrame(
        field_summary_rows
    )

    field_summary_file = os.path.join(
        OUTPUT_DIR,
        "field_comparison.csv",
    )

    field_summary_df.to_csv(
        field_summary_file,
        index=False,
    )

    # ========================================================
    # METHOD SUMMARY
    # ========================================================

    method_rows = []

    for method in sorted(
        detailed_df["method"].unique()
    ):

        method_df = detailed_df[
            detailed_df["method"] == method
        ]

        evaluated = len(
            method_df
        )

        correct = int(
            method_df[
                "exact_match"
            ].sum()
        )

        field_accuracy = (
            correct
            / evaluated
            * 100
            if evaluated
            else 0
        )

        character_accuracy = (
            method_df[
                "character_accuracy"
            ].mean()
            if evaluated
            else 0
        )

        incorrect_or_missing = (
            evaluated
            - correct
        )

        review_rate = (
            incorrect_or_missing
            / evaluated
            * 100
            if evaluated
            else 0
        )

        ocr_confidence = method_df[
            "ocr_confidence"
        ].dropna().mean()

        method_rows.append({
            "method": method,
            "invoices_tested": method_df[
                "image"
            ].nunique(),
            "correct_fields": correct,
            "evaluated_fields": evaluated,
            "aggregate_field_accuracy": round(
                field_accuracy,
                2,
            ),
            "character_accuracy": round(
                character_accuracy,
                2,
            ),
            "manual_review_proxy_rate": round(
                review_rate,
                2,
            ),
            "average_tesseract_confidence": (
                round(
                    ocr_confidence,
                    2,
                )
                if pd.notna(ocr_confidence)
                else None
            ),
        })

    method_summary_df = pd.DataFrame(
        method_rows
    )

    method_summary_df = method_summary_df.sort_values(
        "aggregate_field_accuracy",
        ascending=False,
    )

    method_summary_file = os.path.join(
        OUTPUT_DIR,
        "method_comparison.csv",
    )

    method_summary_df.to_csv(
        method_summary_file,
        index=False,
    )

    # ========================================================
    # BASELINE VS BEST
    # ========================================================

    original_row = method_summary_df[
        method_summary_df["method"] == "Original"
    ]

    if original_row.empty:

        print(
            "\nWARNING: Original baseline not found."
        )

        return

    original = original_row.iloc[0]

    best = method_summary_df.iloc[0]

    comparison_rows = []

    metrics = [
        (
            "Character Accuracy",
            "character_accuracy",
            "%",
        ),
        (
            "Overall Field Accuracy",
            "aggregate_field_accuracy",
            "%",
        ),
        (
            "Manual Review Proxy Rate",
            "manual_review_proxy_rate",
            "%",
        ),
    ]

    for label, column, unit in metrics:

        baseline_value = float(
            original[column]
        )

        improved_value = float(
            best[column]
        )

        if "Review" in label:

            improvement = (
                baseline_value
                - improved_value
            )

        else:

            improvement = (
                improved_value
                - baseline_value
            )

        comparison_rows.append({
            "metric": label,
            "baseline_method": "Original",
            "improved_method": best["method"],
            "baseline_value": round(
                baseline_value,
                2,
            ),
            "improved_value": round(
                improved_value,
                2,
            ),
            "improvement_percentage_points": round(
                improvement,
                2,
            ),
        })

    # --------------------------------------------------------
    # Individual field comparison
    # --------------------------------------------------------

    for field in BENCHMARK_FIELDS:

        baseline_field = field_summary_df[
            (
                field_summary_df["method"]
                == "Original"
            )
            &
            (
                field_summary_df["field"]
                == field
            )
        ]

        improved_field = field_summary_df[
            (
                field_summary_df["method"]
                == best["method"]
            )
            &
            (
                field_summary_df["field"]
                == field
            )
        ]

        if baseline_field.empty or improved_field.empty:
            continue

        baseline_value = float(
            baseline_field.iloc[0][
                "exact_field_accuracy"
            ]
        )

        improved_value = float(
            improved_field.iloc[0][
                "exact_field_accuracy"
            ]
        )

        comparison_rows.append({
            "metric": f"{field} Accuracy",
            "baseline_method": "Original",
            "improved_method": best["method"],
            "baseline_value": round(
                baseline_value,
                2,
            ),
            "improved_value": round(
                improved_value,
                2,
            ),
            "improvement_percentage_points": round(
                improved_value
                - baseline_value,
                2,
            ),
        })

    # --------------------------------------------------------
    # Combined amount accuracy
    # --------------------------------------------------------

    for method_name in [
        "Original",
        best["method"],
    ]:

        amount_df = field_summary_df[
            (
                field_summary_df["method"]
                == method_name
            )
            &
            (
                field_summary_df["field"].isin(
                    AMOUNT_FIELDS
                )
            )
        ]

        amount_accuracy = amount_df[
            "exact_field_accuracy"
        ].mean()

        if method_name == "Original":
            baseline_amount = amount_accuracy
        else:
            improved_amount = amount_accuracy

    comparison_rows.append({
        "metric": "Amount Fields Accuracy",
        "baseline_method": "Original",
        "improved_method": best["method"],
        "baseline_value": round(
            baseline_amount,
            2,
        ),
        "improved_value": round(
            improved_amount,
            2,
        ),
        "improvement_percentage_points": round(
            improved_amount
            - baseline_amount,
            2,
        ),
    })

    comparison_df = pd.DataFrame(
        comparison_rows
    )

    comparison_file = os.path.join(
        OUTPUT_DIR,
        "benchmark_comparison.csv",
    )

    comparison_df.to_csv(
        comparison_file,
        index=False,
    )

    # ========================================================
    # CONSOLE REPORT
    # ========================================================

    print()
    print("=" * 70)
    print("BASELINE VS IMPROVED DATASET EVALUATION")
    print("=" * 70)

    print()

    print(
        f"Baseline method : {original['method']}"
    )

    print(
        f"Improved method : {best['method']}"
    )

    print()

    print(
        comparison_df[
            [
                "metric",
                "baseline_value",
                "improved_value",
                "improvement_percentage_points",
            ]
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # GRAPH 1 — BASELINE VS BEST METRICS
    # ========================================================

    plot_metrics = comparison_df[
        comparison_df["metric"].isin(
            [
                "Character Accuracy",
                "Overall Field Accuracy",
                "Amount Fields Accuracy",
            ]
        )
    ].copy()

    x = range(
        len(plot_metrics)
    )

    width = 0.35

    plt.figure(
        figsize=(11, 6)
    )

    plt.bar(
        [
            i - width / 2
            for i in x
        ],
        plot_metrics[
            "baseline_value"
        ],
        width=width,
        label="Original Baseline",
    )

    plt.bar(
        [
            i + width / 2
            for i in x
        ],
        plot_metrics[
            "improved_value"
        ],
        width=width,
        label=best["method"],
    )

    plt.xticks(
        list(x),
        plot_metrics["metric"],
        rotation=20,
        ha="right",
    )

    plt.ylabel("Accuracy (%)")
    plt.title(
        "Baseline vs Best Preprocessing"
    )
    plt.ylim(0, 100)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "baseline_vs_best_metrics.png",
        ),
        dpi=150,
    )

    plt.close()

    # ========================================================
    # GRAPH 2 — FIELD ACCURACY BASELINE VS BEST
    # ========================================================

    field_plot = comparison_df[
        comparison_df["metric"].str.endswith(
            "Accuracy"
        )
        &
        ~comparison_df["metric"].isin(
            [
                "Character Accuracy",
                "Overall Field Accuracy",
                "Amount Fields Accuracy",
            ]
        )
    ].copy()

    plt.figure(
        figsize=(13, 7)
    )

    x = range(
        len(field_plot)
    )

    plt.bar(
        [
            i - width / 2
            for i in x
        ],
        field_plot[
            "baseline_value"
        ],
        width=width,
        label="Original Baseline",
    )

    plt.bar(
        [
            i + width / 2
            for i in x
        ],
        field_plot[
            "improved_value"
        ],
        width=width,
        label=best["method"],
    )

    plt.xticks(
        list(x),
        [
            metric.replace(
                " Accuracy",
                "",
            )
            for metric in field_plot[
                "metric"
            ]
        ],
        rotation=35,
        ha="right",
    )

    plt.ylabel("Exact Field Accuracy (%)")
    plt.title(
        "Field-Level Accuracy: Baseline vs Best Preprocessing"
    )
    plt.ylim(0, 100)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "field_accuracy_baseline_vs_best.png",
        ),
        dpi=150,
    )

    plt.close()

    # ========================================================
    # GRAPH 3 — ALL PREPROCESSING METHODS
    # ========================================================

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        method_summary_df["method"],
        method_summary_df[
            "aggregate_field_accuracy"
        ],
    )

    plt.ylabel(
        "Aggregate Field Accuracy (%)"
    )

    plt.xlabel(
        "Preprocessing Method"
    )

    plt.title(
        "OCR Field Accuracy Across Preprocessing Methods"
    )

    plt.ylim(0, 100)

    plt.xticks(
        rotation=30
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "all_methods_field_accuracy.png",
        ),
        dpi=150,
    )

    plt.close()

    # ========================================================
    # GRAPH 4 — MANUAL REVIEW PROXY
    # ========================================================

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        method_summary_df["method"],
        method_summary_df[
            "manual_review_proxy_rate"
        ],
    )

    plt.ylabel(
        "Incorrect/Missing Fields (%)"
    )

    plt.xlabel(
        "Preprocessing Method"
    )

    plt.title(
        "Manual-Review Proxy Rate Across Methods"
    )

    plt.ylim(0, 100)

    plt.xticks(
        rotation=30
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "all_methods_manual_review_rate.png",
        ),
        dpi=150,
    )

    plt.close()

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print("=" * 70)
    print("BENCHMARK COMPLETED")
    print("=" * 70)

    print()
    print(
        f"Best preprocessing method: "
        f"{best['method']}"
    )

    print(
        f"Baseline field accuracy: "
        f"{original['aggregate_field_accuracy']:.2f}%"
    )

    print(
        f"Best field accuracy: "
        f"{best['aggregate_field_accuracy']:.2f}%"
    )

    print(
        f"Field accuracy improvement: "
        f"{best['aggregate_field_accuracy'] - original['aggregate_field_accuracy']:+.2f} "
        f"percentage points"
    )

    print(
        f"Baseline character accuracy: "
        f"{original['character_accuracy']:.2f}%"
    )

    print(
        f"Best character accuracy: "
        f"{best['character_accuracy']:.2f}%"
    )

    print(
        f"Character accuracy improvement: "
        f"{best['character_accuracy'] - original['character_accuracy']:+.2f} "
        f"percentage points"
    )

    print(
        f"Baseline manual-review proxy: "
        f"{original['manual_review_proxy_rate']:.2f}%"
    )

    print(
        f"Best manual-review proxy: "
        f"{best['manual_review_proxy_rate']:.2f}%"
    )

    print(
        f"Manual-review proxy reduction: "
        f"{original['manual_review_proxy_rate'] - best['manual_review_proxy_rate']:+.2f} "
        f"percentage points"
    )

    print()
    print("Files generated:")
    print(
        f"  {detailed_file}"
    )
    print(
        f"  {field_summary_file}"
    )
    print(
        f"  {method_summary_file}"
    )
    print(
        f"  {comparison_file}"
    )

    print()
    print(
        f"Graphs saved in:\n"
        f"  {OUTPUT_DIR}"
    )

    print()
    print(
        "Important:"
    )

    print(
        "Character accuracy is calculated from "
        "predicted vs ground-truth field text."
    )

    print(
        "Field accuracy is exact normalized field matching."
    )

    print(
        "Tesseract confidence is reported separately "
        "and is NOT treated as factual accuracy."
    )

    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()


