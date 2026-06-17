"""
Runs on GitHub Actions (cloud) — counting schedule reminders for spira.html.
No state file — dedup handled by the cron schedule itself (one job per slot).
Cloud-only backup for when the PC is off; the precise path is notify_spira.py
via Task Scheduler (every 5 min).
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_utc = datetime.now(timezone.utc)
IL_OFFSET = 3 if 3 <= _utc.month <= 10 else 2
now_il  = _utc + timedelta(hours=IL_OFFSET)
dow     = (now_il.weekday() + 1) % 7
today_str = now_il.strftime('%Y-%m-%d')
print(f'Israel time: {now_il.strftime("%A %Y-%m-%d %H:%M")}  dow={dow}  UTC+{IL_OFFSET}')

BRANCH = '208'

CHOR = [
    {'dow': 0, 'day': 'א', 'items': ['כביסה','מטליות','אלומיניום','שקיות','ארוסולים','אקונומיקה','אסלות','מדיח','בע"ח','ניקוי כלים','נייר מגבת','נייר טואלט']},
    {'dow': 1, 'day': 'ב', 'items': ['קפה','תה','עוגיות וביסקוויטים','ופלים','מתוקים','פריכיות','מוצרי אפייה','דבש, ריבה, ממרח','חטיפים']},
    {'dow': 2, 'day': 'ג', 'items': ['אורז','קטניות','פסטה','מרקים ותבשילים','חרדל, טחינה, מיונז','שימורי דגים','כבושים','שימורי ירקות','מוצרי עגבניה','רטבים']},
    {'dow': 3, 'day': 'ד', 'items': ['משק"ל','יין','בירה','משקאות חריפים','נקטר, סירופים ופחיות','דגני בוקר','חטיפי דגנים','שמן','שמן זית','יסוד']},
    {'dow': 4, 'day': 'ה', 'items': ['שמפו','סבון','היגיינת הפה','דאודורנטים','היגיינה נשית','מזון תינוקות','מגבונים','חיתולים']},
]

PACHAT = [
    {'d': '2026-05-11', 'items': ['סכו"ם'],               'codes': ['831']},
    {'d': '2026-05-18', 'items': ['מאגדות גלידה'],        'codes': ['203']},
    {'d': '2026-05-25', 'items': ['גלידות משפחתיות'],     'codes': ['202']},
    {'d': '2026-06-01', 'items': ['עיתונים ומגזינים'],    'codes': ['955']},
    {'d': '2026-06-08', 'items': ['סטים מצעים'],          'codes': ['913']},
    {'d': '2026-06-15', 'items': ['איפור'],                'codes': ['413','414']},
    {'d': '2026-06-22', 'items': ['קרמים'],               'codes': ['427']},
    {'d': '2026-06-29', 'items': ['בישום'],               'codes': ['400','401','402','403']},
    {'d': '2026-07-06', 'items': ['אביזרי סלולר'],        'codes': ['430']},
    {'d': '2026-07-13', 'items': ['דגים קפואים'],         'codes': ['112']},
    {'d': '2026-07-20', 'items': ['מוצרי קו קופות'],      'codes': ['690']},
    {'d': '2026-07-27', 'items': ['דג סלמון'],            'codes': ['114']},
    {'d': '2026-08-03', 'items': ['בשר קפוא חלקים'],      'codes': ['181']},
    {'d': '2026-08-10', 'items': ['אביזרי תינוקות'],      'codes': ['452']},
    {'d': '2026-08-17', 'items': ['אביזרי גילוח'],        'codes': ['438']},
]

YOMI = [
    {'d': '2026-05-17', 'dn': 'א', 'delay': True,  'items': ['סבונים']},
    {'d': '2026-05-18', 'dn': 'ב', 'delay': True,  'items': ['יין']},
    {'d': '2026-05-19', 'dn': 'ג', 'delay': True,  'items': ['חטיפי דגנים']},
    {'d': '2026-05-20', 'dn': 'ד', 'delay': True,  'items': ['קפה']},
    {'d': '2026-05-24', 'dn': 'א', 'items': ['אורז, קטניות, פירורי לחם, קוסקוס']},
    {'d': '2026-05-25', 'dn': 'ב', 'items': ['חטיפים'], 'special': 'חלב וסלטים'},
    {'d': '2026-05-26', 'dn': 'ג', 'items': ['כביסה']},
    {'d': '2026-05-27', 'dn': 'ד', 'items': ['מדיח']},
    {'d': '2026-05-31', 'dn': 'א', 'items': ['אסלות, אקונומיקה, רצפה וכללי']},
    {'d': '2026-06-01', 'dn': 'ב', 'items': ['דגני בוקר']},
    {'d': '2026-06-02', 'dn': 'ג', 'items': ['שקיות']},
    {'d': '2026-06-03', 'dn': 'ד', 'items': ['בירה']},
    {'d': '2026-06-07', 'dn': 'א', 'items': ['היגיינה נשית, נייר טואלט']},
    {'d': '2026-06-08', 'dn': 'ב', 'items': ['עוגיות וביסקוויטים']},
    {'d': '2026-06-09', 'dn': 'ג', 'items': ['בייגלה']},
    {'d': '2026-06-10', 'dn': 'ד', 'items': ['פריכיות']},
    {'d': '2026-06-14', 'dn': 'א', 'items': ['שמן זית, שמנים']},
    {'d': '2026-06-15', 'dn': 'ב', 'items': ['משק"ל']},
    {'d': '2026-06-16', 'dn': 'ג', 'items': ['רטבים']},
    {'d': '2026-06-17', 'dn': 'ד', 'items': ['חרדל, טחינה, מיונז']},
    {'d': '2026-06-21', 'dn': 'א', 'items': ['שימורי דגים, שימורי ירקות']},
    {'d': '2026-06-22', 'dn': 'ב', 'items': ['היגיינת הפה'], 'special': 'חלב וסלטים'},
    {'d': '2026-06-23', 'dn': 'ג', 'items': ['מתוקים']},
    {'d': '2026-06-24', 'dn': 'ד', 'items': ['משקאות חריפים']},
    {'d': '2026-06-28', 'dn': 'א', 'items': ['כבושים, מוצרי עגבניה']},
    {'d': '2026-06-29', 'dn': 'ב', 'items': ['פסטה']},
    {'d': '2026-06-30', 'dn': 'ג', 'items': ['תה']},
    {'d': '2026-07-01', 'dn': 'ד', 'items': ['ופלים']},
    {'d': '2026-07-05', 'dn': 'א', 'items': ['מטליות, נייר מגבת']},
    {'d': '2026-07-06', 'dn': 'ב', 'items': ['מוצרי אפייה']},
    {'d': '2026-07-07', 'dn': 'ג', 'items': ['מרקים ותבשילים']},
    {'d': '2026-07-08', 'dn': 'ד', 'items': ['בע"ח']},
    {'d': '2026-07-12', 'dn': 'א', 'items': ['אלומיניום, מוצרי יסוד']},
    {'d': '2026-07-13', 'dn': 'ב', 'items': ['שמפו']},
    {'d': '2026-07-14', 'dn': 'ג', 'items': ['ניקוי כלים']},
    {'d': '2026-07-15', 'dn': 'ד', 'items': ['נקטר, סירופים ופחיות']},
    {'d': '2026-07-19', 'dn': 'א', 'items': ['מזון תינוקות, חיתולים']},
    {'d': '2026-07-20', 'dn': 'ב', 'items': ['דבש, ריבה, ממרח']},
    {'d': '2026-07-21', 'dn': 'ג', 'items': ['דאודורנטים']},
    {'d': '2026-07-22', 'dn': 'ד', 'items': ['מגבונים']},
]

SPECIAL_DATES = {
    '2026-06-13': [
        {'id': 'chor_s',   'label': 'חור במדף',    'detail': 'טלביזיות, מקררים, מאווררים, חשמל ביתי'},
        {'id': 'yomi_s',   'label': 'ספירה יומית', 'detail': 'ירקות'},
        {'id': 'pachat_s', 'label': 'פחת',          'detail': 'גרילים ופחמים'},
    ]
}


def get_today_sections(date_str, dow_):
    sections = []
    cd = next((c for c in CHOR if c['dow'] == dow_), None)
    if cd:
        sections.append({'id': 'chor', 'label': 'חור במדף',
                          'detail': "יום " + cd['day'] + "' — " + ', '.join(cd['items'])})
    tp = next((p for p in PACHAT if p['d'] == date_str), None)
    if tp:
        sections.append({'id': 'pachat', 'label': 'פחת',
                          'detail': ', '.join(tp['items']) + ' [פלנ׳: ' + ', '.join(tp['codes']) + ']'})
    ty = next((y for y in YOMI if y['d'] == date_str and y['items'] and not y.get('delay')), None)
    if ty:
        sunday_extra = ['עגלות לקוחות', 'מזון תינוקות'] if ty['dn'] == 'א' else []
        detail = ', '.join(ty['items'] + sunday_extra)
        if ty.get('special'):
            detail += ' | 🥛 ' + ty['special']
        sections.append({'id': 'yomi', 'label': 'ספירה יומית', 'detail': detail})
    sections += SPECIAL_DATES.get(date_str, [])
    return sections


managers = common.get_managers(BRANCH)
sections = get_today_sections(today_str, dow)

if not sections:
    print('No counts scheduled today. Exiting.')
    sys.exit(0)

done_state = common.get_daily_state(BRANCH, today_str)

date_he = f"{now_il.day} {now_il.strftime('%B')} {now_il.year}"
tg_lines = [f'<b>📋 ריכוז ספירות — {date_he} ({now_il.strftime("%H:%M")})</b>', '<i>📡 GitHub Cloud</i>', '']
html_lines = [f'<h3>📋 ריכוז ספירות — {date_he} ({now_il.strftime("%H:%M")})</h3>']
for s in sections:
    mark = '✅' if done_state.get(s['id']) else '❌'
    tg_lines.append(f"{mark} <b>{s['label']}</b>\n{s['detail']}\n")
    html_lines.append(f"<p>{mark} <b>{s['label']}</b><br>{s['detail']}</p>")

print('Sending spira reminder (cloud backup)...')
common.send_telegram_to_managers(managers, '\n'.join(tg_lines))
common.send_email_to_managers(managers, f'ריכוז ספירות 208 — {date_he} {now_il.strftime("%H:%M")}',
                               '\n'.join(html_lines))
