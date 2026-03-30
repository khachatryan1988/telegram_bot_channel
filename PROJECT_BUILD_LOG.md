# Domus Giveaway Bot Project Build Log

## Purpose

This document records the practical implementation steps that were completed while building the current MVP. It is intended for future developers who need to understand not only the final structure, but also the sequence of decisions and the rationale behind them.

## Initial project baseline

The project was built as an MVP Telegram giveaway bot with the following constraints:

- one bot
- one Telegram channel: `@domus_stores_test_1`
- Armenian-only user-facing UI
- Python + `aiogram` + SQLite
- no FSM unless the flow genuinely requires multi-step state
- no dashboards, queues, Redis, Celery, Docker orchestration, or PostgreSQL

The implementation kept the flow router-based and deliberately simple.

## Step 1. Project structure review and alignment

The existing repository structure was reviewed and aligned with the intended MVP layout:

- `main.py` as the runtime entry point
- `config.py` for environment-based configuration
- `texts.py` for Armenian UI strings
- `app/handlers/` for user/admin routers
- `app/services/` for business logic
- `app/repositories/` for SQLite access
- `app/db/` for schema and DB bootstrap
- `app/keyboards/` for Telegram keyboards

The repository layer was already being used instead of a monolithic file, so that approach was preserved.

## Step 2. Referral flow and participation model

The user flow was implemented and/or validated around these rules:

- `/start` accepts deep links in format `ref_<tg_id>`
- a user record is created on first contact
- `participant_status` row is ensured for each user
- referral binding happens only on first start flow
- self-referral is blocked
- invited users are not rebound to another referrer
- referral progress is recalculated only from verified invites
- eligibility is granted when verified referrals reach `REFERRAL_TARGET`

The deterministic part of the accounting lives in:

- `app/repositories/referrals.py`
- `app/repositories/status.py`
- `app/services/referral.py`

## Step 3. Subscription verification flow

Channel membership verification was implemented using Telegram API checks:

- user presses the Armenian participation button
- bot checks membership in the configured channel
- verification status is persisted
- referral progress is recalculated for the user
- if the user has a referrer, that referrer's progress is recalculated as well
- the user receives a personal referral link and progress display

This logic is centered in:

- `app/handlers/user.py`
- `app/services/verification.py`

## Step 4. Manual draw and redraw flow

The admin flow was implemented with commands:

- `/stats`
- `/participants`
- `/draw`
- `/redraw`
- `/winner`

Winner selection logic includes:

- choosing only from eligible users
- re-checking channel membership before confirming a winner
- creating a draw record
- creating a winner record
- sending a direct Telegram message to the winner

The main files involved are:

- `app/handlers/admin.py`
- `app/services/draw.py`
- `app/repositories/draws.py`
- `app/repositories/winners.py`

## Step 5. Winner response tracking in 48 hours

A minimal winner acknowledgment mechanism was added for MVP.

Implemented behavior:

- the bot sends the winner a message with a confirmation button
- the button text is `Հաստատել արձագանքս`
- pressing the button stores response timing
- if no response is received before the deadline, admin can run `/redraw`

Persisted timestamps:

- `winner_notified_at`
- `response_deadline_at`
- `responded_at`

Database changes were made in:

- `app/db/schema.sql`
- `app/db/init_db.py`

Logic changes were made in:

- `app/services/draw.py`
- `app/repositories/winners.py`
- `app/handlers/user.py`
- `app/handlers/admin.py`
- `app/keyboards/main.py`
- `texts.py`

Backward compatibility for existing SQLite DBs was handled through init-time column checks in `app/db/init_db.py`.

## Step 6. Production-minimum hardening

To make the bot safer to run in a minimal production setup, three infrastructure additions were made.

### Centralized logging

Logging was centralized into:

- `app/logging_setup.py`

and wired from:

- `main.py`

### Error handling

An exception-handling middleware was added:

- `app/middlewares/error.py`

This middleware:

- catches unhandled handler exceptions
- logs the error
- sends a generic safe Armenian error message to the user

### Duplicate update protection

A lightweight deduplication middleware was added:

- `app/middlewares/dedup.py`

This keeps an in-memory rolling set of processed `update_id` values and skips duplicates in the current process lifetime.

### Update lifecycle logging

Middleware was added in:

- `app/middlewares/logging.py`

This logs message/callback handling context to simplify troubleshooting.

## Step 7. Tests

Minimal tests were added in `tests/`:

- `tests/test_referral_service.py`
- `tests/test_repositories_smoke.py`
- `tests/conftest.py`

Covered areas:

- referral counting only from verified invites
- eligibility threshold behavior
- idempotent referral binding
- DB schema bootstrap smoke checks
- repository smoke checks for users, referrals, draws, winners, and DB connections

## Step 8. Developer onboarding

The repository README was rewritten to include:

- project purpose
- stack
- environment variables
- setup commands
- run command
- test command
- current production-minimum guarantees

Main file:

- `README.md`

## Step 9. Environment setup and verification

The following practical verification steps were completed during implementation:

1. Python bytecode compilation was run with `python3 -m compileall .`
2. A local virtual environment was created with `python3 -m venv .venv`
3. Dependencies were installed with `.venv/bin/pip install -r requirements.txt`
4. Test bootstrap was fixed so the project root is importable during `pytest`
5. Tests were run successfully with `.venv/bin/pytest`

Result at the time of writing:

- test suite passed: `7 passed`

## Design decisions intentionally preserved

- routers instead of introducing FSM
- SQLite instead of adding external infrastructure
- repository functions with straightforward SQL instead of abstraction-heavy ORM patterns
- admin-driven draw/redraw flow
- environment-only sensitive config
- Armenian-only user-facing texts

## Notes for future developers

- The current bot is an MVP for a single contest flow, not a reusable contest platform.
- Before extending behavior, preserve the deterministic referral rules.
- Avoid adding infrastructure unless there is a real operational requirement.
- If future requirements add multi-step admin moderation or winner claim forms, only then consider FSM.
