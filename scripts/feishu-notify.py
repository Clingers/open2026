#!/usr/bin/env python3
"""
Feishu notification wrapper for ops-monitor tick output
Parses the ops-monitor tick output and sends to Feishu chat
"""
import json
import sys
import subprocess
from pathlib import Path

def read_tick_log(log_file="/var/log/ops-monitor-tick.log"):
    """Read the latest tick output from log file"""
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        # Get the last non-empty section
        sections = []
        current = []
        for line in lines:
            if line.startswith('==='):
                if current:
                    sections.append(''.join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append(''.join(current))
        return sections[-1] if sections else ""
    except Exception as e:
        return f"Error reading log: {e}"

def send_to_feishu(message):
    """Send message to Feishu via OpenClaw message tool"""
    try:
        # Use OpenClaw message send to the current chat context
        # In OpenClaw runtime, we can use the message tool programmatically
        # For now, just print to stdout as fallback
        print(f"Would send to Feishu: {message[:200]}...")
        return True
    except Exception as e:
        print(f"Failed to send: {e}")
        return False

def main():
    # Check if there's any alert (ERROR or ACTION REQUIRED)
    content = read_tick_log()
    
    # Simple parsing: if contains ERROR or ACTION REQUIRED, send alert
    if "ERROR" in content or "ACTION REQUIRED" in content or "ALERT" in content:
        # This is an alert, send it
        send_to_feishu(f"🚨 Ops Alert:\n\n{content}")
    else:
        # Normal status, maybe send summary
        # For now, just log
        pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())