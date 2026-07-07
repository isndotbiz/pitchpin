# ISA — pitchpin

> Ideal State Artifact for `pitchpin`, an open-source, scriptable, command-line pitch-correction tool. Grounded in the repo's README.md and `pitchpin.py` (single-file uv script) as of commit `7301fb4`.

## Problem

Open-source pitch tools are almost all real-time autotune VST plugins that need a GUI/DAW and can't be scripted, batched, or dropped into a pipeline. The transparent "correct a whole take to a key" move — keeping formants and timing intact — usually means reaching for a paid, trial-locked, export-gated tool. There is no free, MIT, offline, note-aware, command-line option for that one job.

## Vision

A tiny, dependency-light CLI that pins a monophonic vocal to a chosen key/scale in one call — formants and timing preserved — so it can be batched over a folder or wired into an automated audio pipeline. Built clean-room on the open-source WORLD vocoder (BSD) and public DSP, monophonic-only by design (polyphonic note access is patent-encumbered and deliberately out of scope), and free to export with no nag.

## Goal

Keep `pitchpin.py` a correct, transparent, single-command pitch-correction tool: analyze a single-voice take with WORLD, snap each voiced F0 to the nearest note in the chosen key/scale blended by `--strength`, and resynthesize with the original spectral envelope and timing — verifiably running end-to-end via `uv run pitchpin.py`.

## Criteria

- [ ] `python3 -m py_compile pitchpin.py` passes (no syntax errors).
- [ ] `uv run pitchpin.py in.wav out.wav --key A --scale minor` produces a mono output at the source samplerate and prints the voiced-frames / correction summary line.
- [ ] Every CLI flag documented in README.md (`--key`, `--scale`, `--strength`, `--fast`) maps to real, working argparse behavior.
- [ ] Unknown `--key` / `--scale` values exit with a clear error message (not a traceback).
- [ ] Correction stays transparent: original spectral envelope (`sp`) and aperiodicity (`ap`) are preserved; only F0 is modified (no chipmunking or time-smear).
- [ ] Stays clean-room and monophonic-only — no proprietary/decompiled code, no polyphonic note-access path.

## Constraints

- **Single-file design.** The whole tool is `pitchpin.py` with inline uv script metadata (PEP 723 `# /// script` block declaring `pyworld`, `soundfile`, `numpy<2`, `setuptools<80`). Keep deps minimal and pinned there; don't fragment into a package without reason.
- **Python (not TypeScript) by ecosystem necessity** — WORLD vocoder access is via `pyworld`; this is a justified Python project.
- **Run via `uv`** (`/opt/homebrew/bin/uv` present), not `pip install` into a global env.
- **Off-limits / do not touch:** `LICENSE` (MIT), `.git/`, any user audio files (`*.wav`, `*.flac` — git-ignored), `.venv/`, `__pycache__/`. Never `git push` to `origin` (https://github.com/isndotbiz/pitchpin.git) or publish releases without explicit approval — it is a public repo.
- **Clean-room invariant is legal, not just stylistic:** no proprietary pitch-correction code may be referenced, decompiled, or reverse-engineered; polyphonic separation must stay out of scope.

## Out of Scope

- Polyphonic / multi-voice note access and separation (patent-encumbered, deliberately excluded).
- Real-time / live autotune (this is offline/batch only).
- GUI of any kind (roadmap lists an *optional* minimal note view, but the tool is CLI-first).
- Stereo-preserving output (currently downmixes to mono; a roadmap item, not current behavior).
- CREPE/torchcrepe F0 backends and per-note MIDI overrides (roadmap, not yet built).
