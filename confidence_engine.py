import re
from difflib import SequenceMatcher


# ============================================================
# OCR CONFIDENCE ENGINE
# ============================================================
#
# Reports measured Tesseract OCR confidence.
# It does NOT claim factual correctness.
# Validation is handled separately by validation_engine.py.
#
# The GUI passes Tesseract word-level data:
#     [{"text": "...", "confidence": 95.2}, ...]
#
# Field confidence is calculated from real Tesseract confidence
# values belonging to OCR words matched to that field.
# ============================================================


def normalize_token(value):
    """Normalize text for OCR matching."""
    if value is None:
        return ""

    return re.sub(
        r"[^A-Za-z0-9]",
        "",
        str(value)
    ).upper()


def _tokenize_value(value):
    """Return alphanumeric pieces of an extracted value."""
    return re.findall(
        r"[A-Za-z0-9]+",
        str(value or "")
    )


def _prepare_ocr_words(ocr_words):
    """Clean Tesseract word-level OCR results."""
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
                "confidence": confidence,
            }
        )

    return prepared


def _confidence_for_indices(
    prepared_words,
    indices
):
    """Return real Tesseract confidence values for OCR words."""
    return [
        prepared_words[index]["confidence"]
        for index in indices
        if 0 <= index < len(prepared_words)
    ]


def _best_sequence_match(
    target_full,
    prepared_words,
    start_index=0,
    end_index=None,
):
    """
    Find the strongest consecutive OCR-word sequence matching target.
    """
    if not target_full or not prepared_words:
        return None, 0.0

    if end_index is None:
        end_index = len(prepared_words)

    end_index = min(
        end_index,
        len(prepared_words)
    )

    if start_index >= end_index:
        return None, 0.0

    target_token_count = max(
        1,
        len(
            re.findall(
                r"[A-Za-z0-9]+",
                target_full
            )
        )
    )

    max_window = min(
        end_index - start_index,
        max(1, target_token_count + 3)
    )

    best_indices = None
    best_score = 0.0

    for start in range(
        start_index,
        end_index
    ):
        joined = ""

        for window_size in range(
            1,
            max_window + 1
        ):
            end = start + window_size

            if end > end_index:
                break

            joined += prepared_words[
                end - 1
            ]["normalized"]

            if not joined:
                continue

            if joined == target_full:
                return (
                    list(range(start, end)),
                    1.0
                )

            score = SequenceMatcher(
                None,
                target_full,
                joined
            ).ratio()

            if score > best_score:
                best_score = score
                best_indices = list(
                    range(start, end)
                )

    return best_indices, best_score


def _find_label_positions(
    field,
    prepared_words
):
    """
    Find OCR positions associated with an invoice field label.
    """
    field_normalized = normalize_token(field)

    if not field_normalized:
        return []

    positions = []

    for index, word in enumerate(
        prepared_words
    ):
        word_normalized = word["normalized"]

        if not word_normalized:
            continue

        if (
            word_normalized == field_normalized
            or field_normalized in word_normalized
            or word_normalized in field_normalized
        ):
            positions.append(index)

    aliases = {
        "SELLERTAXID": ["TAXID", "TAX"],
        "CLIENTTAXID": ["TAXID", "TAX"],
        "SELLERIBAN": ["IBAN"],
        "INVOICENUMBER": ["INVOICE"],
        "INVOICEDATE": ["DATE"],
        "NETWORTH": ["NETWORTH", "NET"],
        "VAT": ["VAT"],
        "GROSSWORTH": ["GROSSWORTH", "GROSS"],
    }

    for alias in aliases.get(
        field_normalized,
        []
    ):
        for index, word in enumerate(
            prepared_words
        ):
            if word["normalized"] == alias:
                positions.append(index)

    return sorted(set(positions))


def _match_value_to_ocr_words(
    field,
    value,
    ocr_words
):
    """
    Match an extracted field value to Tesseract OCR words.

    The matcher first searches near the field label, then searches
    the complete OCR sequence, and finally falls back to token-level
    fuzzy matching.

    Returned confidence values are always the real Tesseract values.
    """
    if value is None:
        return []

    value = str(value).strip()

    if not value:
        return []

    prepared_words = _prepare_ocr_words(
        ocr_words
    )

    if not prepared_words:
        return []

    target_full = normalize_token(value)

    if not target_full:
        return []

    # 1. Prefer a value found close to its field label.
    label_positions = _find_label_positions(
        field,
        prepared_words
    )

    best_indices = None
    best_score = 0.0

    for label_position in label_positions:
        local_start = label_position + 1
        local_end = min(
            len(prepared_words),
            label_position + 12
        )

        indices, score = _best_sequence_match(
            target_full,
            prepared_words,
            local_start,
            local_end
        )

        if indices is not None and score > best_score:
            best_indices = indices
            best_score = score

        if score == 1.0:
            return _confidence_for_indices(
                prepared_words,
                indices
            )

    # 2. Search the whole OCR output.
    indices, score = _best_sequence_match(
        target_full,
        prepared_words
    )

    if indices is not None and score > best_score:
        best_indices = indices
        best_score = score

    if (
        best_indices is not None
        and best_score >= 0.80
    ):
        return _confidence_for_indices(
            prepared_words,
            best_indices
        )

    # 3. Token-level fallback.
    value_tokens = _tokenize_value(value)

    if not value_tokens:
        return []

    matched_confidences = []
    used_indices = set()

    for token in value_tokens:
        target = normalize_token(token)

        if not target:
            continue

        best_index = None
        best_ratio = 0.0

        # Exact normalized token match.
        for index, word in enumerate(
            prepared_words
        ):
            if index in used_indices:
                continue

            if word["normalized"] == target:
                best_index = index
                best_ratio = 1.0
                break

        # Fuzzy token match.
        if best_index is None:
            for index, word in enumerate(
                prepared_words
            ):
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

        if (
            best_index is not None
            and best_ratio >= 0.75
        ):
            matched_confidences.append(
                prepared_words[
                    best_index
                ]["confidence"]
            )
            used_indices.add(best_index)

    # For multi-token values, require all pieces to be matched.
    if (
        len(matched_confidences)
        < len(value_tokens)
    ):
        return []

    return matched_confidences


def calculate_ocr_confidence(
    field,
    value,
    ocr_words
):
    """
    Calculate real field-level Tesseract OCR confidence.

    Returns None if the value cannot be reliably matched.
    """
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    matched_confidences = _match_value_to_ocr_words(
        field,
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


def calculate_field_confidence(
    field,
    value,
    ocr_words=None
):
    """
    Return field confidence and review status.

    Normal GUI operation uses word-level Tesseract data.
    """
    if (
        value is None
        or not str(value).strip()
    ):
        return {
            "confidence": None,
            "status": "MANUAL REVIEW",
            "review": True,
            "confidence_available": False,
            "confidence_source": "none",
        }

    # Backward compatibility for older callers that pass a number.
    if isinstance(
        ocr_words,
        (int, float)
    ):
        confidence = max(
            0.0,
            min(
                float(ocr_words),
                100.0
            )
        )

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
            "confidence": round(confidence),
            "status": status,
            "review": review,
            "confidence_available": True,
            "confidence_source": "overall",
        }

    confidence = calculate_ocr_confidence(
        field,
        value,
        ocr_words
    )

    if confidence is None:
        return {
            "confidence": None,
            "status": "OCR CONF. N/A",
            "review": True,
            "confidence_available": False,
            "confidence_source": "unmatched",
        }

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
        "confidence_available": True,
        "confidence_source": "field_word_level",
    }


def analyze_fields(
    extracted_data,
    ocr_words=None
):
    """
    Analyze every extracted invoice field.
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
            ),
        }

    return results


def format_confidence_output(
    field_results
):
    """
    Optional text formatter for non-GUI use.
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

        confidence_text = (
            "N/A"
            if confidence is None
            else f"{confidence}%"
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
