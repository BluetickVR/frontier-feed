# Routine 3 — Evening push

**Schedule:** 19:30 daily (local time)
**Repo:** anshulpadyal/frontier-feed

## Prompt

```
Run the evening digest — smaller than morning, only top 3.

1. env:
   - python -m venv .venv && source .venv/bin/activate
   - pip install -e .

2. pull latest reactions (webhook may have added them since lunch):
   - git pull --rebase --autostash origin main

3. Run:
   - feed digest --slot evening

4. commit + push:
   - git add state/ digests/
   - git diff --cached --quiet || git commit -m "routine: evening digest $(date -u +%Y-%m-%dT%H:%M)"
   - git push origin main

5. Report the JSON one-liner.
```

## Notes

- Evening uses the same fetchers and scoring, but the `evening_push_max_items`
  budget (set in context.yaml, default 3) caps output.
- If morning already consumed everything, evening may be empty — that's fine,
  don't worry if it says "quiet evening".
