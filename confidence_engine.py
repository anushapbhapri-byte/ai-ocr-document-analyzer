import re
from difflib import SequenceMatcher


# ============================================================
# OCR CONFIDENCE ENGINE
# ============================================================
#
# IMPORTANT:
# The confidence shown by this module is the REAL OCR
# recognition confidence returned by Tesseract.
#
# It is NOT:
# - probability that the value is factually correct
# - validation confidence
# - a manually invented heuristic percentage
#
# Validation is handled separately by validation_engine.py.
# ============================================================


# ============================================================
# TOKEN NORMALIZATION
# ============================================================

def normalize_token(value):
    """
    Normalize a token so OCR words can be compared safely.

    Example:
        "1,16,800.00" -> "11680000"
        "KA-01-AB-1234" -> "KA01AB1234"
    """

    if value is None:
        return ""

    return re.sub(
        r"[^A-Za-z0-9]",
        "",
        str(value)
    ).upper()


# ============================================================
# EXTRACT OCR WORDS
# ============================================================

def _prepare_ocr_words(ocr_words):
    """
    Convert Tesseract word-level output into a clean list.

    Expected input:

    [
        {
            "text": "GSTIN",
            "confidence": 96.5
        },
        {
            "text": "29AAAAA1234F000",
            "confidence": 94.2
        }
    ]

    Returns normalized OCR tokens with confidence.
    """

    if not isinstance(ocr_words, (list, tuple)):
        return []

    prepared = []

    for item in ocr_words:

        if not isinstance(item, dict):
            continue

        text = str(
            item.get("text", "")
        ).strip()

        if not text:
            continue

        try:
            confidence = float(
                item.get("confidence", -1)
            )
        except (TypeError, ValueError):
            continue

        # Tesseract uses negative values for
        # non-word levels / invalid confidence.
        if confidence < 0:
            continue

        confidence = max(
            0.0,
            min(confidence, 100.0)
        )

        normalized = normalize_token(text)

        if not normalized:
            continue

        prepared.append(
            {
                "text": text,
                "normalized": normalized,
                "confidence": confidence
            }
        )

    return prepared


# ============================================================
# MATCH EXTRACTED VALUE TO OCR WORDS
# ============================================================

def _match_value_to_ocr_words(value, ocr_words):
    """
    Match the extracted field value against the actual
    Tesseract OCR words.

    Returns the confidence values of the OCR words
    that correspond to the extracted value.
    """

    value_tokens = re.findall(
        r"[A-Za-z0-9]+",
        str(value)
    )

    if not value_tokens:
        return []

    prepared_words = _prepare_ocr_words(
        ocr_words
    )

    if not prepared_words:
        return []

    matched_confidences = []
    used_indices = set()

    for token in value_tokens:

        target = normalize_token(token)

        if not target:
            continue

        best_index = None
        best_ratio = 0.0

        # ----------------------------------------------------
        # 1. Exact normalized match
        # ----------------------------------------------------

        for index, word in enumerate(prepared_words):

            if index in used_indices:
                continue

            if word["normalized"] == target:

                best_index = index
                best_ratio = 1.0
                break

        # ----------------------------------------------------
        # 2. Fuzzy match if exact match was not found
        # ----------------------------------------------------

        if best_index is None:

            for index, word in enumerate(prepared_words):

                if index in used_indices:
                    continue

                ratio = SequenceMatcher(
                    None,
                    target,
                    word["normalized"]
                ).ratio()

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_index = index

        # ----------------------------------------------------
        # Accept only reasonably strong matches
        # ----------------------------------------------------

        if (
            best_index is not None
            and best_ratio >= 0.75
        ):

            matched_confidences.append(
                prepared_words[best_index]["confidence"]
            )

            used_indices.add(best_index)

    return matched_confidences


# ============================================================
# CALCULATE REAL OCR CONFIDENCE
# ============================================================

def calculate_ocr_confidence(
    field,
    value,
    ocr_words
):
    """
    Calculate field-level OCR confidence using actual
    Tesseract word-level confidence values.

    Returns None when the field cannot be matched
    reliably to Tesseract OCR words.

    IMPORTANT:
    None is intentional.

    We NEVER invent a value such as 70%.
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    matched_confidences = _match_value_to_ocr_words(
        value,
        ocr_words
    )

    if not matched_confidences:
        return None

    average_confidence = (
        sum(matched_confidences)
        / len(matched_confidences)
    )

    return round(
        max(
            0.0,
            min(
                average_confidence,
                100.0
            )
        )
    )


# ============================================================
# FIELD CONFIDENCE
# ============================================================

def calculate_field_confidence(
    field,
    value,
    ocr_words=None
):
    """
    Return REAL OCR confidence for one extracted field.

    The confidence is derived from Tesseract's actual
    word-level recognition confidence.

    It is NOT a probability of factual correctness.
    """

    if value is None or not str(value).strip():

        return {
            "confidence": None,
            "status": "MANUAL REVIEW",
            "review": True,
            "confidence_available": False
        }

    confidence = calculate_ocr_confidence(
        field,
        value,
        ocr_words
    )

    # --------------------------------------------------------
    # No measured OCR confidence available
    # --------------------------------------------------------

    if confidence is None:

        return {
            "confidence": None,
            "status": "OCR CONF. N/A",
            "review": True,
            "confidence_available": False
        }

    # --------------------------------------------------------
    # Confidence thresholds
    #
    # These are REVIEW thresholds, not probability claims.
    # --------------------------------------------------------

    if confidence >= 85:

        status = "OK"
        review = False

    elif confidence >= 60:

        status = "CHECK"
        review = True

    else:

        status = "LOW OCR"
        review = True

    return {
        "confidence": confidence,
        "status": status,
        "review": review,
        "confidence_available": True
    }


# ============================================================
# COMPLETE FIELD ANALYSIS
# ============================================================

def analyze_fields(
    extracted_data,
    ocr_words=None
):
    """
    Analyze every extracted invoice field.

    Parameters
    ----------
    extracted_data : dict
        Extracted invoice fields.

    ocr_words : list
        Actual Tesseract word-level OCR results.

    Returns
    -------
    dict
        Structure expected by gui_app.py.
    """

    if not isinstance(
        extracted_data,
        dict
    ):
        return {}

    results = {}

    for field, value in extracted_data.items():

        results[field] = {
            "value": value,
            **calculate_field_confidence(
                field,
                value,
                ocr_words
            )
        }

    return results


# ============================================================
# TEXT FORMATTER
# ============================================================

def format_confidence_output(
    field_results
):
    """
    Optional text formatter.

    Clearly distinguishes measured OCR confidence
    from unavailable confidence.
    """

    lines = []
    review_count = 0

    for field, result in field_results.items():

        value = result.get(
            "value",
            ""
        )

        confidence = result.get(
            "confidence"
        )

        status = result.get(
            "status",
            "CHECK"
        )

        if result.get(
            "review",
            True
        ):
            review_count += 1
            symbol = "⚠"
        else:
            symbol = "✓"

        if confidence is None:

            confidence_text = "N/A"

        else:

            confidence_text = (
                f"{confidence}%"
            )

        lines.append(
            f"{field}: {value}\n"
            f"   OCR Confidence: "
            f"{confidence_text} | "
            f"{symbol} {status}\n"
        )

    if review_count:

        lines.append(
            f"\n⚠ {review_count} "
            f"field(s) require attention."
        )

    else:

        lines.append(
            "\n✓ All extracted fields "
            "passed the OCR confidence check."
        )

    return "\n".join(lines)