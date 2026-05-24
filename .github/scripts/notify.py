import os, json, urllib.request, datetime, sys

# שעון ישראל קיץ (IDT) = UTC + 3
# בחורף (נובמבר–מרץ) שנה IDT ל-IST: hours=2
now_il = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
h, m   = now_il.hour, now_il.minute
cur    = h * 60 + m

# Python: שני=0 … ראשון=6  →  JS/schedule: ראשון=0 … שבת=6
dow = (now_il.weekday() + 1) % 7

# לוז הזמנות: {יום: [(שעה, דקה, שם, אייקון), ...]}
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

orders     = SCH.get(dow, [])
to_notify  = []

for (dh, dm, name, icon) in orders:
    dl   = dh * 60 + dm
    diff = dl - cur
    if 25 <= diff <= 35:          # אזהרה ~30 דקות לפני
        to_notify.append((name, icon, f'עוד 30 דקות! עד {dh:02d}:{dm:02d}'))
    elif -5 <= diff <= 5:          # בדיוק בדדליין
        to_notify.append((name, icon, f'⚠️ הגיע הזמן! עד {dh:02d}:{dm:02d}'))

if not to_notify:
    print(f'[{now_il.strftime("%H:%M")} IDT, day={dow}] Nothing to notify.')
    sys.exit(0)

lines = [f'{icon} {name} — {msg}' for (name, icon, msg) in to_notify]
body  = '\n'.join(lines)
title = '📦 הזמנות סחורה'
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
