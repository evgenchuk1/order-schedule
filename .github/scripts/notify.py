import os, json, urllib.request, sys, datetime

trigger = ' '.join(os.environ.get('TRIGGER_SCHEDULE', '').split())
now_il  = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
dow     = (now_il.weekday() + 1) % 7   # Sun=0 … Sat=6

# Map cron-string → 'digest' | (deadline_hour, is_warning)
SLOT_MAP = {
    '30 4 * * 0,1,2,3,4,5': 'digest',
    # warn 30 min before deadline
    '30 5 * * 0,1,2,3':   (9,  True),
    '30 5 * * 5':          (9,  True),
    '30 6 * * 0,1,2,3':   (10, True),
    '30 6 * * 5':          (10, True),
    '30 7 * * 0,1,2,3,4': (11, True),
    '30 8 * * 0,1,2,3,4': (12, True),
    '30 9 * * 2,4':        (13, True),
    # at deadline
    '0 6 * * 0,1,2,3':    (9,  False),
    '0 6 * * 5':           (9,  False),
    '0 7 * * 0,1,2,3':    (10, False),
    '0 7 * * 5':           (10, False),
    '0 8 * * 0,1,2,3,4':  (11, False),
    '0 9 * * 0,1,2,3,4':  (12, False),
    '0 10 * * 2,4':        (13, False),
}

SCH = {
    0: [  # ראשון — Sunday
        ( 9, 0, 'עופות',                 '🐔'),
        (10, 0, 'שוהם ירקות',            '🥦'),
        (10, 0, 'שוהם מצוננים',          '🧀'),
        (11, 0, 'קוקה קולה',             '🍾'),
        (11, 0, 'טמפו',                  '🍾'),
        (11, 0, 'יפאורה',                '🍵'),
        (12, 0, 'מודיעין מכולת / Green', '🥫'),
        (12, 0, 'פארם',                  '🧴'),
    ],
    1: [  # שני — Monday
        ( 9, 0, 'עופות',                 '🐔'),
        (10, 0, 'שוהם ירקות',            '🥦'),
        (11, 0, 'יפאורה',                '🍵'),
        (12, 0, 'רשל"ץ כלי ניקיון',     '🧹'),
        (12, 0, 'משוקלדים',              '🍫'),
    ],
    2: [  # שלישי — Tuesday
        ( 9, 0, 'עופות',                 '🐔'),
        (10, 0, 'שוהם ירקות',            '🥦'),
        (11, 0, 'קוקה קולה',             '🍾'),
        (11, 0, 'טמפו',                  '🍾'),
        (12, 0, 'מודיעין מכולת / Green', '🥫'),
        (12, 0, 'רשל"ץ כלי ניקיון',     '🧹'),
        (12, 0, 'פארם',                  '🧴'),
        (12, 0, 'משוקלדים',              '🍫'),
        (13, 0, 'מאפית',                 '🍞'),
    ],
    3: [  # רביעי — Wednesday
        ( 9, 0, 'עופות',                 '🐔'),
        (10, 0, 'שוהם ירקות',            '🥦'),
        (10, 0, 'שוהם מצוננים',          '🧀'),
        (11, 0, 'יפאורה',                '🍵'),
        (12, 0, 'מודיעין מכולת / Green', '🥫'),
        (12, 0, 'רשל"ץ כלי ניקיון',     '🧹'),
        (12, 0, 'משוקלדים',              '🍫'),
    ],
    4: [  # חמישי — Thursday
        (11, 0, 'טמפו',                  '🍾'),
        (12, 0, 'מודיעין מכולת / Green', '🥫'),
        (12, 0, 'רשל"ץ כלי ניקיון',     '🧹'),
        (12, 0, 'פארם',                  '🧴'),
        (12, 0, 'משוקלדים',              '🍫'),
        (13, 0, 'מאפית',                 '🍞'),
    ],
    5: [  # שישי — Friday
        ( 9, 0, 'שוהם ירקות',            '🥦'),
        (10, 0, 'ירקות Green יבולי בר',  '🌿'),
    ],
}

DAY_HE = {0:'ראשון', 1:'שני', 2:'שלישי', 3:'רביעי', 4:'חמישי', 5:'שישי', 6:'שבת'}

orders = SCH.get(dow, [])
slot   = SLOT_MAP.get(trigger)

print(f'trigger={repr(trigger)}  slot={slot}  dow={dow}  time={now_il.strftime("%H:%M")} IDT')

if slot is None:
    print('Unknown trigger — nothing to send.')
    sys.exit(0)

if slot == 'digest':
    if not orders:
        print('No orders today.')
        sys.exit(0)
    lines = [f'יום {DAY_HE[dow]} — הזמנות היום:']
    for (dh, dm, name, icon) in orders:
        lines.append(f'{icon} {name} — עד {dh:02d}:{dm:02d}')
    title = '📦 הזמנות סחורה — בוקר טוב'
    body  = '\n'.join(lines)
else:
    target_h, is_warning = slot
    matched = [(name, icon) for (dh, dm, name, icon) in orders if dh == target_h]
    if not matched:
        print(f'No orders at {target_h}:00 today (dow={dow}).')
        sys.exit(0)
    if is_warning:
        msg = f'עוד 30 דקות! עד {target_h:02d}:00'
    else:
        msg = f'⚠️ הגיע הזמן! עד {target_h:02d}:00'
    lines = [f'{icon} {name} — {msg}' for (name, icon) in matched]
    title = '📦 הזמנות סחורה'
    body  = '\n'.join(lines)

print(f'Sending:\n{body}')

payload = json.dumps({
    'app_id':            os.environ['ONESIGNAL_APP_ID'],
    'included_segments': ['All'],
    'headings':  {'he': title, 'en': title},
    'contents':  {'he': body,  'en': body},
    'url':       'https://evgenchuk1.github.io/order-schedule/',
    'priority':  10,
}).encode()

req = urllib.request.Request(
    'https://onesignal.com/api/v1/notifications',
    data=payload,
    headers={
        'Content-Type':  'application/json',
        'Authorization': f'Basic {os.environ["ONESIGNAL_API_KEY"]}',
    }
)
with urllib.request.urlopen(req) as resp:
    r = json.loads(resp.read())
    print(f'Sent to {r.get("recipients", 0)} device(s). id={r.get("id")}')
