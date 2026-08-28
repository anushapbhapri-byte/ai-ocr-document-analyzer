import csv
import os


BENCHMARK_SUMMARY = os.path.join(
    "outputs",
    "benchmark",
    "method_comparison.csv",
)


def _load_benchmark_winner():
    """
    Load the globally validated preprocessing winner from the
    benchmark dataset.

    The GUI must NOT select a method using character count.
    Character count is only descriptive and is not an accuracy metric.

    Returns:
        (method_name, field_accuracy) or (None, None)
    """

    if not os.path.exists(BENCHMARK_SUMMARY):
        return None, None

    try:
        with open(
            BENCHMARK_SUMMARY,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            rows = list(csv.DictReader(file))

        if not rows:
            return None, None

        best_method = None
        best_accuracy = -1.0

        for row in rows:

            method = str(
                row.get("method", "")
            ).strip()

            raw_accuracy = row.get(
                "aggregate_field_accuracy",
                row.get("field_accuracy", ""),
            )

            try:
                accuracy = float(raw_accuracy)
            except (TypeError, ValueError):
                continue

            if method and accuracy > best_accuracy:
                best_accuracy = accuracy
                best_method = method

        if best_method is None:
            return None, None

        return best_method, best_accuracy

    except (OSError, csv.Error, ValueError):
        return None, None


def calculate_quality_score(text, confidence):
    """
    Calculate a lightweight OCR quality indicator for the legacy
    command-line pipeline.

    This is a diagnostic score only; it is NOT ground-truth accuracy.
    It combines measured Tesseract confidence with a simple text
    completeness signal so the CLI can continue to produce the
    historical quality graph without importing a nonexistent function.
    """
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    text = str(text or "").strip()
    word_count = len(text.split())

    # A normal invoice OCR result in this project contains substantially
    # more than 20 words. Treat 100 words as a practical completeness
    # ceiling rather than claiming this is an accuracy metric.
    completeness = min(word_count / 100.0, 1.0) * 100.0

    score = (confidence * 0.8) + (completeness * 0.2)
    return round(max(0.0, min(score, 100.0)), 2)


def generate_report(results):
    """
    Generate the live OCR method-comparison report used by gui_app.py.

    IMPORTANT:
    The GUI no longer selects a method by character count.

    Method selection is based on the manually verified benchmark
    stored in outputs/benchmark/method_comparison.csv.

    The benchmark winner is a DATASET-LEVEL recommendation. It does
    not claim that the same method is mathematically optimal for
    every individual invoice.

    Returns:
        report, recommended_method
    """

    report = "===== OCR METHOD COMPARISON =====\n\n"

    report += (
        "Method        Words     Characters   "
        "OCR Conf.     Time\n"
    )
    report += (
        "-------------------------------------------------------\n"
    )

    # ------------------------------------------------------------
    # Read the validated dataset-level winner.
    # ------------------------------------------------------------

    benchmark_method, benchmark_accuracy = (
        _load_benchmark_winner()
    )

    # ------------------------------------------------------------
    # Display live OCR statistics.
    # ------------------------------------------------------------

    for method, result in results.items():

        # Current gui_app.py stores results as dictionaries.
        words = result.get("words", 0)
        chars = result.get("chars", 0)
        confidence = result.get(
            "confidence",
            0.0,
        )
        processing_time = result.get(
            "time",
            0.0,
        )

        try:
            confidence_display = (
                f"{float(confidence):.1f}%"
            )
        except (TypeError, ValueError):
            confidence_display = str(
                confidence
            )

        try:
            time_display = (
                f"{float(processing_time):.3f}s"
            )
        except (TypeError, ValueError):
            time_display = str(
                processing_time
            )

        report += (
            f"{method:<14}"
            f"{words:<10}"
            f"{chars:<13}"
            f"{confidence_display:<13}"
            f"{time_display}\n"
        )

    # ------------------------------------------------------------
    # Select the validated benchmark winner.
    # ------------------------------------------------------------

    if benchmark_method:

        recommended_method = benchmark_method

        report += "\n"
        report += (
            "DATASET-VALIDATED RECOMMENDATION\n"
        )
        report += (
            f"Recommended Method: "
            f"{recommended_method}\n"
        )
        report += (
            f"Ground-truth field accuracy: "
            f"{benchmark_accuracy:.2f}%\n"
        )
        report += (
            "\nThis recommendation comes from the "
            "manually verified 50-invoice benchmark.\n"
        )
        report += (
            "It is a dataset-level recommendation, "
            "not a claim that every individual invoice "
            "has the same optimal preprocessing method.\n"
        )

    else:

        # There is no defensible ground-truth-based way to
        # choose a "best" method from live OCR character count.
        # Do not silently fall back to that invalid heuristic.
        recommended_method = "Threshold"

        report += "\n"
        report += (
            "RECOMMENDED METHOD: Threshold\n"
        )
        report += (
            "\nThe validated benchmark summary was not found.\n"
        )
        report += (
            "Threshold is the project's validated benchmark "
            "winner and is used as the configured default.\n"
        )

    return report, recommended_method