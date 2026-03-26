# 工业质量统计分析工具

**版本**: 2.1.0  
**创建**: 2026-03-26 02:31  
**更新**: 2026-03-26 11:30  
**作者**: 德善 (code)  
**目标用户**: 工厂/质量工程师

---

## 🎉 v2.1.0 新特性

- ✨ **新增图表类型**: 时间序列图、帕累托图
- 🧠 **智能洞察引擎**: 自动生成分析摘要、关键发现、改进建议
- 🎨 **UI 美化升级**: Bootstrap 5 现代化界面，响应式设计
- 📱 **拖拽上传**: 支持拖放 CSV 文件
- 🔧 **代码优化**: 模块化架构，utils.py 统一工具函数
- 🐛 **Bug 修复**: 修复 CSV 注释行处理、列名空格、路径问题

---

## 功能特性

### ✅ 核心统计
- 平均值、中位数、众数
- 最大值、最小值、极差
- 方差、标准差、变异系数
- 数据分布偏度、峰度

### 📈 Minitab风格图表
- **SPC控制图**: X-R图、X-S图、p图、np图
- **评估图 (6种)**: 直方图、箱线图、QQ图、茎叶图、时间序列图、帕累托图
- **热力图**: 相关性热力图、数据密度热力图
- **方程分析**: 散点图、回归拟合、残差分析
- **过程能力**: Cp/Cpk 分析（需规格限）

### 🧠 智能洞察
- 每个分析自动生成文字报告
- 总体摘要、关键发现、改进建议
- 异常检测、趋势分析、稳定性评估

### 📊 数据支持
- CSV 文件导入（支持注释行 #）
- 自动数据类型识别
- 缺失值处理
- 列名自动去空格

### 📄 报告输出
- PNG 高质量图表
- PDF 综合分析报告
- 浏览器直接渲染（无需下载）
- JSON 格式数据接口

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### CLI 使用

```bash
# 基础统计
python -m cli.main stats --file data/sample.csv --column diameter

# 评估图 (6种类型)
python -m cli.main assess --file data/sample.csv --column diameter --type histogram
python -m cli.main assess --file data/sample.csv --column diameter --type timeseries
python -m cli.main assess --file data/sample.csv --column diameter --type pareto

# 生成SPC X-R控制图
python -m cli.main spc --file data/production.csv --column diameter --subgroup-size 5

# 生成热力图 (相关性)
python -m cli.main heatmap --file data/quality_matrix.csv

# 回归分析
python -m cli.main regression --file data/regression.csv --x temperature --y quality

# 过程能力分析
python -m cli.main capability --file data/sample.csv --column diameter --lsl 9.8 --usl 10.2

# 完整分析报告
python -m cli.main report --file data/sample.csv --column diameter --lsl 9.8 --usl 10.2
```

### Web界面 (推荐)

```bash
cd web
source venv/bin/activate  # 激活虚拟环境
python app.py
# 访问 http://localhost:5000
```

**Web 功能**:
- 📊 7 种分析类型（基础统计、SPC、评估图、热力图、回归、能力、报告）
- 🎨 Bootstrap 5 现代化界面
- 🖱️ 拖拽上传 CSV 文件
- 🧠 智能洞察自动生成
- 📱 响应式设计（移动端友好）
- 🖼️ 图片/PDF 浏览器直接渲染

---

## 项目结构

```
industrial-quality-stats/
├── core/
│   ├── statistics.py    # 基础统计计算
│   ├── spc.py          # SPC控制图
│   ├── assessment.py   # 评估图 (直方图/箱线图/QQ图)
│   ├── heatmap.py      # 热力图
│   ├── regression.py   # 回归分析
│   └── capability.py   # 过程能力 (Cp/Cpk)
├── cli/
│   ├── commands.py     # CLI命令实现
│   └── main.py         # CLI入口点
├── web/
│   ├── app.py          # FastAPI/Flask应用
│   └── templates/      # HTML模板
├── config/
│   └── config.yaml     # 默认配置
├── data/               # 示例数据
├── output/             # 图表输出目录
├── tests/              # 单元测试
├── requirements.txt    # Python依赖
└── README.md           # 本文档
```

---

## 配置说明

编辑 `config/config.yaml`:

```yaml
# 图表样式
charts:
  dpi: 300
  figsize: [10, 6]
  style: seaborn-v0_8-whitegrid
  colors:
    - "#1f77b4"
    - "#ff7f0e"
    - "#2ca02c"

# SPC控制限系数 (子组大小n)
spc:
  factors:
    n=2: A2=1.880, D3=0, D4=3.267
    n=3: A2=1.023, D3=0, D4=2.575
    # ... 更多

# 输出格式
output:
  format: png
  directory: output/
  include_stats: true
```

---

## 开发状态

- [x] 项目结构创建
- [x] 核心统计模块
- [x] SPC控制图 (X-R)
- [x] 评估图 (6种：直方图/箱线图/QQ/茎叶/时间序列/帕累托)
- [x] 热力图 (相关性矩阵)
- [x] 回归分析 (线性回归)
- [x] 过程能力 (Cp/Cpk)
- [x] CLI命令 (7个命令)
- [x] Web界面 (Flask + Bootstrap 5)
- [x] PDF报告生成
- [x] 智能洞察引擎
- [x] UI 美化 (响应式设计)
- [ ] Docker 容器化
- [ ] 单元测试

---

**开始使用**: `python -m iqs --help`## 项目结构

```
industrial-quality-stats/
├── core/
│   ├── statistics.py    # 基础统计计算
│   ├── spc.py          # SPC控制图 (X-R)
│   ├── assessment.py   # 评估图 (直方图/箱线图/QQ/茎叶/时间序列/帕累托)
│   ├── insights.py     # 智能洞察引擎 ⭐ NEW
│   ├── heatmap.py      # 热力图
│   ├── regression.py   # 回归分析
│   ├── capability.py   # 过程能力 (Cp/Cpk)
│   └── report.py       # PDF报告生成器
├── cli/                # 命令行接口
│   └── main.py         # CLI命令集 (7个命令)
├── web/                # Web 后端 Flask 应用
│   ├── app.py          # Flask API (7个端点)
│   ├── utils.py        # 工具函数模块 ⭐ NEW
│   ├── templates/
│   │   └── index.html  # Bootstrap 5 美化界面 ⭐ UPDATED
│   └── venv/           # Python 虚拟环境
├── data/               # 示例数据
│   ├── diameter_clean.csv
│   ├── quality_matrix.csv
│   └── regression_clean.csv
├── output/             # 输出目录 (PNG + PDF)
│   └── web_output/     # Web 输出目录
├── release.sh          # 自动发布脚本 ⭐ NEW
├── requirements.txt    # Python依赖
└── README.md           # 本文档
```

**核心文件说明**:
- `web/utils.py`: 统一错误处理、工具函数、SPC 系数表
- `core/insights.py`: InsightGenerator 类，自动生成分析洞察
- `web/templates/index.html`: Bootstrap 5 原生响应式设计，支持拖拽上传

---

## 🎯 常见问题

### Q1: 图表中文字显示异常？

**A**: 系统缺少中文字体。安装字体:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei

# CentOS/RHEL
sudo yum install wqy-zenhei-fonts
```

---

### Q2: 如何添加 Excel 文件支持？

**A**: 工程师目前支持 CSV。如需 Excel，安装 openpyxl:

```bash
pip install openpyxl
```

然后修改 CLI 的数据读取部分使用 `pd.read_excel()`。

---

### Q3: 报告生成失败？

**A**: 使用 `--pdf-name` 指定文件名，或检查 `output` 目录权限:

```bash
mkdir -p output
chmod 755 output
```

---

## 📝 开发备注

- 独立工具，无需 OpenClaw 环境
- 仅支持 CSV 数据格式
- PNG 图表使用 300 DPI，适合打印
- PDF 报告使用 A4 纸张格式

---

## 📄 许可证

MIT License

---

**开发者**: 德善 (code @ Project OpenClaw)  
**版本**: v1.0.0-MVP | 2026-03-26  
**灵感来源**: Minitab 统计分析工具

---

## 🌐 在线演示

访问 GitHub Pages 静态演示页面：

**[https://clingers.github.io/open2026/](https://clingers.github.io/open2026/)**

*注意：演示页面为静态版本，仅展示 UI 和交互流程。完整分析功能需部署后端服务。*

---

## 🚀 完整部署（后端 + 前端）

### 方式1：本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动后端 API (Flask)
python3 -m web.app

# 在新终端启动前端（或直接访问 docs/index.html）
# 前端为静态页面，可双击打开使用
```

访问：
- Web UI: http://localhost:5000 (需后端)
- 静态演示: file:///path/to/docs/index.html

### 方式2：云服务器部署

```bash
# 1. 拉取代码
git clone https://github.com/Clingers/open2026.git
cd open2026

# 2. 安装依赖（生产环境建议使用 gunicorn）
pip install -r requirements.txt

# 3. 启动服务
python3 -m web.app --host 0.0.0.0 --port 5000

# 4. 配置反向代理（Nginx）和系统服务（systemd）
```

---

## 📦 项目结构

```
├── docs/                    # GitHub Pages 静态文件
│   └── index.html          # 演示页面
├── web/                    # 后端 Flask 应用
│   ├── app.py
│   └── templates/
├── cli/                    # 命令行工具
├── core/                   # 核心分析模块
├── data/                   # 示例数据
├── output/                 # 生成结果目录
├── iqs.py                  # 主入口 (推荐)
├── iqs.sh / iqs.bat        # 启动脚本
├── README.md
└── requirements.txt
```

---

## 📄 许可证

MIT License

---

**开发者**: 德善 (code @ Project OpenClaw)  
**版本**: v2.1.0 | 2026-03-26  
**GitHub**: https://github.com/Clingers/open2026

---

## 📦 依赖项

```
Flask==3.0.0
pandas==2.1.4
matplotlib==3.8.2
scipy==1.11.4
seaborn==0.13.0
reportlab==4.0.7
scikit-learn==1.3.2
numpy==1.26.2
```
