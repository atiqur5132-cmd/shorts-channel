"""Build a HyperFrames captions sub-composition from a transcript.json.

Usage: py -I make_captions.py <transcript.json> <out.html> [--fix "is an=isn't"] ...
Groups 1-3 words, breaking on punctuation and pauses; key money words get colour.
"""
import json
import re
import sys

KEY_GREEN = {"legal", "buy", "stocks", "value", "grow", "growth", "own", "assets", "loan"}
KEY_GOLD = {"billionaires", "borrow", "propublica", "25", "richest", "3.4%", "earn", "paycheck", "america", "heirs", "interest", "income"}
KEY_RED = {"tax", "tax.", "taxed", "die", "never", "no", "isn't"}

MAX_WORDS = 3
PAUSE = 0.15


def clean(t):
    return re.sub(r"[^\w%.'$]", "", t).strip(".").lower() or t.lower()


def main():
    src, out = sys.argv[1], sys.argv[2]
    fixes = []
    args = sys.argv[3:]
    for i, a in enumerate(args):
        if a == "--fix":
            pat, rep = args[i + 1].split("=")
            fixes.append((pat.split(" "), rep))
        elif a in ("--green", "--gold", "--red"):
            target = {"--green": KEY_GREEN, "--gold": KEY_GOLD, "--red": KEY_RED}[a]
            target.update(w.strip().lower() for w in args[i + 1].split(",") if w.strip())

    words = json.load(open(src, encoding="utf-8"))
    words = words["words"] if isinstance(words, dict) else words
    # merge mis-heard multi-token words, e.g. "is an" -> "isn't"
    merged = []
    i = 0
    while i < len(words):
        hit = None
        for pat, rep in fixes:
            seg = words[i:i + len(pat)]
            if len(seg) == len(pat) and [clean(w["text"]) for w in seg] == [p.lower() for p in pat]:
                hit = (len(pat), rep)
                break
        if hit:
            n, rep = hit
            seg = words[i:i + n]
            punct = re.sub(r"[\w'%.$]+", "", seg[-1]["text"])
            merged.append({"text": rep + punct, "start": seg[0]["start"], "end": seg[-1]["end"]})
            i += n
        else:
            merged.append(words[i])
            i += 1

    groups, cur = [], []
    for k, w in enumerate(merged):
        cur.append(w)
        nxt = merged[k + 1] if k + 1 < len(merged) else None
        brk = (
            len(cur) >= MAX_WORDS
            or re.search(r"[,?!:]$|[^\d]\.$|%\.$", w["text"])
            or (nxt and nxt["start"] - w["end"] >= PAUSE)
            or nxt is None
        )
        if brk:
            groups.append(cur)
            cur = []

    html_groups, js = [], []
    for gi, g in enumerate(groups):
        start = max(0.1, g[0]["start"] - 0.05)
        end = groups[gi + 1][0]["start"] - 0.02 if gi + 1 < len(groups) else g[-1]["end"] + 0.6
        spans = []
        for wi, w in enumerate(g):
            word = re.sub(r"[,.:;!?]+$", "", w["text"]) if not re.search(r"\d\.\d", w["text"]) else w["text"].rstrip(".")
            c = clean(w["text"])
            cls = "cw"
            if c in KEY_RED:
                cls += " k-red"
            elif c in KEY_GOLD:
                cls += " k-gold"
            elif c in KEY_GREEN:
                cls += " k-green"
            wid = f"cap-{gi}-{wi}"
            spans.append(f'<span id="{wid}" class="{cls}">{word.upper()}</span>')
            js.append(f'tl.fromTo("#{wid}", {{ scale: 0.6, opacity: 0.35 }}, {{ scale: 1, opacity: 1, duration: 0.12, ease: "back.out(3)" }}, {w["start"]:.2f});')
        gid = f"cap-{gi}"
        dur = end - start
        html_groups.append(
            f'<div id="{gid}" class="cap clip" data-start="{start:.2f}" data-duration="{dur:.2f}">{" ".join(spans)}</div>'
        )
        js.append(f'tl.fromTo("#{gid}", {{ y: 26, scale: 0.92 }}, {{ y: 0, scale: 1, duration: 0.14, ease: "power3.out" }}, {start:.2f});')

    total = groups[-1][-1]["end"] + 0.6
    page = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .cap {{
      position: absolute; left: 0; width: 100%; top: 1150px; text-align: center;
      font-family: "Montserrat", sans-serif; font-weight: 900; font-size: 92px; line-height: 1.1;
      color: #ffffff; overflow: visible;
    }}
    .cw {{
      display: inline-block; margin: 0 10px;
      -webkit-text-stroke: 14px #000000; paint-order: stroke fill;
      text-shadow: 0 8px 0 rgba(0, 0, 0, 0.9), 0 0 30px rgba(0, 0, 0, 0.6);
    }}
    .k-green {{ color: #2be07a; }}
    .k-gold {{ color: #ffc83d; }}
    .k-red {{ color: #ff4a4a; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    {chr(10).join("    " + h for h in html_groups).strip()}
  </div>
  <script>
    // shrink any group that would overflow the 900px safe width
    document.querySelectorAll("#root .cap").forEach((el) => {{
      const fit = window.__hyperframes && window.__hyperframes.fitTextFontSize;
      if (fit) {{
        const r = fit(el.textContent, {{ fontFamily: "Montserrat", fontWeight: 900, maxWidth: 860, baseSize: 92, minSize: 56 }});
        if (r && r.fontSize) el.style.fontSize = r.fontSize + "px";
      }}
    }});
    const tl = gsap.timeline({{ paused: true }});
    {(chr(10) + "    ").join(js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
    open(out, "w", encoding="utf-8").write(page)
    print(f"{len(groups)} groups, ends {total:.2f}s -> {out}")


if __name__ == "__main__":
    main()
