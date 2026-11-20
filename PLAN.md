# PLAN.md — RecallDeck build (Steps 3–8)

Steps 1 (research) and 2 (spec) are done. Each step below ends with the git workflow in
project rules (local): show `git status` + summary, propose a commit message, **wait for "ok push"**.
Scope is fixed by `PRD.md` (MVP IN/OUT). Build nothing from the OUT list.

---

## Step 3 — Bot + DB + SM-2 (with tests)
**Goal:** working bot skeleton, data model, and a tested scheduling core — no Mini App yet.
- Project scaffold: `backend/` per project rules (local), `requirements.txt`, `.env.example`.
- DB models (SQLAlchemy async, SQLite): `users` (id=tg user_id, tz, reminder_hour,
  `last_reminded_on` date, premium_until, created_at, source), `decks`, `cards` (front,
  back, ease, interval, repetitions, due_at), `events` (append-only),
  `payments` (telegram_payment_charge_id UNIQUE).
- `core/sm2.py`: pure SM-2 function `schedule(card, grade)` for grades Again/Good/Easy
  (q=2/4/5); Again resets repetitions and interval→1.
- `core/deep_link.py`: parse `/start=<source>` → store `source`, emit `start(source)` event.
- `core/list_parser.py`: split each line **only** on a separator surrounded by spaces
  (`" - "`, `" — "`, `" – "`) **or** on the **first** `":"`; never on a bare `-`/`—`
  inside a word. First match wins; trim both sides; skip blank/unparseable lines.
- `app/bot_runner.py`: separate entrypoint running aiogram polling (scheduler added in Step 4).
- Bot handlers: `/start` (greeting + "Open RecallDeck" web_app button), `/paysupport`.
- **Tests (pytest):** SM-2 transitions (incl. lapse), deep-link source parsing, and list
  parser incl. **`"well-known - famous"` → (`well-known`, `famous`)**,
  **`"self-esteem — confidence"` → (`self-esteem`, `confidence`)**,
  **`"ratio: a:b relation"` → (`ratio`, `a:b relation`)**. Pass before moving on.
- Run the bot via `python -m app.bot_runner`; confirm `/start` replies with the Mini App button.

## Step 4 — Mini App (React)
**Goal:** the full core loop playable end-to-end against the API.
- `frontend/` scaffold: Vite + React + TS + Tailwind + `@telegram-apps/sdk-react`.
- On first open: read timezone via `Intl.DateTimeFormat().resolvedOptions().timeZone`,
  POST to settings; default reminder hour 19:00 local.
- Screens: Home (decks, due count, streak, stats), Deck (cards CRUD), **Paste-a-list**
  onboarding (primary), manual add + CSV import (secondary), Review (one card, 3 buttons
  Again/Good/Easy, flip to reveal back).
- API (FastAPI) with **initData validation on every call**: decks/cards CRUD, start-review,
  grade-card, stats, settings, events.
- APScheduler (inside `bot_runner`, not FastAPI): **one job every hour** that selects users
  whose **local hour == reminder_hour** AND who have cards due AND `last_reminded_on < today`
  (local), sends the reminder, and sets `last_reminded_on = today` — so no user is pinged
  twice the same day.
- Emit events: `onboarding_done`, `first_review_done`, `review_day`.
- **Exit check:** create deck by paste → review → grade → streak:1, all under 60s.

## Step 5 — Stars payments
**Goal:** Free limits enforced; Premium unlock via Stars.
- Free caps: 2 decks / 60 cards; inline paywall at the cap and after `first_review_done`
  (emit `paywall_view`).
- Monthly: native Stars **subscription** invoice (XTR, 30-day); handle
  `successful_payment` + subscription renewal; set/extend `premium_until`.
- Yearly: one-time XTR invoice (1499); on success `premium_until = max(now, premium_until)
  + 365d`. Emit `pay(plan)`.
- **Idempotency:** insert `telegram_payment_charge_id` (UNIQUE); duplicate = no-op.
- `/paysupport` + `refundStarPayment` path implemented.

## Step 6 — QA from a non-premium account ✅ DONE
**Goal:** verify gating and the funnel as a real free user (separate Telegram account).
Passed: free flow, paywall, real 1-Star test purchase (second account), admin notice, /refund.
- Walk the funnel: `start(source)` via a `?start=reels` link → paste list → review →
  paywall_view → (test) pay monthly → premium unlocked → caps lifted.
- Verify: initData rejection on tampered/expired data; duplicate payment is a no-op;
  refund restores non-premium; reminder fires at 19:00 local; free caps block correctly.
- Fix bugs found; keep notes for README.

## Step 7 — Deploy  ✅ (code ready; Railway Hobby, from GitHub repo)
**Goal:** public, always-on bot + Mini App over HTTPS.
- **One Railway service, one volume** (SQLite is a single file). In prod everything runs in
  **one process**: `uvicorn app.main:app` serves the API *and* the built frontend (same origin,
  no CORS) and starts bot polling + scheduler inside the FastAPI lifespan when `RUN_BOT=1`.
  `railway.json` pins `numReplicas: 1` so there is exactly ONE poller and ONE scheduler.
- **Local dev unchanged:** `uvicorn app.main:app --reload` (RUN_BOT unset → API + static only)
  and `python -m app.bot_runner` (the only poller/scheduler) stay as before.
- **Alembic migrations run on startup** (`apply_migrations()`), replacing `create_all` — future
  schema changes never require deleting the DB. Initial migration = current schema.
- `Dockerfile` (multi-stage) builds the frontend (`npm run build`) and the Python image.
- `DATABASE_URL=sqlite+aiosqlite:////data/recalldeck.db` points at the Railway volume (`/data`).
- `GET /health` for Railway health checks.
- ✅ `/help` command; ✅ `set_my_commands` (start, help, paysupport); ✅ `set_chat_menu_button`
  with production `WEBAPP_URL`; ✅ prices from env (`PRICE_MONTHLY`/`PRICE_YEARLY`, defaults 199/1499).
- Switch `SUPPORT_EMAIL` to the dedicated work email before launch.
- Dashboard/BotFather steps (manual): create project from GitHub, add `/data` volume, set env
  vars (`BOT_TOKEN`, `WEBAPP_URL`, `DATABASE_URL`, `SUPPORT_EMAIL`, `ADMIN_ID`, `RUN_BOT=1`),
  generate a domain → put it in `WEBAPP_URL`, set the BotFather menu-button URL.
- Smoke test end-to-end on the live URL from a phone.

**Backups (manual for now):** SQLite lives on the Railway volume at `/data/recalldeck.db`.
Periodically copy it off the volume via the Railway CLI (`railway ssh` / `railway run` a shell
and `cp`/stream `/data/recalldeck.db` out) and keep it off-site. Automate (scheduled dump →
object storage) after launch.

## Step 8 — README with GIF
**Goal:** a launch-ready repo + assets for distribution (PRD §1 Distribution).
- `README.md`: what it is, the audience, screenshots + a short **GIF** of the 60-second core
  loop, run/deploy instructions, pricing, privacy (data stored = PRD §5).
- Prepare deep links per source (`?start=reels`, `?start=dir_tgfind`, etc.) and a short
  pitch line for discussion-group answers + a Reels/Shorts script.
- Submit to bot directories (c); line up the $10 paid test (d).
