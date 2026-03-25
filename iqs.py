#!/usr/bin/env python3
"""
工业质量统计工具主入口
使用: python3 iqs.py 或 ./iqs (Linux/macOS)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.main import cli

if __name__ == '__main__':
    cli()
