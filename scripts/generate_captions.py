#!/usr/bin/env python3
"""Generate captions for audio/video using OpenAI Whisper (free, open-source)."""

import subprocess
import argparse
from pathlib import Path
from _console import console, spinner

REPO = Path(__file__).parent.parent
AUDIO_DIR = REPO / "assets" / "audio"
VIDEO_DIR = REPO / "assets" / "video" / "edited"


def generate_captions(input_path: Path, output_format: str = "srt") -> Path:
    """Generate captions using Whisper CLI. Requires: pip install openai-whisper"""
    cmd = [
        "whisper",
        str(input_path),
        "--language", "English",
        "--output_format", output_format,
        "--output_dir", str(input_path.parent),
    ]

    with spinner() as progress:
        progress.add_task(f"Transcribing {input_path.name}...")
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except FileNotFoundError:
            console.print("[error]Error:[/error] whisper not found.")
            console.print("Install: [bold]pip install openai-whisper[/bold]")
            exit(1)
        except subprocess.CalledProcessError as e:
            console.print(f"[error]Error:[/error] Whisper failed")
            if e.stderr:
                console.print(e.stderr.decode())
            exit(1)

    caption_file = input_path.parent / f"{input_path.stem}.{output_format}"
    console.print(f"[success]✓ Saved:[/success] {caption_file.relative_to(REPO)}")
    return caption_file


parser = argparse.ArgumentParser(
    description="Generate captions from audio/video using OpenAI Whisper (free)."
)
parser.add_argument("--audio", help="Path to audio file (WAV/MP3). Takes priority over --slug.")
parser.add_argument(
    "--slug",
    help="File slug — looks for assets/audio/{slug}_voiceover.wav, then assets/video/edited/{slug}.mp4",
)
parser.add_argument("--format", default="srt", choices=["srt", "vtt", "txt"], help="Caption format")
args = parser.parse_args()

if args.audio:
    input_path = Path(args.audio)
    if not input_path.is_absolute():
        input_path = REPO / input_path
elif args.slug:
    audio_guess = AUDIO_DIR / f"{args.slug}_voiceover.wav"
    video_guess = VIDEO_DIR / f"{args.slug}.mp4"
    if audio_guess.exists():
        input_path = audio_guess
    elif video_guess.exists():
        input_path = video_guess
    else:
        console.print(f"[error]Error:[/error] No file found for slug '[bold]{args.slug}[/bold]'")
        console.print(f"  Tried: {audio_guess.relative_to(REPO)}")
        console.print(f"  Tried: {video_guess.relative_to(REPO)}")
        available = sorted(list(AUDIO_DIR.glob("*.wav")) + list(AUDIO_DIR.glob("*.mp3")))
        if available:
            console.print("\n[info]Available audio files:[/info]")
            for f in available:
                console.print(f"  {f.name}")
        exit(1)
else:
    parser.error("Provide [bold]--audio <path>[/bold] or [bold]--slug <slug>[/bold]")

if not input_path.exists():
    console.print(f"[error]Error:[/error] File not found: {input_path}")
    exit(1)

console.print(f"[info]Input:[/info]  {input_path.relative_to(REPO)}")
console.print(f"[info]Format:[/info] {args.format.upper()}")
console.print()

generate_captions(input_path, args.format)
