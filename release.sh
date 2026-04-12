#!/bin/bash
# 工业质量统计工具 - 发布脚本
# 用法: ./release.sh [版本号]
# 示例: ./release.sh v2.1.0

set -e  # 遇到错误立即退出

VERSION=${1:-}
if [[ -z "$VERSION" ]]; then
  echo "用法: $0 <版本号>"
  echo "示例: $0 v2.1.0"
  exit 1
fi

# 校验版本格式
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "错误: 版本号格式应为 vX.Y.Z (如 v2.1.0)"
  exit 1
fi

echo "🔖 正在发布版本 $VERSION ..."

# 1. 更新 README.md 版本号
echo "📝 更新 README.md 版本号..."
sed -i "s/^**版本**:.*/**版本**: $VERSION | $(date +%Y-%m-%d)/" README.md
echo "  - README.md 已更新"

# 2. 提交更改
echo "💾 提交更改..."
git add README.md
git commit -m "chore: 发布版本 $VERSION" || echo "  ⚠️  无文件需要提交"

# 3. 打标签
echo "🏷️  创建 Git tag..."
git tag -a "$VERSION" -m "版本 $VERSION"

# 4. 推送
echo "🚀 推送到远程仓库..."
git push origin master || git push origin main || echo "  ⚠️  推送失败，请手动推送"
git push origin "$VERSION" || echo "  ⚠️  标签推送失败，请手动推送"

echo ""
echo "✅ 版本 $VERSION 发布完成！"
echo ""
echo "后续步骤:"
echo "1. 在 GitHub 上手动创建 Release: https://github.com/Clingers/open2026/releases/new"
echo "2. 选择 tag: $VERSION"
echo "3. 填写发布说明（可参考以下模板）"
echo ""
echo "发布说明模板:"
cat << 'EOF'
## 🎉 新特性

### ✨ 新增功能
- [功能1]
- [功能2]

### 🐛 Bug 修复
- [修复1]
- [修复2]

### 📊 测试
- ✅ 所有功能测试通过

### 📦 安装
```bash
git clone https://github.com/Clingers/open2026.git
cd open2026/industrial-quality-stats
pip install -r requirements.txt
```

### 🚀 快速启动
```bash
cd web
source venv/bin/activate
python app.py
# 访问 http://localhost:5000
```
EOF
echo ""
echo "当前状态:"
echo "  - Git tag: $VERSION"
echo "  - 分支: $(git branch --show-current)"
echo "  - 最新提交: $(git log -1 --oneline)"
