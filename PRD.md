# RecallDeck — Product Requirements (MVP)

**Date:** 2026-11-20 · **Status:** draft for approval · **Owner:** Davyd Shvetsov
**One line:** A dead-simple vocabulary drill that lives inside Telegram and pushes you one
review a day — built for IELTS/English-exam learners, not for Anki power users.

---

## 1. Positioning

### The one narrow audience: IELTS / English-exam vocabulary learners
Not "language learners" in general — specifically people grinding English-exam vocabulary
(IELTS/TOEFL), who are highly motivated by a test date. **Evidence the audience exists and
is huge on Telegram** (these are *proof of size*, not distribution channels — see below):

- `English Vocabulary | Vocabularies` — **131.88K** members — https://telemetr.io/en/channels/1175253390-english_ielts_vocabularyy
- `IELTS With Masters` — **108.91K** members — (per https://collaborator.pro/blog/tg-english-groups)
- `English language` — **386,209** subscribers; `English Grammar TOEFL IELTS` — **293,682** — (per https://collaborator.pro/blog/tg-english-groups)
- 1,304+ language channels catalogued — https://telegram-store.com/catalog/product-category/channels/languages

**Why this audience (vs generic learners):** a deadline (exam date) drives daily urgency and
willingness to pay; their need is narrow (drill a finite set of exam words), which lets me
stay far simpler than general tools.

### Audience test (first 2 weeks)
The product is niche-neutral (drill *any* words/terms), so the same build lets me test which
deadline-driven, vocabulary-heavy audience converts best. I'll run **2–3 audiences in parallel**,
each with its own deep link `?start=<source>` (attributed via the `start(source)` event, §8):
- `?start=aud_ielts` — IELTS / English-exam vocabulary (the primary hypothesis above).
- `?start=aud_polish` — Russian speakers learning Polish vocabulary.
- `?start=aud_med` — medical / nursing terminology students.

**Decision rule:** after 2 weeks, compare the funnel per source
(start → onboarding_done → first_review_done → pay) and double down on the winner; IELTS stays
the default hypothesis unless another audience clearly out-converts it.

### Distribution — how I actually reach them (honest, near-$0)
The big channels above are **admin-only broadcast channels**: posting in them is **not free**
(it means paid ads or an admin deal), so they are NOT a free growth channel. Real plan:

- **(a) Comments / answers in open IELTS *discussion groups*** — where learners can post and
  ask questions; I genuinely help and mention the bot where relevant. Free.
- **(b) Own short-form video** — TikTok / Instagram Reels / YouTube Shorts ("1 IELTS word a
  day, drilled in Telegram"). Free, compounding, my own content.
- **(c) Bot directories** — submit to tgfind, StoreBot, @BotsArchive, BotoStore. Free.
- **(d) Small paid test posts** in *mid-size* channels, funded by the **$10 budget** — one or
  two cheap placements purely to measure CAC and compare against (a)–(c).

Every source uses its own **deep link `?start=<source>`** (e.g. `?start=reels`,
`?start=group_ieltsX`, `?start=dir_tgfind`, `?start=paid_chanY`) so acquisition is attributed
per source via the `start(source)` event (§8).

### The angle: "one job, zero setup, inside the app you already have"
Competitors win on **feature count** (FSRS-5, AI decks from PDF, duels, leagues, study pets).
I deliberately **do not** compete there. My promise: *type a word, get drilled once a day,
keep a streak — nothing to configure, nothing to install.*

Honest caveat (see Kill criteria): **MemoCard** already occupies "minimal + free +
open-source." So "simple" alone is not a moat — my moat is **(a)** a specific audience I can
reach for free and **(b)** a single-purpose daily habit loop. If I cannot out-distribute on
the audited channels, this idea fails and I stop (§6).

### Competitor table

| Product | What it is | Strength (why not to fight it) | Link |
|---|---|---|---|
| **Memoniq** | Telegram Mini App | FSRS-5, AI decks from PDF/paste, quizzes, duels, study pet | https://memoniq.app/ · https://t.me/memoniq_bot |
| **MemoCard** | Open-source Telegram Mini App, Telegram-contest winner, ~1k MAU | Already "minimal config + smart reminders", free, cross-platform | https://memocard.org/ · https://github.com/kubk/memo-card · https://t.me/memo_card_bot |
| **Lexicorn** | AI vocabulary-builder Telegram bot | Auto-builds cards (translation, context, examples), any language | https://lexicorn.ai/ |
| **Anki** | Desktop/mobile SRS incumbent | FSRS default since v24.11; vast shared-deck ecosystem; AnkiMobile paid | https://apps.ankiweb.net/ · https://en.wikipedia.org/wiki/Anki |

**My positioning vs all four:** they are *general-purpose study platforms*. RecallDeck is a
*single-purpose exam-vocab habit* that meets one audience where they already are. I win on
narrowness and distribution, never on feature count.

---

## 2. Core loop (time-to-first-value < 60 seconds)

```
/start=<source> in bot
  → bot sends one button: "Open RecallDeck"  (opens Mini App)
  → Mini App opens on an empty starter deck "My IELTS words"
  → on first open: read timezone via Intl, save to settings; set reminder hour = 19:00 local
  → MAIN path — user PASTES a list (one pair per line), e.g.:
        ubiquitous - present everywhere
        mitigate: to make less severe
        candid — honest and direct
      → bot/app parses each line into front/back cards     [~20s]
    (secondary path: type cards manually; also CSV import)
  → taps "Start review"
  → first card shown → tap one of: Again / Good / Easy (SM-2) → streak = 1  [first value]
  → "Come back tomorrow" — daily review push scheduled at 19:00 local
NEXT DAY (19:00 local)
  → bot push: "5 cards due 🔥 streak 1 — Review now"
  → user opens, grades due cards, streak → 2
```

First value = **the first graded card + streak:1**, reachable in under a minute with no
configuration (pasting a list is the fast path). The daily bot push is the retention engine;
the streak is the hook.

---

## 3. Scope

### MVP — IN
- **Paste a list (main onboarding path)**: user pastes lines, one pair per line. Each line
  splits **only** on a space-surrounded separator (`" - "`, `" — "`, `" – "`) **or** on the
  **first** `":"` — never on a bare `-`/`—` inside a word (so `well-known - famous` and
  `ratio: a:b relation` parse correctly). One card per valid line; blanks/unparseable skipped.
- **Deck/card CRUD** in the Mini App (create/rename/delete deck; add/edit/delete cards;
  front/back text only). Manual card typing is the secondary add path.
- **CSV import** (`front,back` rows) to populate a deck fast.
- **SM-2 scheduler** (classic SuperMemo-2: ease factor, interval, repetitions). Deliberately
  SM-2, not FSRS — simpler, good enough, no tuning.
- **Exactly 3 grade buttons — Again / Good / Easy — everywhere**, mapped to SM-2 grades:
  `Again → q=2` (lapse: reset repetitions, interval→1), `Good → q=4`, `Easy → q=5`.
  (We collapse SM-2's 0–5 scale to these three; no "Hard" button.)
- **Daily review reminder** sent by the bot at the user's reminder hour (default **19:00
  local**, from the detected timezone), listing cards due today with a one-tap "Review now".
- **Streak** (consecutive days with ≥1 completed review) shown in bot + Mini App.
- **Simple stats**: cards due today, total cards, current streak, reviews done this week.

### MVP — OUT (explicitly deferred)
- AI card generation (from PDF/paste/YouTube).
- Duels, leagues, leaderboards, study pet.
- Deck sharing / public decks / marketplace.
- Cloze cards, images/audio on cards.
- Anki `.apkg` import, FSRS algorithm.

Rationale: every OUT item is where Memoniq/Anki are strong; shipping them would make us a
worse clone. Staying OUT keeps the 1–2 day build and the "zero setup" promise intact.

---

## 4. Plans & monetization (B2C, paid to me in Stars)

| Plan | Price | Limits |
|---|---|---|
| **Free** | 0 | Up to **2 decks / 60 cards total**, daily reminder, streak, stats, CSV import |
| **Premium (monthly)** | **199 ⭐ / 30 days** as a **native Telegram Stars subscription** (auto-renews via Telegram) | Unlimited decks & cards, custom reminder time, multiple reminders/day |
| **Premium (yearly)** | **1,499 ⭐ one-time** payment that **extends access by 365 days** (not a subscription) | Same Premium features |

Rules:
- Monthly = Telegram-managed recurring Stars subscription (we read/renew expiry from
  Telegram's subscription events). Yearly = single invoice; on success we set
  `premium_until = max(now, premium_until) + 365 days`.
- **Paywall is shown only after the user completes their FIRST review session** (value
  before ask). Never on `/start`, never before first value.
- Free users hitting the 2-deck/60-card cap see the paywall inline at the point of friction.
- Everything is Stars-only (digital goods must be sold in Stars).

---

## 5. Non-goals / data & security posture
- Store **only**: Telegram `user_id`, settings (reminder hour, timezone, locale), deck/card
  text the user authored, SM-2 scheduling fields, streak counters, `premium_until`,
  and payment idempotency keys (`telegram_payment_charge_id`). **Nothing else.**
- No sensitive-data categories, no third-party money/tokens/keys, no payouts, no marketplace.
- Full security rules live in project rules (local) (initData validation, idempotent payments,
  `/paysupport`, refunds).

---

## 6. Kill criteria (decide 3 weeks after public launch, or at 200 activated users — whichever first)

Stop (or hard-pivot) if **any** of these is true:

| Metric | Kill threshold |
|---|---|
| **Distribution** (the core thesis) | Fewer than **300** `/start` users in 3 weeks across ALL sources (a)–(d) combined, including the $10 paid test |
| **Activation** | Fewer than **40%** of `/start` users complete their first review session |
| **Habit / D7 retention** | Fewer than **15%** of activated users return to review on day 7 |
| **Willingness to pay** | Fewer than **2%** free→Premium conversion after 3 weeks |
| **First revenue** | Fewer than **5 paying users** in the first 3 weeks |
| **Renewal** | More than **70%** of monthly subscribers fail to renew into month 2 |

If distribution passes but activation/retention fail → fix the loop, not the audience.
If distribution fails → the whole "reach them free in existing channels" thesis is wrong → stop.

---

## 7. Success picture (first 60 days, non-binding target)
~300–600 `/start`, ≥45% activation, ≥20% D7, 10–25 paying users → ~2,000–5,000 ⭐/mo gross,
enough signal to justify adding ONE feature from the OUT list (likely AI card generation).

## 8. Event tracking (minimum set to judge the funnel + kill criteria)
Store as append-only rows: `user_id`, `event`, `source?`, `plan?`, `ts`. No PII beyond
`user_id`. Events:

- `start(source)` — `/start=<source>` fired; `source` from the deep link (defaults `direct`).
- `onboarding_done` — first deck has ≥1 card (via paste/manual/CSV).
- `first_review_done` — first ever review session completed (the activation event).
- `paywall_view` — paywall shown (only after first review, or at a free-cap hit).
- `pay(plan)` — successful Stars payment; `plan ∈ {monthly, yearly}`.
- `review_day(d1, d7)` — returning review on day-1 and day-7 after activation (retention).

These map 1:1 to the funnel: `start → onboarding_done → first_review_done → paywall_view →
pay`, with `review_day` for retention — exactly the numbers the Kill criteria (§6) test.
