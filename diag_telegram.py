"""Diagnostic script to trace Telegram token source."""
import os
import json
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

print('=== Environment Variables (os.environ) ===')
print(f'TELEGRAM_BOT_TOKEN: {os.environ.get("TELEGRAM_BOT_TOKEN", "NOT SET")}')
print(f'TELEGRAM_CHAT_ID: {os.environ.get("TELEGRAM_CHAT_ID", "NOT SET")}')

print()
print('=== Checking .env files ===')
env_paths = [
    Path('.env'),
    Path('D:/MyProjectSpace/01_Workflows/agent-runner-v2/.env'),
]
for p in env_paths:
    if p.exists():
        print(f'Found: {p.resolve()}')
        content = p.read_text()
        for line in content.split('\n'):
            if 'TELEGRAM' in line.upper():
                print(f'  {line}')
    else:
        print(f'Not found: {p}')

print()
print('=== dotenv find_dotenv ===')
found = find_dotenv(usecwd=True)
print(f'find_dotenv found: {found}')

print()
print('=== config.json fallback ===')
cfg = Path.home() / '.ukbe-runner' / 'config.json'
if cfg.exists():
    c = json.loads(cfg.read_text())
    tg = c.get('notification', {}).get('telegram', {})
    print(f'telegram.enabled: {tg.get("enabled", "not set")}')
    print(f'telegram.bot_token: {tg.get("bot_token", "not set")}')
    print(f'telegram.chat_id: {tg.get("chat_id", "not set")}')
else:
    print('config.json not found')

print()
print('=== Parent process environment check ===')
print(f'PID: {os.getpid()}')
print(f'TELEGRAM_BOT_TOKEN in environ: {"TELEGRAM_BOT_TOKEN" in os.environ}')
print(f'TELEGRAM_CHAT_ID in environ: {"TELEGRAM_CHAT_ID" in os.environ}')
