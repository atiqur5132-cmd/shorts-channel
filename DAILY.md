# Daily short: runbook

One finance short per day for **The Rich Rules** (@TheRichRulesShorts). The look is fixed (see `pilot-01/SPEC.md`);
`tools/` builds everything from a `brief.json`. Nothing is published without the owner's OK.

## 1. Topic + research (about 10 min)
- Take the next unused idea from `TOPICS.md` (or a fresh, timely one). Never repeat a topic.
- Verify every number from 2 reliable sources (official data, a major outlet, or a well-known book). Note the sources in the brief.
- No financial advice, no "buy X" calls, no claims we can't source. Education only.

## 2. Brief
Create `shorts/NN-slug/brief.json` (copy the shape of `shorts/02-buffett-time/brief.json`):
- `script`: 80–100 words (30–45 s at 1.1x). Line 1 is the hook (a surprising claim). End on a line that loops or lands a lesson.
- Write numbers as words in the script ("eighty-one point five"); the transcript turns them back into digits.
- `title` ≤ 60 chars + `#shorts`; `description`: 1–2 lines + `Source: ...`; `tags`: 6–10.

## 3. Voice
`py -I tools/voice.py shorts/NN-slug`. Then print the words with their times and pick a **plain-word cue** for each shot.
Cues are never numbers.

## 4. Photos
- `py -I tools/images.py search shorts/NN-slug "<query>"`, then look at `work/sheet-*.jpg`.
- Use `--mode full` only for images labelled **FULL** (Wikimedia, ≥1900 px); use `--mode card` for everything else.
  Set `--cx` so the subject is in frame. Use `--grade mono` for death/loss beats.
- You can reuse photos from `pilot-01/assets/img` or older shorts (copy them, fills included).

## 5. Shots + build
- Write 7–9 shots in `brief.json` (types: photo, title, card, paper, bignum, chart; see the docstring in `tools/build_short.py`).
  Vary them: never two of the same type in a row; one stamp per 2–3 shots; one title (hard-cut word) max.
- `py -I tools/build_short.py shorts/NN-slug`, then `npx -y hyperframes@0.8.208 check` inside the folder: 0 errors.
- `npx -y hyperframes@0.8.208 snapshot --at <middle of each shot>` and LOOK: text overlaps, stamps off-screen,
  low contrast (add `"dark": true` to a photo shot). Fix the brief and rebuild.

## 6. Render
`bash tools/render_cloud.sh shorts/NN-slug "Add short NN (<topic>)"` → `renders/final.mp4` and `renders/phone.mp4`.
Check the duration and the loudness (about -14 LUFS).

## 7. Approval
Send `renders/phone.mp4` to the owner with the title, description and tags. **Wait for an explicit yes.**

## 8. Upload (only after the yes)
The Chrome extension can't put files over 10 MB into an upload box, so the **owner picks the file**:
1. Copy `renders/final.mp4` to `C:\Users\atiqu\Desktop\youtube ch\UPLOAD\NN-slug.mp4`.
2. Through Claude in Chrome (launch Chrome with `Start-Process chrome.exe` if needed) open
   `https://studio.youtube.com/channel/UCTK8SpirJ81YVH-Jw8gb34Q/videos/upload?d=ud`, then ask the owner to click
   "Select files", choose that file, and say "ho gaya".
3. Title; the description goes above the default footer (ctrl+Home, type, then 2 Enters); "No, it's not made for kids";
   Show advanced settings → AI use: **No** (narrated explainer: no real person faked, no real footage altered,
   no fake realistic scene, no AI music); add video-specific tags.
4. Next ×3 → Visibility **Public**. **Wait until the footer says "Checks complete. No issues found."**, then Publish.
   If the checks find a problem, don't publish: tell the owner.
5. Add the URL and date to `TOPICS.md` under "Published", then commit and push.
