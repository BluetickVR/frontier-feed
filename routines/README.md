# Claude Max Routines for frontier-feed

Five routines cover the full autonomous loop. Create each one in Claude Code Web
(Settings → Routines → New Routine). For every routine:

- **Repository:** `anshulpadyal/frontier-feed` (your private GitHub fork)
- **Connectors:** none needed beyond git
- **Secrets to attach** (once per routine, or at workspace level):
  `GROQ_API_KEY`, `GEMINI_API_KEY` (optional), `TAVILY_API_KEY`,
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ANTHROPIC_API_KEY` (optional)

Each routine is a **scheduled** type. All times are in your local timezone —
set the timezone once at the workspace level.

| # | File | Cadence | Purpose |
|---|---|---|---|
| 1 | `01-morning-push.md` | 06:45 daily | Fetch + rank + push 5-6 items |
| 2 | `02-follow-up.md` | 13:00 daily | Handle overnight/morning `?` reactions |
| 3 | `03-evening-push.md` | 19:30 daily | Top 3 items from remaining signal |
| 4 | `04-journal-retune.md` | 22:00 daily | Journal today + retune source weights |
| 5 | `05-weekly-synth.md` | Sunday 21:00 | Weekly trend rollup |

After creating each routine, run it manually once from the UI to confirm it
executes clean. If it fails, read the session transcript — error messages are
self-explanatory.

## Shared setup block (paste at the top of every routine prompt)

```
Set up the environment:
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -e .`
3. Verify: `feed doctor` — this sends a test message to my Telegram. If it
   fails, STOP and report the error. Don't proceed with the rest.
```

This is included in each routine prompt already.
