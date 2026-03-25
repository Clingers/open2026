#!/bin/bash
# 工业质量统计工具启动脚本
# 使用方法: ./iqs.sh [命令] [参数]
# 示例: ./iqs.sh report --file data.csv --column diameter --lsl 24.5 --usl 25.5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
export PYTHONPATH

python3 "$SCRIPT_DIR/cli/main.py" "$@"
