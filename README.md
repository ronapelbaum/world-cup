# המדריך הגדול למונדיאל 2026 ⚽

[![Lint](https://github.com/ronapelbaum/world-cup/actions/workflows/lint.yml/badge.svg)](https://github.com/ronapelbaum/world-cup/actions/workflows/lint.yml)

אפליקציית ווב חינוכית וכיפית בעברית (RTL) שמלמדת ילדים על מונדיאל 2026 — 16 נבחרות מובילות,
שחקנים, חידונים, איך הטורניר עובד וקו זמן. בסגנון אלבום מדבקות צבעוני.

## הרצה מקומית

האפליקציה **סטטית לחלוטין** — כל הנתונים מוטמעים בתוך `index.html` (אובייקט `window.WC`), אין שום
קריאת `fetch`/רשת לנתונים. אפשר פשוט לפתוח את `index.html` בדפדפן, או להגיש דרך כל שרת קבצים סטטי:

```bash
cd world-cup
python3 -m http.server 8000   # ואז: http://localhost:8000
```

הנתונים נשמרים כקבצי מקור ב-`data/` ומוטמעים ל-`index.html` ע"י סקריפט בנייה. **אחרי כל עריכת נתונים
הריצו**:

```bash
python3 scripts/build_inline.py   # מטמיע מחדש את data/ לתוך index.html
```

## מבנה

```
index.html            # האפליקציה — עיצוב + לוגיקה + נתונים מוטמעים (window.WC). סטטי, ללא fetch
data/                 # מקור הנתונים (נערך ידנית; מוטמע ל-index.html ע"י build_inline.py)
  manifest.json       # רשימת הנבחרות (שמות קבצים)
  positions, structure, schedule, stadiums, groups, nations, matches, legends, records, knockout .json
  teams/<id>.json     # 16 קבצי נבחרת (סכמה אחידה)
scripts/
  build_inline.py     # מטמיע את data/ לתוך index.html (להריץ אחרי עריכת נתונים)
  lint_assets.py      # בדיקת קישורים/תמונות
player_images/         # תמונות שחקנים (קבצים סטטיים)
players.txt · download_player_images.py
```

## הוספת נבחרת חדשה

1. צרו `data/teams/<id>.json` לפי הסכמה של קובץ קיים.
2. הוסיפו את שם הקובץ ל-`data/manifest.json`.
3. הריצו `python3 scripts/build_inline.py` כדי להטמיע את השינוי ל-`index.html`.
   הנבחרת תופיע אוטומטית בסרגל הצד — אין צורך לגעת בקוד.

## תמונות שחקנים

התמונות מורדות מוויקיפדיה לפי שם **באנגלית** (שדה `en` בכל שחקן), ונשמרות ב-`player_images/`.
שדה `img` של כל שחקן מצביע על הקובץ המקומי. אם תמונה חסרה — מוצג אווטאר מאויר אוטומטית.

לרענון/השלמת תמונות:

```bash
python3 download_player_images.py players.txt -o player_images
```

(הסקריפט מדלג על תמונות שכבר קיימות.)

## פריסה ל-GitHub Pages

```bash
git add -A
git commit -m "Deploy"
git push
```

ואז ב-GitHub: **Settings → Pages → Deploy from branch → `main` / root**.
כל הנתיבים יחסיים, כך שהאתר עובד גם תחת תת-נתיב כמו `/world-cup/`.

## CI — בדיקת קישורים (lint)

`scripts/lint_assets.py` (ספריית תקן בלבד, ללא תלויות) בודק שהאפליקציה לא מפנה לקבצים חסרים:

- **נכשל** אם קובץ `data/*.json` שמופיע ב-`index.html` חסר, אם נבחרת ב-`manifest.json` חסרה קובץ, או אם JSON לא תקין.
- **אזהרה** (לא מפיל) על שחקן/אגדה שאין לו תמונה ב-`player_images/`.

הרצה מקומית: `python3 scripts/lint_assets.py`

ה-workflow מחכה ב-`ci/lint.yml`. **להפעלה**: העבירו אותו ל-`.github/workflows/lint.yml`
(`git mv ci/lint.yml .github/workflows/lint.yml` לאחר `gh auth refresh -s workflow`, או הדביקו דרך GitHub → Actions → New workflow). מאז הוא ירוץ על כל PR ו-push ל-main.

> המידע (סגלים, גילאים, מועדונים) הוא להמחשה ולומדה ועשוי להשתנות עד יוני 2026.
> כינויי נבחרות שלא אומתו בעברית הושארו ריקים (ראו שדה `nickNote`).
