# iQOO Hackathon — AI Content Engine Progress

---

## 1. Project Context

This repository contains the **AI Content Engine**, a Streamlit web application that generates complete marketing campaigns from a product brief (name, audience, tone). It is being used as the **base/reference prototype** for an iQOO hackathon idea.

The hackathon concept is:

> "A small seller points their phone at a product, describes what they want to advertise, and receives a complete campaign ready to publish."

The eventual hackathon implementation is intended to be **phone-first** and may use:

- iQOO camera input
- Voice input
- Local / open-source AI models
- On-device inference / Snapdragon NPU
- iQOO Office Kit integration
- Phone-to-laptop workflow

**None of these are implemented yet.** Phase 1 uses the existing Streamlit app running in a browser.

---

## 2. Important Original-Work Rule

> **The existing AI Content Engine is PRE-EXISTING work.**

It must **not** be represented as software created during the iQOO hackathon.

For the current Phase 1 work, it is being used only as a **prototype/reference/base** to demonstrate the core campaign-generation idea in a browser before the final phone-first architecture is built.

The actual hackathon implementation will need to:

- Follow the event's original-work rules.
- Clearly disclose which components are pre-existing.
- Rebuild or substantially extend the system according to the event's requirements.

Any future session or team member working on this project must respect this boundary.

---

## 3. Current Phase

**Current phase: PHASE 1 — Prototype**

### Phase 1 objective

Demonstrate the core campaign-generation experience (input → full campaign output) before implementing the final phone-first architecture. The goal is to show the user story end-to-end in a browser.

### Phase 1 explicitly does NOT implement

- Native Android app
- Snapdragon NPU / on-device LLM inference
- iQOO Office Kit integration
- Camera or voice input (beyond a browser file-upload widget)
- Production backend or API server
- Authentication or user accounts
- Complex computer vision pipeline
- Full production architecture

---

## 4. Target Phase 1 User Flow

The intended flow a user follows in the Phase 1 Streamlit prototype:

1. Upload a product photo *(optional — shown as reference only; not sent to the image model)*
2. Enter a product name and/or short description
3. Select an advertising goal
4. Select a target audience (preset or custom free-text)
5. Select a theme/tone
6. Click **Create Campaign**
7. Receive a complete generated campaign

### Advertising goals (current list)

- Product Launch
- Festival Promotion
- Flash Sale
- Special Offer
- Brand Awareness
- New Store Opening
- Seasonal Promotion

### Audience presets (current list)

- College Students
- Young Professionals
- Families
- Gamers
- Budget-Conscious Buyers
- Premium Customers
- Custom… *(triggers a free-text input field)*

### Tones (current list)

- Premium
- Eco
- Playful
- Professional
- Luxury
- Minimal
- Friendly

---

## 5. Expected Outputs

The Phase 1 prototype produces the following for each campaign:

| # | Output | Notes |
|---|---|---|
| 1 | Hero advertisement visual | AI-generated image via OpenRouter / Gemini Flash Image |
| 2 | Campaign tagline | ≤ 10 words, tone-matched |
| 3 | Instagram copy | Platform-specific post text |
| 4 | LinkedIn copy | Platform-specific post text, no hashtags |
| 5 | X / Twitter copy | ≤ 280 characters |
| 6 | Promotional video | Runway Gen-3 cloud video; Ken Burns local MP4 fallback |

A **blog introduction** (100–120 words) is still generated internally as rich context for the social post generation step, but it is **not displayed** in the new UI. The output is social-first.

---

## 6. Work Already Completed

The following changes were made to the codebase in the Phase 1 implementation session. All changes are minimal and surgical — existing logic was preserved wherever possible.

### `config.py`

- Added `AD_GOALS: list[str]` — 7 advertising purpose options.
- Added `AUDIENCE_OPTIONS: list[str]` — 7 audience presets including the `"Custom…"` sentinel.
- `TONE_STYLES`, `TEXT_MODEL`, `IMAGE_MODEL`, `VIDEO_DURATION`, and all API key loading are **unchanged**.

### `text_gen.py`

- Added `ad_goal: str = ""` parameter to:
  - `generate_tagline` — goal woven into the few-shot user prompt.
  - `generate_blog` — goal added to the role-prompting user message.
  - `_gen_social_platform` — goal added to the copywriter user message.
  - `generate_social_posts` — goal forwarded to `_gen_social_platform`.
- The advertising goal is incorporated into all prompt strings so generated copy reflects the campaign purpose.
- `_chat()`, `probe_affordance()`, retry logic, token-budget handling, and the module-level OpenAI client are **completely unchanged**.

### `image_gen.py`

- Added `ad_goal: str = ""` parameter to `build_image_prompt` and `generate_image`.
- Goal is embedded in the image prompt subject line as `"for a {ad_goal} campaign"`.
- Added a code comment explaining why the uploaded product photo is **not** sent to the image model in Phase 1 (the current OpenRouter/Gemini image API does not accept image input for generation).
- The OpenAI client setup, API call, `_extract_image_url`, and `extra_body` modalities are **unchanged**.

### `video_gen.py`

- Added `ad_goal: str = ""` parameter to `build_motion_prompt` and `generate_video`.
- Goal is embedded in the motion prompt as `"({ad_goal} campaign)"`.
- The Runway client construction, `image_to_video.create` call, polling loop, and error handling are **unchanged**.

### `app.py`

The UI was substantially rewritten to replace the sidebar-based developer demo layout with a clean, centred, phone-friendly campaign creation flow.

**Input section (above the fold):**
- Product photo file uploader (optional, jpg/jpeg/png/webp)
- Product Name / Description text input
- Advertising Goal selectbox (from `AD_GOALS`)
- Target Audience selectbox (from `AUDIENCE_OPTIONS`) — selecting `"Custom…"` reveals a free-text input
- Theme / Tone selectbox (from `TONE_STYLES`)
- **🚀 Create Campaign** primary button (full-width)

**Output section (after clicking Create Campaign):**

| Stage | Output |
|---|---|
| 1 | Uploaded product photo (if provided) — reference thumbnail with Phase 1 note |
| 2 | Hero Advertisement image + collapsible image prompt |
| 3 | Campaign Tagline |
| 4 | Social Media Copy — tabbed: Instagram / LinkedIn / X / Twitter |
| 5 | Promotional Video (cloud or local fallback) |
| — | `st.success("Campaign ready! 🎉")` footer |

**Preserved unchanged from the original app.py:**
- `get_artifacts_dir()` helper
- `download_image()` helper
- Hero image download to `artifacts/hero_image.png`
- Entire local Ken Burns video fallback block
- All billing/credit error detection and user-facing messages
- `st.stop()` on validation failures

### Environment fix

`pydantic-core==2.46.4` was **force-reinstalled** using `python -m pip install --force-reinstall`.

The compiled native extension `_pydantic_core.cp313-win_amd64.pyd` (5.1 MB) was missing from `.venv/Lib/site-packages/pydantic_core/` — the wheel had installed incorrectly at some earlier point. Without it, `import pydantic` fails, which cascades to `import openai` and `import runwayml` also failing, which means the app cannot start. After reinstall, the `.pyd` is present and all imports work.

This was an **environment/dependency repair**, not a feature change. No source files were modified for this fix.

---

### Post-Phase-1 fixes (same session, 19–20 September 2026)

The following additional changes were made after the initial Phase 1 implementation, in response to real testing findings.

#### `app.py` — uploaded photo fallback for failed image generation

When AI image generation fails (e.g. credit exhaustion), the pipeline previously halted with `st.stop()`. It now:

- Shows the specific failure reason as `st.warning()` (never hidden)
- If the user uploaded a product photo: applies a PIL letterbox + dark-border treatment, saves the result to `artifacts/hero_image.png`, and continues the pipeline
- Displays the fallback visual with a clear `st.info()` label distinguishing it from an AI-generated image
- If no photo was uploaded: shows `st.error()` and halts — same behaviour as before
- Stage 4 (video): guards against `image_url is None` when in fallback mode, skipping Runway cleanly and going straight to Ken Burns

PIL (`Pillow`) was already a project dependency — no new packages added.

#### `config.py` — `TEXT_MODEL` changed to free model, made env-overridable

- `TEXT_MODEL` changed from `"openai/gpt-4o"` (paid) to `"poolside/laguna-s-2.1:free"` (free) as the default
- Now readable from `TEXT_MODEL` environment variable, allowing model switching without editing code
- `IMAGE_MODEL` is **unchanged**
- To switch back to GPT-4o when credits are available: set `TEXT_MODEL=openai/gpt-4o` in `.env`

#### `text_gen.py` — `probe_affordance()` bypassed for free models

- `generate_tagline` now checks `TEXT_MODEL.endswith(":free")` before calling `probe_affordance()`
- Free models never return 402 "can only afford N tokens" — calling the probe wastes scarce daily-quota requests
- When using a free model: `max_tokens=32` fixed budget used directly (taglines are always short)
- When using a paid model: `probe_affordance()` runs exactly as before
- All other logic in `_chat()`, retry loop, and backoff is **unchanged**

---

## 7. Validation Already Performed

The following checks were run and **all passed** after the Phase 1 changes and environment fix:

### Package imports

| Package | Version | Status |
|---|---|---|
| `pydantic` | 2.13.4 | ✅ |
| `openai` | 2.44.0 | ✅ |
| `runwayml` | 5.4.0 | ✅ |
| `moviepy` | 2.2.1 | ✅ |
| `httpx` | 0.28.1 | ✅ |
| `streamlit` | 1.58.0 | ✅ |

### Syntax and static checks

- `py_compile` on all 6 source files: ✅ (exit 0)
- AST inspection confirmed `ad_goal` parameter present in all 8 public functions across `text_gen`, `image_gen`, `video_gen`: ✅
- All `from X import Y` names in `app.py` verified to exist in their source modules: ✅

### Logic and call-signature checks

- `AD_GOALS` (7), `AUDIENCE_OPTIONS` (7), `TONE_STYLES` (7), `VIDEO_DURATION` (8): ✅
- `Custom…` sentinel correctly routes to free-text input: ✅
- `generate_image` called with `tagline=""` and `ad_goal=ad_goal` — arguments bind without error: ✅
- `ad_goal` present in generated image prompt subject line: ✅
- `ad_goal` present in Runway motion prompt: ✅
- `generate_tagline`, `generate_social_posts`, `generate_video` — all call bindings verified: ✅
- `RunwayML` client constructs without error on placeholder key (fails only at API call time, which is caught): ✅

### Live runtime check

- Ken Burns local video fallback rendered a real MP4 from `hero.png`: ✅ (21 KB output, cleaned up after test)

---

## 8. Manual End-to-End Test — 19 September 2026

A full manual test of the Phase 1 prototype was run in the browser on **19 September 2026**. This is the definitive functional baseline for Phase 1.

### Test setup

- App started with `streamlit run app.py` at `http://localhost:8501`
- A real product photo uploaded via the file uploader
- Product name/description, advertising goal, target audience, and tone filled in
- **Create Campaign** clicked

### Results by component

| Component | Result | Notes |
|---|---|---|
| UI input form | ✅ Worked | All dropdowns, text inputs, file uploader, and button rendered and responded correctly |
| Product photo upload | ✅ Worked | Photo accepted, saved to `artifacts/`, displayed as reference |
| AI image generation | ❌ Unavailable | OpenRouter image credits exhausted — 402 returned. Warning shown correctly; pipeline did **not** halt. |
| Uploaded photo fallback (hero visual) | ✅ Worked | PIL letterbox + border treatment applied; fallback image displayed with `st.info()` label clearly distinguishing it from an AI-generated visual |
| Campaign tagline | ✅ Generated | `poolside/laguna-s-2.1:free` model produced a relevant, on-brief tagline |
| Blog introduction (internal) | ✅ Generated | Used as context for social copy; not shown in UI as designed |
| Instagram copy | ✅ Generated | Platform-specific post displayed in tab |
| LinkedIn copy | ✅ Generated | Platform-specific post displayed in tab |
| X / Twitter copy | ✅ Generated | Platform-specific post displayed in tab |
| Cloud video (Runway) | ❌ Unavailable | Runway key is a placeholder — fell through to local fallback correctly |
| Local video fallback (Ken Burns) | ✅ Worked | Ken Burns MP4 rendered from the fallback hero image and played in the browser |
| End-to-end pipeline completion | ✅ Complete | `Campaign ready! 🎉` shown; all outputs visible |

### Summary

The complete campaign flow — photo upload → tagline → social copy → promotional video — **demonstrated successfully end-to-end**. The two unavailable components (AI image generation, Runway cloud video) degraded gracefully with clear user-facing messages and automatic fallbacks, exactly as designed.

Text generation, uploaded-photo hero visual, all three social platform posts, and the local Ken Burns video all worked in a single campaign run.

### What remains unavailable (requires external access)

| Component | Blocker | How to unblock |
|---|---|---|
| AI hero image generation | OpenRouter image credits exhausted | Top up at [OpenRouter Settings](https://openrouter.ai/settings/credits) |
| Runway cloud video | Placeholder API key in `.env` | Replace `RUNWAY_API_KEY` with a real Runway ML key |

---

## 8. How to Run the Prototype

```bash
cd C:\Projects\AI-ContentEngine
.venv\Scripts\activate
streamlit run app.py
```

Opens at `http://localhost:8501`.

### Required configuration (`.env`)

```env
OPENROUTER_API_KEY=sk-or-v1-...          # required for text + image generation
OPENROUTER_IMAGE_API_KEY=sk-or-v1-...   # optional; falls back to OPENROUTER_API_KEY
RUNWAY_API_KEY=your_runway_key_here      # optional; local MP4 fallback used if missing
```

The `.env` file is already present in the project root with real OpenRouter keys. The Runway key is still a placeholder — the local fallback fires automatically.

---

## 9. Known Limitations (Phase 1)

| Limitation | Status | Notes |
|---|---|---|
| AI image generation unavailable | ⚠️ Credits exhausted | OpenRouter image credits depleted. Photo fallback works. Unblock: top up at OpenRouter Settings. |
| Uploaded photo is text-context only | By design | Not sent to image model — AI generates visuals from description. Photo-input generation deferred to a later phase. Disclosed in UI. |
| Runway cloud video unavailable | By design | Placeholder API key. Local Ken Burns MP4 fallback works reliably. Unblock: set a real `RUNWAY_API_KEY` in `.env`. |
| Text generation: 50 req/day free cap | Known constraint | OpenRouter free tier = 50 free-model requests/day account-wide. One campaign uses 5 requests. Resets daily. Model: `poolside/laguna-s-2.1:free`. Switch to paid model via `TEXT_MODEL` env var when credits available. |
| Blog intro not shown in UI | By design | Generated internally as social-post context. Not displayed — social-first output is intentional. |
| Browser-based only | By design | Final hackathon version will be native Android with camera/voice. Phase 1 is Streamlit only. |

---

## 10. Files in This Repository

```
AI-ContentEngine/
├── app.py                  # Streamlit UI — Phase 1 campaign creator (with photo fallback)
├── config.py               # Env vars, AD_GOALS, AUDIENCE_OPTIONS, TONE_STYLES; TEXT_MODEL defaults to free model
├── text_gen.py             # Tagline, blog, social post generation; probe bypassed for free models
├── image_gen.py            # Hero image generation (OpenRouter/Gemini Flash Image)
├── video_gen.py            # Cloud video generation (Runway Gen-3 Turbo)
├── local_video.py          # Ken Burns fallback video (MoviePy + bundled FFmpeg)
├── spec.md                 # Technical specification
├── readme.md               # User-facing documentation
├── HACKATHON_PROGRESS.md   # This file — handoff/progress document
├── .env                    # API keys (not committed)
├── .gitignore
├── hero.png                # Sample image used for local video fallback testing
└── artifacts/              # Runtime output directory (created automatically)
    ├── hero_image.png      # Hero image from last run (AI-generated or photo fallback)
    ├── product_photo.*     # Uploaded product photo from last run (if provided)
    └── hero_video.mp4      # Local fallback video from last run (if generated)
```

---

## 11. Next Steps (Future Phases)

These are **not started** and should be planned and scoped before implementation:

- **Phase 2 — Enhanced prototype:** Improve output quality, add copy-to-clipboard, add download-all-assets button, refine UI polish.
- **Phase 3 — Phone-first prototype:** Explore progressive web app (PWA) or React Native wrapper so the Streamlit prototype can be demoed from a phone browser.
- **Phase 4 — On-device / hackathon build:** Native Android, Snapdragon NPU, on-device LLM, iQOO camera integration, iQOO Office Kit, voice input.

Any Phase 4 work must be original and disclosed correctly per the hackathon rules.
