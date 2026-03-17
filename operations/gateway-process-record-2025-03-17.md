# OpenClaw Gateway 进程记录

**记录时间**: 2025-03-17 15:50 GMT+8
**记录人**: 珍珠 (Ops Specialist)
**主机**: VM-0-7-ubuntu

---

## 🖥️ 网关进程状态

### 进程信息
```
PID: 407334
PPID: 1202
User: root
Command: openclaw-gateway
运行时间: 0:24.07 (约24分钟)
状态: S ( sleeping )
```

### 资源消耗
- **CPU**: 0.0% (top显示), 平均负载: 0.87/0.35/0.12
- **内存**:
  - VSZ: 31.9 GB (虚拟内存)
  - RSS: 587 MB (实际物理内存)
  - %MEM: 29.6%
- **系统内存**: 1.9 GB 总内存, 895 MB 已用, 248 MB 空闲

---

## ⚙️ 网关配置

### 基础设置 (来自 openclaw.json)
```json
{
  "port": 18952,
  "mode": "local",
  "bind": "lan",
  "controlUi": {
    "basePath": "/txtk83",
    "allowedOrigins": ["http://111.231.12.20:18952"],
    "allowInsecureAuth": true,
    "dangerouslyDisableDeviceAuth": true
  },
  "auth": {
    "mode": "token",
    "token": "73ea8886ea9c7664d232e951fe057e69b34d30df8c0b856c"
  }
}
```

**关键参数:**
- **监听端口**: 18952
- **绑定地址**: lan (本地网络)
- **控制台路径**: `/txtk83`
- **认证方式**: token
- **设备认证**: 已禁用 (dangerouslyDisableDeviceAuth: true)

---

## 🔒 安全状态评估

| 项目 | 状态 | 说明 |
|------|------|------|
| 端口开放 | ✅ | 18952 监听中 |
| 认证 | ✅ | Token 保护 |
| 设备认证 | ⚠️ | 已禁用 (方便但降低安全性) |
| HTTPS | ❓ | 未明确配置 (HTTP) |
| 访问控制 | ⚠️ | allowedOrigins 限制单一域名 |

**建议:**
- 考虑启用设备认证 (生产环境)
- 配置 HTTPS/TLS 加密
- 定期轮换 token

---

## 📊 进程生命周期

- **启动时间**: 约 15:25 (推断，运行24分钟)
- **启动方式**: 可能是手动或通过脚本
- **系统服务**: 未注册 systemd (No systemctl service)

**推荐:**
创建 systemd service 文件，实现自动重启和管理：

```ini
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/openclaw-gateway --config /root/.openclaw/openclaw.json
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🔗 网络连接

```bash
# 检查监听端口
$ netstat -tlnp | grep 18952
# 或
$ ss -tlnp | grep 18952
```

---

## 📝 备注

- 网关进程运行稳定，内存占用 29.6% (587 MB)
- 虚拟内存较大 (31.9 GB) 但实际使用少，正常
- 当前没有配置自动重启机制
- Token 认证已启用，设备认证处于测试模式

---

*下次更新: 建议监控网关日志 (/var/log/openclaw/gateway.log) 和定期检查进程状态*
