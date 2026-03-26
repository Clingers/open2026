#!/bin/bash
# 工业质量统计工具 - 发布脚本
# 用法: ./release.sh [版本号] [选项]
# 示例: ./release.sh v1.0.0 --skip-tests --github-release

set -e  # 遇到错误立即退出

VERSION=${1:-}
if [[ -z "$VERSION" ]]; then
  echo "用法: $0 <版本号>  [--skip-tests] [--skip-lint] [--github-release]"
  echo "示例: $0 v1.0.0"
  echo ""
  echo "选项:"
  echo "  --skip-tests       跳过测试 (默认: 运行 pytest)"
  echo "  --skip-lint        跳过代码检查 (默认: 运行 flake8)"
  echo "  --github-release   自动创建 GitHub Release (需要 GITHUB_TOKEN)"
  exit 1
fi

# 校验版本格式
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "错误: 版本号格式应为 vX.Y.Z (如 v1.0.0)"
  exit 1
fi

# 解析可选参数
SKIP_TESTS=false
SKIP_LINT=false
CREATE_GITHUB_RELEASE=false
shift
while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-tests) SKIP_TESTS=true ;;
    --skip-lint) SKIP_LINT=true ;;
    --github-release) CREATE_GITHUB_RELEASE=true ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
  shift
done

echo "🔖 正在发布版本 $VERSION ..."

# 0. 检查是否在正确的目录
if [[ ! -f "pyproject.toml" ]]; then
  echo "错误: 请在项目根目录运行此脚本"
  exit 1
fi

# 1. 固定文档版本
echo "📝 更新文档版本号..."
if [[ -f "docs/README.md" ]]; then
  sed -i "s/^version:/version: $VERSION/" docs/README.md
  echo "  - 已更新 docs/README.md"
fi

# 2. 生成版本文件
echo "📦 生成版本文件..."
cat > VERSION << EOF
$VERSION
EOF
echo "  - VERSION 文件已创建"

# 3. 运行测试和检查 (可选)
if [[ "$SKIP_TESTS" == "false" ]]; then
  echo "🧪 运行测试..."
  if command -v pytest &> /dev/null; then
    python -m pytest tests/ -v --tb=short
    echo "  ✅ 测试通过"
  else
    echo "⚠️  pytest 未安装，跳过测试"
    echo "  提示: pip install pytest"
  fi
else
  echo "⏭️  跳过测试"
fi

if [[ "$SKIP_LINT" == "false" ]]; then
  echo "🔍 运行代码检查..."
  if command -v flake8 &> /dev/null; then
    python -m flake8 cli/ core/ --max-line-length=100 || true
    echo "  ✅ 代码检查完成"
  else
    echo "⚠️  flake8 未安装，跳过 lint"
    echo "  提示: pip install flake8"
  fi
else
  echo "⏭️  跳过 lint"
fi

# 4. 更新 CHANGELOG
if [[ -f "CHANGELOG.md" ]]; then
  echo "📜 更新 CHANGELOG.md..."
  DATE=$(date +%Y-%m-%d)
  cat > CHANGELOG.new << EOF
## [$VERSION] - $DATE

### 新增
- [待填写]

### 修复
- [待填写]

### 改进
- [待填写]

$(cat CHANGELOG.md)
EOF
  mv CHANGELOG.new CHANGELOG.md
  echo "  - CHANGELOG.md 已更新"
else
  echo "⚠️  未找到 CHANGELOG.md，跳过"
fi

# 5. 提交版本文件
echo "💾 提交版本文件和更新..."
git add docs/README.md VERSION CHANGELOG.md
git commit -m "chore: 发布版本 $VERSION

- 固定文档版本
- 生成 VERSION 文件
- 更新 CHANGELOG" || echo "  ⚠️  无文件需要提交或提交失败"

# 6. 打标签
echo "🏷️  创建 Git tag..."
git tag -a "$VERSION" -m "版本 $VERSION"

# 7. 推送
echo "🚀 推送到远程仓库..."
git push origin main || git push origin master || echo "  ⚠️  推送失败，请手动推送"
git push origin "$VERSION" || echo "  ⚠️  标签推送失败，请手动推送"

# 8. 创建 GitHub Release (可选)
if [[ "$CREATE_GITHUB_RELEASE" == "true" ]]; then
  echo "🐙 创建 GitHub Release..."
  if command -v gh &> /dev/null; then
    # 检查是否已认证
    if gh auth status &> /dev/null; then
      gh release create "$VERSION" \
        --title "版本 $VERSION" \
        --notes "自动发布的版本 $VERSION。请在此附上构建产物和发布说明。" \
        --latest=false
      echo "  ✅ GitHub Release 已创建"
    else
      echo "❌ GitHub CLI 未认证，请运行: gh auth login"
      exit 1
    fi
  elif [[ -n "$GITHUB_TOKEN" ]]; then
    # 使用 GITHUB_TOKEN 创建 release
    gh_release_notes="自动发布的版本 $VERSION。请在此附上构建产物和发布说明。"
    curl -X POST \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      https://api.github.com/repos/$(git config --get remote.origin.url | sed 's|^.*github.com[:/]\([^/]*/[^.]*\).*|\1|')/releases \
      -d "{\"tag_name\":\"$VERSION\",\"name\":\"版本 $VERSION\",\"body\":\"$gh_release_notes\"}"
    echo "  ✅ GitHub Release 已创建"
  else
    echo "❌ 未找到 GitHub CLI 或 GITHUB_TOKEN，无法自动创建 Release"
    echo "  请手动在 GitHub 页面创建 Release，或安装 gh CLI: https://cli.github.com/"
    exit 1
  fi
else
  echo "⏭️  跳过 GitHub Release 创建"
fi

echo ""
echo "✅ 版本 $VERSION 发布完成！"
echo ""
echo "后续步骤:"
echo "1. 如果未自动创建，请手动在 GitHub 上创建 Release (可上传构建产物)"
echo "2. 如需发布 PyPI: python -m build && twine upload dist/*"
echo "3. 更新 README 中的徽章和安装指令"
echo ""
echo "当前状态:"
echo "  - Git tag: $VERSION"
echo "  - 分支: $(git branch --show-current)"
echo "  - 最新提交: $(git log -1 --oneline)"
