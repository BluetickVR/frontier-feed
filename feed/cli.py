"""feed — CLI entrypoint.

Examples:
  feed digest --slot morning
  feed digest --slot evening --only github_trending
  feed follow-ups
  feed journal
  feed weekly
  feed doctor
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

app = typer.Typer(add_completion=False, no_args_is_help=True,
                  help="frontier-feed — personal AI-frontier intel pipeline")


@app.command()
def digest(
    slot: str = typer.Option("morning", help="morning | evening"),
    only: str = typer.Option("", help="comma-separated fetcher names"),
    no_push: bool = typer.Option(False, help="don't send to Telegram"),
    dry_run: bool = typer.Option(False, help="fetch+rank but don't save state or push"),
):
    """Run a digest cycle."""
    from feed.digest import run_digest
    fetchers = [s.strip() for s in only.split(",") if s.strip()] or None
    res = run_digest(slot=slot, only=fetchers, push=not no_push, dry_run=dry_run)
    typer.echo(json.dumps(res, indent=2))


@app.command("follow-ups")
def follow_ups(hours: int = typer.Option(18, help="lookback window for '?' reactions")):
    """For each '?' reaction, run Tavily + synthesize a dossier, push it."""
    from feed.follow_up import run_follow_ups
    res = run_follow_ups(lookback_hours=hours)
    typer.echo(json.dumps(res, indent=2))


@app.command()
def journal():
    """Write today's journal + retune source weights."""
    from feed.journal import run_journal
    res = run_journal()
    typer.echo(json.dumps({k: v for k, v in res.items() if k != "weights"}, indent=2))


@app.command()
def weekly():
    """Sunday synthesis across the week's journals."""
    from feed.weekly import run_weekly_synth
    res = run_weekly_synth()
    typer.echo(json.dumps(res, indent=2))


@app.command()
def send(text: str = typer.Argument(...)):
    """Send a raw text message to your Telegram chat (for testing)."""
    from feed.push import send_text
    r = send_text(text)
    typer.echo(json.dumps({"message_id": r.get("message_id")}, indent=2))


@app.command()
def doctor():
    """Sanity-check env + reach out to each provider once."""
    required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "GROQ_API_KEY"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        typer.echo(f"MISSING env: {', '.join(missing)}", err=True)
        raise typer.Exit(1)

    # telegram reach
    from feed.push import send_text
    try:
        send_text("🩺 doctor: frontier-feed is online.", disable_preview=True)
        typer.echo("telegram: OK")
    except Exception as e:
        typer.echo(f"telegram: FAIL {e}", err=True)

    # groq reach
    try:
        from feed.llm import chat
        out = chat("summarize", "Reply with the single word: pong",
                   system="You reply with exactly one word.", temperature=0, max_tokens=8)
        typer.echo(f"groq: OK ({out!r})")
    except Exception as e:
        typer.echo(f"groq: FAIL {e}", err=True)

    typer.echo("doctor done.")


@app.command()
def poll():
    """Poll Telegram for reactions (used by GitHub Actions every 5 min)."""
    from feed.poll import run_poll
    res = run_poll()
    typer.echo(json.dumps(res, indent=2))


@app.command()
def sync():
    """Push state + today's output files to GitHub via API (no git push needed)."""
    from feed.sync import sync_state
    res = sync_state()
    typer.echo(json.dumps(res, indent=2))


@app.command()
def state():
    """Print state summary."""
    from feed.state import load_pointers, load_reactions, load_weights
    p = load_pointers()
    r = load_reactions()
    w = load_weights()
    typer.echo(json.dumps({
        "pointers": {k: v.isoformat() for k, v in p.items()},
        "reaction_count": len(r),
        "weights": w,
    }, indent=2))


if __name__ == "__main__":
    app()
