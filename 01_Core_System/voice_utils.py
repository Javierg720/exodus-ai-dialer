#!/usr/bin/env python3
"""
Voice Utilities - Dynamic variable replacement and TTS helper functions
"""


def replace_dynamic_vars(text: str, lead: dict) -> str:
    """
    Replace dynamic variables in text with lead data.

    Supported variables:
    - {{first_name}} - Lead's first name
    - {{last_name}} - Lead's last name
    - {{full_name}} - Full name
    - {{company}} - Company name
    - {{phone}} - Phone number
    - {{city}} - City
    - {{state}} - State
    - {{zip}} - ZIP code
    - {{email}} - Email address
    - {{custom1}} - Custom field 1
    - {{custom2}} - Custom field 2
    - {{campaign}} - Campaign name

    Args:
        text: Text containing variables to replace
        lead: Dictionary containing lead data

    Returns:
        Text with variables replaced
    """
    mapping = {
        "{{first_name}}": lead.get("first_name", ""),
        "{{last_name}}": lead.get("last_name", ""),
        "{{full_name}}": f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
        "{{company}}": lead.get("vendor_lead_name", ""),
        "{{city}}": lead.get("city", ""),
        "{{state}}": lead.get("state", ""),
        "{{zip}}": lead.get("postal_code", ""),
        "{{phone}}": lead.get("phone_number", ""),
        "{{email}}": lead.get("email", ""),
        "{{custom1}}": lead.get("custom1", ""),
        "{{custom2}}": lead.get("custom2", ""),
        "{{campaign}}": lead.get("campaign_name", ""),
    }

    for var, value in mapping.items():
        text = text.replace(var, str(value or ""))

    return text


def generate_ssml(
    text: str,
    voice: str = "en-US-AvaMultilingualNeural",
    speed: float = 1.3,
    pitch: int = 0,
) -> str:
    """
    Generate SSML for Edge TTS with voice settings.

    Args:
        text: Text to convert to speech
        voice: Voice name (e.g., 'en-US-AvaMultilingualNeural')
        speed: Speech rate (0.5 to 2.0, default 1.3)
        pitch: Pitch adjustment in Hz (-100 to +100, default 0)

    Returns:
        SSML string ready for Edge TTS
    """
    # Format pitch with sign
    pitch_str = f"{pitch:+}Hz"

    ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="{voice}">
    <prosody rate="{speed:.2f}" pitch="{pitch_str}">
      {text}
    </prosody>
  </voice>
</speak>'''

    return ssml


def get_voice_config(campaign: dict) -> dict:
    """
    Get voice configuration from campaign settings.

    Args:
        campaign: Campaign dictionary with voice settings

    Returns:
        Dictionary with voice configuration
    """
    return {
        "voice": campaign.get("tts_voice", "en-US-AvaMultilingualNeural"),
        "speed": campaign.get("tts_speed", 1.3),
        "pitch": campaign.get("tts_pitch", 0),
        "interrupt_sensitivity": campaign.get("interrupt_sensitivity", 0.5),
    }


# Example usage:
if __name__ == "__main__":
    # Test data
    lead_data = {
        "first_name": "John",
        "last_name": "Smith",
        "vendor_lead_name": "Acme Corp",
        "city": "San Francisco",
        "state": "CA",
        "phone_number": "4155551234",
    }

    # Test prompt with variables
    prompt = "Hi {{first_name}}, this is Sarah from {{company}}. I'm calling about the funding opportunity for your business in {{city}}, {{state}}. How are you today?"

    # Replace variables
    personalized = replace_dynamic_vars(prompt, lead_data)
    print("Personalized:", personalized)

    # Generate SSML
    ssml = generate_ssml(personalized, speed=1.3, pitch=10)
    print("\nSSML:", ssml)
