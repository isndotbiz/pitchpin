# pitchpin

**Open-source, scriptable pitch correction.** Pin a monophonic vocal to a musical scale while keeping the **formants and timing intact** — the transparent "correct pitch" move you'd normally reach for a paid tool to do. No GUI required, no license, no nag, fully scriptable.

Built **clean-room** on the open-source [WORLD vocoder](https://github.com/mmorise/World) (BSD) and public DSP. No proprietary code was decompiled or reverse-engineered, and it is **monophonic only by design** — polyphonic note access is patented elsewhere and is deliberately out of scope.

## Why
Most open-source pitch tools are real-time autotune VSTs. `pitchpin` is the *offline, note-aware, command-line* kind — correct a whole take to a key in one call, drop it into a pipeline, batch a folder. It exports (unlike trial-locked tools), it's free, and it's MIT.

## Install & run
Requires [`uv`](https://docs.astral.sh/uv/) (handles all deps automatically — WORLD/pyworld, soundfile, numpy):

```bash
uv run pitchpin.py in.wav out.wav --key A --scale minor
```

Examples:
```bash
uv run pitchpin.py vocal.wav tuned.wav                       # chromatic (nearest semitone)
uv run pitchpin.py vocal.wav tuned.wav --key C --scale major
uv run pitchpin.py vocal.wav tuned.wav --key A --scale minor --strength 0.6   # natural, not hard
uv run pitchpin.py vocal.wav tuned.wav --fast                # quicker F0, lower accuracy
```

| flag | meaning |
|---|---|
| `--key` | root note (`A`, `C#`, `Eb`, …). Omit for chromatic. |
| `--scale` | `minor`, `major`, `chromatic`, `minor_pentatonic`, `major_pentatonic` |
| `--strength` | `0` = off … `1` = full correction (default `1`) |
| `--fast` | use `dio`+`stonemask` instead of `harvest` (faster, less accurate) |

**I/O:** WAV/FLAC/OGG (anything libsndfile reads). Stereo is downmixed to mono (single-voice use case); output is mono at the source samplerate.

## How it works
1. **Analyze** with WORLD → `F0` (pitch), spectral envelope (formants), aperiodicity.
2. **Snap** each voiced `F0` to the nearest note allowed by the chosen key/scale, blended by `--strength`.
3. **Resynthesize** with the corrected `F0` but the **original envelope + timing** — so it retunes without chipmunking or time-smearing.

## Scope & limitations
- **Monophonic** (one voice). Polyphonic separation is out of scope (and patent-encumbered).
- Offline/batch, not real-time.
- Heavy correction on a noisy/breathy take can artifact — lower `--strength` or clean the input first.

## Roadmap
- [ ] CREPE/torchcrepe F0 option for higher accuracy
- [ ] Stereo-preserving mode
- [ ] Per-note overrides (MIDI map) for hands-on editing
- [ ] Optional minimal GUI (note view)

## Credits & licenses
- [WORLD](https://github.com/mmorise/World) by Masanori Morise — BSD-3-Clause (the analysis/synthesis engine)
- [pyworld](https://github.com/JeremyCCHsu/Python-Wrapper-for-World-Vocoder) — MIT
- `pitchpin` itself: **MIT** (see `LICENSE`)

Not affiliated with or derived from any commercial pitch-correction product.
