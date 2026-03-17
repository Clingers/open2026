#!/usr/bin/env python3
import psutil, subprocess, logging, sys, os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
CPU_WARN, CPU_CRIT = 80, 90
MEM_WARN, MEM_CRIT = 85, 90
DISK_WARN = 85

def check_services():
  alerts = []
  try:
    subprocess.run(['pgrep', '-f', 'openclaw-gateway'], check=True, capture_output=True)
  except subprocess.CalledProcessError:
    alerts.append("❌ OpenClaw gateway 停止")
  try:
    subprocess.run(['pgrep', '-f', 'agent-team-orchestration'], check=True, capture_output=True)
  except subprocess.CalledProcessError:
    alerts.append("❌ agent-team-orchestration 停止")
  return alerts

def check_system():
  alerts = []
  cpu = psutil.cpu_percent(interval=1)
  mem = psutil.virtual_memory().percent
  disk = psutil.disk_usage('/').percent
  if cpu >= CPU_CRIT:
    alerts.append(f"🔴 CPU 过载: {cpu}%")
  elif cpu >= CPU_WARN:
    alerts.append(f"🟡 CPU 警告: {cpu}%")
  if mem >= MEM_CRIT:
    alerts.append(f"🔥 内存不足: {mem}%")
  elif mem >= MEM_WARN:
    alerts.append(f"🟡 内存警告: {mem}%")
  if disk >= DISK_WARN:
    alerts.append(f"🟡 磁盘空间不足: {disk}%")
  return alerts

if __name__ == "__main__":
  sys_alerts = check_system()
  svc_alerts = check_services()
  all_alerts = sys_alerts + svc_alerts
  if all_alerts:
    logger.error("告警: " + " | ".join(all_alerts))
    print("ALERT_TRIGGERED:" + "|".join(all_alerts))
    sys.exit(1)
  else:
    logger.info("系统正常")
    sys.exit(0)
