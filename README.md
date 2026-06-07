# המדריך הגדול למונדיאל 2026 ⚽

[![Lint](https://github.com/ronapelbaum/world-cup/actions/workflows/lint.yml/badge.svg)](https://github.com/ronapelbaum/world-cup/actions/workflows/lint.yml)

אפליקציית ווב חינוכית וכיפית בעברית (RTL) שמלמדת ילדים על מונדיאל 2026 — 16 נבחרות מובילות,
שחקנים, חידונים, איך הטורניר עובד וקו זמן. בסגנון אלבום מדבקות צבעוני.

## הרצה מקומית

האפליקציה טוענת את הנתונים מקבצי JSON, ולכן חייבים להגיש אותה דרך שרת (לא לפתוח `index.html` ישירות
כקובץ — `file://` חוסם טעינת JSON). שרת סטטי קטן מספיק:

```bash
cd world-cup
python3 -m http.server 8000
# ואז פותחים בדפדפן:  http://localhost:8000
```

(אפשר גם `npx serve` במקום.)

## מבנה

```
index.html            # האפליקציה (עיצוב + לוגיקה + טעינת נתונים אסינכרונית)
data/
  manifest.json       # רשימת הנבחרות (שמות קבצים)
  positions.json      # תוויות וצבעי קווים (שוער/הגנה/קישור/התקפה)
  structure.json      # מבנה הטורניר + שיטת הנקודות
  schedule.json       # תחנות קו הזמן
  teams/<id>.json     # 16 קבצי נבחרת (סכמה אחידה)
player_images/         # תמונות שחקנים (מורדות מוויקיפדיה)
players.txt            # קלט לסקריפט הורדת התמונות (שמות באנגלית)
download_player_images.py
```

## הוספת נבחרת חדשה

1. צרו `data/teams/<id>.json` לפי הסכמה של קובץ קיים.
2. הוסיפו את שם הקובץ ל-`data/manifest.json`.
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
