import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///recalldeck.db")
AUTH_MAX_AGE_SECONDS = 24 * 60 * 60
