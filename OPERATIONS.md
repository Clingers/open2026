# OPERATIONS.md - 系统运维状态

**更新时间**: 2025-03-17
**负责人**: 珍珠 (Kid Ops Specialist)

---

## 📊 当前系统状态

### 磁盘使用
- **总容量**: 49.1 GB
- **已使用**: 18.6 GB (38%)
- **可用空间**: 28.3 GB (62%) ✅
- **工作区**: `/root/.openclaw/workspace-zhenzhu`

### Git 状态
- ✅ **近期已初始化 Git 仓库**
- 主分支: `main`
- 提交历史: 2 次提交
- 首次提交时间: 2025-03-17
- `.gitignore` 已配置 (排除日志和临时文件)

### 负载情况
- 系统运行正常
- 无异常负载报告

---

## 🔧 已安装技能

### P0 - 核心运维技能

| 技能名 | 版本 | 状态 | 用途 |
|--------|------|------|------|
| ops-dashboard | 1.0.1 | ✅ 已安装 | 快速查看系统健康（磁盘、git、资源） |
| ops-framework | 0.1.0 | ✅ 已安装 | 长任务执行、检查点、监控告警框架 |
| auto-monitor | 1.0.0 | ✅ 已安装 | 主动监控系统状态，自动汇报异常 |
| log-analyzer | 1.0.0 | ✅ 已安装 | 日志解析、搜索和分析，调试利器 |
| cron-scheduling | 1.0.0 | ✅ 已安装 | 定时任务管理（cron/systemd timer） |
| rhandus-alerting-system | 1.0.0 | ✅ 已安装 | 集中式告警系统，多通道通知 |

### 使用示例

#### ops-dashboard
```bash
# 查看基本状态
python3 skills/ops-dashboard/scripts/ops_dashboard.py --show summary

# 查看详细资源
python3 skills/ops-dashboard/scripts/ops_dashboard.py --show resources

# JSON 输出供其他脚本使用
python3 skills/ops-dashboard/scripts/ops_dashboard.py --output json
```

#### ops-framework
```bash
# 验证配置
python3 skills/ops-framework/ops-monitor.py validate-config --config-file ~/.openclaw/net/config/ops-jobs.json

# 查看任务状态
python3 skills/ops-framework/ops-monitor.py status

# 运行监控周期
python3 skills/ops-framework/ops-monitor.py tick
```

#### auto-monitor
```bash
# 自动监控（主动汇报，无需人工触发）
# 配置为定时任务，定期检查并主动报告
```

#### log-analyzer
```bash
# 搜索错误日志
log-analyzer search /var/log/syslog --pattern "ERROR\|CRITICAL"

# 实时监控日志
log-analyzer tail /var/log/app.log --follow

# 分析堆栈跟踪
log-analyzer parse-stack trace.log
```

#### cron-scheduling
```bash
# 列出所有定时任务
cron list

# 创建新的cron任务
cron create "*/5 * * * * /root/.openclaw/workspace-zhenzhu/skills/ops-framework/ops-monitor.py tick"

# 管理systemd timer
systemd-timer list
```

#### rhandus-alerting-system
```bash
# 设置磁盘空间告警
alert threshold system.disk --path / --max 90 --channel telegram

# 监控关键服务
alert monitor https://localhost:18952/health --interval 60 --channel telegram

# 查看活跃告警
alert status --active

# 配置Telegram通道（需要设置TELEGRAM_CHAT_ID）
```

---

## 🚀 进行中的长监控项目

### system-health-monitor
- **状态**: ✅ **运行中** (通过 systemd timer 每5分钟触发)
- **启动时间**: 2025-03-17 12:15
- **类型**: 长运行读取任务
- **频率**: 每5分钟收集一次健康指标
- **自动恢复**: ✅ 启用
- **配置文件**: `/root/.openclaw/net/config/ops-jobs.json`
- **系统日志**: `journalctl -t ops-monitor`
- **告警日志**: `/root/.openclaw/workspace-zhenzhu/monitoring/alerts.log` (如有异常)

**监控指标**:
- 磁盘使用率
- Git 状态
- 系统负载
- 大目录占用

**通知机制**:
- ✅ 正常状态: 记录到 systemd journal (tag: ops-monitor)
- ⚠️ 异常状态: 记录到 alerts.log 并可通过 wrapper 扩展通知
- 🔄 可配置 Feishu/Telegram/Email 通知 (待配置)

---

## 🎯 下一步计划

### 已完成 ✅
- ✅ Git 版本控制已初始化
- ✅ 安装核心运维技能套件（6个技能）
- ✅ 启动 system-health-monitor 长监控任务
- ✅ 配置 systemd timer 自动运行 ops-monitor tick（每5分钟）
- ✅ 实现基础监控输出（stdout/journald）

### 进行中 🔄
- 🔄 **配置 Feishu 通知集成** - 通过 openclaw message send 发送告警
- 🔄 **配置 rhandus-alerting-system** - 高级告警规则和多通道通知
- 🔄 **设置关键指标阈值告警** - 磁盘、内存、CPU、服务健康
- 🔄 **配置日志轮转策略** - 管理 /tmp/health-monitor.log 和 alerts.log

### 待完成 ⏳
- ⏳ 建立日志轮转和归档策略
- ⏳ 配置自动备份工作区配置
- ⏳ 创建 incident post-mortem 模板
- ⏳ 设置 ops-dashboard 定期报告（日报/周报）
- ⏳ 集成 Feishu/Telegram 通知渠道

---

## 📚 运维手册 (Playbooks)

### 故障处理指南

| 场景 | 手册 | 链接 |
|------|------|------|
| 磁盘空间不足 | Disk Space Crisis | `playbooks/disk-space-crisis.md` |
| OpenClaw 服务宕机 | Gateway Recovery | `playbooks/openclaw-gateway-recovery.md` |
| 监控告警失效 | Monitoring Failure | `playbooks/monitoring-failure.md` (待创建) |
| 日志轮转问题 | Log Rotation | `playbooks/log-rotation.md` (待创建) |

### 使用流程
1. 识别问题类型
2. 打开对应 playbook
3. 按步骤执行
4. 记录处理结果到 `incidents/` 目录

### 演练计划
- [ ] 每月一次故障演练
- [ ] 每季度更新 playbooks
- [ ] 每次实际故障后优化流程

---

## 📝 事件管理 (Incidents)

### 目录结构
```
incidents/
├── TEMPLATE.md           # 报告模板
├── YYYY-MM-DD-title.md   # 历史事件报告
└── index.md              # 事件索引（自动生成）
```

### 报告规范
- 发现后24小时内提交报告
- 使用 `TEMPLATE.md` 作为基础
- 关注根因分析而非表面现象
- 包含可执行的改进措施

### 跟踪表格（自动维护）

| 事件 | 严重性 | 开始时间 | 解决时间 | MTTR | 根本原因 |
|------|--------|----------|----------|------|----------|
| [查看所有](incidents/) | - | - | - | - | - |

### 事后复盘 (Post-Mortem)
- 技术复盘: 发生了什么？为什么？
- 流程复盘: 响应是否及时？沟通是否顺畅？
- 改进复盘: 如何防止再次发生？

---

## 🕐 定时任务配置

### ops-monitor tick (报告生成)
**频率**: 每 30 分钟  
**调度**: crontab `*/30 * * * * /usr/local/bin/ops-monitor-tick`  
**日志**: `/var/log/ops-monitor-tick.log`  
**状态**: ✅ 已配置并运行中

**首次运行**: 2026-03-17 14:03

### memory-hygiene (记忆数据库维护)
**频率**: 每周日凌晨 02:00  
**调度**: crontab `0 2 * * 0 /root/.openclaw/workspace-zhenzhu/scripts/memory-hygiene.py`  
**日志**: `/var/log/memory-hygiene.log`  
**功能**: 
- 数据库 VACUUM 压缩
- 清理过期记录
- 大小监控与报告
**状态**: ✅ 已配置

**首次运行**: 2026-03-17 14:09 (DB 68.0 KB, 已是最简状态)

---

## 📦 初始化完成报告

**日期**: 2025-03-17 12:18 GMT+8
**操作**: Git 仓库初始化
**结果**: ✅ 成功

### Git 配置
- 主分支: `main`
- 总提交数: 2
- 首次提交: ae3256a (workspace setup)
- 最新提交: dd75252 (.gitignore)
- 已跟踪文件: 27 个
- 忽略模式: 日志、缓存、备份

### 版本控制内容
- ✅ Identity & Philosophy (SOUL.md, IDENTITY.md)
- ✅ Operational Docs (OPERATIONS.md)
- ✅ Monitoring Configs (ops-jobs.json, health_status.py)
- ✅ Skill Files (ops-dashboard, ops-framework)
- ✅ Documentation (monitoring/, skill-vetting-)

---

*小小运维珍珠，守护系统稳定！🔧🧒✨*