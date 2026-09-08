import re
from datetime import datetime


# ============================================================
# FIELD VALIDATION ENGINE
# ============================================================

def validate_field(field, value):
    """
    Validate one extracted invoice field.

    Returns:
        {
            "valid": True/False,
            "reason": "..."
        }
    """

    if value is None:
        return {
            "valid": False,
            "reason": "Field is empty"
        }

    value = str(value).strip()

    if not value:
        return {
            "valid": False,
            "reason": "Field is empty"
        }

    # --------------------------------------------------------
    # GSTIN
    # --------------------------------------------------------

    if field == "GSTIN":

        if re.fullmatch(
            r"[0-9]{2}[A-Z0-9]{13}",
            value.upper()
        ):
            return {
                "valid": True,
                "reason": "Valid GSTIN format"
            }

        return {
            "valid": False,
            "reason": "Invalid GSTIN format"
        }

    # --------------------------------------------------------
    # INVOICE NUMBER
    # --------------------------------------------------------

    if field == "Invoice Number":

        if re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9./_-]*",
            value
        ):
            return {
                "valid": True,
                "reason": "Valid invoice number format"
            }

        return {
            "valid": False,
            "reason": "Invalid invoice number format"
        }

    # --------------------------------------------------------
    # INVOICE DATE
    # --------------------------------------------------------

    if field == "Invoice Date":

        date_formats = [
            "%d-%b-%y",
            "%d-%b-%Y",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%d-%m-%Y",
            "%d-%m-%y",
            "%Y-%m-%d",
        ]

        for fmt in date_formats:

            try:
                datetime.strptime(str(value).strip(), fmt)

                return {
                    "valid": True,
                    "reason": "Valid date"
                }

            except ValueError:
                continue

        return {
            "valid": False,
            "reason": "Invalid date format"
        }

    # --------------------------------------------------------
    # VEHICLE NUMBER
    # --------------------------------------------------------

    if field == "Vehicle Number":

        vehicle = value.upper().replace(" ", "")

        if re.fullmatch(
            r"[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}",
            vehicle
        ):
            return {
                "valid": True,
                "reason": "Valid vehicle number format"
            }

        return {
            "valid": False,
            "reason": "Invalid vehicle number format"
        }

    # --------------------------------------------------------
    # IFSC
    # --------------------------------------------------------

    if field == "IFSC":

        if re.fullmatch(
            r"[A-Z]{4}0[A-Z0-9]{6}",
            value.upper()
        ):
            return {
                "valid": True,
                "reason": "Valid IFSC format"
            }

        return {
            "valid": False,
            "reason": "Invalid IFSC format"
        }

    # --------------------------------------------------------
    # ACCOUNT NUMBER
    # --------------------------------------------------------

    if field == "Account Number":

        account = value.replace(" ", "")

        if re.fullmatch(r"[0-9]{6,20}", account):
            return {
                "valid": True,
                "reason": "Valid account number format"
            }

        return {
            "valid": False,
            "reason": "Invalid account number format"
        }

    # --------------------------------------------------------
    # TOTAL AMOUNT
    # --------------------------------------------------------

    if field == "Total Amount":

        amount = value.replace(",", "")
        amount = amount.replace("₹", "")
        amount = amount.strip()

        try:

            number = float(amount)

            if number >= 0:

                return {
                    "valid": True,
                    "reason": "Valid monetary value"
                }

        except ValueError:
            pass

        return {
            "valid": False,
            "reason": "Invalid monetary value"
        }

    # --------------------------------------------------------
    # COMPANY NAME
    # --------------------------------------------------------

    if field == "Company Name":

        if (
            len(value) >= 3
            and any(char.isalpha() for char in value)
        ):
            return {
                "valid": True,
                "reason": "Readable company name"
            }

        return {
            "valid": False,
            "reason": "Company name appears incomplete"
        }

    # --------------------------------------------------------
    # BANK
    # --------------------------------------------------------

    if field in ("Bank", "Bank Name"):

        if (
            len(value) >= 3
            and any(char.isalpha() for char in value)
        ):
            return {
                "valid": True,
                "reason": "Readable bank name"
            }

        return {
            "valid": False,
            "reason": "Bank name appears incomplete"
        }

    # --------------------------------------------------------
    # GENERIC TEXT FIELDS
    # --------------------------------------------------------

    if len(value) >= 2:

        return {
            "valid": True,
            "reason": "Readable extracted value"
        }

    return {
        "valid": False,
        "reason": "Value appears too short"
    }


# ============================================================
# VALIDATE ALL FIELDS
# ============================================================

def validate_invoice(invoice_data):
    """
    Validate all extracted invoice fields.

    Returns:
        {
            field_name: {
                value,
                valid,
                reason
            }
        }
    """

    results = {}

    if not isinstance(invoice_data, dict):
        return results

    for field, value in invoice_data.items():

        validation = validate_field(
            field,
            value
        )

        results[field] = {
            "value": value,
            "valid": validation["valid"],
            "reason": validation["reason"]
        }

    return results