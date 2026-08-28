import os
import time
import cv2
import pandas as pd

from ocr_engine import (
    create_ocr_variants,
    ocr_with_word_confidence,
    calculate_average_ocr_confidence,
)

from data_extractor import extract_invoice_data


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_INPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "batch_invoices",
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "batch",
)

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
}

FIELDS = [
    "Invoice Number",
    "Invoice Date",
    "Seller Tax ID",
    "Client Tax ID",
    "Seller IBAN",
    "Net Worth",
    "VAT",
    "Gross Worth",
]


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _select_method(variants):
    """
    Use the dataset-validated preprocessing recommendation.
    """
    if "Threshold" in variants:
        return "Threshold"

    return next(iter(variants))


def _review_status(data, confidence):
    """
    Operational review heuristic.

    Manual review is triggered when:
      - a benchmark field is missing, OR
      - average Tesseract OCR confidence is below 70%.

    This is a workflow heuristic, NOT a probability of correctness.
    """

    missing = [
        field
        for field in FIELDS
        if not str(data.get(field, "")).strip()
    ]

    if missing:
        return (
            "MANUAL REVIEW",
            "Missing: " + ", ".join(missing),
        )

    if confidence < 70:
        return (
            "MANUAL REVIEW",
            "Low OCR confidence",
        )

    return (
        "AUTO ACCEPT",
        "All benchmark fields present",
    )


def process_invoice(image_path):
    """
    Process one invoice using the dataset-validated Threshold method.
    """

    start = time.perf_counter()

    image = cv2.imread(image_path)

    if image is None:
        return {
            "Invoice": os.path.basename(image_path),
            "Processing Method": "ERROR",
            **{field: "" for field in FIELDS},
            "OCR Confidence": 0.0,
            "Validation Status": "ERROR",
            "Manual Review": "YES",
            "Review Reason": "Image could not be read",
            "Processing Time (seconds)": round(
                time.perf_counter() - start,
                3,
            ),
        }

    variants = create_ocr_variants(image)

    method = _select_method(variants)

    processed_image = variants[method]

    # IMPORTANT:
    # The second return value is word_data, not a numeric confidence.
    text, word_data = ocr_with_word_confidence(
        processed_image,
        psm=6,
    )

    # Correctly calculate the average confidence.
    average_confidence = calculate_average_ocr_confidence(
        word_data
    )

    data = extract_invoice_data(
        text,
        processed_image,
    )

    status, reason = _review_status(
        data,
        average_confidence,
    )

    return {
        "Invoice": os.path.basename(image_path),
        "Processing Method": method,
        **{
            field: data.get(field, "")
            for field in FIELDS
        },
        "OCR Confidence": round(
            average_confidence,
            2,
        ),
        "Validation Status": status,
        "Manual Review": (
            "YES"
            if status == "MANUAL REVIEW"
            else "NO"
        ),
        "Review Reason": reason,
        "Processing Time (seconds)": round(
            time.perf_counter() - start,
            3,
        ),
    }


def process_batch(input_dir=DEFAULT_INPUT_DIR):
    """
    Process every supported invoice image in input_dir.
    """

    print("=" * 68)
    print("BATCH INVOICE PROCESSING")
    print("=" * 68)

    if not os.path.isdir(input_dir):
        print()
        print(
            "Input folder does not exist:"
        )
        print(input_dir)
        print()
        print(
            "Create it and place invoice images inside it."
        )
        return None

    files = sorted(
        filename
        for filename in os.listdir(input_dir)
        if os.path.splitext(filename)[1].lower()
        in SUPPORTED_EXTENSIONS
    )

    if not files:
        print()
        print(
            "No supported invoice images found."
        )
        print(
            "Supported formats:",
            ", ".join(
                sorted(SUPPORTED_EXTENSIONS)
            ),
        )
        return None

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    print()
    print(
        f"Input folder   : {input_dir}"
    )
    print(
        f"Invoices found : {len(files)}"
    )
    print()

    results = []

    for index, filename in enumerate(
        files,
        start=1,
    ):
        print(
            f"[{index}/{len(files)}] Processing {filename}"
        )

        image_path = os.path.join(
            input_dir,
            filename,
        )

        try:
            result = process_invoice(
                image_path
            )

        except Exception as exc:
            result = {
                "Invoice": filename,
                "Processing Method": "ERROR",
                **{
                    field: ""
                    for field in FIELDS
                },
                "OCR Confidence": 0.0,
                "Validation Status": "ERROR",
                "Manual Review": "YES",
                "Review Reason": (
                    f"Processing error: {exc}"
                ),
                "Processing Time (seconds)": 0.0,
            }

        results.append(result)

    columns = [
        "Invoice",
        "Processing Method",
        *FIELDS,
        "OCR Confidence",
        "Validation Status",
        "Manual Review",
        "Review Reason",
        "Processing Time (seconds)",
    ]

    df = pd.DataFrame(
        results
    ).reindex(
        columns=columns
    )

    csv_path = os.path.join(
        OUTPUT_DIR,
        "batch_invoice_results.csv",
    )

    xlsx_path = os.path.join(
        OUTPUT_DIR,
        "batch_invoice_results.xlsx",
    )

    df.to_csv(
        csv_path,
        index=False,
    )

    df.to_excel(
        xlsx_path,
        index=False,
        engine="openpyxl",
    )

    # ========================================================
    # BATCH KPIs
    # ========================================================

    total = len(df)

    auto_accepted = int(
        (
            df["Validation Status"]
            == "AUTO ACCEPT"
        ).sum()
    )

    manual_review = int(
        (
            df["Manual Review"]
            == "YES"
        ).sum()
    )

    errors = int(
        (
            df["Validation Status"]
            == "ERROR"
        ).sum()
    )

    straight_through_rate = (
        auto_accepted
        / total
        * 100
        if total
        else 0
    )

    manual_review_rate = (
        manual_review
        / total
        * 100
        if total
        else 0
    )

    average_time = (
        pd.to_numeric(
            df["Processing Time (seconds)"],
            errors="coerce",
        ).mean()
        if total
        else 0
    )

    print()
    print("=" * 68)
    print("BATCH KPIs")
    print("=" * 68)

    print(
        f"Total invoices          : {total}"
    )

    print(
        f"Auto accepted           : {auto_accepted}"
    )

    print(
        f"Manual review           : {manual_review}"
    )

    print(
        f"Processing errors       : {errors}"
    )

    print(
        f"Straight-through rate   : "
        f"{straight_through_rate:.2f}%"
    )

    print(
        f"Manual-review rate      : "
        f"{manual_review_rate:.2f}%"
    )

    print(
        f"Average processing time : "
        f"{average_time:.3f} seconds/invoice"
    )

    print()
    print("=" * 68)
    print("FILES GENERATED")
    print("=" * 68)

    print(
        f"CSV   : {csv_path}"
    )

    print(
        f"Excel : {xlsx_path}"
    )

    print()
    print(
        "BATCH INVOICE PROCESSOR COMPLETED"
    )

    return df


if __name__ == "__main__":
    process_batch()