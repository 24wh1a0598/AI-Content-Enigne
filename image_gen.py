"""Image generation – builds a structured prompt and calls OpenRouter."""
import atexit
import httpx
from openai import OpenAI
from config import OPENROUTER_IMAGE_API_KEY, OPENROUTER_BASE_URL, IMAGE_MODEL, TONE_STYLES

_httpx_client = httpx.Client()
atexit.register(_httpx_client.close)
_client = OpenAI(
    api_key=OPENROUTER_IMAGE_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    http_client=_httpx_client,
)


def build_image_prompt(product: str, audience: str, tone: str, tagline: str, ad_goal: str = "") -> str:
    """Construct a detailed image generation prompt from campaign context.

    ad_goal (e.g. "Flash Sale", "Product Launch") is added to the subject line so
    the generated visual reflects the advertising purpose.
    Note: the uploaded product photo is NOT sent to the image model in this Phase 1
    prototype — the current OpenRouter/Gemini image API does not accept an image as
    input. The product description is used instead. Image-input support can be added
    in a later phase when a vision-capable generation model is available.
    """
    tone_key = tone.lower()
    style_map = TONE_STYLES.get(tone_key, TONE_STYLES["professional"])

    goal_clause = f" for a {ad_goal} campaign" if ad_goal else ""

    return (
        f"Subject: {product} product hero shot for {audience}{goal_clause}. "
        f"Concept inspired by the campaign idea: '{tagline}'. "
        f"Style: {style_map['style']}. "
        f"Lighting: {style_map['lighting']}. "
        f"Colour palette: {style_map['palette']}. "
        "Composition: centered subject, rule of thirds. "
        "Camera: slight low angle, shallow depth of field. "
        "Constraints: no text, no logos, no watermarks, high quality, 16:9 composition, "
        "commercial advertising quality."
    )


def _extract_image_url(message) -> str:
    """Pull the first image URL or data URL from an OpenRouter chat response."""
    images = getattr(message, "images", None) or []
    if not images:
        raise RuntimeError("Image model returned no images")

    first = images[0]
    if isinstance(first, dict):
        url = first.get("image_url") or first.get("url")
        if isinstance(url, dict):
            url = url.get("url")
    else:
        url_obj = getattr(first, "image_url", None) or getattr(first, "url", None)
        url = getattr(url_obj, "url", url_obj) if url_obj else None

    if not url:
        raise RuntimeError("Image model returned an empty image payload")

    return url


def generate_image(product: str, audience: str, tone: str, tagline: str, ad_goal: str = "") -> tuple[str, str]:
    """
    Generate a hero image via OpenRouter (same provider as text generation).

    Returns
    -------
    (image_url, prompt_used)
    """
    prompt = build_image_prompt(product, audience, tone, tagline, ad_goal=ad_goal)
    resp = _client.chat.completions.create(
        model=IMAGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        extra_body={"modalities": ["image", "text"]},
    )
    image_url = _extract_image_url(resp.choices[0].message)
    return image_url, prompt
