"""Generate a HyperFrames short from <short-dir>/brief.json + assets (voice, transcript, images).

  py -I tools/build_short.py <short-dir>

brief.json
{
  "slug": "02-...", "title": "...", "description": "...", "tags": [...],
  "script": ["line", ...],                       # voiceover (tools/voice.py reads it)
  "music": "tunnel-vision.mp3",                  # from library/bgm
  "captions": {"green": [], "gold": [], "red": [], "fix": ["is an=isn't"]},
  "shots": [ {"type": ..., "cue": "<first word of the shot>", ...}, ... ]
}
Shot types (every shot runs from its cue word until the next shot's cue):
  photo  : img (full-bleed), kicker?, headline?, stamp?, counter?
  title  : img (full-bleed), word, color (g|y|r)       -> one huge word, hard cut
  card   : img (card + "<img>-fill"), kicker?, headline?, stamp?, counter?
  paper  : fill, card?, title, rows [[k, v], ...], stamp?, minus? (row indexes printed red)
  bignum : fill, kicker, from, to, decimals, prefix?, suffix?, land (cue word), label?, source?
  chart  : fill, kicker, up ("STOCKS"), flat ("INTEREST")
stamp   = {"text", "color": g|y|r, "cue"}      counter = {"from","to","decimals","prefix","suffix","cue","color"}
Headline markup: [g]..[/g] [y]..[/y] [r]..[/r] colours, "\\n" for a line break.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COMMON_CSS = open(os.path.join(HERE, "common.css"), encoding="utf-8").read()
COMMON_JS = open(os.path.join(HERE, "common.js"), encoding="utf-8").read()
COLORS = {"g": "#35e07a", "y": "#ffc940", "r": "#ff3b30", "w": "#ffffff"}
SFX = {"impact-bass-1": (2.116, 0.073, 0.15), "impact-bass-2": (2.592, 1.986, 0.13),
       "whoosh": (0.575, 0.162, 0.4), "whoosh-short": (0.575, 0.162, 0.4), "pop": (0.72, 0.12, 0.9)}


def norm(w):
    return re.sub(r"[^\w%$.']", "", w.lower()).strip(".").replace("’", "'")


def markup(text):
    t = html.escape(text).replace("\\n", "<br />").replace("\n", "<br />")
    return re.sub(r"\[(g|y|r)\](.*?)\[/\1\]", r'<span class="\1">\2</span>', t)


def plain_len(text):
    t = re.sub(r"\[/?[gyr]\]", "", text).replace("\\n", "\n")
    return max(len(x) for x in t.split("\n")), t.count("\n") + 1


def hsize(text, given=None, maxw=940, cap=330):
    if given:
        return given
    L, _ = plain_len(text)
    return int(min(cap, maxw / (0.43 * max(L, 1))))


class Cues:
    def __init__(self, words):
        self.w = words
        self.n = [norm(x["text"]) for x in words]

    def find(self, cue, start=0, end=None):
        cue_n = norm(cue)
        end = len(self.w) if end is None else end
        for i in range(start, end):
            if self.n[i] == cue_n or self.n[i].startswith(cue_n) and len(cue_n) >= 4:
                return i
        raise SystemExit(f'cue "{cue}" not found after word {start} ("{self.w[min(start, len(self.w)-1)]["text"]}")')


def esc_js(s):
    return json.dumps(s)


def build(short):
    brief = json.load(open(os.path.join(short, "brief.json"), encoding="utf-8"))
    words = json.load(open(os.path.join(short, "assets", "transcript.json"), encoding="utf-8"))["words"]
    cues = Cues(words)
    total = round(words[-1]["end"] + 1.7, 2)

    # resolve shot start indexes
    shots = brief["shots"]
    idx = []
    pos = 0
    for k, s in enumerate(shots):
        i = 0 if k == 0 else cues.find(s["cue"], pos)
        idx.append(i)
        pos = i + 1
    starts = [0.0 if k == 0 else round(words[i]["start"] - 0.04, 2) for k, i in enumerate(idx)]
    ends = starts[1:] + [total]

    comp_dir = os.path.join(short, "compositions")
    if os.path.isdir(comp_dir):
        shutil.rmtree(comp_dir)
    os.makedirs(comp_dir)
    hits = []  # (time, kind, priority)
    hosts = []
    for k, s in enumerate(shots):
        sid = f"s{k + 1:02d}"
        t0, t1 = starts[k], ends[k]
        dur = round(t1 - t0, 2)
        wstart = idx[k]
        wend = idx[k + 1] if k + 1 < len(idx) else len(words)

        def local(cue, offset=0.0):
            i = cues.find(cue, wstart, wend)
            return round(words[i]["start"] - t0 + offset, 2)

        css, body, js, bg = [], [], [], []
        typ = s["type"]
        whip = (k % 3 == 2) and typ not in ("title",) and k > 0
        js.append(f'tl.set("#{sid}-rig", {{ x: 0, y: 0 }}, 0);')
        if whip:
            js.append(f'tl.fromTo("#{sid}-rig", {{ x: {1150 if k % 2 else -1150} }}, {{ x: 0, duration: 0.3, ease: "expo.out", immediateRender: false }}, 0);')
            hits.append((t0 - 0.06, "whoosh-short" if k % 2 else "whoosh", 1))

        def img_tag(name, cls_id, alt):
            return f'<img id="{sid}-{cls_id}" src="assets/img/{name}.jpg" alt="{html.escape(alt)}" />'

        def full_photo(name):
            bg.append(f'<div class="ph"><div id="{sid}-move" class="ph-move">{img_tag(name, "img", s.get("alt", name))}</div></div>')
            bg.append('<div class="scrim-top"></div><div class="vig"></div>' + ('<div class="scrim-top"></div>' if s.get("dark") else ""))
            a, b = (1.12, 1.0) if k % 2 == 0 else (1.02, 1.1)
            js.append(f'tl.fromTo("#{sid}-move", {{ scale: {a} }}, {{ scale: {b}, duration: {dur}, ease: "power2.out" }}, 0);')

        def fill(name):
            bg.append(f'<div class="fill">{img_tag(name + "-fill", "fill", "")}</div><div class="scrim-top"></div>')
            js.append(f'tl.fromTo("#{sid}-fill", {{ scale: 1.1 }}, {{ scale: 1.0, duration: {dur}, ease: "power1.out" }}, 0);')

        y = 220  # running top of the next block
        if s.get("kicker"):
            css.append(f"#{sid}-kick {{ top: {y}px; }}")
            body.append(f'<div id="{sid}-kick" class="kick">{markup(s["kicker"])}</div>')
            js.append(f'M.words(tl, "#{sid}-kick", 0.08, 0.07);')
            klen = len(re.sub(r"\[/?[gyr]\]", "", s["kicker"]))
            y += 66 * max(1, -(-klen // 23)) + 6  # Montserrat 900 58px: ~23 caps per line

        def headline(text, size=None, center=False, at=0.06):
            nonlocal y
            sz = hsize(text, size)
            _, lines = plain_len(text)
            al = "text-align:center; left:0; right:0;" if center else ""
            css.append(f"#{sid}-hl {{ top: {y}px; font-size: {sz}px; {al} }}")
            body.append(f'<div id="{sid}-hl" class="hl">{markup(text)}</div>')
            js.append(f'M.slam(tl, "#{sid}-hl", {at}, 1.5);')
            y += int(sz * 0.9 * lines) + 30

        def counter(c):
            nonlocal y
            sz = c.get("size", 230)
            col = COLORS[c.get("color", "g")]
            fmt = f'(v) => {esc_js(c.get("prefix", ""))} + v.toFixed({c.get("decimals", 0)}) + {esc_js(c.get("suffix", ""))}'
            first = f'{c.get("prefix", "")}{c["from"]:.{c.get("decimals", 0)}f}{c.get("suffix", "")}'
            css.append(f"#{sid}-count {{ top: {y}px; font-size: {sz}px; color: {col}; }}")
            body.append(f'<div id="{sid}-count" class="hl">{html.escape(first)}</div>')
            land = local(c["cue"]) if c.get("cue") else min(1.5, dur - 1.2)
            js.append(f'tl.fromTo("#{sid}-count", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, 0.12);')
            js.append(f'M.count(tl, "#{sid}-count", {max(0.2, land - 1.1)}, 1.1, {c["from"]}, {c["to"]}, {fmt});')
            hits.append((t0 + land + 0.02, "pop", 3))
            y += int(sz * 0.9) + 30

        def stamp(st, top, left=110):
            col = COLORS[st.get("color", "r")]
            at = local(st["cue"]) if st.get("cue") else max(0.3, dur * 0.45)
            at = round(max(0.4, min(at, dur - 1.55)), 2)  # leave time to read it
            rot = -6 if k % 2 else -4
            size = st.get("size") or min(78, int(840 / (0.70 * max(len(st["text"]), 1))))
            left = min(left, max(60, 1020 - int(len(st["text"]) * size * 0.70) - 90))
            css.append(f"#{sid}-stamp {{ left: {left}px; top: {top}px; color: {col}; font-size: {size}px; }}")
            body.append(f'<div id="{sid}-stamp" class="stamp" data-layout-allow-overlap>{html.escape(st["text"])}</div>')
            js.append(f'M.stamp(tl, "#{sid}-stamp", {at}, {rot});')
            js.append(f'M.shake(tl, "#{sid}-rig", {round(at + 0.16, 2)}, 14);')
            hits.append((t0 + at + 0.16, "impact", 0))

        if typ == "photo":
            full_photo(s["img"])
            if s.get("headline"):
                headline(s["headline"], s.get("hsize"))
            if s.get("counter"):
                counter(s["counter"])
            if s.get("stamp"):
                stamp(s["stamp"], s["stamp"].get("y", max(y + 40, 700)))
        elif typ == "title":
            full_photo(s["img"])
            col = s.get("color", "g")
            css.append(f"#{sid}-word {{ top: 470px; left: 0; right: 0; text-align: center; font-size: {s.get('size', 400)}px; }}")
            body.append(f'<div id="{sid}-word" class="hl {col}">{html.escape(s["word"])}</div>')
            js.append(f'tl.fromTo("#{sid}-word", {{ scale: 1.35 }}, {{ scale: 1, duration: 0.22, ease: "expo.out" }}, 0);')
            hits.append((t0 + 0.02, "impact", 1))
        elif typ == "card":
            fill(s["img"])
            if s.get("headline"):
                headline(s["headline"], s.get("hsize"))
            if s.get("counter"):
                counter(s["counter"])
            w, h = Image.open(os.path.join(short, "assets", "img", s["img"] + ".jpg")).size
            top = max(y + 10, 330)
            cw = 900
            ch = int(cw * h / w)
            if top + ch > 1110:
                ch = 1110 - top
                cw = min(900, int(ch * w / h))
            left = (1080 - cw) // 2
            css.append(f"#{sid}-card {{ left: {left}px; top: {top}px; width: {cw}px; height: {ch}px; }}")
            body.append(f'<div id="{sid}-card" class="card">{img_tag(s["img"], "cimg", s.get("alt", s["img"]))}</div>')
            js.append(f'M.cardIn(tl, "#{sid}-card", 0.05, {8 if k % 2 else -7}, {-2 if k % 2 else 2}, 280);')
            js.append(f'tl.fromTo("#{sid}-cimg", {{ scale: 1 }}, {{ scale: 1.1, duration: {dur}, ease: "power1.inOut" }}, 0);')
            if s.get("stamp"):
                stamp(s["stamp"], s["stamp"].get("y", top + int(ch * 0.42)), s["stamp"].get("x", 100))
        elif typ == "paper":
            fill(s["fill"])
            if s.get("headline"):
                headline(s["headline"], s.get("hsize"))
            if s.get("card"):
                w, h = Image.open(os.path.join(short, "assets", "img", s["card"] + ".jpg")).size
                ch = min(560, int(900 * h / w))
                css.append(f"#{sid}-card {{ left: 90px; top: {max(y, 240)}px; width: 900px; height: {ch}px; }}")
                body.append(f'<div id="{sid}-card" class="card">{img_tag(s["card"], "cimg", s.get("alt", s["card"]))}</div>')
                js.append(f'M.cardIn(tl, "#{sid}-card", 0.05, -7, 2, 260);')
                y = max(y, 240) + ch - 80
            rows = s["rows"]
            ptop = max(y, 330)
            minus = set(s.get("minus", []))
            css.append(f"#{sid}-paper {{ left: 120px; top: {ptop}px; width: 840px; padding: 36px 46px 120px; font-size: 34px; line-height: 1.55; }}"
                       f"#{sid}-paper .p-title {{ font-weight: 700; font-size: 42px; letter-spacing: 0.05em; border-bottom: 3px solid #141414; padding-bottom: 10px; margin-bottom: 14px; }}"
                       f"#{sid}-paper .row {{ display: flex; justify-content: space-between; }}"
                       f"#{sid}-paper .row b {{ font-weight: 700; }} #{sid}-paper .minus b {{ color: #d0261c; }}")
            rws = "".join(f'<div class="row{" minus" if i in minus else ""}"><span>{html.escape(a)}</span><b>{html.escape(b)}</b></div>' for i, (a, b) in enumerate(rows))
            body.append(f'<div id="{sid}-paper" class="paper"><div class="p-title">{html.escape(s["title"])}</div>{rws}</div>')
            js.append(f'M.cardIn(tl, "#{sid}-paper", 0.35, 6, -2, 420);')
            js.append(f'tl.fromTo("#{sid}-paper .row", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, stagger: 0.22, ease: "power2.out" }}, 0.75);')
            if s.get("stamp"):
                stamp(s["stamp"], ptop + 36 + 96 + len(rows) * 53 + 14, 150)
        elif typ == "bignum":
            fill(s["fill"])
            css.append(f"#{sid}-kick {{ text-align: center; top: 236px; }}")
            land = local(s["land"]) if s.get("land") else dur * 0.6
            d = s.get("decimals", 0)
            fmt = f'(v) => {esc_js(s.get("prefix", ""))} + v.toFixed({d}) + {esc_js(s.get("suffix", ""))}'
            first = f'{s.get("prefix", "")}{s["from"]:.{d}f}{s.get("suffix", "")}'
            css.append(f"#{sid}-num {{ top: 330px; left: 0; right: 0; text-align: center; font-size: {s.get('size', 520)}px; }}")
            body.append(f'<div id="{sid}-num" class="hl">{html.escape(first)}</div>')
            js.append(f'tl.fromTo("#{sid}-num", {{ scale: 0.7, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.25, ease: "expo.out" }}, 0.05);')
            js.append(f'M.count(tl, "#{sid}-num", {max(0.2, round(land - 1.3, 2))}, 1.3, {s["from"]}, {s["to"]}, {fmt});')
            js.append(f'tl.fromTo("#{sid}-num", {{ color: "#ffffff" }}, {{ color: "{COLORS[s.get("color", "y")]}", duration: 0.12, ease: "none", immediateRender: false }}, {land});')
            js.append(f'M.shake(tl, "#{sid}-rig", {land}, 12);')
            hits.append((t0 + land + 0.02, "pop", 2))
            if s.get("label"):
                css.append(f"#{sid}-label {{ top: 860px; text-align: center; font-size: 46px; }}")
                body.append(f'<div id="{sid}-label" class="kick">{markup(s["label"])}</div>')
                js.append(f'M.words(tl, "#{sid}-label", 0.3, 0.05);')
            if s.get("source"):
                css.append(f"#{sid}-src {{ position: absolute; left: 0; right: 0; top: 1050px; text-align: center; font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 30px; color: rgba(255,255,255,.82); text-shadow: 0 3px 0 rgba(0,0,0,.8); }}")
                body.append(f'<div id="{sid}-src">{html.escape(s["source"])}</div>')
                js.append(f'tl.fromTo("#{sid}-src", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.3);')
        elif typ == "chart":
            fill(s["fill"])
            up, flat = html.escape(s.get("up", "UP")), html.escape(s.get("flat", "FLAT"))
            down = s.get("down", False)
            g_path = "M40,600 C300,560 560,420 820,120" if not down else "M40,120 C300,160 560,300 820,600"
            r_path = "M40,600 C300,585 560,560 820,520"
            css.append(f"#{sid}-chart {{ position: absolute; left: 60px; top: {max(y, 330)}px; width: 960px; height: 700px; }}"
                       f"#{sid}-chart text {{ font-family: 'Montserrat', sans-serif; font-weight: 900; font-size: 40px; }}")
            body.append(f'''<svg id="{sid}-chart" viewBox="0 0 960 700">
  <line x1="40" y1="640" x2="940" y2="640" stroke="rgba(255,255,255,0.55)" stroke-width="4" />
  <line x1="40" y1="40" x2="40" y2="640" stroke="rgba(255,255,255,0.55)" stroke-width="4" />
  <path id="{sid}-g" d="{g_path}" fill="none" stroke="{'#ff3b30' if down else '#35e07a'}" stroke-width="14" stroke-linecap="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="100" />
  <path id="{sid}-r" d="{r_path}" fill="none" stroke="{'#35e07a' if down else '#ff3b30'}" stroke-width="14" stroke-linecap="round" pathLength="100" stroke-dasharray="100 120" stroke-dashoffset="100" />
  <text id="{sid}-lg" x="{560 if down else 610}" y="{560 if down else 95}" fill="{'#ff3b30' if down else '#35e07a'}">{up}</text>
  <text id="{sid}-lr" x="560" y="{490 if down else 600}" fill="{'#35e07a' if down else '#ff3b30'}">{flat}</text>
</svg>''')
            js.append(f'tl.fromTo("#{sid}-g", {{ attr: {{ "stroke-dashoffset": 100 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: 1.2, ease: "power2.inOut" }}, 0.2);')
            js.append(f'tl.fromTo("#{sid}-r", {{ attr: {{ "stroke-dashoffset": 100 }} }}, {{ attr: {{ "stroke-dashoffset": 0 }}, duration: 1.2, ease: "power2.inOut" }}, 0.3);')
            js.append(f'tl.fromTo("#{sid}-lg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, 1.0);')
            js.append(f'tl.fromTo("#{sid}-lr", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, 1.3);')
        else:
            raise SystemExit(f"unknown shot type {typ}")

        page = f"""<template>
  <style>
    /*@css*/
{COMMON_CSS}    /*@css-end*/
    {chr(10).join("    " + c for c in css).strip()}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1080" data-height="1920">
    <div id="{sid}-rig" class="rig">
      <div id="{sid}-shot" class="shot clip" data-start="0" data-duration="{dur}">
        {chr(10).join("        " + b for b in bg + body).strip()}
      </div>
    </div>
  </div>
  <script>
    //@js
{COMMON_JS}    //@js-end
    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join("    " + j for j in js).strip()}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""
        open(os.path.join(comp_dir, sid + ".html"), "w", encoding="utf-8").write(page)
        hosts.append(f'<div id="{sid}" class="scene-host" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                     f'data-start="{t0}" data-duration="{dur}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>')

    # captions
    cap = brief.get("captions", {})
    cmd = [sys.executable, "-I", os.path.join(HERE, "make_captions.py"), os.path.join(short, "assets", "transcript.json"),
           os.path.join(comp_dir, "captions.html")]
    for f in cap.get("fix", []):
        cmd += ["--fix", f]
    for key in ("green", "gold", "red"):
        if cap.get(key):
            cmd += [f"--{key}", ",".join(cap[key])]
    subprocess.run(cmd, check=True)

    # media
    for sub in ("bgm", "sfx"):
        os.makedirs(os.path.join(short, "assets", sub), exist_ok=True)
    music = brief.get("music", "tunnel-vision.mp3")
    src_music = os.path.join(ROOT, "library", "bgm", music)
    mlen = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src_music],
                                capture_output=True, text=True).stdout.strip() or 0)
    if mlen < total + 0.5:  # loop the bed so it covers the whole short
        music = music.rsplit(".", 1)[0] + "-loop.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "3", "-i", src_music, "-t", str(total + 1),
                        "-c:a", "libmp3lame", "-q:a", "2", os.path.join(short, "assets", "bgm", music)], check=True)
    else:
        shutil.copy(src_music, os.path.join(short, "assets", "bgm", music))
    shutil.copy(os.path.join(ROOT, "library", "grain.png"), os.path.join(short, "assets", "img", "grain.png"))

    # sound effects: stamps first, then titles, counters, whips; max 12, never two within 0.35 s
    hits.sort(key=lambda h: (h[2], h[0]))
    chosen = []
    for t, kind, pr in hits:
        if len(chosen) >= 12:
            break
        if any(abs(t - c[0]) < 0.35 for c in chosen):
            continue
        chosen.append((t, kind, pr))
    chosen.sort()
    audio, impacts, track_end = [], 0, {}
    for n, (t, kind, _) in enumerate(chosen):
        if kind == "impact":
            kind = "impact-bass-1" if impacts % 3 != 2 or t < 2.2 else "impact-bass-2"
            impacts += 1
        length, peak, vol = SFX[kind]
        start = round(max(0.0, t - peak + 0.033), 2)
        length = round(min(length, total - start), 3)
        tr = 6
        while track_end.get(tr, -1) > start:
            tr += 1
        track_end[tr] = start + length
        shutil.copy(os.path.join(ROOT, "library", "sfx", kind + ".mp3"), os.path.join(short, "assets", "sfx", kind + ".mp3"))
        audio.append(f'<audio id="sfx-{n:02d}" src="assets/sfx/{kind}.mp3" data-start="{start}" data-duration="{length}" data-track-index="{tr}" data-volume="{vol}"></audio>')

    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0b0b0b; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: #0b0b0b; }}
      .scene-host {{ z-index: 10; }}
      #captions {{ z-index: 30; }}
      #grain {{ position: absolute; inset: 0; z-index: 40; pointer-events: none; background-image: url("assets/img/grain.png"); background-size: 512px 512px; opacity: 0.08; mix-blend-mode: overlay; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1080" data-height="1920">
      {chr(10).join("      " + h for h in hosts).strip()}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{total}" data-track-index="2" data-track-kind="captions" data-width="1080" data-height="1920"></div>
      <div id="grain" class="clip" data-start="0" data-duration="{total}" data-track-index="3" data-layout-allow-overlap data-layout-ignore></div>
      <audio id="voice" src="assets/voice.wav" data-start="0" data-track-index="4" data-volume="1"></audio>
      <audio id="music" src="assets/bgm/{music}" data-start="0" data-duration="{total}" data-track-index="5" data-volume="{brief.get('music_volume', 0.09)}" data-fade-in="0.3" data-fade-out="1.6"></audio>
      {chr(10).join("      " + a for a in audio).strip()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#grain", {{ backgroundPosition: "0px 0px" }}, {{ backgroundPosition: "85591px 58993px", duration: {total}, ease: "steps({int(total * 15)})" }}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    open(os.path.join(short, "index.html"), "w", encoding="utf-8").write(index)
    for f in ("package.json", "hyperframes.json"):
        if not os.path.exists(os.path.join(short, f)):
            src = json.load(open(os.path.join(ROOT, "pilot-01", f), encoding="utf-8"))
            if f == "package.json":
                src["name"] = brief["slug"]
            else:
                src.pop("registryItems", None)
            json.dump(src, open(os.path.join(short, f), "w", encoding="utf-8"), indent=2)
    print(f"built {len(shots)} shots, {len(chosen)} sfx, {total}s -> {short}")
    for k, (a, b) in enumerate(zip(starts, ends)):
        print(f"  s{k + 1:02d} {shots[k]['type']:7s} {a:6.2f}-{b:6.2f}")


if __name__ == "__main__":
    build(sys.argv[1])
