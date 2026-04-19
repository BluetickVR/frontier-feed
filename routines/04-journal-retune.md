# Routine 4 — Journal + retune

**Schedule:** 22:00 daily (local time)
**Repo:** anshulpadyal/frontier-feed

## Prompt

```
Close out the day: read today's reactions, retune source weights, write journal.

1. env:
   - python -m venv .venv && source .venv/bin/activate
   - pip install -e .

2. pull latest:
   - git pull --rebase --autostash origin main

3. Run:
   - feed journal

   This reads the last 24h of reactions, recomputes source_weights.yaml, writes
   a journal markdown file, and pings Telegram with a one-liner summary.

4. commit + push:
   - git add state/ journals/
   - git diff --cached --quiet || git commit -m "routine: journal $(date -u +%Y-%m-%dT%H:%M)"
   - git push origin main

5. Report the JSON one-liner (reaction count + path).
```

## Notes

- Retune is idempotent: source_weights.yaml is recomputed from scratch every
  call using *all* historical reactions. No drift.
- Floor is 0.3, cap is 2.0 — a source can't be fully muted or infinitely
  amplified by reactions. This is on purpose.
