"""Convert desktop MP3s to seamless loop files.

Strategy:
- Convert each MP3 to WAV via ffmpeg.
- Extract a ~16s middle section (where the groove/mood is usually most consistent).
- Crossfade head↔tail with a 2s equal-power fade to make it loop seamlessly.
- Save to core/static/core/audio/ and update the generator registry.

This gives us real musical content instead of synthesized noise, while keeping
browser playback smooth (hard-cut loop with crossfaded boundaries).
"""
import os
import shutil
import subprocess
import wave

import numpy as np

SR = 22050
DESKTOP = os.path.expanduser("~/Desktop")
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core", "static", "core", "audio"))
os.makedirs(OUT_DIR, exist_ok=True)

TRACKS = {
    "rain": "Colorful-Flowers(chosic.com).mp3",
    "lofi": "Daydreams-chosic.com_.mp3",
    "cafe": "Ghostrifter-Official-Purple-Dream(chosic.com).mp3",
}


def ffmpeg_mp3_to_wav(src, dst):
    subprocess.run(
        ["/opt/homebrew/bin/ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ar", str(SR), "-ac", "1", dst],
        check=True,
    )


def read_wav(path):
    with wave.open(path, "rb") as wf:
        n = wf.getnframes()
        raw = wf.readframes(n)
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return arr


def extract_section(sig, duration_seconds=16.0, fade_seconds=2.0):
    target = int(SR * duration_seconds)
    fade = int(SR * fade_seconds)
    # Take the middle-most section; if too short, pad with silence.
    start = max(0, (len(sig) - target) // 2)
    end = start + target
    if end > len(sig):
        end = len(sig)
        start = max(0, end - target)
    section = sig[start:end].copy()
    if len(section) < target:
        pad = np.zeros(target, dtype=np.float32)
        pad[: len(section)] = section
        section = pad
    # Crossfade head/tail for seamless loop.
    head = section[:fade].copy()
    tail = section[-fade:].copy()
    fade_in = np.linspace(0.0, 1.0, fade)
    fade_out = np.linspace(1.0, 0.0, fade)
    section[:fade] = head * fade_in + tail * fade_out
    section[-fade:] = section[-fade:] * fade_out + head * fade_in
    return section


def write_wav(path, sig):
    pcm = np.clip(sig, -1.0, 1.0)
    pcm = (pcm * 32767 * 0.85).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def main():
    tmp = os.path.join(OUT_DIR, "_tmp_import.wav")
    written = []
    for name, mp3 in TRACKS.items():
        src = os.path.join(DESKTOP, mp3)
        if not os.path.exists(src):
            print(f"  SKIP {name}: {src} not found")
            continue
        ffmpeg_mp3_to_wav(src, tmp)
        sig = read_wav(tmp)
        loop = extract_section(sig, duration_seconds=16.0, fade_seconds=2.0)
        dst = os.path.join(OUT_DIR, f"{name}.wav")
        write_wav(dst, loop)
        size = os.path.getsize(dst)
        written.append((name, dst, size))
        print(f"  wrote {dst} ({size // 1024} KB)")
    if os.path.exists(tmp):
        os.remove(tmp)
    print(f"\nDone. Imported {len(written)} tracks from Desktop.")


if __name__ == "__main__":
    main()