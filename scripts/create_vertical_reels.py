#!/usr/bin/env python3
"""Convert + crop horizontal videos to vertical reels with timestamp selection."""

import subprocess
import argparse
from pathlib import Path

REPO = Path(__file__).parent.parent
VIDEO_DIR = REPO / "assets" / "video" / "edited"

def time_to_seconds(time_str):
    """Convert HH:MM:SS or MM:SS to seconds."""
    parts = time_str.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return int(time_str)

def create_reel(mp4_path, output_path, start_time="0", duration="60", srt_path=None):
    """Crop video to 9:16 vertical, optionally from timestamp, with optional caption burn-in."""

    start_sec = time_to_seconds(start_time)
    dur_sec = time_to_seconds(duration)

    # Build filter chain (escape commas in crop params)
    vf = "crop=min(iw\\,ih*9/16):min(ih\\,iw*16/9),scale=1080:1920"

    if srt_path and Path(srt_path).exists():
        # Import here to avoid circular import
        try:
            from create_story_clips import extract_captions_for_window, parse_srt, write_temp_srt

            captions = parse_srt(Path(srt_path))
            window_captions = extract_captions_for_window(captions, start_sec, dur_sec)

            if window_captions:
                temp_srt = Path("/tmp") / f"reel_{Path(output_path).stem}.srt"
                write_temp_srt(window_captions, temp_srt)

                # Add subtitle filter
                subtitle_filter = (
                    f"subtitles='{temp_srt}':force_style="
                    "'FontSize=22,PrimaryColour=&H00FFFFFF,"
                    "OutlineColour=&H00000000,Outline=2,Shadow=1,"
                    "Alignment=2,MarginV=60'"
                )
                vf = f"{vf},{subtitle_filter}"
        except (ImportError, ModuleNotFoundError):
            print("Warning: create_story_clips not found. Skipping caption burn-in for reel.")

    cmd = [
        "ffmpeg", "-i", str(mp4_path),
        "-ss", str(start_sec), "-t", str(dur_sec),
        "-vf", vf,
        "-c:v", "h264_videotoolbox", "-c:a", "aac", "-y",
        str(output_path)
    ]

    print(f"Creating reel: {start_time} ({dur_sec}s)" + (" with captions" if srt_path else ""))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr[-200:]}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create vertical YouTube Shorts/Reels from horizontal video.")
    parser.add_argument("--slug", required=True, help="Blog slug (filename without extension)")
    parser.add_argument("--start", default="0", help="Start time (MM:SS or HH:MM:SS, default 0)")
    parser.add_argument("--duration", default="60", help="Duration in seconds (default 60)")
    parser.add_argument("--output-dir", default=str(VIDEO_DIR), help="Output directory (default assets/video/edited/)")
    parser.add_argument("--output-name", help="Output filename (default {slug}_reel.mp4)")
    parser.add_argument("--srt", help="Optional SRT file for caption burn-in")
    args = parser.parse_args()

    mp4 = VIDEO_DIR / f"{args.slug}.mp4"
    output_dir = Path(args.output_dir)
    output_name = args.output_name or f"{args.slug}_reel.mp4"
    reel = output_dir / output_name

    if not mp4.exists():
        print(f"Error: Video not found: {mp4}")
        exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    create_reel(mp4, reel, args.start, args.duration, srt_path=args.srt)
    print(f"✓ Saved: {reel}")
