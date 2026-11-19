# Market Research — Telegram Bot / Mini App SaaS (Stars payments)

**Date:** 2026-11-19
**Analyst:** Davyd Shvetsov
**Goal:** Find a SaaS idea, buildable as an MVP in 1–2 days (Python/aiogram 3 + React/Tailwind), monetized in Telegram Stars, promotable on a $10 budget, that people will pay for.

---

## 0. Method & data-quality note

- Target window: fresh signals, last ~90 days (Aug–Nov 2026).
- Sources attempted via Playwright browser (read-only, never logged in): Reddit, Product Hunt, Indie Hackers, TGStat, app-store/forum reviews.
- **Access limitations (important for honesty):**
  - **Reddit** — fully blocked for this agent. Web UI returned a human-check wall, `old.reddit.com` redirected to login, the `.json` API returned **HTTP 403**, and `WebFetch` on reddit.com was refused. → Where I could not get a primary quote with a date, I mark it **"no data"** and rely on secondary/aggregated search results instead. **No quotes were invented.**
  - **Product Hunt** — Topic page loaded, but "highest rated" is historical (2014–2018). Usable for competitor landscape, weak for freshness.
  - **Indie Hackers** — post pages returned HTTP 403 to WebFetch; only search-snippet level data.
  - **TGStat** — homepage loaded; `/ratings/bots` path 404 (structure changed). Usable only at homepage/category level.
- Every signal below carries a link + date + quote where obtainable; otherwise "no data".

---

## 1. Demand signals collected

### A. Regulatory tailwind — Telegram now MANDATES Stars for digital goods (strongest macro signal)
- **Source:** paystars.uz — "Digital goods in bots and Mini Apps must be paid with Telegram Stars" — https://paystars.uz/en/news/digital-goods-in-bots-only-via-telegram-stars/ (accessed 2026-11-19)
- **Source:** pulseagent.io — "Telegram digital goods must be paid in Stars inside bots — the payment rules for storefronts" — https://pulseagent.io/en/feed/telegram-stars-in-bot-payment-rules/ (accessed 2026-11-19)
- **Quote (aggregated):** "payments for digital goods and services sold inside a bot or Mini App must be accepted exclusively in Telegram Stars… Bots that break the rule may be restricted. Mixing Telegram Stars with other payment methods inside Telegram is what gets storefronts in trouble."
- **Why it matters:** Every creator who currently sells digital access via Gumroad/Stripe links inside Telegram is now *forced* toward a Stars-native tool. Fresh, time-boxed demand with a compliance deadline behind it.

### B. Paid-channel / subscription admin pain (strong, dated, specific)
- **Source:** GitHub PR #47, Zedanara/Telegram-Subscription-Manager — https://github.com/Zedanara/Telegram-Subscription-Manager/pull/47 — **opened 2026-10-03**
- **Quote:** need to *"compare 'who paid' against 'who is actually in the channel' before moving the channel to paid-only"*; the Bot API **cannot list channel members**, so removing legacy free members "remains a manual step by the channel owner."
- **Source:** getvarta.com — "How to Moderate a Paid Telegram Community in 2026" — https://getvarta.com/blog/moderate-paid-telegram-community-trust-layer-2026/ (accessed 2026-11-19)
- **Quote (aggregated):** "In paid Telegram communities, every trust failure has a direct revenue cost… free communities tolerate noise, paid communities collapse under it."
- **Competitors (market is validated / crowded):** KnorpelSenf/subscription-manager-bot (open-source, self-host), mavibot.ai SubClub bot, grambase.ai guides. → Demand proven; gap = *hosted, zero-config, Stars-only, 5-minute setup*.

### C. Creators pay to sell digital products; Gumroad fees resented (willingness-to-pay)
- **Source:** sellfy.com — "Gumroad Alternatives (2026)" — https://sellfy.com/blog/best-gumroad-alternatives/ (accessed 2026-11-19)
- **Source:** instantdm.com — "8 Best Gumroad Alternatives… 2026" — https://instantdm.com/blog/gumroad-alternatives-for-digital-products (accessed 2026-11-19)
- **Quote (aggregated):** "The Reddit consensus is that Gumroad's 10% fee is too high in 2026." Gumroad = 10% + $0.50/sale; Lemon Squeezy 5%; Payhip free tier 5%.
- **Why it matters:** Creators already pay to sell digital products. None of the listed alternatives is Telegram-Stars-native → white space given signal A.

### D. Telegram monetization is real money (proof of payment at the ecosystem level)
- **Source:** exitbid.io — "Telegram Bot Monetization in 2026: Stars, Revenue Streams & Value" — https://exitbid.io/blog/telegram-bot-monetization-2026 (accessed 2026-11-19)
- **Source:** Indie Hackers — "From $0 to $5,000/month with Telegram Channels: my story" — https://www.indiehackers.com/post/from-0-to-5-000-month-with-telegram-channels-my-story-806fbe32c4 (title/snippet only; page returned 403, body = **no data**)
- **Quote (aggregated):** "Stars-native bots now look more like subscription SaaS — revenue is recurring, measurable, transferable." Bots trade at 18–36× MRR; "500 paying subscribers at $9.99/mo ≈ $5,000/mo." Telegram pays ~$0.013/Star on desktop/web.

### E. Learning / quiz / course Mini Apps have large audiences (adjacent demand)
- **Source:** airdroid.com — "Best Telegram Bot List for Students 2025" — https://www.airdroid.com/ai-insights/telegram-bot-list-for-students/ (accessed 2026-11-19)
- **Source:** monetag.com — "Learning Through Telegram Mini Apps" — https://monetag.com/blog/learning-through-telegram-mini-apps/ (accessed 2026-11-19)
- **Quote (aggregated):** Telegram's own QuizBot shows **1,525,980 monthly users**; BullBeary edu mini app "over 56,000 monthly users… one of the fastest-growing educational mini apps."

### F. Giveaway / "earning" bot space is scam-saturated (anti-signal — avoid)
- **Source:** sweepzy.co.uk — "Telegram Giveaway Channels: UK Comper's Honest Guide" — https://sweepzy.co.uk/blog/telegram-giveaway-channels-guide (accessed 2026-11-19)
- **Source:** aziqdev.com — "Free Telegram Earning Bots in 2026: Real or Scam?" — https://aziqdev.com/blog/telegram-earning-bots-real-or-scam (accessed 2026-11-19)
- **Quote (aggregated):** "roughly 10–20% legitimate, 80–90% something you don't want to engage with… the classic advance-fee scam."
- **Why it matters:** High association with fraud → poisoned category, Telegram actively restricts. Avoid.

### G. Small-business reminders / review collection is a proven but SMS/email-dominated market
- **Source:** goreminders.com — automated review-request software — https://www.goreminders.com/automated-review-request-software-for-small-businesses (accessed 2026-11-19)
- **Source:** Google Workspace Marketplace SMS reminder apps (multiple) — e.g. https://workspace.google.com/marketplace/app/sms_reminder_for_google_calendar/187871939123 (accessed 2026-11-19)
- **Quote (aggregated):** SMS reminders "reduce no-shows by up to 50%"; review tools send "1 reminder if they forget, then stop."
- **Why it matters:** Proven willingness-to-pay, BUT buyers are offline SMBs → **hard to reach 100 for free, and they live on SMS/WhatsApp, not Telegram.** Weak Telegram fit + weak free reach.

### H. Competitor landscape (Product Hunt / catalog)
- **Source:** Product Hunt Telegram topic — https://www.producthunt.com/topics/telegram (accessed 2026-11-19)
- **Quote:** "Commerce-minded users favor **Botcommerce** to launch sales bots with payments and inventory inside chats." → full-store competitor exists; it's heavyweight (catalog + inventory), leaving the *simple single-product / single-gate* wedge open.
- **Source:** tgfind.app language-learning category — https://tgfind.app/categories/language-learning (accessed 2026-11-19) — confirms active bot directories exist = free distribution channels.

---

## 2. Ten ideas, scored 1–5

Scores (1 = weak, 5 = strong). Dimensions: **Pain** = pain frequency · **Pay** = proof people pay · **Reach** = reach 100 users with $0 · **Speed** = MVP in 1–2 days · **Gap** = competitor gap · **Ret** = retention · **TG fit** = fit for Telegram. Higher total = better.

| # | Idea | Pain | Pay | Reach | Speed | Gap | Ret | TG fit | Total | Tarpit? |
|---|------|:----:|:---:|:-----:|:-----:|:---:|:---:|:------:|:-----:|:-------:|
| 1 | **Stars-native paid-access manager** for private channels/groups (auto-add payers, auto-kick on expiry, Mini App dashboard) | 5 | 5 | 4 | 4 | 3 | 5 | 5 | **31** | no |
| 2 | **Stars paywall for digital products** ("Gumroad-for-Stars": sell a file/link, instant delivery) | 4 | 5 | 4 | 5 | 4 | 3 | 5 | **30** | no |
| 3 | Paid **quiz/course delivery Mini App** for educators (sell a course in Stars, track progress) | 4 | 4 | 3 | 3 | 4 | 4 | 5 | **27** | no |
| 4 | **Tip jar / "buy me a coffee" in Stars** for creators + supporter wall | 3 | 4 | 4 | 5 | 3 | 3 | 5 | **27** | no |
| 5 | **Feedback / support-ticket bot** for small Telegram shops (inbox + canned replies) | 3 | 3 | 3 | 4 | 3 | 3 | 4 | **23** | no |
| 6 | **Giveaway/contest growth bot** (verified random draw, requirement checks) | 4 | 3 | 4 | 4 | 1 | 2 | 4 | **22** | **yes** |
| 7 | **Appointment booking + no-show reminders** for solo service providers | 4 | 4 | 2 | 3 | 2 | 4 | 2 | **21** | partly |
| 8 | **Google-review collection/reminder** bot for SMBs | 3 | 4 | 2 | 3 | 2 | 3 | 2 | **19** | no |
| 9 | **Channel analytics / audience insights** bot | 3 | 3 | 3 | 2 | 1 | 3 | 4 | **19** | **yes** (TGStat etc.) |
| 10 | **Group anti-spam / moderation** bot | 4 | 2 | 3 | 3 | 1 | 4 | 4 | **21** | **yes** (Rose, Shieldy…) |

**Tarpits flagged:** #6 giveaways (scam-poisoned + thousands of clones), #9 analytics (TGStat/Combot dominate), #10 moderation (Rose/Shieldy/Combot — built thousands of times, mostly free).

---

## 3. Final pick

### 🏆 Idea #1 — **Stars-native paid-access manager for private Telegram channels & groups**

**One-liner:** *Turn any Telegram channel or group into a paid membership in 5 minutes — users pay in Stars, the bot adds them automatically and kicks them when their subscription expires. No Stripe, no spreadsheets, no coding.*

**Why this one (justification against the 7 criteria):**
1. **Pain (5):** Dated, specific, recurring. The Oct 3 2026 GitHub PR spells out the exact pain — the Bot API can't list members, so owners reconcile "who paid vs who's in" by hand. Every paid community hits this.
2. **Pay (5):** Market already pays — existing subscription bots, 18–36× MRR valuations, "500 subs × $9.99 ≈ $5k/mo." We charge the *creator* a flat Stars subscription (clean, since Stars revenue lands in the owner's balance).
3. **Reach, $0 (4):** Buyers (channel/group owners) are reachable **inside Telegram itself** — bot directories (tgfind, StoreBot, @BotsArchive), "make money on Telegram" channels, admin groups, plus r/Telegram-adjacent and #buildinpublic. No ad spend required.
4. **Speed (4):** aiogram 3 bot: create invoice (`sendInvoice` with `XTR` currency) → on `successful_payment` generate a single-use invite link (`createChatInviteLink`) → store expiry → a scheduler kicks (`banChatMember`+unban) on expiry. React/Tailwind Mini App = owner dashboard. Doable in 1–2 days.
5. **Gap (3):** Crowded but fragmented — competitors are either **self-host/open-source** (KnorpelSenf, Zedanara) or **full stores** (Botcommerce) or Stripe-first. Gap = *hosted, zero-config, Stars-only, 5-minute setup* with a clean dashboard + solving the reconciliation UX. (Honest: this is the weakest score — crowding is the main risk, mitigated by positioning on simplicity + Stars-only + the 2026 Stars mandate.)
6. **Retention (5):** Recurring by nature — the owner keeps paying us monthly as long as their community earns. Churn only if their community dies.
7. **TG fit (5):** Impossible to replicate outside Telegram; Stars + invite links + membership are all native primitives.

**Fast-follow (same codebase):** Idea #2 (one-time digital product sale with instant delivery) is the same payment+delivery plumbing minus the scheduler — ship it week 2 to widen the funnel.

### Product name
**Gatekeep** (working name; alt: *StarLock*, *PaidGate*). Tagline: *"Paid access for your Telegram, powered by Stars."*

### Pricing — 2 plans (charged to the channel owner, in Stars)
> Stars ≈ $0.013–0.02 each depending on platform; prices chosen for round Stars amounts and clear value vs. the $5k/mo they can earn.

| Plan | Price | Limits / features |
|------|-------|-------------------|
| **Starter** | **299 ⭐ / month** (~$4–6) | 1 channel *or* group · up to 150 active members · auto-add + auto-kick on expiry · basic dashboard · single price tier |
| **Pro** | **1,299 ⭐ / month** (~$17–25) | unlimited channels/groups · unlimited members · multiple price tiers & trials · "who-paid-vs-who's-in" reconciliation report · CSV export · custom welcome message / branding |

(First 50 owners: free Pro for 3 months to seed reviews and case studies.)

### Where to find the first 100 users (all free)
1. **Telegram bot directories:** tgfind.app, StoreBot (@storebot), @BotsArchive, BotoStore — submit listing.
2. **"Monetize on Telegram" / creator channels & admin groups** — offer free Pro in exchange for feedback; comment where owners ask "how do I charge for my channel."
3. **Niche subreddits** (manual, read-rules-first): r/Telegram, r/TelegramBots, r/SaaS "Show", r/SideProject, r/NewTubers / creator subs.
4. **Indie Hackers "Show IH"** + build-in-public updates.
5. **X/Twitter #buildinpublic**, and reply to creators posting Gumroad links: *"Telegram now requires Stars for in-app digital goods — want a 5-min setup?"* (ties to signal A).
6. **Product Hunt launch** once stable.
7. **Direct outreach** to small paid-channel owners found via TGStat categories.

---

## 4. Risks & open questions
- **Crowding (main risk):** differentiate hard on *simplicity + Stars-only + the compliance angle*, not features.
- **API member-listing limit is real** — we must design reconciliation around payment records we control, not `getChatMembers` (which doesn't exist for channels). Turn the limitation into our value prop.
- **Trust barrier:** owners route money through us → need transparent "Stars go straight to your balance, we only manage access" messaging.
- **Reddit data gap:** primary Reddit quotes = **no data** (blocked). Validate top pains with 5–10 manual owner DMs before/while building.
