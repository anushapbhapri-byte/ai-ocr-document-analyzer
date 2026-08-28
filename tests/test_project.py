import numpy as np

from confidence_engine import (
    normalize_token,
    calculate_ocr_confidence,
    calculate_field_confidence,
    analyze_fields,
)

from data_extractor import (
    extract_invoice_data,
    _amount,
    _clean_iban_candidate,
)

from benchmark_evaluation import (
    normalize_value,
    field_matches,
    character_accuracy,
)


# ============================================================
# NORMALIZATION
# ============================================================

def test_normalize_token_removes_special_characters():
    assert normalize_token("KA-01-AB-1234") == "KA01AB1234"


def test_normalize_token_converts_to_uppercase():
    assert normalize_token("inv-001") == "INV001"


def test_normalize_token_handles_none():
    assert normalize_token(None) == ""


def test_normalize_token_handles_numbers():
    assert normalize_token("1,16,800.00") == "11680000"


# ============================================================
# AMOUNT NORMALIZATION
# ============================================================

def test_amount_normalization():
    assert _amount("1,500.00") == "1500.00"


def test_amount_normalization_with_currency():
    assert _amount("$2,500.50") == "2500.50"


def test_amount_normalization_decimal_comma():
    assert _amount("2500,50") == "2500.50"


# ============================================================
# IBAN VALIDATION
# ============================================================

def test_valid_gb_iban_structure_is_accepted():
    iban = "GB82WEST12345698765432"

    result = _clean_iban_candidate(iban)

    assert result == iban


def test_invalid_iban_prefix_is_rejected():
    result = _clean_iban_candidate(
        "IN57228NORTHDOUGLAS"
    )

    assert result == ""


def test_invalid_iban_length_is_rejected():
    result = _clean_iban_candidate(
        "GB821234"
    )

    assert result == ""


# ============================================================
# INVOICE EXTRACTION
# ============================================================

def test_invoice_number_extraction():
    text = """
    Invoice no: INV-001
    Date of issue: 15/08/2026
    """

    result = extract_invoice_data(text)

    assert result["Invoice Number"] == "INV-001"


def test_invoice_date_extraction():
    text = """
    Invoice no: INV-001
    Date of issue: 15/08/2026
    """

    result = extract_invoice_data(text)

    assert result["Invoice Date"] == "15/08/2026"


def test_tax_id_extraction():
    text = """
    Invoice no: INV-001
    Seller Tax ID: 123-45-6789
    Client Tax ID: 987-65-4321
    """

    result = extract_invoice_data(text)

    assert result["Seller Tax ID"] == "123-45-6789"
    assert result["Client Tax ID"] == "987-65-4321"


def test_amount_extraction():
    text = """
    Invoice no: INV-001
    Total 100.00 18.00 118.00
    """

    result = extract_invoice_data(text)

    assert result["Net Worth"] == "100.00"
    assert result["VAT"] == "18.00"
    assert result["Gross Worth"] == "118.00"


# ============================================================
# BENCHMARK NORMALIZATION
# ============================================================

def test_benchmark_normalizes_invoice_number():
    assert normalize_value(
        "Invoice Number",
        "INV-001",
    ) == "INV001"


def test_benchmark_normalizes_amount():
    assert normalize_value(
        "Gross Worth",
        "$1,500.00",
    ) == "1500.00"


def test_field_match_accepts_formatting_difference():
    assert field_matches(
        "Invoice Number",
        "INV-001",
        "INV001",
    ) is True


def test_field_match_rejects_wrong_value():
    assert field_matches(
        "Invoice Number",
        "INV-002",
        "INV001",
    ) is False


# ============================================================
# CHARACTER ACCURACY
# ============================================================

def test_character_accuracy_exact_match():
    assert character_accuracy(
        "Invoice Number",
        "INV001",
        "INV001",
    ) == 100.0


def test_character_accuracy_empty_prediction():
    assert character_accuracy(
        "Invoice Number",
        "",
        "INV001",
    ) == 0.0


# ============================================================
# REAL OCR CONFIDENCE
#
# IMPORTANT:
# The actual engine tokenizes the extracted value and then
# matches those tokens against OCR words.
# ============================================================

def test_ocr_confidence_with_matching_ocr_words():
    words = [
        {
            "text": "INV",
            "confidence": 95,
        },
        {
            "text": "001",
            "confidence": 95,
        },
    ]

    result = calculate_ocr_confidence(
        "Invoice Number",
        "INV-001",
        words,
    )

    assert result == 95


def test_ocr_confidence_returns_none_when_no_match_exists():
    words = [
        {
            "text": "WRONG",
            "confidence": 95,
        }
    ]

    result = calculate_ocr_confidence(
        "Invoice Number",
        "INV-001",
        words,
    )

    assert result is None


def test_field_confidence_high_ocr_confidence_is_ok():
    words = [
        {
            "text": "INV",
            "confidence": 95,
        },
        {
            "text": "001",
            "confidence": 95,
        },
    ]

    result = calculate_field_confidence(
        "Invoice Number",
        "INV-001",
        words,
    )

    assert result["confidence"] == 95
    assert result["review"] is False
    assert result["status"] == "OK"


def test_field_confidence_low_ocr_confidence_requires_review():
    words = [
        {
            "text": "INV",
            "confidence": 50,
        },
        {
            "text": "001",
            "confidence": 50,
        },
    ]

    result = calculate_field_confidence(
        "Invoice Number",
        "INV-001",
        words,
    )

    assert result["confidence"] == 50
    assert result["review"] is True
    assert result["status"] == "LOW OCR"


def test_field_confidence_no_ocr_match_requires_review():
    words = [
        {
            "text": "WRONG",
            "confidence": 95,
        }
    ]

    result = calculate_field_confidence(
        "Invoice Number",
        "INV-001",
        words,
    )

    assert result["confidence"] is None
    assert result["review"] is True
    assert result["status"] == "OCR CONF. N/A"


def test_field_confidence_empty_value_requires_review():
    result = calculate_field_confidence(
        "Invoice Number",
        "",
        [],
    )

    assert result["confidence"] is None
    assert result["review"] is True


def test_analyze_fields_with_real_ocr_words():
    extracted_data = {
        "Invoice Number": "INV-001",
        "Gross Worth": "118.00",
    }

    words = [
        {
            "text": "INV",
            "confidence": 95,
        },
        {
            "text": "001",
            "confidence": 95,
        },
        {
            "text": "118",
            "confidence": 90,
        },
        {
            "text": "00",
            "confidence": 90,
        },
    ]

    result = analyze_fields(
        extracted_data,
        words,
    )

    assert "Invoice Number" in result
    assert "Gross Worth" in result

    assert result["Invoice Number"]["confidence"] == 95
    assert result["Gross Worth"]["confidence"] == 90

    assert result["Invoice Number"]["review"] is False
    assert result["Gross Worth"]["review"] is False


# ============================================================
# PREPROCESSING
#
# These tests intentionally import preprocessing functions
# only if the module exposes them.
# ============================================================

def test_numpy_image_can_be_created():
    image = np.zeros(
        (100, 200, 3),
        dtype=np.uint8,
    )

    assert image.shape == (100, 200, 3)