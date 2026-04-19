# frontier-feed webhook

Tiny FastAPI app that receives Telegram replies, extracts single-char reactions,
and appends them to `state/reactions.jsonl` in the GitHub repo.

## One-time deploy

```bash
brew install flyctl              # or curl -L https://fly.io/install.sh | sh
fly auth login
cd webhook
fly launch --no-deploy           # accept app name (or edit fly.toml)

# secrets — replace values with real ones
WEBHOOK_SECRET=$(openssl rand -hex 16)
fly secrets set \
  TELEGRAM_WEBHOOK_SECRET="$WEBHOOK_SECRET" \
  TELEGRAM_BOT_TOKEN="<bot-token>" \
  TELEGRAM_CHAT_ID="<chat-id>" \
  GITHUB_TOKEN="<github-pat-repo-scope>" \
  GITHUB_REPO="anshulpadyal/frontier-feed" \
  GITHUB_BRANCH="main"

fly deploy

# register the URL with Telegram
APP_URL=$(fly status --json | jq -r .Hostname)
curl "https://api.telegram.org/bot<bot-token>/setWebhook?url=https://$APP_URL/webhook/$WEBHOOK_SECRET"
```

Verify:
- `curl https://$APP_URL/healthz` → `{"ok":true,...}`
- Reply `.` to one of the bot's items in Telegram → bot confirms `✓ . saved for <id>`
- Check GitHub → new commit updating `state/reactions.jsonl`
