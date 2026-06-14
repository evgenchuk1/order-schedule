"""
Runs on GitHub Actions (cloud). No state file — deduplication is handled
by the cron schedule itself (one job per time slot).
Sends:
  - Morning summary at ~06:30 IL time
  - Hourly reminder at ~07:30-13:30 IL time
No proximity reminders (those need 5-min precision → Task Scheduler on PC).
"""
import json, sys, urllib.request
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── Israel time ─────────────────────────────────────────────────────────────
_utc = datetime.now(timezone.utc)
IL_OFFSET = 3 if 3 <= _utc.month <= 10 else 2
now_il  = _utc + timedelta(hours=IL_OFFSET)
dow     = (now_il.weekday() + 1) % 7   # Sun=0 … Sat=6
cur_min = now_il.hour * 60 + now_il.minute
print(f'Israel time: {now_il.strftime("%A %Y-%m-%d %H:%M")}  dow={dow}  UTC+{IL_OFFSET}')

# ─── Telegram ────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = '8445627382:AAHtPl2bAWhkyiqdy29PgsoCBgGxyn8HWiI'
TELEGRAM_CHAT_ID = '8290509506'

def send_telegram(text):
    url  = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = json.dumps({'chat_id': TELEGRAM_CHAT_ID, 'text': text,
                       'parse_mode': 'HTML'},
                      ensure_ascii=False).encode('utf-8')
    req  = urllib.request.Request(url, data=data,
                                  headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            r = json.loads(resp.read())
            print(f'Telegram ok, msg_id={r.get("result",{}).get("message_id")}')
    except Exception as e:
        print(f'Telegram error: {e}')
        sys.exit(1)

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

def dl_to_min(s):
    h, m = map(int, s.split(':'))
    return h * 60 + m

orders = SCH.get(dow, [])
if not orders:
    print('No orders today (Friday/Saturday or empty day). Exiting.')
    sys.exit(0)

# ─── Decide what to send based on current IL time ────────────────────────────
MORNING_MIN = 6 * 60 + 30   # 06:30
HOURLY_MINS = [h * 60 + 30 for h in range(7, 14)]  # 07:30 … 13:30

# Morning summary: job is scheduled at 06:30 IL, just send it
if cur_min < 7 * 60:
    day_names = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
    lines = [
        f'<b>☀️ בוקר טוב! לוז ספירות ליום {day_names[dow]} — {now_il.strftime("%d/%m/%Y")}</b>',
        f'<i>📡 GitHub Cloud • {now_il.strftime("%H:%M")}</i>',
        '',
    ]
    for item in orders:
        line = f"{item['ic']} <b>{item['nm']}</b>  ·  עד {item['dl']}"
        if item['nt']:
            line += f"  ·  {item['nt']}"
        lines.append(line)
    lines += ['', f'סה"כ {len(orders)} ספירות היום']
    print('Sending morning summary...')
    send_telegram('\n'.join(lines))

# Hourly reminder: job scheduled at H:30, send reminder of remaining orders
else:
    upcoming = [it for it in orders if dl_to_min(it['dl']) > cur_min]
    passed   = [it for it in orders if dl_to_min(it['dl']) <= cur_min]
    lines = [
        f'<b>⏰ תזכורת שעתית — {now_il.strftime("%H:%M")}</b>',
        f'<i>📡 GitHub Cloud</i>',
        '',
    ]
    if upcoming:
        lines.append('<b>📋 ממתין לביצוע:</b>')
        for it in upcoming:
            diff = dl_to_min(it['dl']) - cur_min
            lines.append(f"  {it['ic']} {it['nm']}  ·  עד {it['dl']}  ({diff} דק׳)")
    if passed:
        lines += ['', '<b>✅ אמור להיות בוצע:</b>']
        for it in passed:
            lines.append(f"  {it['ic']} {it['nm']}  ·  היה עד {it['dl']}")
    if not upcoming and not passed:
        lines.append('אין ספירות היום')
    print(f'Sending hourly reminder ({now_il.strftime("%H:%M")})...')
    send_telegram('\n'.join(lines))
