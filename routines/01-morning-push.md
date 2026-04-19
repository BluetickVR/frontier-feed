# Routine 1 — Morning push

**Schedule:** 06:45 daily (local time)
**Repo:** anshulpadyal/frontier-feed

## Prompt

```
You are running the frontier-feed morning digest. Do exactly this:

1. Activate the environment:
   - python -m venv .venv && source .venv/bin/activate
   - pip install -e .

2. Run the digest:
   - feed digest --slot morning

3. Commit and push:
   - git config user.email "routine@frontier-feed"
   - git config user.name "frontier-feed-routine"
   - git add state/ digests/
   - git diff --cached --quiet || git commit -m "routine: morning digest $(date -u +%Y-%m-%dT%H:%M)"
   - git push origin main

4. Report back with a one-line summary of the JSON output from step 2 (how many
   items were fetched, ranked, selected, pushed).

If `feed doctor` would fail (missing secret), fix the secret before anything
else. Do NOT send "silent failure" messages. Either the push happens or I know
it didn't.
```

## Notes

- The `digest` command writes a markdown digest file to `digests/` and pushes
  selected items to Telegram in the process.
- If zero items pass the threshold, it sends a "🤫 quiet morning" message
  instead. This is correct — don't treat it as a failure.
- The push is chatty (one message per item). You'll get 5-6 messages at 06:45.
