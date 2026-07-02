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
TEXT_MODEL = "openai/gpt-4o"
IMAGE_MODEL = "google/gemini-3.1-flash-image"
VIDEO_DURATION = 8         # seconds

TONE_STYLES: dict[str, dict] = {
    "premium":      {"style": "photorealistic",      "lighting": "dramatic studio lighting",   "palette": "rich deep tones, gold accents"},
    "eco":          {"style": "watercolour illustration", "lighting": "soft natural daylight",  "palette": "earthy greens, warm neutrals"},
    "playful":      {"style": "bright digital illustration", "lighting": "vibrant even lighting", "palette": "vivid multicolour"},
    "professional": {"style": "commercial photography",  "lighting": "editorial lighting",      "palette": "clean neutrals, confident blues"},
    "luxury":       {"style": "high-fashion photography", "lighting": "cinematic low-key",      "palette": "black, white, champagne gold"},
    "minimal":      {"style": "clean modern product shot", "lighting": "soft diffused shadows", "palette": "white, light grey, single accent"},
    "friendly":     {"style": "warm lifestyle photography", "lighting": "golden-hour natural",  "palette": "warm pastels, approachable tones"},
}
