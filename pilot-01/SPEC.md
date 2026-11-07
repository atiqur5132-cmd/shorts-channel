# SPEC: Pilot 01 v2, "Buy, Borrow, Die"

GOAL:    The viewer understands the 3-step strategy in 45 s and feels "wait, that's legal?!". They rewatch or follow.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps
TIME:    45.4 s x 30 = 1362 frames. The voice (am_michael, 1.1x) is the clock. Music: "Tunnel Vision" (AudioWay, CC0), about 107 bpm.

LOOK:    Medium = documentary photo collage. The ground is always a real photograph, never a void.
         - Full-bleed photos (hi-res Wikimedia) get the deep-contrast grade, a 22% vignette and 5% grain.
         - Low-res photos (1024 px) are never stretched full-bleed. They become a CARD: rounded 26 px corners,
           a 6 px #F4F1EA border, a hard shadow of 0 34px 60px rgba(0,0,0,.55), rotated -3..+3 deg,
           over a baked blurred and darkened copy of the same photo (gaussian sigma 28, brightness -0.28).
         - Paper objects (loan agreement, paystub, cost-basis tag, newspaper clipping) are #F4F1EA paper
           with ink #141414, set in IBM Plex Mono 500/700 because they are printed documents.
         - Ink #FFFFFF for type over photos, with a hard shadow of 0 6px 0 rgba(0,0,0,.85) and no glow.
         - Accents, one per shot: money green #35E07A (gain / buy), gold #FFC940 (numbers, borrow, own),
           tax red #FF3B30 (tax, die, stamps).
         - Display face League Gothic (sizes 200-520 px, tracking 0). Kicker and labels in Montserrat 900.
         - Captions: Montserrat 900, 92 px, white with a 14 px black stroke, top 1150 px, key words coloured.
OBJECTS: a loan agreement (paper, dotted leaders, an APPROVED rubber stamp); a paystub (paper, line items,
         red deductions); a price tag with a string hole (cost basis); a newspaper clipping (torn edge);
         25 person icons (head and shoulders) in a 5x5 grid; two line charts (stocks vs interest).
MOTION:  arrivals expo.out / power4.out over 0.18-0.5 s; camera push power1.inOut; exits power3.in,
         40% shorter than arrivals. Stamps: scale 2.3 -> 1 with rotation, 0.16 s, then a 6-frame frame shake.
         Cards: from y+260 and rot 9 deg -> settle in 0.55 s expo.out. Photos: a slow push of 1.00 -> 1.07
         per shot (continuous motion on the ground, never on landed titles). Landed titles hold dead still.
SHOTS:   (global seconds)
  0.00-3.60  HOOK: skyscrapers at night, full-bleed. Frame 0 already reads "BILLIONAIRES / PAY ALMOST / NO TAX".
             "NO TAX" punches on "tax" (1.12). LEGAL stamp (green) at 2.95 with a pop.
  3.60-5.44  NAME: hard cuts on the words. Kicker "IT'S CALLED" over the dark skyline, then BUY (green, Wall St
             flags, 4.16, impact), BORROW (gold, cash stacks, 4.64, whoosh), DIE (red, graveyard, 5.04, impact).
  5.44-10.32 STEP 1 BUY: the Wall St flags shot continues, numeral "1" + BUY. 6.70: trading-laptop card rises,
             a "$1B -> $10B" counter climbs. 8.80: "NO SALE = NO TAX" stamp + pop.
  10.32-20.48 STEP 2 BORROW: cash stacks + "2 BORROW" (whip-in, whoosh). 11.60: vault card + loan agreement paper,
             APPROVED stamp at 13.2. 14.08: cash-fan full-bleed, "LOAN != INCOME"; 15.92 "INCOME TAX: $0" stamp +
             impact. 16.96: yacht and jet cards toss in. 18.60: chart, green STOCKS line outruns red INTEREST.
  20.48-28.88 STEP 3 DIE: dip to black, the graveyard fades up, "3 DIE" lands on "Die" (21.60); the music ducks.
             22.24: villa card + cost-basis tag "BOUGHT AT $1B" -> struck -> "NOW $10B" (25.6).
             26.56: gold bars full-bleed, "+$9B GROWTH"; 27.76 "NEVER TAXED" stamp + impact.
  28.88-35.60 RATE: blurred NYC night; a newspaper clipping "LEAKED IRS DATA" (whoosh). 30.3: 25 person icons.
             32.5: a giant 37% counts down to 3.4%, landing at 33.76 + pop. Label "TRUE TAX RATE".
  35.60-39.84 YOU: office-worker card, "MEANWHILE, YOU:"; a paystub rises; the deductions print red; WITHHELD stamp at 37.3.
  39.84-45.40 OUTRO: dark office full-bleed, "HOW MUCH YOU EARN" struck through on "earn" (42.0); a hard cut at 42.56
             to the Wall St flags (a callback to BUY), "WHAT YOU OWN" in gold + impact; held 2.8 s.
BANNED:  dark void grounds; glow, bloom, neon; grid backgrounds; floating dots; "STEP 01" small-caps labels;
         three cards in a row; synthesized music or tones; more than 12 sound effects; the same whoosh twice
         in a row; text drifting after it lands; white flash on every cut.
QA:      frames 0, 2.0, 3.2, 4.3, 4.8, 5.2, 7.5, 9.5, 12.8, 15.0, 16.3, 17.5, 19.6, 21.9, 24.0, 26.0, 28.2,
         30.0, 31.5, 34.5, 37.8, 41.8, 44.5: the photo reads as what it is, no text under 1150 px except
         captions, every number is correct, and nothing important sits in the top 168 px.
