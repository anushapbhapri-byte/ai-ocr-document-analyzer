import cv2
import pytesseract

from preprocess import (
    to_gray,
    apply_threshold,
    adaptive_threshold,
    denoise,
    resize_image,
    sharpen_image
)


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

def _configure_tesseract():
    """Configure Tesseract without requiring a machine-specific path."""
    import os
    import shutil

    configured = os.environ.get("TESSERACT_CMD", "").strip()
    candidates = [configured] if configured else []

    # Common Windows installation locations are fallbacks, not requirements.
    if os.name == "nt":
        candidates.extend([
            os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"),
                         "Tesseract-OCR", "tesseract.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                         "Tesseract-OCR", "tesseract.exe"),
        ])

    discovered = shutil.which("tesseract")
    if discovered:
        candidates.append(discovered)

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            pytesseract.pytesseract.tesseract_cmd = candidate
            return candidate

    # Leave pytesseract's default behavior intact so PATH-based installs work.
    return getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")

TESSERACT_CMD = _configure_tesseract()


# ============================================================
# BASIC OCR
# ============================================================

def extract_text(image):
    """
    Perform normal OCR and return extracted text.
    """
    if image is None:
        return ""

    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"OCR error: {e}")
        return ""


# ============================================================
# CREATE OCR PREPROCESSING VARIANTS
# ============================================================

def create_ocr_variants(image):
    """
    Create multiple preprocessing versions of the same image.

    These variants are used for benchmark comparison.

    Returns:
        Dictionary:
            method name -> processed image
    """

    if image is None:
        return {}

    variants = {
        "Original": image,
        "Gray": to_gray(image),
        "Threshold": apply_threshold(image),
        "Adaptive": adaptive_threshold(image),
        "Denoise": denoise(image),
        "Resize": resize_image(image),
        "Sharpen": sharpen_image(image),
    }

    return variants


# ============================================================
# OCR WITH REAL TESSERACT CONFIDENCE
# ============================================================

def ocr_with_word_confidence(image, psm=6):
    """
    Perform OCR and return:

        1. Extracted OCR text
        2. Word-level confidence values from Tesseract

    IMPORTANT:
        Tesseract confidence is an OCR recognition signal.

        It is NOT:
        - a probability that the field is factually correct
        - ground-truth accuracy
        - a guarantee that the extracted value is correct

    Example returned word:

        {
            "text": "GSTIN",
            "confidence": 94.52
        }
    """

    if image is None:
        return "", []

    config = f"--oem 3 --psm {psm}"

    try:
        data = pytesseract.image_to_data(
            image,
            config=config,
            output_type=pytesseract.Output.DICT
        )
    except Exception as e:
        print(f"Tesseract confidence error: {e}")
        return "", []

    words = []

    for i in range(len(data["text"])):

        word = str(data["text"][i]).strip()

        if not word:
            continue

        try:
            confidence = float(data["conf"][i])
        except (TypeError, ValueError):
            confidence = -1

        # Tesseract can return -1 for non-word levels.
        if confidence < 0:
            continue

        words.append({
            "text": word,
            "confidence": confidence
        })

    text = " ".join(
        item["text"]
        for item in words
    )

    return text, words


# ============================================================
# CALCULATE AVERAGE TESSERACT CONFIDENCE
# ============================================================

def calculate_average_ocr_confidence(words):
    """
    Calculate the average word-level Tesseract confidence.

    This is a measured OCR confidence signal.

    It should NOT be interpreted as field correctness.
    """

    if not words:
        return 0.0

    confidences = [
        float(item["confidence"])
        for item in words
        if item.get("confidence") is not None
    ]

    if not confidences:
        return 0.0

    return round(
        sum(confidences) / len(confidences),
        2
    )


# ============================================================
# OCR PIPELINE
# ============================================================

def run_ocr_pipeline(image_path):
    """
    Run OCR using all preprocessing methods.

    Each result contains:

        method
        image
        text
        words
        chars
        ocr_confidence

    ocr_confidence is the measured average Tesseract
    word-level confidence for that preprocessing method.
    """

    image = cv2.imread(image_path)

    if image is None:
        print("Error: Image not found!")
        return []

    methods = create_ocr_variants(image)

    results = []

    for name, img in methods.items():

        # Normal OCR text
        text = extract_text(img)

        # Real Tesseract confidence
        confidence_text, word_data = (
            ocr_with_word_confidence(img)
        )

        average_confidence = (
            calculate_average_ocr_confidence(word_data)
        )

        # Use normal OCR text as the primary extracted text.
        # If it is empty, fall back to confidence OCR text.
        if not text.strip():
            text = confidence_text

        results.append({
            "method": name,
            "image": img,
            "text": text,
            "words": len(text.split()),
            "chars": len(text),
            "ocr_confidence": average_confidence,
            "word_data": word_data
        })

    return results


# ============================================================
# GET OCR CONFIDENCE FOR A SELECTED IMAGE
# ============================================================

def get_ocr_confidence(image):
    """
    Convenience function used by the GUI.

    Returns:

        OCR text
        Word-level Tesseract confidence data
    """

    return ocr_with_word_confidence(image)


# ============================================================
# GET AVERAGE OCR CONFIDENCE
# ============================================================

def get_average_ocr_confidence(image):
    """
    Convenience function that returns the average
    Tesseract word-level confidence for an image.
    """

    _, words = ocr_with_word_confidence(image)

    return calculate_average_ocr_confidence(words)


# ============================================================
# OPTIONAL: SAVE OCR TEXT
# ============================================================

def save_text(path, text):
    """
    Save OCR text to a UTF-8 text file.
    """

    with open(path, "w", encoding="utf-8") as file:
        file.write(text)