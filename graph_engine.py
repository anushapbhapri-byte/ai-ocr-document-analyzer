import os
import matplotlib.pyplot as plt


def create_graphs(
    methods,
    words,
    confidences,
    quality_scores,
    best_method=None
):
    """
    Create OCR performance graphs.

    Graphs created:
    1. Measured OCR confidence
    2. OCR quality score
    3. Word count diagnostic

    IMPORTANT:
    The quality score is a quality indicator.
    It is NOT ground-truth OCR accuracy.
    """

    # =========================================================
    # CREATE OUTPUT FOLDER
    # =========================================================

    os.makedirs("outputs", exist_ok=True)

    # =========================================================
    # GRAPH 1 — MEASURED OCR CONFIDENCE
    # =========================================================

    plt.figure(figsize=(10, 5))

    bars = plt.bar(
        methods,
        confidences
    )

    plt.title(
        "Measured OCR Confidence by Preprocessing Method"
    )

    plt.xlabel(
        "Preprocessing Method"
    )

    plt.ylabel(
        "Average Tesseract Confidence (%)"
    )

    plt.ylim(0, 100)

    plt.xticks(
        rotation=30,
        ha="right"
    )

    # Display values above bars
    for bar, value in zip(bars, confidences):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9
        )

    if best_method in methods:

        plt.figtext(
            0.5,
            0.01,
            f"Selected method: {best_method}",
            ha="center",
            fontsize=9
        )

        plt.tight_layout(
            rect=[0, 0.04, 1, 1]
        )

    else:

        plt.tight_layout()

    plt.savefig(
        "outputs/ocr_confidence_graph.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # =========================================================
    # GRAPH 2 — OCR QUALITY SCORE
    # =========================================================

    plt.figure(figsize=(10, 5))

    bars = plt.bar(
        methods,
        quality_scores
    )

    plt.title(
        "OCR Quality Score by Preprocessing Method\n"
        "(Quality indicator — NOT ground-truth accuracy)"
    )

    plt.xlabel(
        "Preprocessing Method"
    )

    plt.ylabel(
        "Quality Score (0–100)"
    )

    plt.ylim(0, 100)

    plt.xticks(
        rotation=30,
        ha="right"
    )

    # Display values above bars
    for bar, value in zip(bars, quality_scores):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.1f}",
            ha="center",
            va="bottom",
            fontsize=9
        )

    if best_method in methods:

        plt.figtext(
            0.5,
            0.01,
            f"Selected method: {best_method}",
            ha="center",
            fontsize=9
        )

        plt.tight_layout(
            rect=[0, 0.04, 1, 1]
        )

    else:

        plt.tight_layout()

    plt.savefig(
        "outputs/ocr_quality_graph.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # =========================================================
    # GRAPH 3 — WORD COUNT DIAGNOSTIC
    # =========================================================

    plt.figure(figsize=(10, 5))

    bars = plt.bar(
        methods,
        words
    )

    plt.title(
        "OCR Word Count by Preprocessing Method\n"
        "(Diagnostic metric — not an accuracy measure)"
    )

    plt.xlabel(
        "Preprocessing Method"
    )

    plt.ylabel(
        "Words Detected"
    )

    plt.xticks(
        rotation=30,
        ha="right"
    )

    # Display values above bars
    for bar, value in zip(bars, words):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(value),
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.tight_layout()

    plt.savefig(
        "outputs/word_count_graph.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # =========================================================
    # COMPLETION MESSAGE
    # =========================================================

    print(
        "OCR performance graphs saved in outputs folder."
    )