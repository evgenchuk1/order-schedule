#!/usr/bin/env python3
"""
One-off onboarding helper: ask a manager to send any message to the bot
(@-mention or just "hi"), then run this script — it prints chat_id + name
for everyone who has messaged the bot recently. Copy the chat_id into
spira.html's hanhala (management) UI, Telegram Chat ID field, for that role.
"""
import json, sys, urllib.request
sys.path.insert(0, __file__.rsplit('\\', 1)[0])
import common

url = f'https://api.telegram.org/bot{common.TELEGRAM_TOKEN}/getUpdates'
with urllib.request.urlopen(url, timeout=15) as resp:
    data = json.loads(resp.read())

if not data.get('ok'):
    print('Telegram API error:', data)
    sys.exit(1)

seen = {}
for upd in data.get('result', []):
    msg = upd.get('message') or upd.get('channel_post')
    if not msg:
        continue
    chat = msg.get('chat', {})
    chat_id = chat.get('id')
    name = ' '.join(filter(None, [chat.get('first_name'), chat.get('last_name')])) or chat.get('title') or '?'
    text = msg.get('text', '')
    seen[chat_id] = (name, text)

if not seen:
    print('No messages found. Ask the manager to send any message to the bot first, then run this again.')
else:
    print(f'{"chat_id":<16} {"name":<25} last message')
    print('-' * 70)
    for chat_id, (name, text) in seen.items():
        print(f'{chat_id:<16} {name:<25} {text[:40]}')
