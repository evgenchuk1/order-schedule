import os, json, sys, urllib.request
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ─── Israel time (auto DST: UTC+3 Mar-Oct, UTC+2 Nov-Feb) ──────────────────
_utc = datetime.now(timezone.utc)
IL_OFFSET = 3 if 3 <= _utc.month <= 10 else 2
now_il  = _utc + timedelta(hours=IL_OFFSET)
dow     = (now_il.weekday() + 1) % 7   # Sun=0, Mon=1 … Sat=6
cur_min = now_il.hour * 60 + now_il.minute
print(f'Israel time: {now_il.strftime("%A %H:%M")}  dow={dow}  UTC+{IL_OFFSET}')

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
    5: [], 6: [],
}

# ─── Timing config ───────────────────────────────────────────────────────────
REMIND_AT  = [40, 30, 20, 10, 0]   # minutes before deadline
POST_EVERY = 10                     # after deadline: repeat every N minutes
POST_MAX   = 120                    # stop after N minutes past deadline
WINDOW     = 9                      # match window (absorbs GitHub Actions cron jitter)

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
    dl = dl_to_min(item['dl'])

    # Pre-deadline: fire at dl-40, dl-30, dl-20, dl-10, dl
    fired = False
    for offset in REMIND_AT:
        if in_window(cur_min, dl - offset):
            groups[item['dl']].append((item, False))
            fired = True
            break

    if not fired:
        # Post-deadline: fire at dl+10, dl+20, … up to dl+POST_MAX
        mins_over = cur_min - dl
        if 0 < mins_over <= POST_MAX:
            slot_start = (mins_over // POST_EVERY) * POST_EVERY
            if in_window(cur_min, dl + slot_start):
                groups[item['dl']].append((item, True))

if not groups:
    print(f'Nothing due at {now_il.strftime("%H:%M")}. Exiting.')
    sys.exit(0)

# ─── Build and send one push per deadline slot ────────────────────────────────
APP_ID  = os.environ['ONESIGNAL_APP_ID']
API_KEY = os.environ['ONESIGNAL_API_KEY']

for dl_str, entries in groups.items():
    dl       = dl_to_min(dl_str)
    diff     = dl - cur_min
    is_over  = entries[0][1]

    if not is_over:
        if diff <= 1:
            title = f'⚠️ הזמן עכשיו! מועד אחרון — {dl_str}'
            sub   = f'הגיע הזמן! עד {dl_str}'
        else:
            title = f'📦 תזכורת הזמנה — עוד {diff} דקות'
            sub   = f'עד {dl_str} (נותרו {diff} דקות)'
    else:
        late = cur_min - dl
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

    payload = json.dumps({
        'app_id':                 APP_ID,
        'included_segments':      ['All'],
        'headings':               {'he': title, 'en': title},
        'contents':               {'he': body,  'en': body},
        'url':                    'https://evgenchuk1.github.io/order-schedule/',
        'priority':               10,
        'ios_interruption_level': 'time-sensitive',
        'ios_badgeType':          'Increase',
        'ios_badgeCount':         1,
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(
        'https://onesignal.com/api/v1/notifications',
        data=payload,
        headers={
            'Content-Type':  'application/json; charset=utf-8',
            'Authorization': f'Basic {API_KEY}',
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            r = json.loads(resp.read())
            print(f'Delivered to {r.get("recipients", 0)} device(s). id={r.get("id")}')
    except urllib.error.HTTPError as e:
        print(f'HTTP {e.code}: {e.read().decode()}')
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
