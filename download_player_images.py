#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
הורדת תמונות שחקני כדורגל מ-Wikipedia / Wikimedia.

איך מריצים:
    python download_player_images.py players.txt
    python download_player_images.py players.txt -o images -l en
    python download_player_images.py players.txt --full      # רזולוציה מלאה
    python download_player_images.py players.txt -l he        # ויקיפדיה בעברית

הקובץ players.txt = שם שחקן אחד בכל שורה.
לכל שחקן נשמרת תמונה בתיקיית היעד, עם שם הקובץ = שם השחקן.
"""

import argparse
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests

# ויקיפדיה דורשת User-Agent שמזהה את האפליקציה. אפשר לעדכן את המייל.
USER_AGENT = "PlayerImageDownloader/1.0 (personal use)"


def sanitize_filename(name):
    """מנקה שם כך שיהיה חוקי כשם קובץ בכל מערכת הפעלה."""
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', "", name)   # תווים אסורים
    name = re.sub(r"\s+", " ", name)            # רווחים כפולים
    return name or "unknown"


def search_page_title(session, name, lang, add_keyword):
    """מחפש בוויקיפדיה את הדף הכי מתאים לשם ומחזיר את הכותרת המדויקת."""
    query = f"{name} footballer" if add_keyword else name
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": 1,
        "format": "json",
    }
    r = session.get(url, params=params, timeout=20)
    r.raise_for_status()
    results = r.json().get("query", {}).get("search", [])
    return results[0]["title"] if results else None


def get_image_url(session, title, lang, full):
    """מחזיר את כתובת התמונה הראשית (lead image) של הדף."""
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageimages",
        "format": "json",
        "redirects": 1,
    }
    if full:
        params["piprop"] = "original"
    else:
        params["piprop"] = "thumbnail"
        params["pithumbsize"] = 1000   # רוחב ~1000px, מספיק לפורטרט נקי

    r = session.get(url, params=params, timeout=20)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    for page in pages.values():
        if full and "original" in page:
            return page["original"]["source"]
        if not full and "thumbnail" in page:
            return page["thumbnail"]["source"]
    return None


def extension_from(url, content_type):
    """קובע את סיומת הקובץ לפי כתובת התמונה או לפי סוג התוכן."""
    ext = os.path.splitext(urlparse(url).path)[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"):
        return ext
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
    }
    return mapping.get((content_type or "").split(";")[0].strip(), ".jpg")


def download_image(session, image_url, dest_without_ext):
    """מוריד את התמונה ושומר עם הסיומת הנכונה. מחזיר את הנתיב שנשמר."""
    r = session.get(image_url, timeout=60, stream=True)
    r.raise_for_status()
    ext = extension_from(image_url, r.headers.get("Content-Type", ""))
    dest = dest_without_ext + ext
    with open(dest, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return dest


def main():
    parser = argparse.ArgumentParser(
        description="הורדת תמונות שחקנים מוויקיפדיה לפי קובץ שמות."
    )
    parser.add_argument("input", help="קובץ TXT עם שם שחקן בכל שורה")
    parser.add_argument("-o", "--output", default="player_images",
                        help="תיקיית יעד (ברירת מחדל: player_images)")
    parser.add_argument("-l", "--lang", default="en",
                        help="שפת ויקיפדיה: en, he, es, ... (ברירת מחדל: en)")
    parser.add_argument("--full", action="store_true",
                        help="הורד תמונה ברזולוציה מלאה (קבצים גדולים יותר)")
    parser.add_argument("--no-keyword", action="store_true",
                        help="אל תוסיף 'footballer' לחיפוש (שימושי לעברית)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="השהיה בין בקשות בשניות (ברירת מחדל: 0.5)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"שגיאה: הקובץ '{args.input}' לא נמצא.")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)

    with open(args.input, encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]

    if not names:
        print("הקובץ ריק.")
        sys.exit(1)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    found = skipped = failed = 0
    total = len(names)
    print(f"נמצאו {total} שמות. מוריד לתיקייה '{args.output}'...\n")

    for i, name in enumerate(names, 1):
        safe = sanitize_filename(name)

        # אם כבר קיים קובץ עם השם הזה - מדלגים (מאפשר להריץ שוב בלי לחזור על עבודה)
        existing = [fn for fn in os.listdir(args.output)
                    if os.path.splitext(fn)[0] == safe]
        if existing:
            print(f"[{i}/{total}] {name}: כבר קיים ({existing[0]}), מדלג.")
            skipped += 1
            continue

        try:
            title = search_page_title(session, name, args.lang, not args.no_keyword)
            if not title:
                print(f"[{i}/{total}] {name}: לא נמצא דף מתאים.")
                failed += 1
                continue

            image_url = get_image_url(session, title, args.lang, args.full)
            if not image_url:
                print(f"[{i}/{total}] {name}: נמצא הדף '{title}' אבל אין בו תמונה.")
                failed += 1
                continue

            dest = download_image(session, image_url, os.path.join(args.output, safe))
            print(f"[{i}/{total}] {name}: הורד -> {os.path.basename(dest)}")
            found += 1

        except requests.RequestException as e:
            print(f"[{i}/{total}] {name}: שגיאת רשת ({e}).")
            failed += 1
        except Exception as e:
            print(f"[{i}/{total}] {name}: שגיאה ({e}).")
            failed += 1
        finally:
            time.sleep(args.delay)

    print(f"\nסיום. הורדו: {found} | דולגו: {skipped} | נכשלו: {failed}")


if __name__ == "__main__":
    main()
