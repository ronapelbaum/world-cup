#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dead-reference / asset linter for the World Cup app (stdlib only).

ERRORS (fail CI):
  - a data/*.json file referenced by index.html's bootstrap doesn't exist
  - a team id in data/manifest.json has no data/teams/<id>.json
  - any referenced JSON file fails to parse

WARNINGS (do not fail CI):
  - a player or legend whose photo (img / <en>.jpg) is missing from player_images/
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)

errors, warnings = [], []

# --- read index.html ---
html_path = P("index.html")
if not os.path.exists(html_path):
    print("✖ index.html not found"); sys.exit(1)
html = open(html_path, encoding="utf-8").read()

def load_json(relpath, hard=True):
    fp = P(relpath)
    if not os.path.exists(fp):
        (errors if hard else warnings).append(f"missing file: {relpath}")
        return None
    try:
        return json.load(open(fp, encoding="utf-8"))
    except Exception as e:
        errors.append(f"{relpath} is not valid JSON: {e}")
        return None

# 1) global data files referenced via loadJSON(base+'X.json')
refs = re.findall(r"loadJSON\(base\s*\+\s*'([^']+)'\)", html)
for rel in refs:
    if not os.path.exists(P("data", rel)):
        errors.append(f"index.html references data/{rel} but it does not exist")

# 2) manifest -> team files
team_ids = load_json("data/manifest.json") or []
for tid in team_ids:
    if not os.path.exists(P("data", "teams", tid + ".json")):
        errors.append(f"manifest lists '{tid}' but data/teams/{tid}.json is missing")

# parse the referenced globals (catch broken JSON early)
for rel in refs:
    load_json(os.path.join("data", rel))

# 3) photo references (warnings only)
def photo_missing(img):
    if not img:
        return False
    rel = img.lstrip("./")
    return not os.path.exists(P(rel))

missing_photos = 0
for tid in team_ids:
    data = load_json(os.path.join("data", "teams", tid + ".json"))
    if not data:
        continue
    for pl in data.get("players", []):
        if photo_missing(pl.get("img", "")):
            warnings.append(f"{tid}: missing photo for {pl.get('n','?')} -> {pl.get('img')}")
            missing_photos += 1

legends = load_json("data/legends.json")
if legends:
    for lg in legends:
        en = lg.get("en")
        if en and not os.path.exists(P("player_images", en + ".jpg")):
            warnings.append(f"legend: missing photo {en}.jpg ({lg.get('name','?')})")
            missing_photos += 1

# --- report ---
print("== World Cup asset / dead-reference lint ==")
print(f"referenced data files: {len(refs)} | teams in manifest: {len(team_ids)}")

if warnings:
    print(f"\n::warning::{len(warnings)} non-blocking warnings ({missing_photos} missing photos)")
    for w in warnings[:60]:
        print(f"  ⚠ {w}")
    if len(warnings) > 60:
        print(f"  ... and {len(warnings) - 60} more")

if errors:
    print(f"\n✖ {len(errors)} ERROR(S):")
    for e in errors:
        print(f"::error::{e}")
    sys.exit(1)

print("\n✓ No dead references — all referenced data files and manifest team files exist and parse.")
