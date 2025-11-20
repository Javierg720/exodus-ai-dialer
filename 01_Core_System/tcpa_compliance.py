#!/usr/bin/env python3
"""
TCPA Compliance Module

Ensures all outbound calls comply with TCPA regulations:
- Calls only between 8am-9pm in lead's local timezone
- Respect DNC list (handled by database)
- Answering machine detection (handled by Asterisk)
- Call frequency limits (handled by database)

Usage:
    from tcpa_compliance import TCPACompliance

    tcpa = TCPACompliance()
    if tcpa.can_call_now(phone_number):
        # Make the call
        pass
"""

import pytz
from datetime import datetime, time
from typing import Optional, Tuple
from loguru import logger


# US State timezone mapping (simplified)
STATE_TIMEZONES = {
    "AL": "America/Chicago", "AK": "America/Anchorage", "AZ": "America/Phoenix",
    "AR": "America/Chicago", "CA": "America/Los_Angeles", "CO": "America/Denver",
    "CT": "America/New_York", "DE": "America/New_York", "FL": "America/New_York",
    "GA": "America/New_York", "HI": "Pacific/Honolulu", "ID": "America/Denver",
    "IL": "America/Chicago", "IN": "America/New_York", "IA": "America/Chicago",
    "KS": "America/Chicago", "KY": "America/New_York", "LA": "America/Chicago",
    "ME": "America/New_York", "MD": "America/New_York", "MA": "America/New_York",
    "MI": "America/New_York", "MN": "America/Chicago", "MS": "America/Chicago",
    "MO": "America/Chicago", "MT": "America/Denver", "NE": "America/Chicago",
    "NV": "America/Los_Angeles", "NH": "America/New_York", "NJ": "America/New_York",
    "NM": "America/Denver", "NY": "America/New_York", "NC": "America/New_York",
    "ND": "America/Chicago", "OH": "America/New_York", "OK": "America/Chicago",
    "OR": "America/Los_Angeles", "PA": "America/New_York", "RI": "America/New_York",
    "SC": "America/New_York", "SD": "America/Chicago", "TN": "America/Chicago",
    "TX": "America/Chicago", "UT": "America/Denver", "VT": "America/New_York",
    "VA": "America/New_York", "WA": "America/Los_Angeles", "WV": "America/New_York",
    "WI": "America/Chicago", "WY": "America/Denver", "DC": "America/New_York"
}

# Area code to state mapping (top 100 area codes)
AREA_CODE_TO_STATE = {
    "205": "AL", "251": "AL", "256": "AL", "334": "AL",
    "907": "AK",
    "480": "AZ", "520": "AZ", "602": "AZ", "623": "AZ", "928": "AZ",
    "479": "AR", "501": "AR", "870": "AR",
    "209": "CA", "213": "CA", "310": "CA", "323": "CA", "408": "CA", "415": "CA",
    "424": "CA", "510": "CA", "530": "CA", "559": "CA", "562": "CA", "619": "CA",
    "626": "CA", "650": "CA", "657": "CA", "661": "CA", "707": "CA", "714": "CA",
    "760": "CA", "805": "CA", "818": "CA", "831": "CA", "858": "CA", "909": "CA",
    "916": "CA", "925": "CA", "949": "CA", "951": "CA",
    "303": "CO", "719": "CO", "720": "CO", "970": "CO",
    "203": "CT", "475": "CT", "860": "CT", "959": "CT",
    "302": "DE",
    "239": "FL", "305": "FL", "321": "FL", "352": "FL", "386": "FL", "407": "FL",
    "561": "FL", "727": "FL", "754": "FL", "772": "FL", "786": "FL", "813": "FL",
    "850": "FL", "863": "FL", "904": "FL", "941": "FL", "954": "FL",
    "229": "GA", "404": "GA", "470": "GA", "478": "GA", "678": "GA", "706": "GA",
    "762": "GA", "770": "GA", "912": "GA",
    "808": "HI",
    "208": "ID",
    "217": "IL", "224": "IL", "309": "IL", "312": "IL", "331": "IL", "618": "IL",
    "630": "IL", "708": "IL", "773": "IL", "815": "IL", "847": "IL", "872": "IL",
    "219": "IN", "260": "IN", "317": "IN", "574": "IN", "765": "IN", "812": "IN",
    "319": "IA", "515": "IA", "563": "IA", "641": "IA", "712": "IA",
    "316": "KS", "620": "KS", "785": "KS", "913": "KS",
    "270": "KY", "502": "KY", "606": "KY", "859": "KY",
    "225": "LA", "318": "LA", "337": "LA", "504": "LA", "985": "LA",
    "207": "ME",
    "240": "MD", "301": "MD", "410": "MD", "443": "MD", "667": "MD",
    "339": "MA", "351": "MA", "413": "MA", "508": "MA", "617": "MA", "774": "MA",
    "781": "MA", "857": "MA", "978": "MA",
    "231": "MI", "248": "MI", "269": "MI", "313": "MI", "517": "MI", "586": "MI",
    "616": "MI", "734": "MI", "810": "MI", "906": "MI", "947": "MI", "989": "MI",
    "218": "MN", "320": "MN", "507": "MN", "612": "MN", "651": "MN", "763": "MN",
    "952": "MN",
    "228": "MS", "601": "MS", "662": "MS", "769": "MS",
    "314": "MO", "417": "MO", "573": "MO", "636": "MO", "660": "MO", "816": "MO",
    "406": "MT",
    "308": "NE", "402": "NE", "531": "NE",
    "702": "NV", "725": "NV", "775": "NV",
    "603": "NH",
    "201": "NJ", "551": "NJ", "609": "NJ", "732": "NJ", "848": "NJ", "856": "NJ",
    "862": "NJ", "908": "NJ", "973": "NJ",
    "505": "NM", "575": "NM",
    "212": "NY", "315": "NY", "347": "NY", "516": "NY", "518": "NY", "585": "NY",
    "607": "NY", "631": "NY", "646": "NY", "716": "NY", "718": "NY", "845": "NY",
    "914": "NY", "917": "NY", "929": "NY",
    "252": "NC", "336": "NC", "704": "NC", "828": "NC", "910": "NC", "919": "NC",
    "980": "NC", "984": "NC",
    "701": "ND",
    "216": "OH", "220": "OH", "234": "OH", "330": "OH", "380": "OH", "419": "OH",
    "440": "OH", "513": "OH", "567": "OH", "614": "OH", "740": "OH", "937": "OH",
    "405": "OK", "539": "OK", "580": "OK", "918": "OK",
    "458": "OR", "503": "OR", "541": "OR", "971": "OR",
    "215": "PA", "267": "PA", "272": "PA", "412": "PA", "484": "PA", "570": "PA",
    "610": "PA", "717": "PA", "724": "PA", "814": "PA", "878": "PA",
    "401": "RI",
    "803": "SC", "843": "SC", "854": "SC", "864": "SC",
    "605": "SD",
    "423": "TN", "615": "TN", "731": "TN", "865": "TN", "901": "TN", "931": "TN",
    "210": "TX", "214": "TX", "254": "TX", "281": "TX", "325": "TX", "361": "TX",
    "409": "TX", "430": "TX", "432": "TX", "469": "TX", "512": "TX", "682": "TX",
    "713": "TX", "737": "TX", "806": "TX", "817": "TX", "830": "TX", "832": "TX",
    "903": "TX", "915": "TX", "936": "TX", "940": "TX", "956": "TX", "972": "TX",
    "979": "TX",
    "385": "UT", "435": "UT", "801": "UT",
    "802": "VT",
    "276": "VA", "434": "VA", "540": "VA", "571": "VA", "703": "VA", "757": "VA",
    "804": "VA",
    "206": "WA", "253": "WA", "360": "WA", "425": "WA", "509": "WA", "564": "WA",
    "304": "WV", "681": "WV",
    "262": "WI", "414": "WI", "534": "WI", "608": "WI", "715": "WI", "920": "WI",
    "307": "WY",
    "202": "DC"
}


class TCPACompliance:
    """TCPA compliance checker for outbound calls."""

    def __init__(
        self,
        calling_hours_start: time = time(8, 0),  # 8:00 AM
        calling_hours_end: time = time(21, 0),   # 9:00 PM
        default_timezone: str = "America/New_York"
    ):
        """Initialize TCPA compliance checker.

        Args:
            calling_hours_start: Start of allowed calling window (default 8am)
            calling_hours_end: End of allowed calling window (default 9pm)
            default_timezone: Fallback timezone if can't determine from phone
        """
        self.calling_hours_start = calling_hours_start
        self.calling_hours_end = calling_hours_end
        self.default_timezone = default_timezone

    def get_timezone_for_phone(self, phone_number: str) -> str:
        """Determine timezone for a phone number based on area code.

        Args:
            phone_number: Phone number (10 digits, can include +1 prefix)

        Returns:
            Timezone string (e.g., 'America/New_York')
        """
        # Clean phone number (remove +1, spaces, dashes)
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        if clean_phone.startswith('1'):
            clean_phone = clean_phone[1:]

        # Extract area code (first 3 digits)
        if len(clean_phone) < 10:
            logger.warning(f"Invalid phone number {phone_number}, using default timezone")
            return self.default_timezone

        area_code = clean_phone[:3]

        # Look up state from area code
        state = AREA_CODE_TO_STATE.get(area_code)
        if not state:
            logger.debug(f"Unknown area code {area_code}, using default timezone")
            return self.default_timezone

        # Look up timezone from state
        timezone = STATE_TIMEZONES.get(state, self.default_timezone)
        return timezone

    def get_local_time(self, phone_number: str) -> datetime:
        """Get current local time for a phone number's timezone.

        Args:
            phone_number: Phone number

        Returns:
            Current datetime in lead's local timezone
        """
        tz_string = self.get_timezone_for_phone(phone_number)
        tz = pytz.timezone(tz_string)
        return datetime.now(tz)

    def is_within_calling_hours(self, phone_number: str) -> bool:
        """Check if current time is within TCPA calling hours for this lead.

        Args:
            phone_number: Phone number to check

        Returns:
            True if within calling hours (8am-9pm local time)
        """
        local_time = self.get_local_time(phone_number)
        current_time = local_time.time()

        within_hours = self.calling_hours_start <= current_time <= self.calling_hours_end

        if not within_hours:
            logger.debug(
                f"Phone {phone_number} outside calling hours: {current_time.strftime('%I:%M %p')} "
                f"(allowed {self.calling_hours_start.strftime('%I:%M %p')} - "
                f"{self.calling_hours_end.strftime('%I:%M %p')})"
            )

        return within_hours

    def can_call_now(self, phone_number: str) -> Tuple[bool, Optional[str]]:
        """Check if we can call this number right now.

        Args:
            phone_number: Phone number to check

        Returns:
            Tuple of (can_call, reason_if_not)
        """
        # Check calling hours
        if not self.is_within_calling_hours(phone_number):
            local_time = self.get_local_time(phone_number)
            reason = f"Outside calling hours ({local_time.strftime('%I:%M %p')} local time)"
            return False, reason

        return True, None

    def get_next_allowed_call_time(self, phone_number: str) -> datetime:
        """Get the next time we can call this number.

        Args:
            phone_number: Phone number

        Returns:
            Next allowed call time in UTC
        """
        local_time = self.get_local_time(phone_number)
        tz = local_time.tzinfo

        # If currently within calling hours, can call now
        if self.calling_hours_start <= local_time.time() <= self.calling_hours_end:
            return datetime.now(pytz.UTC)

        # If before calling hours today, return start time today
        if local_time.time() < self.calling_hours_start:
            next_call = local_time.replace(
                hour=self.calling_hours_start.hour,
                minute=self.calling_hours_start.minute,
                second=0,
                microsecond=0
            )
            return next_call.astimezone(pytz.UTC)

        # If after calling hours, return start time tomorrow
        from datetime import timedelta
        next_call = (local_time + timedelta(days=1)).replace(
            hour=self.calling_hours_start.hour,
            minute=self.calling_hours_start.minute,
            second=0,
            microsecond=0
        )
        return next_call.astimezone(pytz.UTC)


# Example usage
if __name__ == "__main__":
    tcpa = TCPACompliance()

    # Test various phone numbers
    test_numbers = [
        "5551234567",  # New York (Eastern)
        "3105551234",  # Los Angeles (Pacific)
        "7735551234",  # Chicago (Central)
        "3035551234",  # Denver (Mountain)
    ]

    print("TCPA Compliance Check")
    print("=" * 60)

    for phone in test_numbers:
        tz = tcpa.get_timezone_for_phone(phone)
        local_time = tcpa.get_local_time(phone)
        can_call, reason = tcpa.can_call_now(phone)

        print(f"\nPhone: {phone}")
        print(f"  Timezone: {tz}")
        print(f"  Local Time: {local_time.strftime('%I:%M %p %Z')}")
        print(f"  Can Call: {'✅ Yes' if can_call else '❌ No'}")
        if reason:
            print(f"  Reason: {reason}")

        if not can_call:
            next_time = tcpa.get_next_allowed_call_time(phone)
            print(f"  Next Available: {next_time.strftime('%Y-%m-%d %I:%M %p %Z')}")
