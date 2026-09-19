"""Video generation – builds a motion prompt and calls the Runway Gen-3 API."""
import atexit
import httpx
import time
import runwayml
from config import RUNWAY_API_KEY, VIDEO_DURATION

_httpx_client = httpx.Client()
atexit.register(_httpx_client.close)
_client = runwayml.RunwayML(api_key=RUNWAY_API_KEY, http_client=_httpx_client)


def build_motion_prompt(product: str, tone: str, tagline: str, ad_goal: str = "") -> str:
    """Construct a cinematic motion prompt for Runway."""
    goal_clause = f" ({ad_goal} campaign)" if ad_goal else ""
    return (
        f"Slow cinematic camera push towards {product}{goal_clause}. "
        f"Inspired by the campaign theme: '{tagline}'. "
        f"Tone: {tone}. "
        "Movement: gentle forward dolly, subtle breathing motion. "
        "Lighting: soft volumetric shifts, warm highlights gradually brightening. "
        "Background: mostly static with slight atmospheric depth. "
        "Style: commercial advertisement, 8-second clip, cinematic 4K quality."
    )


def generate_video(image_url: str, product: str, tone: str, tagline: str, ad_goal: str = "") -> str:
    """
    Animate the hero image using Runway Gen-3.

    Parameters
    ----------
    image_url : publicly accessible URL of the hero image

    Returns
    -------
    URL of the generated video
    """
    motion_prompt = build_motion_prompt(product, tone, tagline, ad_goal=ad_goal)

    task = _client.image_to_video.create(
        model="gen3a_turbo",
        prompt_image=image_url,
        prompt_text=motion_prompt,
        duration=VIDEO_DURATION,
        ratio="1280:720",
    )

    # Poll until the task completes (Runway is async)
    while task.status not in ("SUCCEEDED", "FAILED"):
        time.sleep(5)
        task = _client.tasks.retrieve(task.id)

    if task.status == "FAILED":
        raise RuntimeError(f"Runway task failed: {getattr(task, 'failure', 'unknown error')}")

    return task.output[0]
