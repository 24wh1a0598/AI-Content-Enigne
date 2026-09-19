"""Campaign Creator – Phase 1 prototype.

Evolved from the AI Content Engine base to demonstrate the iQOO hackathon concept:
  "A small seller points their phone at a product and receives a complete
   marketing campaign ready to publish."

This prototype runs entirely in a browser via Streamlit.
The final hackathon version will be a native Android app with on-device AI,
Snapdragon NPU inference, camera input, and iQOO Office Kit integration.
"""
import json
from pathlib import Path

import httpx
import streamlit as st

from config import AD_GOALS, AUDIENCE_OPTIONS, TONE_STYLES, VIDEO_DURATION
from image_gen import generate_image
from local_video import create_ken_burns
from text_gen import generate_blog, generate_social_posts, generate_tagline
from video_gen import generate_video

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Campaign Creator",
    page_icon="📣",
    layout="centered",   # centred feels more phone-like than wide
    initial_sidebar_state="collapsed",
)

# ── Minimal custom CSS – tightens spacing on narrow viewports ─────────────────
st.markdown(
    """
    <style>
    /* Reduce top padding so the header sits higher on mobile */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    /* Make the primary button full-width and a bit taller */
    div.stButton > button[kind="primary"] { width: 100%; padding: 0.65rem 1rem; font-size: 1.05rem; }
    /* Slightly larger tab text */
    button[data-baseweb="tab"] { font-size: 0.95rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_artifacts_dir() -> Path:
    """Return (and create) the artifacts output directory."""
    artifacts = Path("artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)
    return artifacts


def download_image(image_url: str, target_path: Path) -> Path:
    """Download a remote image to a local path and return that path."""
    response = httpx.get(image_url, follow_redirects=True, timeout=30.0)
    response.raise_for_status()
    target_path.write_bytes(response.content)
    return target_path


def save_uploaded_photo(uploaded_file, artifacts_dir: Path) -> Path:
    """Persist the user's uploaded product photo to artifacts/ and return its path."""
    ext = Path(uploaded_file.name).suffix or ".jpg"
    dest = artifacts_dir / f"product_photo{ext}"
    dest.write_bytes(uploaded_file.getbuffer())
    return dest


# ── Header ────────────────────────────────────────────────────────────────────
st.title("📣 Campaign Creator")
st.caption("Point at a product. Get a complete ad campaign.")

st.divider()

# ── Input form ────────────────────────────────────────────────────────────────
# All inputs live in the main body (no sidebar) so they read naturally on a
# phone-sized browser window.

uploaded_photo = st.file_uploader(
    "Product Photo  *(optional)*",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload a photo of your product. Shown alongside the campaign for reference.",
)

product = st.text_input(
    "Product Name / Description",
    placeholder="e.g.  iQOO Neo 9 Pro  —  flagship gaming phone with 144 Hz display",
    help="Give the product a name and optionally a short description.",
)

ad_goal = st.selectbox(
    "Advertising Goal",
    options=AD_GOALS,
    help="What is the purpose of this campaign?",
)

# Audience: preset dropdown + optional custom free-text field
audience_choice = st.selectbox(
    "Target Audience",
    options=AUDIENCE_OPTIONS,
    help="Who are you trying to reach?",
)
if audience_choice == "Custom…":
    audience = st.text_input(
        "Describe your audience",
        placeholder="e.g.  small business owners in tier-2 cities",
    )
else:
    audience = audience_choice

tone = st.selectbox(
    "Theme / Tone",
    options=list(TONE_STYLES.keys()),
    format_func=str.capitalize,
    help="Visual and copy personality for the campaign.",
)

st.write("")   # small spacer
create_btn = st.button("🚀  Create Campaign", type="primary")

# ── Generation pipeline ───────────────────────────────────────────────────────
if create_btn:
    # Validate required fields
    if not product:
        st.error("Please enter a Product Name / Description.")
        st.stop()
    if not audience:
        st.error("Please describe your Target Audience.")
        st.stop()

    st.divider()
    st.subheader("✅  Campaign Generated")

    artifacts_dir = get_artifacts_dir()

    # Save the uploaded photo early so it is available as a fallback if AI
    # image generation fails. The path is None when no photo was uploaded.
    uploaded_photo_path: Path | None = None
    if uploaded_photo is not None:
        uploaded_photo_path = save_uploaded_photo(uploaded_photo, artifacts_dir)

    # ── Stage 1: Hero image ───────────────────────────────────────────────────
    # Try AI generation first. On any failure, fall back to the uploaded photo
    # if one was provided; otherwise halt with an error.
    image_url: str | None = None      # remote URL (set only on AI success)
    hero_path: Path | None = None     # local PNG path (set on AI success or fallback)
    used_photo_fallback: bool = False  # True when the uploaded photo is the hero visual
    image_prompt: str = ""

    with st.spinner("Generating hero advertisement visual…"):
        try:
            image_url, image_prompt = generate_image(
                product, audience, tone, tagline="", ad_goal=ad_goal
            )
        except Exception as e:
            err = str(e)
            # Surface the specific failure reason so it is never hidden.
            if "billing_hard_limit_reached" in err or "Billing hard limit" in err:
                st.warning(
                    "⚠️ AI image generation failed: OpenAI spending limit reached. "
                    "Raise it at [OpenAI Billing](https://platform.openai.com/settings/organization/billing)."
                )
            elif "402" in err or "credits" in err.lower():
                st.warning(
                    "⚠️ AI image generation failed: insufficient OpenRouter credits. "
                    "Top up at [OpenRouter Settings](https://openrouter.ai/settings/credits)."
                )
            else:
                st.warning(f"⚠️ AI image generation failed: {e}")

            # Attempt fallback to the uploaded product photo.
            if uploaded_photo_path is not None and uploaded_photo_path.exists():
                used_photo_fallback = True
            else:
                # No photo uploaded and AI failed — cannot continue.
                st.error(
                    "Campaign generation stopped: no hero visual is available. "
                    "Upload a product photo to continue without AI image generation."
                )
                st.stop()

    if not used_photo_fallback:
        # AI generation succeeded — download to local PNG for video fallback.
        hero_path = artifacts_dir / "hero_image.png"
        with st.spinner("Downloading hero image…"):
            try:
                hero_path = download_image(image_url, hero_path)
            except Exception as e:
                st.warning(f"Could not download hero image; showing remote preview only. {e}")
                hero_path = None
    else:
        # Use the uploaded photo as the hero image.
        # Apply a light PIL presentation treatment: convert to RGB PNG, add a
        # subtle 6-pixel dark border so it reads as a "campaign visual" frame.
        # PIL is already a project dependency (Pillow); no new packages needed.
        from PIL import Image as _PILImage, ImageOps as _ImageOps

        hero_path = artifacts_dir / "hero_image.png"
        try:
            with _PILImage.open(uploaded_photo_path) as img:
                img = img.convert("RGB")
                # Resize to a standard 16:9 canvas (max 1280 wide) while keeping
                # the product centred — letterbox/pillarbox with a dark background.
                target_w, target_h = 1280, 720
                img.thumbnail((target_w, target_h), _PILImage.LANCZOS)
                canvas = _PILImage.new("RGB", (target_w, target_h), (18, 18, 18))
                offset_x = (target_w - img.width) // 2
                offset_y = (target_h - img.height) // 2
                canvas.paste(img, (offset_x, offset_y))
                # Thin dark border as a minimal "ad frame"
                canvas = _ImageOps.expand(canvas, border=6, fill=(30, 30, 30))
                canvas.save(hero_path, "PNG")
        except Exception as pil_err:
            # If PIL treatment fails, just copy the raw upload bytes as-is.
            st.warning(f"Could not apply image treatment: {pil_err}. Using raw photo.")
            hero_path.write_bytes(uploaded_photo_path.read_bytes())

    # ── Hero visual display ───────────────────────────────────────────────────
    st.subheader("🖼️  Hero Advertisement")

    if used_photo_fallback:
        st.info(
            "📸 **Uploaded product photo used as fallback visual.** "
            "AI image generation was unavailable (see warning above). "
            "The rest of the campaign — tagline, social copy, and video — "
            "has been generated from your product description."
        )
        st.image(str(hero_path), use_container_width=True,
                 caption="Hero visual: your uploaded product photo (campaign frame applied)")
        st.caption(
            "ℹ️ *Phase 1 limitation: when OpenRouter credits are unavailable, the uploaded "
            "product photo is used in place of an AI-generated hero image. "
            "AI visual generation will resume once credits are restored.*"
        )
    else:
        st.image(image_url, use_container_width=True)
        with st.expander("Image prompt used"):
            st.caption(image_prompt)

    st.divider()

    # ── Stage 2: Tagline ──────────────────────────────────────────────────────
    with st.spinner("Writing campaign tagline…"):
        try:
            tagline = generate_tagline(product, audience, tone, ad_goal=ad_goal)
        except Exception as e:
            st.error(f"Tagline generation failed: {e}")
            st.stop()

    st.subheader("🏷️  Tagline")
    st.markdown(f"### *{tagline}*")

    st.divider()

    # ── Stage 3: Social media copy ────────────────────────────────────────────
    # The blog intro is generated internally as context for social posts but is
    # not shown on its own – the output is social-first.
    with st.spinner("Writing social media copy…"):
        try:
            blog = generate_blog(product, audience, tone, tagline, ad_goal=ad_goal)
            posts = generate_social_posts(
                product, audience, tone, blog, tagline, ad_goal=ad_goal
            )
        except json.JSONDecodeError as e:
            st.error(f"Social posts returned invalid JSON: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Social media copy generation failed: {e}")
            st.stop()

    st.subheader("📱  Social Media Copy")
    tab_ig, tab_li, tab_tw = st.tabs(["Instagram", "LinkedIn", "X / Twitter"])
    with tab_ig:
        st.write(posts.get("instagram", ""))
    with tab_li:
        st.write(posts.get("linkedin", ""))
    with tab_tw:
        st.write(posts.get("twitter", ""))

    st.divider()

    # ── Stage 4: Promotional video ────────────────────────────────────────────
    st.subheader("🎬  Promotional Video")
    try:
        # Runway requires a publicly accessible image URL. Skip the cloud attempt
        # when we are in fallback mode (no remote URL exists) so we go straight to
        # the local Ken Burns render without surfacing a confusing Runway error.
        if image_url is None:
            raise RuntimeError("No remote image URL available; using local video fallback.")

        with st.spinner("Generating promotional video — this can take ~60 s…"):
            video_url = generate_video(
                image_url, product, tone, tagline, ad_goal=ad_goal
            )
        st.video(video_url)

    except Exception:
        st.info("Cloud video unavailable — rendering a local preview from the hero image.")
        if hero_path is not None and hero_path.exists():
            local_video_path = artifacts_dir / "hero_video.mp4"
            with st.spinner("Rendering local preview…"):
                try:
                    create_ken_burns(str(hero_path), str(local_video_path), duration=VIDEO_DURATION)
                    st.video(str(local_video_path))
                except Exception as fallback_error:
                    st.error(f"Local video fallback also failed: {fallback_error}")
        else:
            st.error("Video preview unavailable: hero image could not be downloaded.")

    st.divider()
    st.success("Campaign ready! 🎉")

else:
    # Empty state – friendly prompt
    st.info("Fill in the details above and press **🚀 Create Campaign** to generate your campaign.")
