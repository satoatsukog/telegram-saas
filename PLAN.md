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

## Step 6 — QA from a non-premium account
**Goal:** verify gating and the funnel as a real free user (separate Telegram account).
- Walk the funnel: `start(source)` via a `?start=reels` link → paste list → review →
  paywall_view → (test) pay monthly → premium unlocked → caps lifted.
- Verify: initData rejection on tampered/expired data; duplicate payment is a no-op;
  refund restores non-premium; reminder fires at 19:00 local; free caps block correctly.
- Fix bugs found; keep notes for README.

## Step 7 — Deploy
**Goal:** public, always-on bot + Mini App over HTTPS.
- Host backend (e.g. Fly.io/Railway/VPS) with persistent SQLite volume; serve the built
  Mini App over HTTPS; set `WEBAPP_URL`, bot menu button → web_app.
- Run the **two processes** (`uvicorn app.main:app` and `python -m app.bot_runner`) as
  separate services; keep polling for MVP; confirm exactly ONE poller and ONE scheduler run
  in prod and survive restarts.
- Switch `SUPPORT_EMAIL` in `.env` to the dedicated work email before launch.
- Smoke test end-to-end on the live URL from a phone.

## Step 8 — README with GIF
**Goal:** a launch-ready repo + assets for distribution (PRD §1 Distribution).
- `README.md`: what it is, the audience, screenshots + a short **GIF** of the 60-second core
  loop, run/deploy instructions, pricing, privacy (data stored = PRD §5).
- Prepare deep links per source (`?start=reels`, `?start=dir_tgfind`, etc.) and a short
  pitch line for discussion-group answers + a Reels/Shorts script.
- Submit to bot directories (c); line up the $10 paid test (d).
