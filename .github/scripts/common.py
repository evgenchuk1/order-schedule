"""
Shared helpers for all notify_*.py scripts:
  - Firestore REST access (managers, daily done-state) — project expiry-tracker-ebf92,
    same one used by Expiry Tracker / Ticket Tracker, open rules (no auth needed).
  - Telegram send (personal chat per manager).
  - Gmail SMTP send (same pattern as trading/send_trading_daily.py).
"""
import json, urllib.request, urllib.error, smtplib
from email.mime.text import MIMEText

FIRESTORE_PROJECT = 'expiry-tracker-ebf92'
FIRESTORE_BASE = f'https://firestore.googleapis.com/v1/projects/{FIRESTORE_PROJECT}/databases/(default)/documents'

TELEGRAM_TOKEN = '8445627382:AAHtPl2bAWhkyiqdy29PgsoCBgGxyn8HWiI'

GMAIL_FROM    = 'evgenchuk1@gmail.com'
GMAIL_APP_PWD = 'rxhr cudb gwmm hsqw'

MGMT_ROLES = ['מנהל', 'סגן מנהל 1', 'סגן מנהל 2', 'סגן מנהל 3', 'קלדן', 'מנהל זמינות']


def _unwrap(value):
    """Convert a single Firestore REST typed value into a plain Python value."""
    if value is None:
        return None
    if 'stringValue' in value:
        return value['stringValue']
    if 'booleanValue' in value:
        return value['booleanValue']
    if 'integerValue' in value:
        return int(value['integerValue'])
    if 'doubleValue' in value:
        return value['doubleValue']
    if 'nullValue' in value:
        return None
    if 'mapValue' in value:
        return _unwrap_fields(value['mapValue'].get('fields', {}))
    if 'arrayValue' in value:
        return [_unwrap(v) for v in value['arrayValue'].get('values', [])]
    return None


def _unwrap_fields(fields):
    return {k: _unwrap(v) for k, v in fields.items()}


def _wrap(value):
    """Convert a plain Python value into a Firestore REST typed value."""
    if isinstance(value, bool):
        return {'booleanValue': value}
    if isinstance(value, int):
        return {'integerValue': str(value)}
    if isinstance(value, float):
        return {'doubleValue': value}
    if isinstance(value, dict):
        return {'mapValue': {'fields': {k: _wrap(v) for k, v in value.items()}}}
    if value is None:
        return {'nullValue': None}
    return {'stringValue': str(value)}


def firestore_get(path):
    """GET a document; returns plain dict of its fields, or {} if missing/error."""
    url = f'{FIRESTORE_BASE}/{path}'
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            doc = json.loads(resp.read())
            return _unwrap_fields(doc.get('fields', {}))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        print(f'Firestore GET error ({path}): {e}')
        return {}
    except Exception as e:
        print(f'Firestore GET error ({path}): {e}')
        return {}


def firestore_set(path, data):
    """PATCH (create-or-overwrite) a document with the given plain dict."""
    url = f'{FIRESTORE_BASE}/{path}'
    body = json.dumps({'fields': {k: _wrap(v) for k, v in data.items()}}).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='PATCH',
                                  headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
            return True
    except Exception as e:
        print(f'Firestore SET error ({path}): {e}')
        return False


def get_managers(branch):
    """Returns list of {name, phone, email, tgChatId} for all filled-in roles of a branch."""
    doc = firestore_get(f'schedule_managers/{branch}')
    roles = doc.get('roles', {}) or {}
    out = []
    for role in MGMT_ROLES:
        key = role.replace(' ', '_')
        m = roles.get(key) or {}
        if m.get('name') or m.get('email') or m.get('tgChatId'):
            out.append(m)
    return out


def get_daily_state(branch, date_str):
    return firestore_get(f'schedule_daily_state/{branch}_{date_str}')


def send_telegram(chat_id, text):
    if not chat_id:
        return False
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = json.dumps({'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'},
                       ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data,
                                  headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            r = json.loads(resp.read())
            print(f'Telegram -> {chat_id}: ok={r.get("ok")}')
            return bool(r.get('ok'))
    except Exception as e:
        print(f'Telegram error -> {chat_id}: {e}')
        return False


def send_telegram_to_managers(managers, text):
    for m in managers:
        if m.get('tgChatId'):
            send_telegram(m['tgChatId'], text)


def send_email(to_list, subject, body_html):
    to_list = [e for e in to_list if e]
    if not to_list:
        return False
    msg = MIMEText(body_html, 'html', 'utf-8')
    msg['From'] = GMAIL_FROM
    msg['To'] = ', '.join(to_list)
    msg['Subject'] = subject
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, local_hostname='localhost') as smtp:
            smtp.login(GMAIL_FROM, GMAIL_APP_PWD)
            smtp.sendmail(GMAIL_FROM, to_list, msg.as_string())
        print(f'Email -> {to_list}: ok')
        return True
    except Exception as e:
        print(f'Email error -> {to_list}: {e}')
        return False


def send_email_to_managers(managers, subject, body_html):
    emails = [m.get('email') for m in managers if m.get('email')]
    return send_email(emails, subject, body_html)
