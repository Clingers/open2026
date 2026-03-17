#!/usr/bin/env python3
"""Check if health monitor is running and return JSON status."""
import json
import subprocess
import sys
from pathlib import Path

def check_status():
    # Check for the monitoring process
    result = subprocess.run(
        ["pgrep", "-f", "ops_dashboard.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        pids = result.stdout.strip().split('\n')
        return {
            "running": True,
            "completed": False,
            "pid": int(pids[0]) if pids[0] else None,
            "level": "ok",
            "message": f"Health monitor running (PIDs: {len(pids)})"
        }
    else:
        return {
            "running": False,
            "completed": False,
            "pid": None,
            "level": "alert",
            "message": "Health monitor is NOT running"
        }

if __name__ == "__main__":
    status = check_status()
    print(json.dumps(status))