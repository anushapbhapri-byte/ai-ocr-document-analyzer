import os
import re
import csv
import cv2
import pytesseract


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_DIR = os.path.join(
    BASE_DIR,
    "data",
    "benchmark",
    "images"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data",
    "benchmark",
    "ground_truth.csv"
)


# ============================================================
# OCR
# ============================================================

def extract_ocr_text(image_path):
    """
    Run OCR on a CLEAN invoice image.

    Ground truth must always be generated from clean images,
    never from noisy images.
    """

    image = cv2.imread(image_path)

    if image is None:
        return ""

    text = pytesseract.image_to_string(
        image,
        config="--oem 3 --psm 6"
    )

    return text


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """Normalize OCR text without removing useful characters."""

    if not text:
        return ""

    text = text.replace("\r", "\n")

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# INVOICE NUMBER
# ============================================================

def extract_invoice_number(text):
    """Extract the invoice number."""

    patterns = [
        r"Invoice\s*(?:no|number|#)\s*[:.]?\s*([A-Za-z0-9./_-]+)",
        r"Invoice\s*[:.]?\s*([A-Za-z0-9./_-]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return ""


# ============================================================
# INVOICE DATE
# ============================================================

def extract_invoice_date(text):
    """Extract the invoice/date-of-issue value."""

    patterns = [

        r"Date\s+of\s+issue\s*:\s*"
        r"([0-9]{1,4}[/-][0-9]{1,2}[/-][0-9]{2,4})",

        r"Invoice\s+Date\s*:\s*"
        r"([0-9]{1,4}[/-][A-Za-z0-9]{1,9}[/-][0-9]{2,4})",

        r"Invoice\s+Date\s*:\s*"
        r"([0-9]{1,4}[/-][0-9]{1,2}[/-][0-9]{2,4})",

        r"Date\s*:\s*"
        r"([0-9]{1,4}[/-][0-9]{1,2}[/-][0-9]{2,4})"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1).strip()

    return ""


# ============================================================
# TAX ID EXTRACTION
# ============================================================

def extract_tax_ids(text):
    """
    Extract Seller Tax ID and Client Tax ID.

    For this benchmark dataset, the first Tax ID detected
    belongs to the Seller and the second Tax ID belongs to
    the Client.

    This function never copies one Tax ID into the other field.
    """

    if not text:
        return "", ""

    text = text.replace("\r", "\n")

    # Tax IDs in this invoice dataset follow:
    # 945-82-2137
    # 942-80-0517
    tax_pattern = (
        r"\bTax\s*Id\s*[:.]?\s*"
        r"([A-Za-z0-9]{2,5}"
        r"(?:-[A-Za-z0-9]{1,5})?"
        r"(?:-[A-Za-z0-9]{1,8})?)"
    )

    matches = re.findall(
        tax_pattern,
        text,
        re.IGNORECASE
    )

    # Remove duplicates while preserving OCR order
    tax_ids = []

    for value in matches:
        value = value.strip()

        if value and value not in tax_ids:
            tax_ids.append(value)

    seller_tax_id = ""
    client_tax_id = ""

    if len(tax_ids) >= 1:
        seller_tax_id = tax_ids[0]

    if len(tax_ids) >= 2:
        client_tax_id = tax_ids[1]

    return seller_tax_id, client_tax_id

    # --------------------------------------------------------
    # Tax ID pattern
    # --------------------------------------------------------

    tax_pattern = (
        r"Tax\s*Id\s*[:.]?\s*"
        r"([A-Za-z0-9]{2,5}"
        r"(?:-[A-Za-z0-9]{2,5})?"
        r"(?:-[A-Za-z0-9]{2,8})?)"
    )

    # --------------------------------------------------------
    # Find Seller and Client headings
    # --------------------------------------------------------

    seller_match = re.search(
        r"\bSeller\s*:",
        text,
        re.IGNORECASE
    )

    client_match = re.search(
        r"\bClient\s*:",
        text,
        re.IGNORECASE
    )

    # ========================================================
    # BOTH HEADINGS FOUND
    # ========================================================

    if seller_match and client_match:

        seller_start = seller_match.end()
        client_start = client_match.end()

        # ----------------------------------------------------
        # Normal invoice order:
        #
        # Seller
        # ...
        # Client
        # ...
        # ----------------------------------------------------

        if seller_start < client_match.start():

            seller_section = text[
                seller_start:
                client_match.start()
            ]

            client_section = text[
                client_start:
            ]

            seller_tax_match = re.search(
                tax_pattern,
                seller_section,
                re.IGNORECASE | re.DOTALL
            )

            client_tax_match = re.search(
                tax_pattern,
                client_section,
                re.IGNORECASE | re.DOTALL
            )

            if seller_tax_match:

                seller_tax_id = (
                    seller_tax_match
                    .group(1)
                    .strip()
                )

            if client_tax_match:

                client_tax_id = (
                    client_tax_match
                    .group(1)
                    .strip()
                )

    # ========================================================
    # ONLY SELLER FOUND
    # ========================================================

    elif seller_match:

        seller_section = text[
            seller_match.end():
        ]

        seller_tax_match = re.search(
            tax_pattern,
            seller_section,
            re.IGNORECASE | re.DOTALL
        )

        if seller_tax_match:

            seller_tax_id = (
                seller_tax_match
                .group(1)
                .strip()
            )

    # ========================================================
    # ONLY CLIENT FOUND
    # ========================================================

    elif client_match:

        client_section = text[
            client_match.end():
        ]

        client_tax_match = re.search(
            tax_pattern,
            client_section,
            re.IGNORECASE | re.DOTALL
        )

        if client_tax_match:

            client_tax_id = (
                client_tax_match
                .group(1)
                .strip()
            )

    # ========================================================
    # NO FALLBACK THAT COPIES VALUES
    # ========================================================

    return seller_tax_id, client_tax_id


# ============================================================
# SELLER IBAN
# ============================================================

def extract_seller_iban(text):
    """
    Extract IBAN specifically associated with the Seller.

    Example:

        Seller:
        ...
        Tax Id: 945-82-2137
        IBAN: GB75MCRL06841367619257
    """

    if not text:
        return ""

    # --------------------------------------------------------
    # First isolate Seller section
    # --------------------------------------------------------

    seller_match = re.search(
        r"\bSeller\s*:(.*?)(?=\bClient\s*:|\Z)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    seller_section = ""

    if seller_match:

        seller_section = seller_match.group(1)

    # --------------------------------------------------------
    # Search explicitly after IBAN label
    # --------------------------------------------------------

    iban_pattern = (
        r"\bIBAN\s*[:.]?\s*"
        r"([A-Z]{2}[A-Z0-9]{13,32})"
    )

    match = re.search(
        iban_pattern,
        seller_section,
        re.IGNORECASE
    )

    if match:

        return (
            match.group(1)
            .replace(" ", "")
            .upper()
        )

    # --------------------------------------------------------
    # Fallback: explicit IBAN anywhere in document
    # --------------------------------------------------------

    match = re.search(
        iban_pattern,
        text,
        re.IGNORECASE
    )

    if match:

        return (
            match.group(1)
            .replace(" ", "")
            .upper()
        )

    return ""


# ============================================================
# AMOUNT NORMALIZATION
# ============================================================

def normalize_amount(value):
    """
    Normalize OCR monetary values.

    Examples:

        5 640,17     -> 5640.17
        5640.17      -> 5640.17
        1,16,800.00  -> 116800.00
    """

    if not value:
        return ""

    value = value.strip()

    # Remove currency symbols
    value = re.sub(
        r"[₹$€£]",
        "",
        value
    )

    # Remove spaces
    value = value.replace(" ", "")

    # European decimal format
    if re.fullmatch(
        r"\d+[.,]\d{2}",
        value
    ):

        if "," in value:

            value = value.replace(
                ",",
                "."
            )

    # Both comma and period
    elif "," in value and "." in value:

        value = value.replace(
            ",",
            ""
        )

    # Multiple commas
    elif value.count(",") > 1:

        parts = value.split(",")

        if len(parts[-1]) == 2:

            value = (
                "".join(parts[:-1])
                + "."
                + parts[-1]
            )

        else:

            value = "".join(parts)

    try:

        number = float(value)

        return f"{number:.2f}"

    except ValueError:

        return ""


# ============================================================
# SUMMARY EXTRACTION
# ============================================================

def extract_summary_values(text):
    """
    Extract:

        Net Worth
        VAT
        Gross Worth

    from the SUMMARY section.
    """

    net_worth = ""
    vat = ""
    gross_worth = ""

    # --------------------------------------------------------
    # Find SUMMARY
    # --------------------------------------------------------

    summary_match = re.search(
        r"\bSUMMARY\b(.*?)(?:\Z)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if summary_match:

        summary = summary_match.group(1)

    else:

        summary = text

    # --------------------------------------------------------
    # Money pattern
    # --------------------------------------------------------

    amount_pattern = (
        r"(?:[$€£₹]?\s*)?"
        r"\d[\d\s,.]*\d"
        r"(?:[.,]\d{1,2})?"
    )

    raw_amounts = re.findall(
        amount_pattern,
        summary
    )

    amounts = []

    for raw in raw_amounts:

        normalized = normalize_amount(raw)

        if normalized:

            amounts.append(normalized)

    # --------------------------------------------------------
    # Remove duplicate values while preserving order
    # --------------------------------------------------------

    unique_amounts = []

    for amount in amounts:

        if amount not in unique_amounts:

            unique_amounts.append(amount)

    # --------------------------------------------------------
    # Typical summary:
    #
    # Net Worth | VAT | Gross Worth
    #
    # If the total row repeats them, the last three
    # unique values represent the summary.
    # --------------------------------------------------------

    if len(unique_amounts) >= 3:

        net_worth = unique_amounts[-3]
        vat = unique_amounts[-2]
        gross_worth = unique_amounts[-1]

    return (
        net_worth,
        vat,
        gross_worth
    )


# ============================================================
# PROCESS ONE INVOICE
# ============================================================

def process_invoice(image_path):

    text = extract_ocr_text(
        image_path
    )

    text = clean_text(
        text
    )

    invoice_number = extract_invoice_number(
        text
    )

    invoice_date = extract_invoice_date(
        text
    )

    seller_tax_id, client_tax_id = extract_tax_ids(
        text
    )

    seller_iban = extract_seller_iban(
        text
    )

    net_worth, vat, gross_worth = extract_summary_values(
        text
    )

    return {

        "image": os.path.basename(
            image_path
        ),

        "Invoice Number": invoice_number,

        "Invoice Date": invoice_date,

        "Seller Tax ID": seller_tax_id,

        "Client Tax ID": client_tax_id,

        "Seller IBAN": seller_iban,

        "Net Worth": net_worth,

        "VAT": vat,

        "Gross Worth": gross_worth
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 65)
    print("GROUND-TRUTH DATASET PREPARATION")
    print("=" * 65)

    # --------------------------------------------------------
    # Check image directory
    # --------------------------------------------------------

    if not os.path.exists(IMAGE_DIR):

        print()
        print("ERROR: Clean invoice image folder not found:")
        print(IMAGE_DIR)
        print()

        return

    # --------------------------------------------------------
    # Get clean invoice images
    # --------------------------------------------------------

    image_files = sorted(
        [
            file
            for file in os.listdir(
                IMAGE_DIR
            )
            if file.lower().endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png"
                )
            )
        ]
    )

    if not image_files:

        print()
        print("ERROR: No invoice images found.")
        print()

        return

    print()
    print(
        f"Found {len(image_files)} "
        "clean invoice images."
    )

    print()
    print(
        "Creating OCR-assisted "
        "benchmark draft..."
    )

    print()

    rows = []

    # --------------------------------------------------------
    # Process every invoice
    # --------------------------------------------------------

    for index, filename in enumerate(
        image_files,
        start=1
    ):

        print(
            f"[{index}/{len(image_files)}] "
            f"Reading {filename}"
        )

        image_path = os.path.join(
            IMAGE_DIR,
            filename
        )

        result = process_invoice(
            image_path
        )

        rows.append(
            result
        )

    # --------------------------------------------------------
    # CSV columns
    # --------------------------------------------------------

    fieldnames = [

        "image",

        "Invoice Number",

        "Invoice Date",

        "Seller Tax ID",

        "Client Tax ID",

        "Seller IBAN",

        "Net Worth",

        "VAT",

        "Gross Worth"
    ]

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(
            OUTPUT_FILE
        ),
        exist_ok=True
    )

    # --------------------------------------------------------
    # Write CSV
    # --------------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    # ========================================================
    # REPORT
    # ========================================================

    print()
    print("=" * 65)
    print("DRAFT CREATED")
    print("=" * 65)

    print()
    print("File:")
    print(OUTPUT_FILE)

    # --------------------------------------------------------
    # Count missing values
    # --------------------------------------------------------

    missing_counts = {

        field: 0

        for field in fieldnames

        if field != "image"
    }

    for row in rows:

        for field in missing_counts:

            value = str(
                row.get(
                    field,
                    ""
                )
            ).strip()

            if not value:

                missing_counts[field] += 1

    print()
    print("Missing values detected:")
    print()

    for field, count in missing_counts.items():

        print(
            f"{field:<20}: {count}"
        )

    # --------------------------------------------------------
    # Show first few rows for quick verification
    # --------------------------------------------------------

    print()
    print("QUICK CHECK — FIRST 5 INVOICES")
    print("-" * 65)

    for row in rows[:5]:

        print()
        print(
            row["image"]
        )

        print(
            "  Invoice Number :",
            row["Invoice Number"]
        )

        print(
            "  Invoice Date   :",
            row["Invoice Date"]
        )

        print(
            "  Seller Tax ID  :",
            row["Seller Tax ID"]
        )

        print(
            "  Client Tax ID  :",
            row["Client Tax ID"]
        )

        print(
            "  Seller IBAN    :",
            row["Seller IBAN"]
        )

        print(
            "  Net Worth      :",
            row["Net Worth"]
        )

        print(
            "  VAT            :",
            row["VAT"]
        )

        print(
            "  Gross Worth    :",
            row["Gross Worth"]
        )

    print()
    print("=" * 65)
    print("IMPORTANT")
    print("=" * 65)

    print()
    print(
        "This CSV is an OCR-assisted DRAFT."
    )

    print(
        "Verify the values against the CLEAN "
        "invoice images before benchmarking."
    )

    print()
    print(
        "Do NOT use noisy images as ground truth."
    )

    print()
    print(
        "Once verified, this CSV becomes the "
        "benchmark reference dataset."
    )

    print("=" * 65)


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    main()  