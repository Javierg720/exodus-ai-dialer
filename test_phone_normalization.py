#!/usr/bin/env python3
"""Test phone normalization logic."""


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number to E.164 format (+1XXXXXXXXXX for US).

    Rules:
    - Strip all non-digits
    - 10 digits: Add +1 prefix (US number without country code)
    - 11 digits starting with 1: Add + prefix only
    - 11 digits NOT starting with 1: Add +1 prefix
    - Other lengths: Add + prefix (international or invalid)
    """
    # Remove all non-digits
    digits = "".join(c for c in phone if c.isdigit())

    # Apply normalization rules
    if len(digits) == 10:
        # 10 digits - US number without country code
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith("1"):
        # 11 digits starting with 1 - already has country code
        return f"+{digits}"
    elif len(digits) == 11 and not digits.startswith("1"):
        # 11 digits NOT starting with 1 - add +1
        return f"+1{digits}"
    else:
        # International or other - just add +
        return f"+{digits}"


# Test cases
test_cases = [
    ("555-123-4567", "+15551234567"),  # 10 digits with dashes
    ("5551234567", "+15551234567"),  # 10 digits plain
    ("15551234567", "+15551234567"),  # 11 digits with 1
    ("+15551234567", "+15551234567"),  # Already formatted
    ("1-555-123-4567", "+15551234567"),  # 11 digits with 1 and dashes
    ("+1 (555) 123-4567", "+15551234567"),  # Formatted with +1
    ("(555) 123-4567", "+15551234567"),  # Formatted 10 digits
]

print("Phone Normalization Test Results")
print("=" * 70)
print(f"{'Input':<25} {'Expected':<20} {'Got':<20} {'Status'}")
print("-" * 70)

all_passed = True
for input_phone, expected in test_cases:
    result = normalize_phone(input_phone)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    if result != expected:
        all_passed = False
    print(f"{input_phone:<25} {expected:<20} {result:<20} {status}")

print("=" * 70)
if all_passed:
    print("✅ All tests passed!")
else:
    print("❌ Some tests failed!")

print("\nNow testing the NEW frontend logic (TypeScript equivalent):")
print("-" * 70)


def frontend_normalize(phone: str) -> str:
    """Frontend normalization logic (TypeScript equivalent)."""
    # Remove all non-digits
    digits = "".join(c for c in phone if c.isdigit())

    # US numbers only (10 or 11 digits)
    if len(digits) == 10:
        return f"+1{digits}"  # Add +1 to 10-digit number
    elif len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"  # Already has 1, just add +
    elif len(digits) == 11 and not digits.startswith("1"):
        return f"+1{digits}"  # Add +1 to 11-digit non-1 number
    else:
        return f"+{digits}"  # International or invalid - just add +


print(f"{'Input':<25} {'Expected':<20} {'Got':<20} {'Status'}")
print("-" * 70)

all_passed_frontend = True
for input_phone, expected in test_cases:
    result = frontend_normalize(input_phone)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    if result != expected:
        all_passed_frontend = False
    print(f"{input_phone:<25} {expected:<20} {result:<20} {status}")

print("=" * 70)
if all_passed_frontend:
    print("✅ All frontend tests passed!")
else:
    print("❌ Some frontend tests failed!")
