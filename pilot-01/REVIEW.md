# REVIEW: Pilot 01 v2

## What changed from v1, and why
- **Sound:** removed the ffmpeg-synthesized bed (its constant 220 Hz buzz was what irritated the user). It is replaced by a real
  CC0 hip-hop loop, "Tunnel Vision" by AudioWay, at 0.09 volume (about 16 dB under the voice). It drops out under
  "Step three. Die." and comes back on the heirs. Effects went from 27 to 12, each tied to a visible stamp, slam or whip;
  the synthesized error and typing sounds were removed.
- **Look:** v1 was text on a dark grid void, which the guide bans by default. v2 is a documentary photo collage: real
  CC0 photos on every frame, paper documents as objects (loan agreement, price tag, newspaper clipping, paystub),
  rubber stamps and frame shakes.
- **Low-res photos** (1024 px) are shown as tilted cards over a blurred copy of the same photo, never stretched full-bleed.

## Measured vs looked at
- `hyperframes check`: 0 errors and 0 warnings (only info-level overlap notes on deliberate collages).
- I looked at frames from all 8 scenes (27 instants plus 2 dense ranges). The sound was **measured, not heard**.
- I found and fixed a bug: `data-motion-blur="on"` dropped captions and cards on frames with rotating cards, so motion blur is OFF.

## Weakest shots and what I'd do with more time
- 20.5–22.2 (graveyard): the mono-fade grade reads as overcast daylight rather than eerie. A real night cemetery photo would be stronger.
- 6.7–10.3 (trading laptop card): the background blur is very dark and the frame is a bit empty under the card.
- The rate scene (28.9–35.6) is all graphics over a blurred city. A real photo of the IRS building would ground it.

## Kept on purpose
- The stamps overlap their paper or photo (that is what a stamp is). They carry `data-layout-allow-overlap` where check flagged them.
- The paystub numbers are illustrative and labelled EXAMPLE on screen.
