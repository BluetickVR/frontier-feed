# frontier-feed — Personal AI-Frontier Intelligence Pipeline

## What this is
Push-based daily AI intelligence bot for Anshul Padyal, Founder/CTO of PropViz (acquired by MagicBricks/Times Group, Dec 2024). Goal: build the #1 real estate tech company in the world using AI + 3D tech.

The system fetches signal from 5 sources, scores with a two-pass LLM scorer tuned to Anshul's ambition, pushes to Telegram, and acts on single-character reactions — dossiers, prototype PRs, auto-tweets, LinkedIn posts.

## Architecture

```
[Claude Max Routines, 5 scheduled] ─┬─ 06:45 IST morning push (01:15 UTC)
                                    ├─ 13:00 IST follow-ups (07:30 UTC)
                                    ├─ 19:30 IST evening push (14:00 UTC)
                                    ├─ 22:00 IST journal+retune (16:30 UTC)
                                    └─ Sun 21:00 IST weekly synth (15:30 UTC)
         │
         ▼
  feed CLI (Groq for scoring, Gemini fallback, Tavily for deep-search)
         │
         ▼
  Telegram bot ◀── GitHub Actions (every 5 min) ── reactions.jsonl → GitHub
         │
         ▼
  Prototype PRs → BluetickVR/propviz-prototypes
  Auto-tweets → Twitter (via session cookies)
  Auto-LinkedIn → LinkedIn (via session cookies)
```

## Run / verify
```bash
cd /Users/anshulpadyal/frontier-feed
source .venv/bin/activate
feed doctor          # health check (Telegram + Groq)
feed digest --slot morning   # manual morning push
feed digest --slot morning --dry-run  # fetch+score without pushing
feed poll            # pick up Telegram reactions
feed follow-ups      # generate dossiers for ? items
feed prototypes      # generate prototype PRs for ! items
feed autopublish     # post tweets (p) and LinkedIn (l) items
feed journal         # nightly retune + journal
feed weekly          # Sunday synthesis
feed sync            # push state to GitHub via API
feed state           # print pointers, reactions, weights
feed draft <item-id> --platform twitter|linkedin  # draft a post
feed send "test message"  # raw Telegram test
```

## 5 Sources (all active)
| Source | Fetcher file | Config key | Items/day |
|---|---|---|---|
| GitHub Trending AI | `feed/fetchers/github_trending.py` | `github_trending` | ~25 |
| Twitter watchlist (27 people) | `feed/fetchers/watchlist_twitter.py` | `watchlist_twitter` | ~20-30 |
| HuggingFace Daily Papers | `feed/fetchers/hf_papers.py` | `hf_papers` | ~10 |
| Show HN (AI filter) | `feed/fetchers/show_hn.py` | `show_hn` | ~15 |
| GitHub Releases (Claude Code, Cursor) | `feed/fetchers/github_releases.py` | `tool_changelogs` | ~5 |

## 7 Reactions
| Tap | Handler | What happens |
|---|---|---|
| `.` | instant | Read, never show again |
| `?` | `feed follow-ups` at 13:00 | Tavily deep-search → 2-paragraph dossier on Telegram |
| `!` | `feed prototypes` at 13:00 | Claude Code writes code → PR in propviz-prototypes → link on Telegram |
| `p` | `feed autopublish` at 13:00 | Draft tweet in Anshul's voice → post from his Twitter |
| `l` | `feed autopublish` at 13:00 | Draft LinkedIn post → post from his LinkedIn |
| `+` | `feed journal` at 22:00 | Source weight goes up (×1.15 per +) |
| `-` | `feed journal` at 22:00 | Source weight goes down (×0.80 per -) |

## Scoring (two-pass)
- **Pass 1** (Groq llama-3.3-70b, all items): quick topic relevance filter
- **Pass 2** (Groq 70B, top 20): "Would this help PropViz build something no other real estate tech company in the world has? Or make his 8-dev team ship 2-5x faster?"
- Configured in `feed/score.py`, topics in `context.yaml`

## Push format (two-tier)
- **Tier 1**: Top 8 (morning) / 4 (evening) as full messages with reaction legend
- **Tier 2**: Remaining above-threshold items as a compact scannable list in one message

## Scheduling — GitHub Actions (migrated from Claude Max routines 2026-04-20)
Claude Max routines hit Telegram 403 from Anthropic's cloud IPs. Migrated all
5 to GitHub Actions which has direct repo access + Telegram works fine.

All Claude Max triggers are DISABLED (IDs kept for reference):
`trig_011DVQqk9Q3Zv9536Qev3PdV`, `trig_011gkwTru1kW67HkWymfNbmF`,
`trig_01LwKsSsJjqGPwZKjutY8ypQ`, `trig_01LmwMoq9ZEcxTW6RiXJuKUg`,
`trig_01QCbqCyRRT7UMSemVjncopf`

## GitHub Actions (ALL scheduling runs here)
Repo: https://github.com/BluetickVR/frontier-feed (public)
Manage: https://github.com/BluetickVR/frontier-feed/actions

| Workflow | Cron (UTC) | IST | What |
|---|---|---|---|
| `morning-push.yml` | `15 1 * * *` | 06:45 | Fetch 5 sources → score → push tier 1+2 to Telegram |
| `follow-ups.yml` | `30 7 * * *` | 13:00 | ? → dossier, ! → prototype, p → tweet, l → LinkedIn |
| `evening-push.yml` | `0 14 * * *` | 19:30 | Same as morning, smaller budget (4 items) |
| `journal.yml` | `30 16 * * *` | 22:00 | Retune weights + write journal + Telegram summary |
| `weekly-synth.yml` | `30 15 * * 0` | Sun 21:00 | Weekly trend rollup |
| `poll-reactions.yml` | `*/5 * * * *` | every 5 min | Poll Telegram for reactions, commit to repo |

Secrets (7): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GROQ_API_KEY`, `TAVILY_API_KEY`,
`TWITTER_AUTH_TOKEN`, `TWITTER_CT0`, `LINKEDIN_COOKIE`

## Repos
- **BluetickVR/frontier-feed** — this repo (public, pipeline code + state)
- **BluetickVR/propviz-prototypes** — sandbox for ! prototype PRs (private)

## Key files to edit
- `context.yaml` — identity, topics, watchlist, budgets. **This is the main tuning knob.** Change what you care about here, not in Python.
- `config.yaml` — LLM routing (groq/gemini/anthropic), fetcher enablement, chunk sizes
- `feed/score.py` — scoring prompts and two-pass logic
- `feed/push.py` — Telegram message format
- `feed/fetchers/` — add new fetchers following the BaseFetcher pattern

## Adding a new fetcher
1. Create `feed/fetchers/<name>.py` — subclass `BaseFetcher`, implement `fetch() -> Iterable[Item]`
2. Register in `feed/fetchers/__init__.py` (import + REGISTRY entry)
3. Add config in `config.yaml` under `fetchers:` with `enabled: true`
4. Test: `feed digest --only <name> --dry-run`

## Secrets location
- **Local**: `.env` file (gitignored) — has all tokens
- **GitHub Actions**: repo secrets (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GROQ_API_KEY)
- **Routines**: tokens are embedded in routine prompts (update via RemoteTrigger API if they change)
- **Twitter cookies** (`ct0`) rotate every few weeks — when watchlist fetcher silently stops returning tweets, grab fresh cookies from x.com and update .env + routine prompts
- **LinkedIn cookie** (`li_at`) — same, rotates periodically

## What's NOT built yet (next session priorities)
1. **Internal state scanner** — connect to convrsespaces/convrse-ai GitHub orgs, scan overnight PRs/CI/commits, cross-reference with AI signal. "Aayush's WhatsApp PR is failing CI + this new Meta API change from yesterday probably caused it."
2. **Competitive intelligence** — watch AbsoluteCX, Sirrus AI, Dawn Digital websites/LinkedIn for product changes, job postings, signals of what they're building.
3. **Team routing** — when a digest item is relevant to a specific dev (Aayush=WhatsApp, Devendra=maps, Chaitanya=frontend), ping them directly instead of everything going through Anshul.
4. **Prototype → production bridge** — track which prototype PRs were merged, generate integration plans, assign to the right dev, track if it shipped.
5. **Time-to-adoption tracking** — "First saw: date. Prototyped: date. Shipped: date." Reported in weekly synth.
6. **Company blog fetchers** — Anthropic, OpenAI, DeepMind, Google AI, Mistral blogs via RSS (URLs already in context.yaml, fetcher not built).

## Dev team context (for team routing)
| Name | Focus area | Route signal about |
|---|---|---|
| Aayush | WhatsApp Bot + AI Caller | Meta API, voice AI, Ultravox, conversational AI |
| Chaitanya | Frontend + Backend + Product | React, 3D rendering, WebGL, Three.js, UI frameworks |
| Devendra | Maps (has idle time) | Mapbox alternatives, spatial data, 3D maps, WebGPU |
| Sachin (dev) | Inventory | Data platforms, real-time sync |
| Ankit | Client apps | Mobile, Android, React Native |
| Rahul | Frontend | UI/UX tools, design systems |

## Anshul's stack
React JS, SVG, Mapbox, Android, Node.js, Python, Gemini, Ultravox, Meta WhatsApp API, WebSockets, AWS S3, Three.js

## Cost
$0/mo new spend. Claude Max (already paid), Groq/Tavily/Gemini (free tier), GitHub Actions (free tier), Telegram (free).
