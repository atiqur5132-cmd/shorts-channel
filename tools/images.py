"""Find and prepare CC0 / public-domain photos for a short.

  py -I tools/images.py search <short-dir> "<query>" [--n 16]
      -> searches Openverse (Wikimedia first for full resolution), writes
         <short-dir>/work/sheet-<slug>.jpg (labelled thumbnails) + candidates json.
  py -I tools/images.py get <short-dir> <id8> <name> [--mode full|card] [--cx 0.5] [--cy 0.5] [--grade deep|mono|none]
      -> downloads the picked image, crops/grades it into <short-dir>/assets/img/<name>.jpg
         (full: 1242x2208 cover crop; card: original aspect + <name>-fill.jpg blurred backdrop)
         and appends the credit to <short-dir>/CREDITS.md.
Images under 1900 px on the short side should be used as cards, never full-bleed.
"""
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

UA = "ShortsBuilder/1.0 (https://hyperframes.heygen.com; personal video project) python-urllib"


def fetch(url, timeout=60, tries=3):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(2 + 3 * i)
    raise RuntimeError(f"fetch failed {url[:90]}: {err}")


def wm_thumb(url, width):
    m = re.match(r"https://upload\.wikimedia\.org/wikipedia/commons/(\w)/(\w\w)/(.+)$", url)
    if not m:
        return None
    a, b, fn = m.groups()
    t = f"https://upload.wikimedia.org/wikipedia/commons/thumb/{a}/{b}/{fn}/{width}px-{fn}"
    return t + ".jpg" if fn.lower().endswith((".tif", ".tiff")) else t


def search(short, query, n=16):
    work = os.path.join(short, "work")
    os.makedirs(work, exist_ok=True)
    results = []
    for extra in ("&source=wikimedia&size=large", "&size=large"):
        url = ("https://api.openverse.org/v1/images/?q=" + urllib.parse.quote(query)
               + "&license=cc0,pdm&page_size=20" + extra)
        try:
            data = json.loads(fetch(url))
        except Exception as e:  # noqa: BLE001
            print("search error:", e)
            continue
        for r in data.get("results", []):
            if r["id"][:8] in {x["id8"] for x in results}:
                continue
            w, h = r.get("width") or 0, r.get("height") or 0
            if w and min(w, h) < 1000:
                continue
            results.append({"id8": r["id"][:8], "id": r["id"], "url": r.get("url"), "thumb": r.get("thumbnail"),
                            "w": w, "h": h, "source": r.get("source"), "license": r.get("license"),
                            "title": (r.get("title") or "")[:80], "creator": r.get("creator"),
                            "landing": r.get("foreign_landing_url")})
            if len(results) >= n:
                break
        if len(results) >= n:
            break
    slug = re.sub(r"\W+", "-", query.lower()).strip("-")[:30]
    db_path = os.path.join(work, "candidates.json")
    db = json.load(open(db_path, encoding="utf-8")) if os.path.exists(db_path) else {}
    for r in results:
        db[r["id8"]] = r
    json.dump(db, open(db_path, "w", encoding="utf-8"), indent=1)
    # contact sheet
    tw, th, cols = 260, 210, 6
    rows = (len(results) + cols - 1) // cols or 1
    sheet = Image.new("RGB", (cols * tw, rows * (th + 34)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    for i, r in enumerate(results):
        th_url = (wm_thumb(r["url"], 330) if r["source"] == "wikimedia" else None) or r["thumb"]
        try:
            im = Image.open(io.BytesIO(fetch(th_url, 40, 2))).convert("RGB")
            im.thumbnail((tw, th))
        except Exception:  # noqa: BLE001
            im = Image.new("RGB", (tw, th), (90, 0, 0))
        x, y = (i % cols) * tw, (i // cols) * (th + 34)
        sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
        hires = "FULL" if min(r["w"], r["h"]) >= 1900 and r["source"] == "wikimedia" else "card"
        d.text((x + 3, y + th + 2), f'{r["id8"]} {r["w"]}x{r["h"]} {hires}', fill=(255, 255, 0), font=font)
        d.text((x + 3, y + th + 17), r["title"][:34], fill=(200, 200, 200), font=font)
        time.sleep(0.4)
    out = os.path.join(work, f"sheet-{slug}.jpg")
    sheet.save(out, quality=85)
    print(out)
    for r in results:
        print(r["id8"], r["w"], r["h"], r["source"], r["license"], "|", r["title"][:60])


def curve(k, mono=False):
    lut = []
    b, h, e = 0.06 * k, 0.04 * k, 2 ** (-0.03 * k)
    for v in range(256):
        x = max(0.0, (v / 255 * e - b) / (1 - b))
        if x > 0.75:
            x = 0.75 + (x - 0.75) * (1 - h * 2)
        if mono:
            x = 0.10 + x * 0.86
        lut.append(int(round(min(1, max(0, x)) * 255)))
    return lut


def grade(im, kind, k):
    if kind == "none":
        return im
    im = ImageEnhance.Contrast(im).enhance(1 + 0.2 * k)
    if kind == "mono":
        im = ImageEnhance.Color(im).enhance(0.08)
        return im.point(curve(k, True) * 3)
    im = im.point(curve(k) * 3)
    return ImageEnhance.Color(im).enhance(1 + 0.06 * k)


def cover(im, W, H, cx=0.5, cy=0.5):
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = int(min(max(cx * im.width - W / 2, 0), im.width - W))
    y = int(min(max(cy * im.height - H / 2, 0), im.height - H))
    return im.crop((x, y, x + W, y + H))


def get(short, id8, name, mode="full", cx=0.5, cy=0.5, kind="deep"):
    db = json.load(open(os.path.join(short, "work", "candidates.json"), encoding="utf-8"))
    r = db[id8]
    url = r["url"]
    if r["source"] == "wikimedia":
        url = wm_thumb(r["url"], 3840) if max(r["w"], r["h"]) > 3840 else r["url"]
    try:
        raw = fetch(url, 120)
    except RuntimeError:
        raw = fetch(r["url"], 120)
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    imgdir = os.path.join(short, "assets", "img")
    os.makedirs(imgdir, exist_ok=True)
    if mode == "full":
        if min(im.size) < 1500:
            print(f"WARNING: {im.size} is low-res for full-bleed; use --mode card")
        out = grade(cover(im, 1242, 2208, cx, cy), kind, 0.8)
        out.save(os.path.join(imgdir, name + ".jpg"), quality=90)
    else:
        if max(im.size) > 1400:
            im.thumbnail((1400, 1400), Image.LANCZOS)
        grade(im, kind, 0.5).save(os.path.join(imgdir, name + ".jpg"), quality=92)
        f = cover(im, 540, 960, cx, cy).filter(ImageFilter.GaussianBlur(14))
        f = ImageEnhance.Color(ImageEnhance.Brightness(f).enhance(0.62)).enhance(0.85)
        f.resize((1080, 1920), Image.BICUBIC).save(os.path.join(imgdir, name + "-fill.jpg"), quality=88)
    cred = os.path.join(short, "CREDITS.md")
    line = (f"- {name}.jpg: \"{r['title']}\" by {r.get('creator') or 'unknown'}, {r['license'].upper()}, "
            f"{r['source']} ({r.get('landing') or r['url']})\n")
    new = not os.path.exists(cred)
    with open(cred, "a", encoding="utf-8") as fh:
        if new:
            fh.write("# Credits (all CC0 / public domain)\n\n")
        fh.write(line)
    print("saved", name, im.size, mode)


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = {a[i][2:]: a[i + 1] for i in range(len(a)) if a[i].startswith("--") and i + 1 < len(a)}
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and not (i > 0 and a[i - 1].startswith("--"))]
    if pos[0] == "search":
        search(pos[1], pos[2], int(opt.get("n", 16)))
    elif pos[0] == "get":
        get(pos[1], pos[2], pos[3], opt.get("mode", "full"), float(opt.get("cx", 0.5)), float(opt.get("cy", 0.5)),
            opt.get("grade", "deep"))
