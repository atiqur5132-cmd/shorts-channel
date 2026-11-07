"""Inject the shared look (common.css) and motion helpers (common.js) into every scene file.

Scene files mark the spots with  /*@css*/ ... /*@css-end*/  inside <style>
and  //@js  ...  //@js-end  inside <script>. Re-running is idempotent.
Usage: py -I tools/inject_common.py <project-dir>
"""
import pathlib
import re
import sys

here = pathlib.Path(__file__).parent
css = (here / "common.css").read_text(encoding="utf-8")
js = (here / "common.js").read_text(encoding="utf-8")
proj = pathlib.Path(sys.argv[1])
n = 0
for f in sorted((proj / "compositions").glob("*.html")):
    s = f.read_text(encoding="utf-8")
    s2 = re.sub(r"/\*@css\*/.*?/\*@css-end\*/", lambda m: "/*@css*/\n" + css + "    /*@css-end*/", s, flags=re.S)
    s2 = re.sub(r"//@js\n.*?//@js-end", lambda m: "//@js\n" + js + "    //@js-end", s2, flags=re.S)
    if s2 != s:
        f.write_text(s2, encoding="utf-8")
        n += 1
print(f"injected into {n} scene file(s)")
