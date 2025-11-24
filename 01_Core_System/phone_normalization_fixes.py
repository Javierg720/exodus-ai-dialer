#!/usr/bin/env python3
"""
Phone Normalization Utility - Standalone module

This can be imported by dialer_db_async.py and other modules.
Fixes the +111111111111 issue by properly validating phone numbers.
"""

import re
from typing import Optional
from loguru import logger


def sanitize_phone_number(phone: str) -> Optional[str]:
    """Sanitize and validate phone number.

    Rules:
    - Remove all non-digits
    - Must be 10-15 digits (international range)
    - Don't add country code if already present
    - Add +1 prefix only for 10-digit US numbers
    - Reject invalid patterns (all same digits, etc.)

    Args:
        phone: Raw phone number string

    Returns:
        Sanitized phone in E.164 format (+1XXXXXXXXXX) or None if invalid

    Examples:
        >>> sanitize_phone_number("555-123-4567")
        '+15551234567'
        >>> sanitize_phone_number("(555) 123-4567")
        '+15551234567'
        >>> sanitize_phone_number("+1 555 123 4567")
        '+15551234567'
        >>> sanitize_phone_number("15551234567")
        '+15551234567'
        >>> sanitize_phone_number("+15551234567")
        '+15551234567'
        >>> sanitize_phone_number("111111111111")
        None
        >>> sanitize_phone_number("+111111111111")
        None
    """
    if not phone:
        return None

    # Remove all non-digits
    digits_only = re.sub(r"\D", "", phone)

    # Validate length (10-15 digits for international compatibility)
    if len(digits_only) < 10 or len(digits_only) > 15:
        logger.warning(f"Invalid phone length: {len(digits_only)} digits ({phone})")
        return None

    # Handle US/Canada numbers (10 or 11 digits)
    if len(digits_only) == 10:
        # 10 digits - add +1 prefix
        result = f"+1{digits_only}"
    elif len(digits_only) == 11 and digits_only.startswith("1"):
        # 11 digits starting with 1 - add + prefix
        result = f"+{digits_only}"
    elif digits_only.startswith("1") and len(digits_only) > 11:
        # Already has country code 1, but too long - invalid
        logger.warning(f"Invalid US/Canada number: too long ({phone})")
        return None
    else:
        # International number or already formatted - add + if missing
        result = f"+{digits_only}" if not phone.startswith("+") else phone

    # Reject obviously invalid patterns (like +111111111111)
    # Check if the number after country code has too many repeated digits
    number_part = result.replace("+1", "", 1)  # Remove country code
    if len(set(number_part)) <= 2:  # Only 1-2 unique digits (like 1111111111)
        logger.warning(f"Invalid phone pattern: too many repeated digits ({phone})")
        return None

    # Additional validation: Check for sequential patterns (1234567890)
    if number_part in ["1234567890", "0123456789", "9876543210"]:
        logger.warning(f"Invalid phone pattern: sequential digits ({phone})")
        return None

    return result


# Test examples
if __name__ == "__main__":
    test_cases = [
        ("555-123-4567", "+15551234567"),
        ("(555) 123-4567", "+15551234567"),
        ("+1 555 123 4567", "+15551234567"),
        ("15551234567", "+15551234567"),
        ("+15551234567", "+15551234567"),
        ("5551234567", "+15551234567"),
        ("111111111111", None),
        ("+111111111111", None),
        ("1111111111", None),
        ("12345", None),
        ("", None),
    ]

    print("Phone Normalization Tests:")
    print("=" * 60)
    for input_phone, expected in test_cases:
        result = sanitize_phone_number(input_phone)
        status = "✅" if result == expected else "❌"
        result_str = str(result) if result else "None"
        expected_str = str(expected) if expected else "None"
        print(
            f"{status} Input: {input_phone:20} → {result_str:20} (expected: {expected_str})"
        )
