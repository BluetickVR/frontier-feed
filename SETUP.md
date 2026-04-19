# frontier-feed — end-to-end setup

From zero to pushing-to-Telegram in one sitting. ~90 minutes if you do it in order.

## Prerequisites

- A machine with Python 3.11+ and git
- A GitHub account (to host the private repo that routines read from)
- A Claude Max subscription (for routines)
- ~10 minutes of phone time (for BotFather)
- A Fly.io account (free tier covers the webhook)

## Stage 0 — Secrets you'll collect along the way

Don't gather them up front — collect as you go. By the end, your `.env` will have:

```
TELEGRAM_BOT_TOKEN   # from @BotFather
TELEGRAM_CHAT_ID     # from getUpdates
GROQ_API_KEY         # you already have this
TAVILY_API_KEY       # you already have this
GEMINI_API_KEY       # optional, recommended — free tier at aistudio.google.com
GITHUB_TOKEN         # PAT with "repo" scope for the webhook
GITHUB_REPO          # anshulpadyal/frontier-feed
```

## Stage 1 — Local install (5 min)

```bash
cd /Users/anshulpadyal/frontier-feed
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
feed --help        # should print the CLI
```

Copy your existing keys into `.env`:

```bash
cp .env.example .env
# then open .env and paste:
# GROQ_API_KEY=...      (reuse from Learning_Project)
# TAVILY_API_KEY=...    (reuse from Learning_Project)
```

Stage 1 is done when `feed --help` prints without error.

## Stage 2 — Telegram bot (10 min, phone + laptop)

**2a. Create the bot.**
On your phone, DM [@BotFather](https://t.me/BotFather):
```
/newbot
```
Follow the prompts. Name it `frontier-feed` and give it a handle like
`anshul_frontier_bot`. Save the **HTTP API token** it gives you — that's your
`TELEGRAM_BOT_TOKEN`.

**2b. Get your chat ID.**
Start a chat with your new bot. Send it any message (e.g. `hi`). Then from
your laptop:
```bash
BOT=<token-from-2a>
curl "https://api.telegram.org/bot$BOT/getUpdates" | jq '.result[-1].message.chat.id'
```
The number that prints is your `TELEGRAM_CHAT_ID`.

**2c. Put both in `.env`.**
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

**2d. Smoke test.**
```bash
feed doctor
```
You should see `telegram: OK` and `groq: OK` and receive a 🩺 message on your phone.
If telegram fails, re-check the token and chat id. If groq fails, re-check your API key.

## Stage 3 — First dry-run (5 min)

```bash
feed digest --slot morning --dry-run
```

Watch the JSON output. You should see something like:
```json
{ "fetched": 25, "fresh": 25, "ranked": 25, "selected": 5, "pushed": 0 }
```

Now the real thing:
```bash
feed digest --slot morning
```

Your phone should light up with a header + 5-6 items. Each item shows source,
title, why-it-matters, link, id, and the reply legend.

**If selected=0**, the relevance threshold is too high for today's signal.
Lower `budgets.relevance_threshold` in `context.yaml` from `0.55` to `0.45`
and re-run.

## Stage 4 — GitHub repo (5 min)

Routines need a public-or-private git repo to pull/push. Create one:

```bash
cd /Users/anshulpadyal/frontier-feed
git init
git add .
git commit -m "initial commit"
gh repo create frontier-feed --private --source=. --remote=origin --push
```

(If you don't use `gh`, create the repo manually on github.com and
`git remote add origin ... && git push -u origin main`.)

**Create a Personal Access Token for the webhook.**
GitHub → Settings → Developer settings → Personal access tokens → Fine-grained.
- Scope: this one repo
- Permissions: **Contents: read and write**
- Expiry: 1 year
Save the token — that's `GITHUB_TOKEN`.

## Stage 5 — Deploy the webhook (15 min)

```bash
# install fly CLI once
brew install flyctl     # mac
fly auth login

cd webhook
fly launch --no-deploy
# when prompted: no to postgres, no to redis, accept region bom (Mumbai) or
# change to one near you. Don't deploy yet.
```

Set secrets:
```bash
WEBHOOK_SECRET=$(openssl rand -hex 16)
echo "remember this secret: $WEBHOOK_SECRET"

fly secrets set \
  TELEGRAM_WEBHOOK_SECRET="$WEBHOOK_SECRET" \
  TELEGRAM_BOT_TOKEN="<token>" \
  TELEGRAM_CHAT_ID="<chat-id>" \
  GITHUB_TOKEN="<pat>" \
  GITHUB_REPO="anshulpadyal/frontier-feed" \
  GITHUB_BRANCH="main"

fly deploy
```

Get the public URL:
```bash
APP_URL=$(fly status --json | jq -r .Hostname)
echo "webhook url: https://$APP_URL"
curl "https://$APP_URL/healthz"    # must print {"ok":true,...}
```

Register with Telegram:
```bash
BOT=<token>
curl "https://api.telegram.org/bot$BOT/setWebhook?url=https://$APP_URL/webhook/$WEBHOOK_SECRET"
# expect: {"ok":true,"result":true,"description":"Webhook was set"}
```

**Verify end-to-end.** Go to Telegram, find one of this morning's pushed items,
**reply** to it with a single `.`. Within ~2 seconds:
- Bot replies: `✓ . saved for <item-id>`
- Your GitHub repo gets a new commit: `reaction: {...}`
- `state/reactions.jsonl` in the repo now has one line.

If not, check `fly logs` for errors.

## Stage 6 — Claude Max routines (20 min)

Open Claude Code web → Settings → Routines → New Routine.

For each of the 5 routines in `routines/`:
1. Set **Trigger: Scheduled** and the time from the routine file.
2. Set **Repository** to your private `frontier-feed` repo.
3. Attach **secrets**: `GROQ_API_KEY`, `GEMINI_API_KEY` (if you have one),
   `TAVILY_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`,
   `ANTHROPIC_API_KEY` (only if you want paid fallback).
4. Paste the prompt from the routine's `.md` file.
5. **Run it manually once** from the UI to confirm. Read the session log. Fix
   anything that breaks before walking away.

Do them in order: 1 → 2 → 3 → 4 → 5. You don't need to wait for their schedule
to fire — manual run is fine for the first check.

## Stage 7 — Observe for 3 days (no changes)

Don't touch the system for 3 days. At 06:45 you get a morning push. Tap
`.` / `?` / `+` / `-` on each item. At 13:00 any `?` items come back as
dossiers. At 19:30 a smaller evening push. At 22:00 you get a one-line journal
summary.

At the end of day 3, ask yourself:
- Was there at least one item per morning that was genuinely useful?
- Did you actually tap through the reactions (or did it feel like work)?
- Did any dossier teach you something you didn't already know?

If yes to all three, proceed to Phase 4 (add more fetchers).
If no, open `context.yaml`, tune topic priorities and threshold, and observe
for 3 more days before adding complexity.

## Stage 8 — Add fetchers one per day (week 2)

Each fetcher is a single file in `feed/fetchers/<name>.py` following
`github_trending.py` as a template. Register it in
`feed/fetchers/__init__.py`. Enable it in `config.yaml`. Commit + push.
Next routine run picks it up automatically.

Order (one per day):
1. HuggingFace Daily Papers
2. arxiv cs.AI RSS
3. Anthropic + OpenAI + DeepMind blogs
4. Show HN (Algolia API, AI filter)
5. Claude Code + Cursor release changelogs
6. Watchlist (Nitter RSS for 15 key people)

## Troubleshooting

**"feed doctor" fails on groq** → `.env` not loaded. From project root, check
`python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(bool(os.environ.get('GROQ_API_KEY')))"`.

**Telegram sends work but reactions don't save** → check `fly logs`. Most
common: GITHUB_TOKEN lacks Contents:write on the repo, or GITHUB_REPO is
misspelled.

**Webhook URL set but Telegram says "Bad Request"** → double-check the URL has
no trailing slash and includes `/webhook/<secret>` with the exact secret from
your Fly secrets.

**All items score 0** → scoring LLM is refusing to return valid JSON. Try
bumping `providers.groq.models.rank` to a 70B model, or switch
`routes.rank` to `gemini`.

**Same item pushed twice** → never re-runs should not happen thanks to
`state/items.jsonl` dedup. If it does, check that routines are doing
`git pull` before running — if they don't, their local state drifts.

## What's next

- **Add vault integration.** When comfortable, add a `feed vault-sync` command
  that writes digest markdown into your Obsidian `Learning_Project/` vault so
  both knowledge systems compound together.
- **Port to WhatsApp** once Telegram has been rock-solid for 3 weeks. Your
  existing Meta API integration makes this a drop-in replacement for
  `feed/push.py`.
- **Add voice follow-ups.** The Tavily + Claude synthesis in `follow_up.py`
  already produces short text that would read well as a TTS audio message.
