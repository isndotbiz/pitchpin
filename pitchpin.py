#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyworld", "soundfile", "numpy<2", "setuptools<80"]
# ///
"""
pitchpin — open-source, scriptable pitch correction.

Pins a monophonic vocal (or any single-voice audio) to a musical scale while
keeping the formants and timing intact — the "transparent correction" you'd
otherwise reach for a paid tool to do. Clean-room: built entirely on the
open-source WORLD vocoder (BSD) + public DSP. No proprietary code, no
decompilation, no patents touched (monophonic only — polyphonic note access is
patented elsewhere and deliberately out of scope).

How it works:
  1. WORLD analysis  -> F0 (pitch), spectral envelope (formants), aperiodicity
  2. snap each voiced F0 to the nearest note allowed by the chosen key/scale
     (blended by --strength, so you can dial natural .. hard)
  3. WORLD resynthesis with the corrected F0 but the ORIGINAL envelope + timing

Usage:
  uv run pitchpin.py in.wav out.wav --key A --scale minor
  uv run pitchpin.py in.wav out.wav                 # chromatic (nearest semitone)
  uv run pitchpin.py in.wav out.wav --key C --scale major --strength 0.6
  uv run pitchpin.py in.wav out.wav --fast           # quicker F0 (dio), lower accuracy

Input/output: WAV/FLAC/OGG (anything libsndfile reads). Stereo is downmixed to
mono (a single voice is the use case); output is mono at the source samplerate.
"""
import argparse, sys
import numpy as np
import soundfile as sf

NOTE_IX = {"C":0,"C#":1,"DB":1,"D":2,"D#":3,"EB":3,"E":4,"F":5,"F#":6,"GB":6,
           "G":7,"G#":8,"AB":8,"A":9,"A#":10,"BB":10,"B":11}
SCALE = {"minor":{0,2,3,5,7,8,10}, "major":{0,2,4,5,7,9,11},
         "chromatic":set(range(12)),
         "minor_pentatonic":{0,3,5,7,10}, "major_pentatonic":{0,2,4,7,9}}
A4 = 440.0

def allowed_classes(key, scale):
    if not key or scale == "chromatic":
        return set(range(12))
    if key.upper() not in NOTE_IX:
        sys.exit(f"unknown key '{key}' (use C, C#, D, ... or Db/Eb spellings)")
    if scale not in SCALE:
        sys.exit(f"unknown scale '{scale}' (one of: {', '.join(SCALE)})")
    root = NOTE_IX[key.upper()]
    return {(root + i) % 12 for i in SCALE[scale]}

def snap_f0(f0, allowed, strength):
    out = np.empty_like(f0)
    for i, hz in enumerate(f0):
        if hz <= 0:
            out[i] = 0.0; continue
        m = 69 + 12 * np.log2(hz / A4); base = int(round(m))
        cands = [base + d for d in range(-3, 4) if ((base + d) - 69) % 12 in allowed]
        if not cands:
            out[i] = hz; continue
        target = min(cands, key=lambda c: abs(c - m))
        blended = m * (1 - strength) + target * strength
        out[i] = A4 * 2 ** ((blended - 69) / 12)
    return out

def main():
    ap = argparse.ArgumentParser(description="pitchpin — open-source pitch correction (WORLD).")
    ap.add_argument("input"); ap.add_argument("output")
    ap.add_argument("--key", default=None, help="root note, e.g. A, C#, Eb (omit = chromatic)")
    ap.add_argument("--scale", default="minor", help="minor|major|chromatic|minor_pentatonic|major_pentatonic")
    ap.add_argument("--strength", type=float, default=1.0, help="0=off .. 1=full correction (default 1)")
    ap.add_argument("--fast", action="store_true", help="use dio+stonemask (faster, less accurate) instead of harvest")
    a = ap.parse_args()
    import pyworld as pw

    y, sr = sf.read(a.input)
    if y.ndim > 1:
        y = y.mean(axis=1)
    x = np.ascontiguousarray(y.astype(np.float64))

    if a.fast:
        f0, t = pw.dio(x, sr); f0 = pw.stonemask(x, f0, t, sr)
    else:
        f0, t = pw.harvest(x, sr)
    sp = pw.cheaptrick(x, f0, t, sr)
    ap_ = pw.d4c(x, f0, t, sr)

    allowed = allowed_classes(a.key, a.scale)
    f0c = snap_f0(f0, allowed, a.strength)

    voiced = f0 > 0
    moved = np.abs(1200 * np.log2(np.where(voiced, f0c / np.maximum(f0, 1e-9), 1)))[voiced]
    out = pw.synthesize(f0c, sp, ap_, sr).astype(np.float32)
    sf.write(a.output, out, sr)
    print(f"pitchpin: {int(voiced.sum())} voiced frames | key={a.key or 'chromatic'} "
          f"{a.scale if a.key else ''} | strength={a.strength} | "
          f"median correction {np.median(moved) if moved.size else 0:.0f} cents -> {a.output}")

if __name__ == "__main__":
    main()
