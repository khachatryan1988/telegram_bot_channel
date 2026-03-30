# AGENTS.md

## Project
Domus Giveaway Bot MVP

## Mission
Build a minimal Telegram giveaway bot for the Domus channel with subscription verification, personal referral links, progress tracking, manual winner draw, and redraw support.

## Core product scope
- One Telegram bot
- One Telegram channel: `@domus_stores_test_1`
- Armenian-only UI
- Manual admin draw flow
- Referral target: 3 verified invites
- Winner response window: 48 hours
- Stack: Python + aiogram + SQLite

## Non-negotiables
1. **MVP only**
   - Do not introduce dashboards, microservices, Redis, Celery, PostgreSQL, Docker orchestration, or web apps unless explicitly requested in a later phase.
2. **Zero hardcode for sensitive config**
   - Use environment variables for bot token, admin IDs, channel username, thresholds, and DB path.
3. **Simple architecture**
   - Keep modules small and readable.
   - Prefer straightforward service functions over abstraction-heavy patterns.
4. **Deterministic referral accounting**
   - A referral counts only if the invited user:
     - entered through a referral link,
     - sent `/start`,
     - passed subscription verification.
5. **No silent rule changes**
   - Do not alter referral threshold, winner response window, or participation rules unless the spec changes.
6. **Armenian UI**
   - User-facing texts must be in Armenian.
   - Prefer clean, natural Armenian wording.

## Functional requirements
- `/start` handles deep links in the format `ref_<code>`
- user can verify subscription to `@domus_stores_test_1`
- bot generates and shows a personal referral link
- progress is shown as `0/3`, `1/3`, `2/3`, `3/3`
- user becomes eligible only after 3 verified referrals
- admin can run `/draw`
- admin can run `/redraw`
- winner has 48 hours to respond
- redraw is possible after expiration

## Suggested folder structure
```text
project/
  bot.py
  config.py
  texts.py
  keyboards.py
  requirements.txt
  app/
    handlers/
      user.py
      admin.py
    services/
      verification.py
      referral.py
      draw.py
    db/
      models.py
      queries.py
      init_db.py
```

## Coding guidelines
- Python 3.14.x
- aiogram 3.26.x
- SQLite for persistence
- clear function names
- no unnecessary metaprogramming
- avoid giant files
- type hints where practical
- log important state transitions

## Referral rules
- prevent self-referral
- one invited user can only belong to one referrer
- do not rebind referrer after initial binding
- count only verified invited users
- keep referral count idempotent

## Winner rules
- winner must be selected from eligible users only
- before confirming winner, re-check channel membership
- create a draw record with deadline
- if no response in 48 hours, mark expired and allow redraw

## Admin rules
Use admin IDs from env.
Supported admin commands:
- `/stats`
- `/participants`
- `/draw`
- `/redraw`
- `/winner`

## Environment variables
- `BOT_TOKEN`
- `CHANNEL_USERNAME`
- `ADMIN_IDS`
- `REFERRAL_TARGET`
- `WINNER_RESPONSE_HOURS`
- `DB_PATH`

## Delivery expectations
When generating code:
- include setup steps
- include `.env.example`
- include `requirements.txt`
- include DB init logic
- include concise README if requested

## Out of scope
- web admin panel
- payment systems
- multiple channels
- multiple contests
- auto-scheduled draws
- advanced anti-fraud systems
- analytics dashboards
