"""Test notification with explicit token override."""
import os

# Force the new token BEFORE importing the module
os.environ["TELEGRAM_BOT_TOKEN"] = "8922911631:AAGcn9U7DoxukRzmDJzzl6yyrX3TkQGYACk"
os.environ["TELEGRAM_CHAT_ID"] = "1531706495"

from agent_runner_v2.notifications import send_notification

r = send_notification('COMPLETED', {
    'job_id': 'KAI-TEST-005',
    'workflow_name': 'connectivity_check_v5',
    'template_group': 'test'
})
print(f'Result: {r}')
