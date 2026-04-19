"""Create and run Claude Code remote triggers via the API.

Uses the GitHub token for auth since we can't access the Claude session token
from a standalone Python process. Falls back gracefully.
"""
from __future__ import annotations

import json
import os
import subprocess


def create_and_run_trigger(trigger_body: dict) -> str | None:
    """Create a trigger and immediately run it. Returns trigger_id or None.

    Uses `claude` CLI if available (it has the auth token).
    Falls back to writing a trigger spec file for manual execution.
    """
    # Write the trigger spec so the routine can pick it up
    spec_path = "/tmp/frontier-feed-trigger.json"
    with open(spec_path, "w") as f:
        json.dump(trigger_body, f, indent=2)

    # Try using claude CLI to create the trigger
    try:
        # The claude CLI has auth context — use it to create + run
        result = subprocess.run(
            ["claude", "-p",
             f"Use the RemoteTrigger tool to: "
             f"1. Create a trigger with this config: {json.dumps(trigger_body)} "
             f"2. Immediately run it with action='run' "
             f"3. Return the trigger_id"],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0 and "trig_" in result.stdout:
            # extract trigger id
            import re
            m = re.search(r"trig_\w+", result.stdout)
            return m.group(0) if m else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None
