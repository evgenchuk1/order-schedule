"""
Runs on GitHub Actions (cloud). No state file — deduplication is handled
by the cron schedule itself (one job per time slot).
Sends only the 06:30 morning summary (Telegram personal + Email) — the
15-min-precision proximity reminders need Task Scheduler on PC, see notify.py.
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Israel time ─────────────────────────────────────────────────────────────
_utc = datetime.now(timezone.utc)
IL_OFFSET = 3 if 3 <= _utc.month <= 10 else 2
now_il  = _utc + timedelta(hours=IL_OFFSET)
dow     = (now_il.weekday() + 1) % 7   # Sun=0 … Sat=6
print(f'Israel time: {now_il.strftime("%A %Y-%m-%d %H:%M")}  dow={dow}  UTC+{IL_OFFSET}')

BRANCH = '208'
managers = common.get_managers(BRANCH)

# ─── Schedule ─────────────────────────────────────────────────────────────────
SCH = {
    0: [  # Sunday
        {'nm': 'שוהם מצוננים 6031',           'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם קטיף 6032',              'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'ראשון לציון 6000',            'dl': '12:05', 'ic': '🏭', 'nt': 'מכולת / מאפית / פארם'},
        {'nm': 'שוהם קטיף — משוקלד',         'dl': '12:05', 'ic': '🍫', 'nt': 'משוקלד'},
        {'nm': 'שטראוס גרופ (מצונן)',         'dl': '12:00', 'ic': '🧀', 'nt': 'מוצרי חלב מצוננים'},
        {'nm': 'תנובה — אגף החלב',            'dl': '13:00', 'ic': '🥛', 'nt': 'חלב / מוצרי חלב'},
        {'nm': 'טרה — משקאות',                'dl': '15:00', 'ic': '🧃', 'nt': ''},
    ],
    1: [  # Monday
        {'nm': 'שוהם מצוננים 6031',           'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',           'dl': '10:05', 'ic': '🥩', 'nt': 'בשר / חלב / נקניקים'},
        {'nm': 'שוהם קטיף 6032',              'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'מודיעין 6030',                'dl': '12:05', 'ic': '🏪', 'nt': 'גרין / מכולת / פארם'},
        {'nm': 'שטראוס גרופ (מצונן)',         'dl': '12:00', 'ic': '🧀', 'nt': 'מוצרי חלב מצוננים'},
        {'nm': 'יפאורה',                       'dl': '15:00', 'ic': '🍵', 'nt': ''},
    ],
    2: [  # Tuesday
        {'nm': 'שוהם מצוננים 6031',           'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',           'dl': '10:05', 'ic': '🥐', 'nt': 'חומרי עזר מאפית'},
        {'nm': 'שוהם קטיף 6032',              'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'ראשון לציון 6000',            'dl': '12:05', 'ic': '🏭', 'nt': 'מכולת / מאפית / פארם'},
        {'nm': 'לב הארץ 6047',               'dl': '12:05', 'ic': '🌿', 'nt': 'גרין / מכולת / פארם / משוקלד'},
        {'nm': 'שטראוס גרופ (מצונן)',         'dl': '12:00', 'ic': '🧀', 'nt': 'מוצרי חלב מצוננים'},
        {'nm': 'טמפו',                         'dl': '13:00', 'ic': '🍾', 'nt': ''},
        {'nm': 'תנובה — אגף החלב',            'dl': '13:00', 'ic': '🥛', 'nt': 'חלב / מוצרי חלב'},
        {'nm': 'שוהם קפואים 6033',            'dl': '13:05', 'ic': '❄️', 'nt': 'קפואים + חומ"ז מאפית'},
        {'nm': 'טרה — משקאות',                'dl': '15:00', 'ic': '🧃', 'nt': ''},
        {'nm': 'קוקה קולה',                   'dl': '17:00', 'ic': '🥤', 'nt': ''},
    ],
    3: [  # Wednesday
        {'nm': 'שוהם מצוננים 6031',           'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',           'dl': '10:05', 'ic': '🥩', 'nt': 'בשר / חלב / נקניקים'},
        {'nm': 'שוהם קטיף 6032',              'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'מודיעין 6030',                'dl': '12:05', 'ic': '🏪', 'nt': 'גרין / מכולת / פארם'},
        {'nm': 'שטראוס גרופ (מצונן)',         'dl': '12:00', 'ic': '🧀', 'nt': 'מוצרי חלב מצוננים'},
        {'nm': 'שוהם קטיף — משוקלד',         'dl': '12:05', 'ic': '🍫', 'nt': 'משוקלד'},
        {'nm': 'תנובה — אגף החלב',            'dl': '13:00', 'ic': '🥛', 'nt': 'חלב / מוצרי חלב'},
        {'nm': 'יפאורה',                       'dl': '15:00', 'ic': '🍵', 'nt': ''},
    ],
    4: [  # Thursday
        {'nm': 'שוהם מצוננים 6031',           'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',           'dl': '10:05', 'ic': '🥐', 'nt': 'חומרי עזר מאפית'},
        {'nm': 'שוהם קטיף 6032',              'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'ראשון לציון 6000',            'dl': '12:05', 'ic': '🏭', 'nt': 'מכולת / מאפית / פארם'},
        {'nm': 'לב הארץ 6047',               'dl': '12:05', 'ic': '🌿', 'nt': 'גרין / מכולת / פארם / משוקלד'},
        {'nm': 'טמפו',                         'dl': '13:00', 'ic': '🍾', 'nt': ''},
        {'nm': 'שוהם קפואים 6033',            'dl': '13:05', 'ic': '❄️', 'nt': 'קפואים + חומ"ז מאפית'},
        {'nm': 'קוקה קולה',                   'dl': '18:00', 'ic': '🥤', 'nt': ''},
        {'nm': 'תנובה — אגף החלב',            'dl': '19:00', 'ic': '🥛', 'nt': 'חלב / מוצרי חלב'},
    ],
    5: [  # Friday
        {'nm': 'שטראוס גרופ (מצונן)',         'dl': '10:00', 'ic': '🧀', 'nt': 'מוצרי חלב מצוננים'},
    ],
    6: [],
}

orders = SCH.get(dow, [])
if not orders:
    print('No orders today (Friday/Saturday or empty day). Exiting.')
    sys.exit(0)

day_names = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
tg_lines = [f'<b>☀️ בוקר טוב! לוז הזמנות ליום {day_names[dow]} — {now_il.strftime("%d/%m/%Y")}</b>',
            '<i>📡 GitHub Cloud</i>', '']
html_lines = [f'<h3>☀️ בוקר טוב! לוז הזמנות ליום {day_names[dow]} — {now_il.strftime("%d/%m/%Y")}</h3>']
for item in orders:
    line = f"{item['ic']} <b>{item['nm']}</b>  ·  עד {item['dl']}"
    if item['nt']:
        line += f"  ·  {item['nt']}"
    tg_lines.append(line)
    html_lines.append(f'<p>{line}</p>')
tg_lines += ['', f'סה"כ {len(orders)} הזמנות היום']
html_lines.append(f'<p>סה"כ {len(orders)} הזמנות היום</p>')

print('Sending morning summary (cloud backup)...')
common.send_telegram_to_managers(managers, '\n'.join(tg_lines))
common.send_email_to_managers(managers, f'לוז הזמנות 208 — {day_names[dow]} {now_il.strftime("%d/%m/%Y")}',
                               '\n'.join(html_lines))
