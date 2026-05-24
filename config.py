import os

CTFTIME_API = "https://ctftime.org/api/v1/events/"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
USER_AGENT  = "ctf-notifier/1.0 (contact: jjh4450git@gamil.com)"
DAYS_AHEAD  = int(os.environ.get("DAYS_AHEAD", "7"))
MAX_EVENTS  = int(os.environ.get("MAX_EVENTS", "20"))
DRY_RUN     = False
# DRY_RUN     = os.environ.get("DRY_RUN", "true").lower() == "true"
DB_PATH     = os.environ.get("CTF_DB_PATH", "./ctf_seen.db")
INTERVAL    = int(os.environ.get("INTERVAL", "0"))