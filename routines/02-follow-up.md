# Routine 2 — Follow-up dossiers

**Schedule:** 13:00 daily (local time)
**Repo:** anshulpadyal/frontier-feed

## Prompt

```
Run the follow-up dossier pass. Steps:

1. Activate env:
   - python -m venv .venv && source .venv/bin/activate
   - pip install -e .

2. Pull latest — the webhook writes reactions.jsonl via GitHub API, so you need
   the freshest state:
   - git pull --rebase --autostash origin main

3. Generate dossiers:
   - feed follow-ups --hours 18

   This reads the last 18 hours of reactions, finds items marked `?`, runs
   Tavily deep-search on each, synthesizes a 2-paragraph briefing, and pushes
   the dossier to Telegram.

4. Commit and push any new dossier files:
   - git add dossiers/ state/
   - git diff --cached --quiet || git commit -m "routine: follow-ups $(date -u +%Y-%m-%dT%H:%M)"
   - git push origin main

5. Report: how many '?' reactions found, how many dossiers produced.
```

## Notes

- If I didn't tap `?` on anything, output will show `{questions: 0, dossiers: 0}`
  and nothing gets pushed. This is correct silence.
- Each dossier is saved as `dossiers/<item-id>.md` so I can read them later in
  long form if the Telegram version is too terse.
