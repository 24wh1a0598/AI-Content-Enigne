import os
import sys

import imageio_ffmpeg
from moviepy import ImageClip
from moviepy import config as moviepy_config


def create_ken_burns(image_path: str, output_path: str = "hero_video.mp4", duration: float = 6.0, zoom_end: float = 1.12, fps: int = 24):
    """Create a short cinematic MP4 from a single image using MoviePy.

    - image_path: path to the hero image (PNG/JPG)
    - output_path: path to write the MP4
    - duration: seconds (5-8 recommended)
    - zoom_end: final zoom factor (1.0=no zoom, 1.12 = 12% zoom)
    """
    clip = ImageClip(image_path).with_duration(duration)
    w, h = clip.size

    # Create a slightly zoomed clip
    zoomed = clip.resized(zoom_end)

    # compute half-deltas for center movement
    dx = (zoomed.w - w) / 2
    dy = (zoomed.h - h) / 2

    # animate a gentle Ken Burns-style zoom + pan using a custom frame transform
    def transform_frame(get_frame, t):
        frame = get_frame(t)
        x = int((zoomed.w - w) * (t / duration) / 2)
        y = int((zoomed.h - h) * (t / duration) * 0.6 / 2)
        return frame[y : y + h, x : x + w]

    animated = zoomed.transform(lambda gf, t: transform_frame(gf, t), apply_to=["mask"])

    # Use imageio-ffmpeg's bundled executable to avoid relying on system ffmpeg PATH
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    moviepy_config.FFMPEG_BINARY = ffmpeg_path

    animated.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio=False,
        threads=4,
        preset="medium",
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python local_video.py path/to/hero.png [output.mp4] [duration_seconds]")
        sys.exit(1)

    img = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "hero_video.mp4"
    dur = float(sys.argv[3]) if len(sys.argv) > 3 else 6.0
    create_ken_burns(img, out, duration=dur)
