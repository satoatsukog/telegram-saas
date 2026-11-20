import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///recalldeck.db")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0") or "0")
RUN_BOT = os.getenv("RUN_BOT", "") == "1"

AUTH_MAX_AGE_SECONDS = 24 * 60 * 60
FREE_DECKS = 2
FREE_CARDS = 60
PRICE_MONTHLY = int(os.getenv("PRICE_MONTHLY", "199"))
PRICE_YEARLY = int(os.getenv("PRICE_YEARLY", "1499"))
SUBSCRIPTION_PERIOD = 2592000
