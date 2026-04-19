# frontier-feed

Personal AI-frontier intelligence pipeline → Telegram. Reactive, routine-driven,
zero-touch once configured.

## What it does

1. **Fetches** daily signal from sources you choose (GitHub Trending, HF Papers,
   arxiv, company blogs, HN, watchlist, tool changelogs).
2. **Ranks** each item against your personal `context.yaml` using a cheap LLM
   (Groq by default).
3. **Pushes** the top 5-6 to your Telegram chat at 06:45 — each with a "why this
   matters to you" line you can tap through in 2 seconds.
4. **Reacts** to your taps: `.` read, `?` dig deeper, `+` more like this,
   `-` less. A webhook on Fly.io captures replies and writes them back to git.
5. **Follows up** at 13:00 on every `?` with a Tavily deep-search + 2-paragraph
   dossier pushed back to Telegram.
6. **Evening push** at 19:30 — smaller, 3 items, re-ranked with today's weight
   adjustments.
7. **Journals** at 22:00 — retunes source weights from today's reactions, writes
   a journal file, pings you with a one-liner.
8. **Weekly synth** Sunday 21:00 — trend rollup, gaps to fix, sources to add/drop.

## Architecture

```
[Fetchers] → [Scorer (Groq)] → [Selector] → [Telegram push]
                                                  ↓
                                            you tap ./?/+/-
                                                  ↓
              [Fly.io webhook] ← Telegram reply ←
                      ↓
                state/reactions.jsonl (git)
                      ↓
       [Claude Max routines on schedule] → loop back to top
```

Nothing local runs all the time. Your Mac can be off. Anthropic's routine
infra fires the scheduled work; the Fly.io box (~256MB always-on) only
captures your Telegram replies.

## Setup

See [SETUP.md](SETUP.md). ~90 minutes end to end if you do it in order.

## Layout

```
frontier-feed/
├── feed/                    # Python package
│   ├── cli.py               # `feed` CLI (digest, follow-ups, journal, weekly, doctor)
│   ├── digest.py            # orchestrator: fetch → rank → push
│   ├── follow_up.py         # '?' reactions → Tavily + briefing
│   ├── journal.py           # nightly retune + journal
│   ├── weekly.py            # Sunday synthesis
│   ├── push.py              # Telegram sender
│   ├── score.py             # LLM-based relevance scorer
│   ├── state.py             # pointers, reactions, weights
│   ├── llm.py               # provider router (groq/gemini/anthropic)
│   ├── models.py            # Item, Reaction
│   └── fetchers/
│       ├── base.py
│       └── github_trending.py
├── webhook/                 # Fly.io deployment
│   ├── main.py              # FastAPI app
│   ├── Dockerfile
│   ├── fly.toml
│   └── README.md
├── routines/                # 5 Claude Max routine prompts
├── state/                   # pointers, reactions.jsonl, weights, items log
├── digests/                 # daily digest markdown
├── dossiers/                # follow-up briefings
├── journals/                # daily journals
├── strategies/              # weekly synthesis
├── context.yaml             # what signal you care about — tune this
├── config.yaml              # LLM routing + fetcher enablement
├── SETUP.md                 # step-by-step setup
└── README.md
```

## Daily commands (if you ever want to run locally)

```bash
feed doctor                          # env + provider health check
feed digest --slot morning           # run the 06:45 cycle now
feed digest --slot evening
feed follow-ups --hours 18           # dossier every '?' from last 18h
feed journal                         # nightly retune
feed weekly                          # Sunday synth
feed send "hi from laptop"           # raw Telegram message test
feed state                           # print pointers, reactions count, weights
```

## Cost

Out of pocket, running indefinitely: **~$0-5/mo**.
- Claude Max (already paid)
- Groq, Gemini, Tavily — all free tier
- Fly.io webhook — free tier covers 256MB always-on
- Telegram — free
- GitHub private repo — free

## Tuning

All tunable state is in **`context.yaml`**:
- `topics.*` — what you care about. Scorer reads these.
- `watchlist.*` — people whose output is almost always worth reading.
- `budgets.relevance_threshold` — lower = more items, higher = pickier.
- `budgets.morning_push_max_items` / `evening_push_max_items` — daily caps.

Nothing else in the system should need editing to change behavior. If you find
yourself wanting to edit Python to tune behavior, the config is wrong.
