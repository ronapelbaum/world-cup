#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bake all data/*.json into index.html as an inlined window.WC object, so the page
is fully static (zero fetch calls). Run after editing any data file:

    python3 scripts/build_inline.py

Source of truth stays in data/. This regenerates the block between
<!--WC_DATA_START--> and <!--WC_DATA_END--> in index.html.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def load(rel): return json.load(open(P(rel), encoding="utf-8"))

manifest = load("data/manifest.json")
data = {
    "positions": load("data/positions.json"),
    "structure": load("data/structure.json"),
    "schedule":  load("data/schedule.json"),
    "stadiums":  load("data/stadiums.json"),
    "groups":    load("data/groups.json"),
    "nations":   load("data/nations.json"),
    "matches":   load("data/matches.json"),
    "legends":   load("data/legends.json"),
    "records":   load("data/records.json"),
    "knockout":  load("data/knockout.json"),
    "teams":     [load("data/teams/%s.json" % tid) for tid in manifest],
}

js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
# Safe to embed inside <script>: escape '<' (prevents </script>, <!--) and line separators.
js = js.replace("<", "\\u003c").replace(" ", "\\u2028").replace(" ", "\\u2029")

block = '<!--WC_DATA_START-->\n<script id="wc-data">window.WC=%s;</script>\n<!--WC_DATA_END-->' % js

html_path = P("index.html")
html = open(html_path, encoding="utf-8").read()
new, n = re.subn(r"<!--WC_DATA_START-->.*?<!--WC_DATA_END-->", lambda m: block, html, flags=re.S)
if n != 1:
    print("✖ expected exactly one WC_DATA marker block, found", n); sys.exit(1)
open(html_path, "w", encoding="utf-8").write(new)

print("✓ inlined window.WC into index.html")
print(f"  teams={len(data['teams'])} groups={len(data['groups'])} matches={len(data['matches'])} "
      f"legends={len(data['legends'])} records={len(data['records'])} | data block: {len(js)//1024} KB")
