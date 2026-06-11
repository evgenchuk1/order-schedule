import json, sys, urllib.request
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

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

# ─── Channels ────────────────────────────────────────────────────────────────
NTFY_TOPIC       = 'hazmana-208-nahal-ora'
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            r = json.loads(resp.read())
            print(f'Telegram: ok={r.get("ok")}  msg_id={r.get("result",{}).get("message_id")}')
    except Exception as e:
        print(f'Telegram error: {e}')

# ─── Schedule (must match index.html SCH exactly) ───────────────────────────
SCH = {
    0: [  # Sunday
        {'nm': 'שוהם מצוננים 6031',    'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם קטיף 6032',       'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'ראשון לציון 6000',     'dl': '12:05', 'ic': '🏭', 'nt': 'מכולת / מאפית / פארם / NF'},
        {'nm': 'שוהם קטיף — משוקלד',  'dl': '12:05', 'ic': '🍫', 'nt': 'משוקלד'},
    ],
    1: [  # Monday
        {'nm': 'שוהם מצוננים 6031',    'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',    'dl': '10:05', 'ic': '🥩', 'nt': 'בשר / חלב / נקניקים'},
        {'nm': 'שוהם קטיף 6032',       'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'מודיעין 6030',          'dl': '12:05', 'ic': '🏪', 'nt': 'גרין / מכולת / פארם / NF'},
        {'nm': 'יפאורה',                'dl': '15:00', 'ic': '🍵', 'nt': ''},
    ],
    2: [  # Tuesday
        {'nm': 'שוהם מצוננים 6031',    'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',    'dl': '10:05', 'ic': '🥐', 'nt': 'חומרי עזר מאפית'},
        {'nm': 'שוהם קטיף 6032',       'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'ראשון לציון 6000',     'dl': '12:05', 'ic': '🏭', 'nt': 'מכולת / מאפית / פארם / NF'},
        {'nm': 'לב הארץ 6047',         'dl': '12:05', 'ic': '🌿', 'nt': 'גרין / מכולת / פארם / NF / משוקלד'},
        {'nm': 'טמפו',                  'dl': '13:00', 'ic': '🍾', 'nt': ''},
        {'nm': 'שוהם קפואים 6033',     'dl': '13:05', 'ic': '❄️', 'nt': 'קפואים + חומ"ז מאפית'},
        {'nm': 'קוקה קולה',             'dl': '17:00', 'ic': '🥤', 'nt': ''},
    ],
    3: [  # Wednesday
        {'nm': 'שוהם מצוננים 6031',    'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',    'dl': '10:05', 'ic': '🥩', 'nt': 'בשר / חלב / נקניקים'},
        {'nm': 'שוהם קטיף 6032',       'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'מודיעין 6030',          'dl': '12:05', 'ic': '🏪', 'nt': 'גרין / מכולת / פארם / NF'},
        {'nm': 'שוהם קטיף — משוקלד',  'dl': '12:05', 'ic': '🍫', 'nt': 'משוקלד'},
        {'nm': 'יפאורה',                'dl': '15:00', 'ic': '🍵', 'nt': ''},
    ],
    4: [  # Thursday
        {'nm': 'שוהם מצוננים 6031',    'dl': '09:05', 'ic': '🐔', 'nt': 'עוף טרי'},
        {'nm': 'שוהם מצוננים 6031',    'dl': '10:05', 'ic': '🥐', 'nt': 'חומרי עזר מאפית'},
        {'nm': 'שוהם קטיף 6032',       'dl': '10:05', 'ic': '🧊', 'nt': '15° / 4° / מכולת'},
        {'nm': 'ראשון לציון 6000',     'dl': '12:05', 'ic': '🏭', 'nt': 'מכולת / מאפית / פארם / NF'},
        {'nm': 'לב הארץ 6047',         'dl': '12:05', 'ic': '🌿', 'nt': 'גרין / מכולת / פארם / NF / משוקלד'},
        {'nm': 'טמפו',                  'dl': '13:00', 'ic': '🍾', 'nt': ''},
        {'nm': 'שוהם קפואים 6033',     'dl': '13:05', 'ic': '❄️', 'nt': 'קפואים + חומ"ז מאפית'},
        {'nm': 'קוקה קולה',             'dl': '18:00', 'ic': '🥤', 'nt': ''},
    ],
    5: [],
    6: [  # Saturday — TEST ONLY, remove after testing
        {'nm': 'פרארי',   'dl': '23:00', 'ic': '🏎️', 'nt': 'טסט'},
        {'nm': 'מזראטי',  'dl': '00:00', 'ic': '🏎️', 'nt': 'טסט'},
    ],
}

# ─── One-time test order: Ferrari today only ─────────────────────────────────
if today_str == '2026-06-11':
    SCH[4].insert(0, {'nm': 'פרארי — טסט חד פעמי', 'dl': '11:00', 'ic': '🏎️', 'nt': 'הזמנת בדיקה'})

# ─── Timing config ───────────────────────────────────────────────────────────
REMIND_AT  = [40, 35, 30, 25, 20, 15, 10, 5, 0]   # minutes before deadline
POST_EVERY = 5                      # after deadline: repeat every N minutes
POST_MAX   = 120                    # stop after N minutes past deadline
WINDOW     = 7                      # match window — slightly wider than cron interval

def dl_to_min(s):
    h, m = map(int, s.split(':'))
    return h * 60 + m

def in_window(cur, target):
    """True if cur is in [target, target+WINDOW)"""
    return 0 <= cur - target < WINDOW

# ─── Find due reminders ───────────────────────────────────────────────────────
orders = SCH.get(dow, [])
if not orders:
    print('No orders today. Exiting.')
    sys.exit(0)

groups = defaultdict(list)   # dl_str → [(item, is_overdue)]

for item in orders:
    dl  = dl_to_min(item['dl'])
    nm  = item['nm']
    dl_s = item['dl']

    for offset in REMIND_AT:
        if in_window(cur_min, dl - offset):
            key = f'{nm}|{dl_s}|r{offset}'
            if key not in today_fired:
                today_fired[key] = now_il.strftime('%H:%M')
                groups[dl_s].append((item, False))
            break

    mins_over = cur_min - dl
    if 0 < mins_over <= POST_MAX:
        slot_start = (mins_over // POST_EVERY) * POST_EVERY
        if in_window(cur_min, dl + slot_start):
            key = f'{nm}|{dl_s}|p{slot_start}'
            if key not in today_fired:
                today_fired[key] = now_il.strftime('%H:%M')
                groups[dl_s].append((item, True))

if not groups:
    save_state({today_str: today_fired})
    print(f'Nothing due at {now_il.strftime("%H:%M")}. Exiting.')
    sys.exit(0)

# ─── Build and send one notification per deadline slot ───────────────────────
for dl_str, entries in groups.items():
    dl      = dl_to_min(dl_str)
    diff    = dl - cur_min
    is_over = any(e[1] for e in entries)

    if not is_over:
        if diff <= 1:
            title = f'⚠️ הזמן עכשיו! מועד אחרון — {dl_str}'
            sub   = f'הגיע הזמן! עד {dl_str}'
        else:
            title = f'📦 תזכורת הזמנה — עוד {diff} דקות'
            sub   = f'עד {dl_str} (נותרו {diff} דקות)'
    else:
        late  = cur_min - dl
        title = f'🚨 עבר המועד! {dl_str} — לפני {late} דק׳'
        sub   = f'⚠️ איחור {late} דקות — הזמן מיד!'

    item_lines = []
    for (item, _) in entries:
        line = f"{item['ic']} {item['nm']}"
        if item['nt']:
            line += f"  ·  {item['nt']}"
        item_lines.append(line)

    body = sub + '\n' + '\n'.join(item_lines)
    print(f'--- Sending ---\n{title}\n{body}\n')

    # ── ntfy.sh ──────────────────────────────────────────────────────────────
    payload = json.dumps({
        'topic':    NTFY_TOPIC,
        'title':    title,
        'message':  body,
        'priority': 5,
        'tags':     ['rotating_light'],
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(
        'https://ntfy.sh',
        data=payload,
        headers={'Content-Type': 'application/json; charset=utf-8'},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            r = json.loads(resp.read())
            print(f'ntfy: id={r.get("id")}')
    except Exception as e:
        print(f'ntfy error: {e}')

    # ── Telegram (reliable native iOS push via APNS) ─────────────────────────
    tg_lines = [f'<b>📋 הזמנות 208 — {title}</b>', '']
    for (item, _) in entries:
        line = f"{item['ic']} <b>{item['nm']}</b>"
        if item['nt']:
            line += f"  · {item['nt']}"
        tg_lines.append(line)
    send_telegram('\n'.join(tg_lines))

# Save state only after all notifications sent successfully
save_state({today_str: today_fired})
