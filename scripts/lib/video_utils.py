#!/usr/bin/env python3
"""Shared ffmpeg + whisper helpers for auto_edit and clip_shorts."""

import json
import re
import subprocess
from pathlib import Path
from typing import Optional


def probe_duration(path: Path) -> float:
    """Return media duration in seconds via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def run_ffmpeg(cmd: list, label: str = "") -> None:
    """Run ffmpeg, surface stderr tail on failure."""
    if label:
        print(f"  ffmpeg: {label}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        tail = res.stderr[-600:]
        raise RuntimeError(f"ffmpeg failed ({label}):\n{tail}")


def transcribe_whisper(media_path: Path, out_dir: Path, model: str = "base") -> dict:
    """Transcribe with whisper. Returns {srt: Path, json: Path, segments: list}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "whisper", str(media_path),
        "--language", "English",
        "--model", model,
        "--output_format", "all",
        "--output_dir", str(out_dir),
        "--word_timestamps", "True",
    ]
    print(f"  whisper transcribing ({model})...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"whisper failed:\n{res.stderr[-400:]}")

    stem = media_path.stem
    srt = out_dir / f"{stem}.srt"
    js = out_dir / f"{stem}.json"
    segments = []
    if js.exists():
        with open(js) as f:
            segments = json.load(f).get("segments", [])
    return {"srt": srt, "json": js, "segments": segments}


def parse_srt(srt_path: Path) -> list:
    """Parse SRT → list of {start, end, text}."""
    if not srt_path.exists():
        return []
    raw = srt_path.read_text()
    blocks = re.split(r"\n\n+", raw.strip())
    out = []
    for blk in blocks:
        lines = blk.strip().split("\n")
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+:\d+:\d+[,.]\d+)\s*-->\s*(\d+:\d+:\d+[,.]\d+)", lines[1])
        if not m:
            continue
        out.append({
            "start": _ts_to_sec(m.group(1)),
            "end": _ts_to_sec(m.group(2)),
            "text": " ".join(lines[2:]).strip(),
        })
    return out


def _ts_to_sec(ts: str) -> float:
    ts = ts.replace(",", ".")
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _sec_to_ts(sec: float) -> str:
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def slice_srt(srt_path: Path, start: float, end: float, out_path: Path) -> None:
    """Write SRT subset for [start,end], times rebased to 0."""
    cues = parse_srt(srt_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    idx = 1
    lines = []
    for c in cues:
        if c["end"] < start or c["start"] > end:
            continue
        s = max(c["start"], start) - start
        e = min(c["end"], end) - start
        lines.append(f"{idx}\n{_sec_to_ts(s)} --> {_sec_to_ts(e)}\n{c['text']}\n")
        idx += 1
    out_path.write_text("\n".join(lines))


def detect_silences(media_path: Path, noise_db: int = -30, min_dur: float = 0.6) -> list:
    """Return list of (start, end) silent regions via ffmpeg silencedetect."""
    cmd = [
        "ffmpeg", "-i", str(media_path), "-af",
        f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    stderr = res.stderr
    starts = [float(m.group(1)) for m in re.finditer(r"silence_start: ([\d.]+)", stderr)]
    ends = [float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)", stderr)]
    return list(zip(starts, ends))


CAPTION_STYLE_LANDSCAPE = (
    "FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,"
    "Alignment=2,MarginV=40,Bold=1"
)

CAPTION_STYLE_PORTRAIT = (
    "FontName=Arial,FontSize=22,PrimaryColour=&H0000FFFF,"
    "OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=2,"
    "Alignment=2,MarginV=300,MarginL=60,MarginR=60,Bold=1"
)


def burn_captions(video_in: Path, srt_in: Path, video_out: Path, style: str = CAPTION_STYLE_LANDSCAPE) -> None:
    """Burn subtitles into video."""
    srt_escaped = str(srt_in).replace(":", r"\:").replace("'", r"\'")
    vf = f"subtitles='{srt_escaped}':force_style='{style}'"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", vf,
        "-c:v", "h264_videotoolbox", "-c:a", "copy",
        str(video_out),
    ]
    run_ffmpeg(cmd, "burn captions")


def overlay_broll(main_video: Path, broll_clips: list, out_path: Path,
                  insertions: list) -> None:
    """Overlay broll segments over main video at given times.

    insertions: [{start: float, duration: float, broll_path: Path}]
    Picture-in-picture style: broll covers full frame, main audio continues.
    """
    if not insertions:
        # No broll → copy
        run_ffmpeg(["ffmpeg", "-y", "-i", str(main_video), "-c", "copy", str(out_path)], "passthrough")
        return

    inputs = ["-i", str(main_video)]
    for ins in insertions:
        inputs += ["-i", str(ins["broll_path"])]

    filters = []
    last = "[0:v]"
    for i, ins in enumerate(insertions, start=1):
        scaled = f"[b{i}]"
        filters.append(f"[{i}:v]scale=1920:1080,setpts=PTS-STARTPTS{scaled}")
        out_lbl = f"[v{i}]"
        filters.append(
            f"{last}{scaled}overlay=enable='between(t,{ins['start']},{ins['start']+ins['duration']})'{out_lbl}"
        )
        last = out_lbl

    filter_complex = ";".join(filters)
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", last, "-map", "0:a",
        "-c:v", "h264_videotoolbox", "-c:a", "aac",
        str(out_path),
    ]
    run_ffmpeg(cmd, f"overlay {len(insertions)} broll clips")


def crop_vertical(video_in: Path, video_out: Path, srt_in: Optional[Path] = None) -> None:
    """Crop landscape → 9:16 vertical (center crop), optional caption burn."""
    vf = "crop=ih*9/16:ih,scale=1080:1920"
    if srt_in and srt_in.exists():
        srt_escaped = str(srt_in).replace(":", r"\:").replace("'", r"\'")
        vf += f",subtitles='{srt_escaped}':force_style='{CAPTION_STYLE_PORTRAIT}'"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", vf,
        "-c:v", "h264_videotoolbox", "-c:a", "aac",
        str(video_out),
    ]
    run_ffmpeg(cmd, "crop vertical + captions")


def cut_segment(video_in: Path, start: float, end: float, out_path: Path) -> None:
    """Cut [start,end] from video (re-encode for frame accuracy)."""
    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
        "-c:v", "h264_videotoolbox", "-c:a", "aac",
        str(out_path),
    ]
    run_ffmpeg(cmd, f"cut {start:.1f}-{end:.1f}s")
