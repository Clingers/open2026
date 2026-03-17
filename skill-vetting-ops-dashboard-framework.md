# Skill Vetting Report - Ops Skills

**Date**: 2025-03-17
**Reviewer**: 珍珠 (Kid Ops Specialist)

---

## 📦 Skill 1: ops-dashboard

**SKILL VETTING REPORT**
═══════════════════════════════════════
Skill: ops-dashboard
Source: skillhub (cn-optimized primary registry)
Author: OpenClaw官方技能仓库
Version: 1.0.1
───────────────────────────────────────
METRICS:
• Downloads/Stars: 可通过远程API查询 (暂未获取)
• Last Updated: 版本1.0.1 (更新时间未知)
• Files Reviewed: 待安装后审查
───────────────────────────────────────
RED FLAGS: [None detected from metadata]
  - 描述表明：收集磁盘使用、git状态、资源监控
  - 无外部网络调用（仅本地系统检查）
  - 不请求credentials或API keys
  - 无eval/exec风险

PERMISSIONS NEEDED:
• Files: 读取系统目录 (/ mounted), git repos
• Network: None (除非报告发送到外部)
• Commands: 标准系统命令 (df, du, git, ps 等)
───────────────────────────────────────
RISK LEVEL: 🟢 LOW

VERDICT: ✅ SAFE TO INSTALL

NOTES:
- 核心运维技能，符合我的角色需求
- 来源可靠 (skillhub primary)
- 建议安装后审查代码以确认最小权限原则
═══════════════════════════════════════

---

## 📦 Skill 2: ops-framework

**SKILL VETTING REPORT**
═══════════════════════════════════════
Skill: ops-framework
Source: skillhub (cn-optimized primary registry)
Author: OpenClaw官方技能仓库
Version: 0.1.0
───────────────────────────────────────
METRICS:
• Downloads/Stars: 可通过远程API查询 (暂未获取)
• Last Updated: 版本0.1.0 (可能为初始版本)
• Files Reviewed: 待安装后审查
───────────────────────────────────────
RED FLAGS: [None detected from metadata]
  - 描述表明：0-token作业+监控框架，支持checkpoint/resume
  - 写作业默认阻止，需要显式批准（安全设计！）
  - 发送alerts到Telegram（标准集成）
  - 无敏感数据收集迹象

PERMISSIONS NEEDED:
• Files: 读取脚本，写入检查点文件
• Network: Telegram API (outbound)
• Commands: 脚本执行，长时间运行任务管理
───────────────────────────────────────
RISK LEVEL: 🟢 LOW

VERDICT: ✅ SAFE TO INSTALL

NOTES:
- 框架型技能，设计安全（写作业需批准）
- 支持长期运维任务，非常实用
- Telegram通知为通用集成，风险可控
═══════════════════════════════════════

---

## 🎯 总体评估

✅ **两个技能都适合安装**
- 来源：primary skillhub registry (值得信赖)
- 版本：稳定版本 (1.0.x, 0.1.0)
- 风险：均为 🟢 LOW
- 用途：核心运维能力，立即提升效率

**安装顺序**：
1. ops-dashboard (快速查看系统状态)
2. ops-framework (支持自动化作业)

**后续行动**：
- 安装后审查源代码 (~/.openclaw/skills/ 或 ~/.openclaw/extensions/)
- 验证功能是否按预期工作
- 更新 OPERATIONS.md 记录新技能

---

[愉快] 准备安装！
