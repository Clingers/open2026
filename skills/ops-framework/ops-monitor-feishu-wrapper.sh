#!/bin/bash
# ops-monitor-feishu-wrapper.sh - 将 ops-monitor 的报告记录并选择性发送

set -euo pipefail

CONFIG_FILE="${CONFIG_FILE:-/root/.openclaw/net/config/ops-jobs.json}"
WORKSPACE="/root/.openclaw/workspace-zhenzhu"

# 生成报告
REPORT=$(python3 "$WORKSPACE/skills/ops-framework/ops-monitor.py" tick \
    --config-file "$CONFIG_FILE" \
    --print-only 2>&1)

EXIT_CODE=$?

# 总是记录到系统日志
if [ $EXIT_CODE -eq 0 ]; then
    logger -t ops-monitor "HEALTH: $REPORT"
else
    logger -t ops-monitor "ERROR: $REPORT"
fi

# 如果有错误或警告，也记录到专用文件
if echo "$REPORT" | grep -qi "error\|fail\|down\|critical\|warn"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $REPORT" >> "$WORKSPACE/monitoring/alerts.log"
fi