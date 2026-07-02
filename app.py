"""Streamlit app – AI Content Engine."""
import json
import streamlit as st
from config import TONE_STYLES
from text_gen import generate_tagline, generate_blog, generate_social_posts
from image_gen import generate_image
from video_gen import generate_video

st.set_page_config(page_title="AI Content Engine", layout="wide")
st.title("🚀 AI Content Engine")
st.caption("Transform a product brief into a complete marketing campaign.")

# ── Sidebar inputs ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Campaign Brief")
    product  = st.text_input("Product Name",    placeholder="e.g. AuraSerum")
    audience = st.text_input("Target Audience", placeholder="e.g. health-conscious women 25-40")
    tone     = st.selectbox("Brand Tone", list(TONE_STYLES.keys()), format_func=str.capitalize)
    generate = st.button("✨ Generate Campaign", use_container_width=True, type="primary")

# ── Main layout ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

if generate:
    if not product or not audience:
        st.sidebar.error("Please fill in Product Name and Target Audience.")
        st.stop()

    # ── Stage 1: Tagline ─────────────────────────────────────────────────────
    with col_left:
        with st.spinner("Generating tagline…"):
            try:
                tagline = generate_tagline(product, audience, tone)
            except Exception as e:
                st.error(f"Tagline generation failed: {e}")
                st.stop()

        st.subheader("🏷️ Campaign Tagline")
        st.markdown(f"> **{tagline}**")

    # ── Stage 2: Blog ────────────────────────────────────────────────────────
    with col_left:
        with st.spinner("Writing blog introduction…"):
            try:
                blog = generate_blog(product, audience, tone, tagline)
            except Exception as e:
                st.error(f"Blog generation failed: {e}")
                st.stop()

        st.subheader("📝 Blog Introduction")
        st.write(blog)

    # ── Stage 3: Social posts ────────────────────────────────────────────────
    with col_left:
        with st.spinner("Crafting social media posts…"):
            try:
                posts = generate_social_posts(product, audience, tone, blog, tagline)
            except json.JSONDecodeError as e:
                st.error(f"Social posts returned invalid JSON: {e}")
                st.stop()
            except Exception as e:
                st.error(f"Social posts generation failed: {e}")
                st.stop()

        st.subheader("📱 Social Media Posts")
        tab_tw, tab_ig, tab_li = st.tabs(["Twitter / X", "Instagram", "LinkedIn"])
        with tab_tw: st.write(posts.get("twitter", ""))
        with tab_ig: st.write(posts.get("instagram", ""))
        with tab_li: st.write(posts.get("linkedin", ""))

    # ── Stage 4: Hero image ──────────────────────────────────────────────────
    with col_right:
        with st.spinner("Generating hero image…"):
            try:
                image_url, image_prompt = generate_image(product, audience, tone, tagline)
            except Exception as e:
                err = str(e)
                if "billing_hard_limit_reached" in err or "Billing hard limit" in err:
                    st.error(
                        "Image generation failed: your OpenAI account has hit its spending limit. "
                        "Raise the limit at [OpenAI Billing](https://platform.openai.com/settings/organization/billing)."
                    )
                elif "402" in err or "credits" in err.lower():
                    st.error(
                        "Image generation failed: insufficient OpenRouter credits. "
                        "Add credits at [OpenRouter Settings](https://openrouter.ai/settings/credits)."
                    )
                else:
                    st.error(f"Image generation failed: {e}")
                st.stop()

        st.subheader("🖼️ Campaign Hero Image")
        st.image(image_url, use_container_width=True)
        with st.expander("Image prompt"):
            st.caption(image_prompt)

    # ── Stage 5: Video ───────────────────────────────────────────────────────
    with col_right:
        with st.spinner("Generating promotional video (this may take ~60s)…"):
            try:
                video_url = generate_video(image_url, product, tone, tagline)
            except Exception as e:
                st.error(f"Video generation failed: {e}")
                st.stop()

        st.subheader("🎬 Promotional Video")
        st.video(video_url)

else:
    col_left.info("Fill in the brief and press **Generate Campaign** to start.")
