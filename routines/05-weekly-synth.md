# Routine 5 — Weekly synthesis

**Schedule:** Sunday 21:00 (local time)
**Repo:** anshulpadyal/frontier-feed

## Prompt

```
Weekly rollup.

1. env:
   - python -m venv .venv && source .venv/bin/activate
   - pip install -e .

2. pull latest:
   - git pull --rebase --autostash origin main

3. Run:
   - feed weekly

   This reads the last 7 days of journals, writes strategies/<year-Www>.md,
   and pushes a trimmed version to Telegram.

4. commit + push:
   - git add strategies/
   - git diff --cached --quiet || git commit -m "routine: weekly synth $(date -u +%Y-%m-%dT%H:%M)"
   - git push origin main

5. Report the JSON one-liner.
```

## Notes

- First run needs at least one journal entry (i.e. you must have reacted to at
  least one item during the week). If there are no journals, it exits cleanly
  with a Telegram note.
- The Telegram version caps at 3200 chars. The full version is in `strategies/`.
