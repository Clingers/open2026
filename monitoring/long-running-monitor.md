# 长监控项目状态

**启动时间**: 2025-03-17 12:15 GMT+8
**状态脚本**: `skills/ops-framework/scripts/health_status.py` (返回 JSON)
**ops-monitor 兼容**: ✅ 通过 (返回符合规范的 JSON)

---

## 📊 监控输出示例

```
🛠️ Ops 快报（12:16:43）

• 系统健康状态连续监控 (system-health-monitor, long_running_read)
- 状态: running (pid=323172)
- 信息: Health monitor running (PIDs: 2)
```

---

## 🔍 当前健康指标

### 1. system-health-monitor (长运行)
- **类型**: long_running_read
- **风险**: read_only
- **频率**: 每5分钟检查一次
- **报告周期**: 每30分钟 (如果启用Telegram告警)
- **自动恢复**: ✅ 启用
- **当前状态**: 正在运行

**命令**:
```bash
python3 skills/ops-dashboard/scripts/ops_dashboard.py --show summary
```

**输出示例**:
```
Disk usage:
  Total: 49.1 GB
  Used:  18.6 GB
  Free:  28.3 GB
```

### 2. disk-space-check (一次性读取)
- **类型**: one_shot_read
- **频率**: 每小时 (建议)
- **用途**: 快速磁盘空间检查
- **状态**: ✅ 就绪，待调度

### 3. verify-backups (备份验证)
- **类型**: one_shot_read
- **用途**: 检查备份文件数量
- **状态**: ⏳ 待启用 (根据需求)

---

## 📊 当前健康指标

- ✅ **磁盘空间**: 18.6 GB / 49.1 GB (38% 使用)
- ⚠️ **Git 状态**: 工作区未初始化 (建议建立版本控制)
- ✅ **监控进程**: PID 323172 运行正常
- ✅ **日志文件**: /tmp/health-monitor.log

---

## 🔔 告警策略 (可选配置)

建议设置以下阈值告警：

| 指标 | 警告阈值 | 严重阈值 | 检查频率 |
|------|---------|---------|---------|
| 磁盘使用率 | >80% | >90% | 每小时 |
| 负载平均值 | >2.0 | >4.0 | 每5分钟 |
| 监控进程停止 | - | 立即 | 持续 |

---

## 🛠️ 管理命令

```bash
# 查看所有任务状态
python3 skills/ops-framework/ops-monitor.py status --config-file /root/.openclaw/net/config/ops-jobs.json

# 启动任务
python3 skills/ops-framework/ops-monitor.py start system-health-monitor --config-file /root/.openclaw/net/config/ops-jobs.json

# 停止任务
python3 skills/ops-framework/ops-monitor.py stop system-health-monitor --config-file /root/.openclaw/net/config/ops-jobs.json

# 运行一次性检查
python3 skills/ops-framework/ops-monitor.py run disk-space-check --config-file /root/.openclaw/net/config/ops-jobs.json

# 运行监控周期 (通过cron/systemd定期调用)
python3 skills/ops-framework/ops-monitor.py tick --config-file /root/.openclaw/net/config/ops-jobs.json
```

---

## 📅 下一步建议

1. ✅ 长监控已启动
2. ⏳ 配置 systemd/cron 自动运行 ops-monitor.py tick
3. ⏳ 集成 Telegram 告警 (需要配置 bot token)
4. ⏳ 建立 Git 仓库版本控制
5. ⏳ 设置磁盘空间阈值告警

---

*珍珠的长监控项目正式启动！🔧🧒✨*