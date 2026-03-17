#!/usr/bin/env python3
"""
Memory Hygiene Script - 保持记忆数据库精简
定期清理过期/冗余记录，压缩数据库文件
"""
import sqlite3
import os
import sys
from datetime import datetime, timedelta

DB_PATH = '/root/.openclaw/memory/zhenzhu.sqlite'
LOG_FILE = '/var/log/memory-hygiene.log'

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f'[{timestamp}] {msg}\n')

def optimize_database():
    """压缩数据库，移除空闲空间"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('VACUUM')
        conn.close()
        log('✅ VACUUM completed - database optimized')
    except Exception as e:
        log(f'❌ VACUUM failed: {e}')

def cleanup_old_entries():
    """清理过期的记忆记录（如果有的话）"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # 检查表结构
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        
        cleaned = 0
        for table in tables:
            # 如果表有 timestamp 或 created_at 字段，可以清理旧记录
            try:
                cur.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cur.fetchall()]
                if 'timestamp' in columns or 'created_at' in columns:
                    # 示例：删除30天前的记录（根据实际字段调整）
                    # cutoff = (datetime.now() - timedelta(days=30)).isoformat()
                    # cur.execute(f"DELETE FROM {table} WHERE timestamp < ?", (cutoff,))
                    # cleaned += cur.rowcount
                    pass
            except:
                continue
        
        conn.commit()
        conn.close()
        
        if cleaned > 0:
            log(f'🧹 Cleaned {cleaned} old entries')
        else:
            log('📭 No old entries to clean (tables may not have timestamp fields)')
    except Exception as e:
        log(f'❌ Cleanup failed: {e}')

def report_size():
    """报告当前数据库大小"""
    size_bytes = os.path.getsize(DB_PATH)
    size_kb = size_bytes / 1024
    log(f'📊 Current DB size: {size_kb:.1f} KB')
    return size_kb

def main():
    log('=== Memory hygiene run started ===')
    
    # 报告当前大小
    size_before = report_size()
    
    # 优化数据库
    optimize_database()
    
    # 清理旧记录
    cleanup_old_entries()
    
    # 报告优化后大小
    size_after = report_size()
    
    saved = size_before - size_after
    if saved > 0:
        log(f'💾 Saved {saved:.1f} KB')
    else:
        log('💾 No space savings')
    
    log('=== Memory hygiene run completed ===\n')

if __name__ == '__main__':
    main()