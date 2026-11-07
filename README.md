# Shorts channel: money & finance

An automated pipeline for YouTube Shorts: the script, the voiceover (Kokoro `am_michael`), captions, visuals
and edit, all rendered with [HyperFrames](https://hyperframes.heygen.com).

## Layout
- `pilot-01/`: "Buy, Borrow, Die", the first short and the master template. See its `SPEC.md`, `REVIEW.md` and `CREDITS.md`.
- `tools/common.css`, `tools/common.js`: the shared look and motion helpers. Run `py tools/inject_common.py <project>` to inject them into the scene files.
- `tools/make_captions.py`: builds word-by-word captions from a transcript.
- `voice-samples/`: the free male TTS voices we compared.

## Render in the cloud (GitHub Actions)
Go to Actions → **Render short** → *Run workflow*, and enter the project folder (e.g. `pilot-01`). Or from a terminal:

```bash
gh workflow run render.yml -f project=pilot-01 -f quality=delivery
```

When the run finishes, download `final.mp4` from the run's **Artifacts** section. It is normalised to -14 LUFS for Shorts.

## Licenses
All photos and music are CC0 or public domain (see each project's `CREDITS.md`).
