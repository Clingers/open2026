# 磁盘空间不足处理手册

## 触发条件
- 磁盘使用率 > 85%
- `/` 分区可用空间 < 10GB

## 检查步骤

### 1. 快速诊断
```bash
# 查看磁盘使用情况
df -h

# 找出大目录
du -sh /* 2>/dev/null | sort -hr | head -10

# 查看工作区占用
du -sh /root/.openclaw/workspace-* | sort -hr
```

### 2. 常见清理目标

#### OpenClaw 相关
```bash
# 清理旧日志
find /var/log -name "*.log.*" -mtime +30 -delete
find /var/log -name "*.gz" -mtime +60 -delete

# 清理 OpenClaw 临时文件
rm -rf /tmp/openclaw-*
rm -rf /root/.openclaw/tmp/*

# 清理工作区缓存
find /root/.openclaw/workspace-* -name "*.pyc" -delete
find /root/.openclaw/workspace-* -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
```

#### 系统缓存
```bash
# 清理 apt 缓存 (Ubuntu/Debian)
apt clean

# 清理 journald 日志 (保留最近7天)
journalctl --vacuum-time=7d

# 清理缩略图缓存
rm -rf /var/lib/snapd/cache/*
```

### 3. 永久清理策略

#### 配置 logrotate
```bash
# /etc/logrotate.d/openclaw
/var/log/openclaw/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

#### 设置监控告警
```bash
# 在 ops-jobs.json 中添加磁盘检查
{
  "id": "disk-space-critical",
  "name": "磁盘空间严重告警",
  "kind": "one_shot_read",
  "enabled": true,
  "risk": "read_only",
  "cwd": "/",
  "commands": {
    "run": ["bash", "-lc", "USE=$(df / | tail -1 | awk '{print $5}' | tr -d '%'); if [ $USE -gt 85 ]; then echo \"CRITICAL: Disk usage ${USE}%\"; exit 1; fi"]
  },
  "policy": {
    "reportEverySeconds": 3600
  }
}
```

## 恢复后验证
```bash
df -h /  # 确认使用率 < 80%
```

## 预防措施
- 配置自动日志轮转
- 设置定期清理任务（每周）
- 监控大文件增长趋势
- 考虑扩容或分区调整

---

**负责人**: 珍珠 (Kid Ops Specialist)
**最后更新**: 2025-03-17