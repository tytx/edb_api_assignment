"""
Input sanitization utilities for XSS protection using industry-standard libraries
"""
import re
import bleach
import phonenumbers
from phonenumbers import NumberParseException


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Sanitize string input to prevent XSS attacks using bleach library
    - Strips leading/trailing whitespace
    - Removes all HTML tags and attributes
    - Enforces maximum length
    - Removes control characters
    """
    if not value:
        return value

    # Strip whitespace
    value = value.strip()

    # Enforce max length
    if len(value) > max_length:
        value = value[:max_length]

    # Remove control characters
    value = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', value)

    # Collapse multiple spaces into one
    value = re.sub(r'\s+', ' ', value)

    # Use bleach to clean any HTML/script tags (removes all tags by default)
    value = bleach.clean(value, tags=[], attributes={}, strip=True)

    return value


def sanitize_name(name: str) -> str:
    """
    Sanitize name fields (firstName, lastName)
    - Max 100 characters
    - Uses bleach for XSS protection
    - Only allows letters, spaces, hyphens, apostrophes, and periods
    """
    if not name:
        return name

    # Basic sanitization with bleach
    name = sanitize_string(name, max_length=100)

    # Remove characters that aren't typical in names
    # Allow: letters (any language), spaces, hyphens, apostrophes, periods
    name = re.sub(r"[^\w\s\-'.]", '', name, flags=re.UNICODE)

    return name.strip()


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number using Google's libphonenumber
    - Supports international formats
    - Defaults to Singapore (SG) region
    - SG mobile: 8/9 digits starting with 8 or 9 (e.g., 81234567, 91234567)
    - SG landline: 8 digits (e.g., 62345678)
    """
    if not phone:
        return True  # Optional field

    try:
        # Try to parse with Singapore as default region
        parsed = phonenumbers.parse(phone, "SG")
        return phonenumbers.is_valid_number(parsed)
    except NumberParseException:
        # If SG parsing fails, try international format
        try:
            parsed = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(parsed)
        except NumberParseException:
            return False


def sanitize_phone_number(phone: str) -> str:
    """
    Sanitize and normalize phone number to E164 format using libphonenumber
    - Defaults to Singapore region
    - Returns standardized international format: +6581234567 (SG), +1234567890 (others)
    """
    if not phone:
        return phone

    try:
        # Try parsing with Singapore as default region
        parsed = phonenumbers.parse(phone, "SG")
        if phonenumbers.is_valid_number(parsed):
            # Return in E164 format (+6581234567 for Singapore)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except NumberParseException:
        # Try international format if SG parsing fails
        try:
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            pass

    # If all parsing fails, return cleaned version (digits + optional leading +)
    if phone.startswith('+'):
        return '+' + re.sub(r'\D', '', phone)
    return re.sub(r'\D', '', phone)
