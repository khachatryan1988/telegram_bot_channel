# PLANS.md

## Current objective
Ship a working MVP Telegram giveaway bot for `@domus_stores_test_1`.

## Product summary
Users join the bot, subscribe to the Domus channel, verify participation, receive a personal referral link, and become eligible after 3 verified referrals. Admin manually selects a winner. The winner must respond within 48 hours or a redraw is performed.

---

## Phase 1 — Project scaffold
### Goal
Set up the minimal runnable bot structure.

### Tasks
- create project structure
- add `requirements.txt`
- add `config.py`
- add `.env.example`
- add base `bot.py`
- initialize SQLite schema

### Deliverable
A bot that starts successfully and connects to Telegram.

---

## Phase 2 — User onboarding
### Goal
Support `/start` and base entry flow.

### Tasks
- parse deep-link payload
- create user record if new
- store referral binding if valid
- show welcome text
- add main buttons

### Deliverable
A new user can enter the bot and see the participation flow.

---

## Phase 3 — Subscription verification
### Goal
Verify that the user is subscribed to `@domus_stores_test_1`.

### Tasks
- add channel button
- add `verify` button handler
- call Telegram membership check
- mark user as verified
- handle unsuccessful verification

### Deliverable
Verified users are correctly identified and stored.

---

## Phase 4 — Referral system
### Goal
Make referrals count only after successful verification.

### Tasks
- generate unique `ref_code` for each user
- build personal referral link
- create `referrals` records
- mark referral as verified only after invited user passes verification
- prevent self-referral
- prevent duplicate counting
- compute progress

### Deliverable
Progress reflects only valid verified invites.

---

## Phase 5 — Eligibility logic
### Goal
Activate participation after 3 verified referrals.

### Tasks
- read referral target from env
- calculate verified referral count
- set `is_eligible`
- notify user on activation

### Deliverable
Users become eligible exactly at threshold.

---

## Phase 6 — Admin draw flow
### Goal
Allow manual winner selection.

### Tasks
- restrict admin commands by ID
- implement `/stats`
- implement `/participants`
- implement `/draw`
- select random user from eligible pool
- re-check winner subscription
- create draw record
- notify winner

### Deliverable
Admin can manually select a valid winner.

---

## Phase 7 — Redraw flow
### Goal
Support replacing a non-responsive winner.

### Tasks
- store response deadline
- implement `/winner`
- implement `/redraw`
- mark previous draw as expired
- exclude expired winner from immediate redraw
- notify new winner

### Deliverable
Admin can perform redraw after the deadline.

---

## Phase 8 — Stabilization
### Goal
Make the MVP safe to test.

### Tasks
- improve logs
- test duplicate `/start`
- test duplicate verification
- test duplicate referral cases
- test users without username
- test admin access restrictions
- test empty eligible pool
- test draw/redraw edge cases

### Deliverable
Bot is ready for pilot use.

---

## Acceptance checklist
- user can start bot
- user can verify channel membership
- user receives personal referral link
- invited user is counted only after verification
- progress updates correctly
- user becomes eligible at 3 verified referrals
- admin can draw winner manually
- winner deadline is stored
- admin can redraw after expiry

---

## Nice-to-have later
- PostgreSQL migration
- Docker support
- webhook deployment
- export participants
- more detailed audit log
- reminder messages before expiry
- admin keyboard instead of slash commands
