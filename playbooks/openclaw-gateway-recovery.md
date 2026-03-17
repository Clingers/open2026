# OpenClaw 服务宕机处理手册

## 触发条件
- OpenClaw gateway 无法访问 (端口 18952)
- `systemctl status openclaw` 显示 inactive/dead
- 健康检查超时或失败

## 检查步骤

### 1. 检查服务状态
```bash
# 查看 gateway 状态
systemctl status openclaw

# 查看所有 OpenClaw 相关单元
systemctl list-units 'openclaw*' --type=service --all

# 查看 ops-monitor timer 状态
systemctl status openclaw-ops-monitor.timer
```

### 2. 检查进程
```bash
# 查找 OpenClaw 进程
ps aux | grep -i openclaw | grep -v grep

# 检查端口占用
ss -tlnp | grep 18952
netstat -tlnp 2>/dev/null | grep 18952
```

### 3. 查看日志
```bash
# Gateway 日志
journalctl -u openclaw -n 50 --no-pager

# 详细日志（如果配置了日志文件）
tail -50 /var/log/openclaw/gateway.log 2>/dev/null || true

# Ops monitor 日志
journalctl -t ops-monitor -n 20 --no-pager
```

### 4. 常见问题与修复

#### 问题: Gateway 进程不存在
**原因**: 服务未启动或崩溃

**解决**:
```bash
# 尝试重启
sudo systemctl restart openclaw

# 如果失败，检查配置
cat /root/.openclaw/openclaw.json | jq '.gateway'

# 验证配置语法
openclaw gateway validate 2>/dev/null || echo "手动验证配置"
```

#### 问题: 端口被占用
**原因**: 另一个进程占用了 18952

**解决**:
```bash
# 查找占用端口的进程
sudo lsof -i :18952

# 停止冲突进程或修改 OpenClaw 端口
# 编辑 /root/.openclaw/openclaw.json:
# "gateway": { "port": 18953 }
```

#### 问题: 权限错误
**原因**: 配置文件权限不正确或设备认证失败

**解决**:
```bash
# 检查 .openclaw 目录权限
ls -la /root/.openclaw/

# 修复权限
sudo chown -R root:root /root/.openclaw
sudo chmod -R 700 /root/.openclaw

# 检查设备认证
cat /root/.openclaw/identity/device.json
```

#### 问题: 内存不足
**原因**: 系统内存不足导致进程被 OOM 杀死

**解决**:
```bash
# 检查内存使用
free -h
top -b -n 1 | head -20

# 清理缓存
sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

# 添加 swap（临时）
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 5. 快速恢复流程

```bash
#!/bin/bash
# /usr/local/bin/openclaw-recovery.sh

set -e

echo "=== OpenClaw 自动恢复脚本 ==="

# 1. 检查并启动服务
if ! systemctl is-active --quiet openclaw; then
    echo "Gateway 未运行，尝试启动..."
    systemctl start openclaw
    sleep 3
fi

# 2. 验证端口监听
if ! ss -tln | grep -q ':18952 '; then
    echo "ERROR: 端口 18952 未监听"
    systemctl status openclaw --no-pager -l
    exit 1
fi

# 3. 健康检查
if ! curl -s http://localhost:18952/health >/dev/null 2>&1; then
    echo "ERROR: 健康检查失败"
    journalctl -u openclaw -n 20 --no-pager
    exit 1
fi

echo "✅ OpenClaw 服务恢复成功"
logger -t openclaw-recovery "Service recovered successfully"
```

### 6. 预防措施

**系统服务配置**:
```bash
# 启用自动重启（systemd）
sudo systemctl enable openclaw
sudo systemctl set-property openclaw.service Restart=always
sudo systemctl set-property openclaw.service RestartSec=10

# 配置资源限制
sudo systemctl edit openclaw.service

# 添加:
[Service]
MemoryMax=512M
CPUQuota=50%
Restart=on-failure
RestartSec=10
```

**监控集成**:
```bash
# 添加 ops-monitor 检查
# 在 ops-jobs.json 中添加:
{
  "id": "openclaw-health-check",
  "name": "OpenClaw Gateway 健康检查",
  "kind": "one_shot_read",
  "enabled": true,
  "risk": "read_only",
  "cwd": "/",
  "commands": {
    "run": ["bash", "-lc", "curl -s -o /dev/null -w '%{http_code}' http://localhost:18952/health | grep -q '200'"]
  },
  "policy": {
    "reportEverySeconds": 300
  }
}
```

## 验证恢复
```bash
# 测试 API 访问
curl http://localhost:18952/health

# 测试 agent 通信
openclaw agent list

# 检查日志有无错误
journalctl -u openclaw --since "5 minutes ago" | grep -i error || echo "No errors found"
```

---

**备用方案**: 如果无法恢复，考虑回滚到之前的稳定版本
```bash
git -C /root/.openclaw/workspace-zhenzhu log --oneline -5
# 找到之前的提交，回滚
```

**紧急联系**: 如持续无法恢复，检查系统资源或联系系统管理员

---

**负责人**: 珍珠 (Kid Ops Specialist)
**最后更新**: 2025-03-17