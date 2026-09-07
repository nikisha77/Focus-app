"""Generate high-quality CC0 ambient loops from scratch.

Note: This script is currently NOT the primary audio source.
The primary source is `scripts/import_desktop_audio.py`, which imports
3 desktop MP3s, extracts 16s loopable sections with crossfade, and saves
them to core/static/core/audio/.

Use this generator only if you want to fall back to 100% synthesized CC0 audio.

Key improvements over the first pass:
- Heavy low-pass filtering so high frequencies are warm, not piercing
- Rain is dense, sustained pink-noise filtered to a soft hiss (no point transients)
- Lofi uses a proper chord progression with a low-passed Rhodes-like sine layer
  and a very soft brushed-snare-like pulse on the 2 and 4
- Cafe is brown noise filtered to "room tone" with sparse, low-volume chatter shimmer
- White noise is gently high-cut so it doesn't fatigue
- Fireplace is brown noise with sparse soft crackles (low-passed, low amplitude)
- All loops are exactly crossfade-loopable (head/tail summed)
"""
import os
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt

SR = 22050
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core", "static", "core", "audio"))
os.makedirs(OUT_DIR, exist_ok=True)


def write_wav(name, signal):
    path = os.path.join(OUT_DIR, f"{name}.wav")
    sig = np.clip(signal, -1.0, 1.0)
    pcm = (sig * 32767 * 0.85).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return path


def to_ogg(wav_path):
    # OGG conversion is best-effort and optional. WAV plays natively in all
    # browsers, so we always keep the WAV. This avoids hard dependency on
    # ffmpeg/libvorbis (e.g. on CI without the full ffmpeg build).
    try:
        subprocess.run(
            ["/opt/homebrew/bin/ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except Exception:
        return wav_path
    ogg_path = wav_path.replace(".wav", ".ogg")
    try:
        subprocess.run(
            [
                "/opt/homebrew/bin/ffmpeg", "-y", "-loglevel", "error",
                "-i", wav_path, "-c:a", "libvorbis", "-q:a", "3", ogg_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.remove(wav_path)
        return ogg_path
    except Exception:
        return wav_path


def _which(cmd):
    from shutil import which
    return which(cmd) is not None


def lowpass(sig, cutoff_hz, order=4):
    sos = butter(order, cutoff_hz / (SR / 2), btype="low", output="sos")
    return sosfiltfilt(sos, sig)


def highpass(sig, cutoff_hz, order=4):
    sos = butter(order, cutoff_hz / (SR / 2), btype="high", output="sos")
    return sosfiltfilt(sos, sig)


def normalize(sig, peak=0.9):
    m = np.max(np.abs(sig))
    if m < 1e-6:
        return sig
    return sig / m * peak


def crossfade_loop(signal, fade_seconds=2.0):
    n = int(fade_seconds * SR)
    if n * 2 >= len(signal):
        n = len(signal) // 4
    fade_in = np.linspace(0.0, 1.0, n)
    fade_out = np.linspace(1.0, 0.0, n)
    sig = signal.copy()
    sig[:n] = sig[:n] * fade_in + signal[-n:] * fade_out
    sig[-n:] = sig[-n:] * fade_out + signal[:n] * fade_in
    return sig


def gen_white_noise(duration=10.0, gain=0.18, cutoff=6000):
    raw = np.random.normal(0, 1, int(SR * duration))
    return lowpass(raw, cutoff) * gain


def gen_pink_noise_via_voss(duration=10.0, gain=0.25):
    """Voss-McCartney pink noise — much smoother than filtered white."""
    n = int(SR * duration)
    rows = 16
    buf = np.zeros(rows)
    out = np.zeros(n)
    for i in range(n):
        idx = 0
        k = i + 1
        while k & 1 and idx < rows - 1:
            idx += 1
            k >>= 1
        buf[idx] = np.random.normal(0, 1)
        out[i] = np.sum(buf) / rows
    out = out - np.mean(out)
    out = out / (np.max(np.abs(out)) + 1e-9)
    return lowpass(out, 8000) * gain


def gen_rain(duration=12.0, gain=0.20):
    """Soft sustained rain: layered filtered pink noise, no transients."""
    base = gen_pink_noise_via_voss(duration, gain=1.0)
    # Heavy low-pass to take the edge off.
    base = lowpass(base, 5500)
    # Add a quiet bed of slightly higher-frequency hisssss.
    high = lowpass(np.random.normal(0, 1, len(base)), 9000)
    mix = base * 0.85 + high * 0.20
    # Very subtle amplitude modulation to suggest gusts.
    t = np.linspace(0, duration, len(mix), endpoint=False)
    gust = 1.0 + 0.06 * np.sin(2 * np.pi * 0.13 * t) + 0.04 * np.sin(2 * np.pi * 0.27 * t + 1.3)
    return normalize(mix * gust) * gain


def gen_fire(duration=12.0, gain=0.22):
    """Warm fire bed: brown-noise-like rumble with soft low crackles."""
    n = int(SR * duration)
    # Long-correlated noise = brown-ish via integration of white.
    white = np.random.normal(0, 1, n)
    brown = np.cumsum(white)
    brown = brown - np.mean(brown)
    brown = brown / np.max(np.abs(brown))
    bed = lowpass(brown, 1200) * 0.9

    # Sparse soft crackles: short filtered bursts with sharp envelope.
    crackles = np.zeros(n)
    num = int(duration * 6)  # very sparse
    for _ in range(num):
        idx = np.random.randint(0, n - int(SR * 0.3))
        length = np.random.randint(int(SR * 0.05), int(SR * 0.18))
        env = np.exp(-np.linspace(0, 25, length))
        burst = np.random.normal(0, 1, length) * env * 0.18
        burst = lowpass(burst, 4000)
        crackles[idx:idx + length] += burst

    mix = bed + crackles
    return normalize(mix) * gain


def gen_cafe(duration=12.0, gain=0.20):
    """Cafe room tone: warm brown-noise bed + low, distant murmur shimmer."""
    n = int(SR * duration)
    white = np.random.normal(0, 1, n)
    brown = np.cumsum(white)
    brown = brown - np.mean(brown)
    brown = brown / np.max(np.abs(brown))
    bed = lowpass(brown, 900) * 0.95

    # Distant murmur: very low-passed pink noise.
    murmur = gen_pink_noise_via_voss(duration, gain=0.30)
    murmur = lowpass(murmur, 700)

    # Very sparse soft clinks (low volume, high-cut).
    clinks = np.zeros(n)
    for _ in range(np.random.randint(2, 5)):
        idx = np.random.randint(0, n - int(SR * 0.4))
        length = int(SR * 0.35)
        env = np.exp(-np.linspace(0, 8, length))
        tone = np.sin(2 * np.pi * np.random.uniform(1400, 2200) * np.linspace(0, 0.35, length))
        clinks[idx:idx + length] += tone * env * 0.06

    mix = bed * 0.55 + murmur * 0.40 + clinks
    return normalize(mix) * gain


def gen_lofi(duration=16.0, gain=0.18):
    """Slow chord progression with soft low-passed sine layer and brushed-pulse rhythm."""
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    # Chord progression in semitones from a root; smooth crossfades between chords.
    # Dm9 -> Cmaj7 -> Bbmaj7 -> Am9 — soft, jazzy.
    # Frequencies for Dm9 (D F A C E)
    chords = [
        [146.83, 174.61, 220.00, 261.63, 329.63],   # Dm9
        [130.81, 164.81, 196.00, 246.94, 293.66],   # Cmaj7
        [116.54, 146.83, 174.61, 220.00, 261.63],   # Bbmaj7 (approx)
    ]
    pad = np.zeros(n)
    chord_dur = duration / len(chords)
    for ci, freqs in enumerate(chords):
        start = int(ci * chord_dur * SR)
        end = int((ci + 1) * chord_dur * SR)
        seg_t = t[start:end] - t[start]
        L = end - start
        seg = np.zeros(L)
        for f in freqs:
            seg += np.sin(2 * np.pi * f * seg_t) * 0.18
            seg += np.sin(2 * np.pi * (f * 1.005) * seg_t) * 0.10  # gentle detune
            seg += np.sin(2 * np.pi * (f * 2.0) * seg_t) * 0.04   # soft harmonic
        pad[start:end] = seg
    pad = lowpass(pad, 1400)

    # Soft brushed-snare-like pulses on beats 2 and 4 of an 8th-note grid.
    bpm = 70
    beat_samples = int(SR * 60 / bpm / 2)  # 8th notes
    rhythm = np.zeros(n)
    step = 0
    pos = 0
    while pos < n:
        if step % 4 in (1, 3):
            env_len = min(int(SR * 0.10), n - pos)
            env = np.exp(-np.linspace(0, 22, env_len))
            noise = np.random.normal(0, 1, env_len)
            rhythm[pos:pos + env_len] += lowpass(noise, 2500) * env * 0.20
        step += 1
        pos += beat_samples

    # Subtle vinyl crackle (very low amplitude, high-passed).
    crackle = highpass(np.random.normal(0, 1, n), 3000) * 0.015

    mix = pad * 0.65 + rhythm + crackle
    return normalize(mix) * gain


def main():
    np.random.seed(42)
    generators = {
        "rain": gen_rain,
        "lofi": gen_lofi,
        "cafe": gen_cafe,
    }
    out_files = []
    for name, fn in generators.items():
        sig = fn()
        sig = crossfade_loop(sig, fade_seconds=2.0)
        wav = write_wav(name, sig)
        out = to_ogg(wav)
        size = os.path.getsize(out)
        out_files.append(out)
        print(f"  wrote {out} ({size//1024} KB)")
    print("\nDone.")


if __name__ == "__main__":
    main()