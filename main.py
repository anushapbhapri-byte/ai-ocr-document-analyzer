import cv2

from preprocess import (
    to_gray,
    apply_threshold,
    adaptive_threshold,
    denoise,
    resize_image,
    sharpen_image
)

from ocr_engine import ocr_with_word_confidence

from analytics import (
    generate_report,
    calculate_quality_score
)

from graph_engine import create_graphs


# ============================================================
# LOAD IMAGE
# ============================================================

image = cv2.imread(
    "data/invoice.jpg"
)

if image is None:

    print(
        "Image not found: data/invoice.jpg"
    )

    raise SystemExit


# ============================================================
# PREPROCESSING METHODS
# ============================================================

methods = {

    "Original": image,

    "Gray": to_gray(image),

    "Threshold": apply_threshold(image),

    "Adaptive": adaptive_threshold(image),

    "Denoise": denoise(image),

    "Resize": resize_image(image),

    "Sharpen": sharpen_image(image)
}


# ============================================================
# OCR ANALYSIS
# ============================================================

results = {}

for name, img in methods.items():

    text, word_data = (
        ocr_with_word_confidence(img)
    )

    confidences = []

    for item in word_data:

        try:
            conf = float(
                item.get(
                    "confidence",
                    -1
                )
            )
        except (TypeError, ValueError):
            conf = -1

        if conf >= 0:
            confidences.append(conf)

    if confidences:

        average_confidence = (
            sum(confidences)
            / len(confidences)
        )

    else:

        average_confidence = 0.0

    quality_score = calculate_quality_score(
    text,
    average_confidence
)

    results[name] = {

        "words": len(text.split()),

        "chars": len(text),

        "confidence": average_confidence,

        "quality": quality_score,

        "time": "",

        "text": text,

        "word_data": word_data
    }


# ============================================================
# PERFORMANCE REPORT
# ============================================================

report, best_method = (
    generate_report(results)
)

print(report)


# ============================================================
# GRAPH DATA
# ============================================================

method_names = list(
    results.keys()
)

word_scores = [
    results[name]["words"]
    for name in method_names
]

confidence_scores = [
    results[name]["confidence"]
    for name in method_names
]

quality_scores = [
    results[name]["quality"]
    if "quality" in results[name]
    else 0.0
    for name in method_names
]


# ============================================================
# CREATE GRAPHS
# ============================================================

create_graphs(
    method_names,
    word_scores,
    confidence_scores,
    quality_scores,
    best_method
)

print(
    f"\nBest preprocessing method: "
    f"{best_method}"
)

print(
    "\nOCR analysis completed successfully."
)