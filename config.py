"""Configuration – loads environment variables and shared constants."""
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_IMAGE_API_KEY: str = os.getenv(
    "OPENROUTER_IMAGE_API_KEY", OPENROUTER_API_KEY
)
RUNWAY_API_KEY: str = os.getenv("RUNWAY_API_KEY", "")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Text model used for tagline, blog, and social post generation.
# Override via TEXT_MODEL env var to switch between paid and free tiers without
# editing this file.  Default is a capable free OpenRouter model so the prototype
# runs without purchased credits.  Switch back to "openai/gpt-4o" (or any other
# paid model) once credits are available.
TEXT_MODEL: str = os.getenv("TEXT_MODEL", "poolside/laguna-s-2.1:free")

IMAGE_MODEL = "google/gemini-3.1-flash-image"
VIDEO_DURATION = 8         # seconds

# ── Campaign input options ────────────────────────────────────────────────────

# Advertising purposes shown in the "Advertising Goal" dropdown.
AD_GOALS: list[str] = [
    "Product Launch",
    "Festival Promotion",
    "Flash Sale",
    "Special Offer",
    "Brand Awareness",
    "New Store Opening",
    "Seasonal Promotion",
]

# Preset audience segments shown in the "Target Audience" dropdown.
# The UI also allows a free-text custom entry.
AUDIENCE_OPTIONS: list[str] = [
    "College Students",
    "Young Professionals",
    "Families",
    "Gamers",
    "Budget-Conscious Buyers",
    "Premium Customers",
    "Custom…",       # sentinel – UI switches to a text input when selected
]

TONE_STYLES: dict[str, dict] = {
    "premium":      {"style": "photorealistic",      "lighting": "dramatic studio lighting",   "palette": "rich deep tones, gold accents"},
    "eco":          {"style": "watercolour illustration", "lighting": "soft natural daylight",  "palette": "earthy greens, warm neutrals"},
    "playful":      {"style": "bright digital illustration", "lighting": "vibrant even lighting", "palette": "vivid multicolour"},
    "professional": {"style": "commercial photography",  "lighting": "editorial lighting",      "palette": "clean neutrals, confident blues"},
    "luxury":       {"style": "high-fashion photography", "lighting": "cinematic low-key",      "palette": "black, white, champagne gold"},
    "minimal":      {"style": "clean modern product shot", "lighting": "soft diffused shadows", "palette": "white, light grey, single accent"},
    "friendly":     {"style": "warm lifestyle photography", "lighting": "golden-hour natural",  "palette": "warm pastels, approachable tones"},
}
