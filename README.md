# 工业质量统计分析工具

**版本**: 1.0.0-mvp  
**创建**: 2026-03-26 02:31  
**作者**: 德善 (code)  
**目标用户**: 工厂/质量工程师

---

## 功能特性

### ✅ 核心统计
- 平均值、中位数、众数
- 最大值、最小值、极差
- 方差、标准差、变异系数
- 数据分布偏度、峰度

### 📈 Minitab风格图表
- **SPC控制图**: X-R图、X-S图、p图、np图
- **评估图**: 直方图、箱线图、QQ图、茎叶图
- **热力图**: 相关性热力图、数据密度热力图
- **方程分析**: 散点图、回归拟合、残差分析

### 📊 数据支持
- CSV / Excel 文件导入
- 多工作表支持
- 自动数据类型识别
- 缺失值处理

### 📄 报告输出
- PNG 高质量图表
- PDF 综合分析报告
- Excel 统计数据导出
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
python -m iqs stats --file data/sample.csv --column diameter

# 生成SPC X-R控制图
python -m iqs spc --file data/production.csv --type xr --output output/

# 生成热力图 (相关性)
python -m iqs heatmap --file data/quality_matrix.csv --output output/heatmap.png

# 完整分析报告
python -m iqs report --file data/sample.csv --output report.pdf
```

### Web界面 (可选)

```bash
python -m iqs.web
# 访问 http://localhost:8080
```

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
- [ ] 核心统计模块 (进行中)
- [ ] SPC控制图
- [ ] 评估图
- [ ] 热力图
- [ ] 方程分析
- [ ] CLI命令
- [ ] Web界面
- [ ] 文档

---

**开始使用**: `python -m iqs --help`│   ├── spc.py          # SPC控制图 (X-R)
│   ├── assessment.py   # 评估图 (直方图/箱线图/QQ/茎叶)
│   ├── heatmap.py      # 热力图
│   ├── regression.py   # 回归分析
│   ├── capability.py   # 过程能力 (Cp/Cpk)
│   └── report.py       # PDF报告生成器
├── cli/                # 命令行接口
│   └── main.py         # CLI命令集
├── data/               # 示例数据
│   ├── diameter_clean.csv
│   ├── quality_matrix.csv
│   └── regression_clean.csv
└── output/             # 输出目录 (PNG + PDF)
```

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
