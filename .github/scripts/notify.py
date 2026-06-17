import json, sys, urllib.request
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

# Force UTF-8 output + tee to log file
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

LOG_FILE = Path(__file__).resolve().parent.parent.parent / 'notify.log'

class _Tee:
    def __init__(self, *streams): self._s = streams
    def write(self, d):
        for s in self._s: s.write(d)
    def flush(self):
        for s in self._s: s.flush()

try:
    _log = open(LOG_FILE, 'a', encoding='utf-8')
    sys.stdout = _Tee(sys.stdout, _log)
    sys.stderr = _Tee(sys.stderr, _log)
except Exception:
    pass

# ─── Israel time (auto DST: UTC+3 Mar-Oct, UTC+2 Nov-Feb) ──────────────────
_utc = datetime.now(timezone.utc)
IL_OFFSET = 3 if 3 <= _utc.month <= 10 else 2
now_il  = _utc + timedelta(hours=IL_OFFSET)
dow     = (now_il.weekday() + 1) % 7   # Sun=0, Mon=1 … Sat=6
cur_min = now_il.hour * 60 + now_il.minute
today_str = now_il.strftime('%Y-%m-%d')
print(f'Israel time: {now_il.strftime("%A %Y-%m-%d %H:%M")}  dow={dow}  UTC+{IL_OFFSET}')

# ─── State file (prevents duplicates across multiple runs in the same window) ─
STATE_FILE = Path(__file__).resolve().parent.parent.parent / 'notify_state.json'

def load_state():
    try:
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'Warning: could not save state: {e}')

state = load_state()
today_fired = state.get(today_str, {})

BRANCH = '208'
managers = common.get_managers(BRANCH)

# ─── Schedule (must match index.html SCH exactly) ───────────────────────────
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

# ─── Timing config ───────────────────────────────────────────────────────────
REMIND_AT  = [60, 45, 30, 15]   # minutes before deadline — exactly these 4, nothing after
WINDOW     = 7                  # match window — slightly wider than cron interval

def dl_to_min(s):
    h, m = map(int, s.split(':'))
    return h * 60 + m

def in_window(cur, target):
    """True if cur is in [target, target+WINDOW)"""
    return 0 <= cur - target < WINDOW

orders = SCH.get(dow, [])

# ─── Morning summary (06:30) — Telegram (personal) + Email ──────────────────
MORNING_MIN = 6 * 60 + 30   # 06:30
if orders and in_window(cur_min, MORNING_MIN):
    key = f'morning|{today_str}'
    if key not in today_fired:
        today_fired[key] = now_il.strftime('%H:%M')
        day_names = ['ראשון', 'שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת']
        tg_lines = [f'<b>☀️ בוקר טוב! לוז הזמנות ליום {day_names[dow]} — {now_il.strftime("%d/%m/%Y")}</b>', '']
        html_lines = [f'<h3>☀️ בוקר טוב! לוז הזמנות ליום {day_names[dow]} — {now_il.strftime("%d/%m/%Y")}</h3>']
        for item in orders:
            line = f"{item['ic']} <b>{item['nm']}</b>  ·  עד {item['dl']}"
            if item['nt']:
                line += f"  ·  {item['nt']}"
            tg_lines.append(line)
            html_lines.append(f'<p>{line}</p>')
        tg_lines.append('')
        tg_lines.append(f'סה"כ {len(orders)} הזמנות היום')
        html_lines.append(f'<p>סה"כ {len(orders)} הזמנות היום</p>')
        print('--- Morning summary ---')
        common.send_telegram_to_managers(managers, '\n'.join(tg_lines))
        common.send_email_to_managers(managers, f'לוז הזמנות 208 — {day_names[dow]} {now_il.strftime("%d/%m/%Y")}',
                                       '\n'.join(html_lines))

# ─── Early exit if no orders today ───────────────────────────────────────────
if not orders:
    save_state({today_str: today_fired})
    print('No orders today. Exiting.')
    sys.exit(0)

# ─── Find due proximity reminders — Telegram only, exactly REMIND_AT offsets ─
groups = defaultdict(list)   # dl_str → [item, ...]

for item in orders:
    dl  = dl_to_min(item['dl'])
    nm  = item['nm']
    dl_s = item['dl']

    for offset in REMIND_AT:
        if in_window(cur_min, dl - offset):
            key = f'{nm}|{dl_s}|r{offset}'
            if key not in today_fired:
                today_fired[key] = now_il.strftime('%H:%M')
                groups[dl_s].append(item)
            break

if not groups:
    save_state({today_str: today_fired})
    print(f'Nothing due at {now_il.strftime("%H:%M")}. Exiting.')
    sys.exit(0)

# ─── Build and send one notification per deadline slot (Telegram only) ───────
for dl_str, entries in groups.items():
    dl   = dl_to_min(dl_str)
    diff = dl - cur_min

    title = f'📦 תזכורת הזמנה — עוד {diff} דקות' if diff > 1 else f'⚠️ הזמן עכשיו! מועד אחרון — {dl_str}'
    sub   = f'עד {dl_str} (נותרו {diff} דקות)' if diff > 1 else f'הגיע הזמן! עד {dl_str}'

    tg_lines = [f'<b>📋 הזמנות 208 — {title}</b>', '', sub]
    for item in entries:
        line = f"{item['ic']} <b>{item['nm']}</b>"
        if item['nt']:
            line += f"  · {item['nt']}"
        tg_lines.append(line)
    print(f'--- Sending proximity reminder ({dl_str}, -{diff}m) ---')
    common.send_telegram_to_managers(managers, '\n'.join(tg_lines))

# Save state only after all notifications sent successfully
save_state({today_str: today_fired})
