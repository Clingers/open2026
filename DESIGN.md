# DESIGN.md - Industrial Quality Statistics Design System

## 1. Visual Theme & Atmosphere

**关键词**: 工业专业、数据驱动、清晰高效、沉稳可靠

**设计哲学**:
- 界面服务于数据，不喧宾夺主
- 色彩系统反映工业场景（蓝色系=专业，绿色=合格，红色=异常）
- 信息密度适中（既有详细数据，又不压迫）
- 专业但不冰冷，在严谨中加入适度圆角和渐变

**密度**: 中等（适合QC工程师日常使用）

---

## 2. Color Palette & Roles

### 主色调 (Primary)
- `primary` = `#0052cc` - IBM工业蓝，主按钮、链接、选中状态
- `primary-hover` = `#0747a6` - 悬停加深
- `primary-light` = `#e6effc` - 浅蓝背景（用于标签、高亮）

### 语义色 (Semantic)
- `success` = `#00a854` - 过程能力充足（Cpk≥1.33）
- `warning` = `#ffab00` - 过程接近失控（趋势警告）
- `danger` = `#ff4d4f` - 超出控制限、不合格品
- `info` = `#1890ff` - 中性信息、下载链接

### 中性灰 (Neutral)
```css
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;
```

### 背景色
- `bg-body` = `#f9fafb` - 网页背景（极浅灰）
- `bg-card` = `#ffffff` - 卡片背景（纯白）
- `bg-sidebar` = `#f3f4f6` - 侧边栏（稍深灰）

---

## 3. Typography Rules

**字体栈**:
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

**中文字体后备**:
```css
font-family: 'Inter', "PingFang SC", "Microsoft YaHei", sans-serif;
```

**字号层次**:
| 用途 | 字号 | 字重 | 行高 |
|------|------|------|------|
| 页面标题 (H1) | 2.25rem (36px) | 700 (Bold) | 1.2 |
| 卡片标题 (H2) | 1.5rem (24px) | 600 (SemiBold) | 1.3 |
| 区块标题 (H3) | 1.25rem (20px) | 600 | 1.4 |
| 正文 (Body) | 1rem (16px) | 400 (Normal) | 1.6 |
| 小字 (Caption) | 0.875rem (14px) | 400 | 1.5 |
| 代码 (Code) | 0.875rem | 400 | 1.5 |

**等宽字体** (数据表格、统计数值):
```css
font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
```

---

## 4. Component Stylings

### 按钮 (Button)

**主按钮** (Primary):
```css
.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}
.btn-primary:hover {
  background: var(--primary-hover);
  box-shadow: var(--shadow-md);
}
.btn-primary:disabled {
  background: var(--gray-400);
  cursor: not-allowed;
}
```

**次要按钮** (Secondary):
```css
.btn-secondary {
  background: white;
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  padding: 0.75rem 1.5rem;
}
.btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--gray-400);
}
```

**危险按钮** (Danger):
```css
.btn-danger {
  background: var(--danger);
  color: white;
  border: none;
  border-radius: var(--radius-md);
}
```

### 卡片 (Card)

**标准卡片**:
```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base);
}
.card:hover {
  box-shadow: var(--shadow-md);
}
.card-header {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: white;
  font-weight: 600;
  padding: 1rem 1.5rem;
  border: none;
}
```

**图表卡片** (结果页使用):
```css
.chart-card {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}
.chart-card img {
  width: 100%;
  height: auto;
  display: block;
}
```

### 表单控件

**输入框**:
```css
.form-control {
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  font-size: 1rem;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 82, 204, 0.15);
  outline: none;
}
```

**选择器** (Select):
```css
.form-select {
  composes: form-control;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px 12px;
  padding-right: 2.5rem;
}
```

### 标签 (Tag / Badge)

**状态标签**:
```css
.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 2px solid transparent;
}

/* 列选择器标签 */
.column-tag {
  composes: tag;
  background: var(--gray-100);
  color: var(--gray-700);
  border-color: var(--gray-200);
}
.column-tag:hover {
  border-color: var(--primary);
}
.column-tag.selected {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

/* 状态徽章 */
.badge-success { background: var(--success); color: white; }
.badge-warning { background: var(--warning); color: white; }
.badge-danger { background: var(--danger); color: white; }
.badge-info { background: var(--info); color: white; }
```

### 步骤指示器 (Steps)

**水平步骤条** (上传→配置→结果):
```css
.steps-indicator {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  position: relative;
}
.steps-indicator::before {
  content: '';
  position: absolute;
  top: 1rem;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gray-200);
  z-index: 0;
}
.step {
  position: relative;
  z-index: 1;
  background: white;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--gray-500);
  font-weight: 500;
}
.step.active {
  color: var(--primary);
}
.step.completed {
  color: var(--success);
}
.step-circle {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 2px solid var(--gray-300);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: white;
}
.step.active .step-circle {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}
.step.completed .step-circle {
  border-color: var(--success);
  background: var(--success);
  color: white;
}
```

---

## 5. Layout Principles

### 栅格系统
基于Bootstrap 5，但自定义间距:
```css
.container-industrial {
  max-width: 1280px;
  padding-left: var(--space-lg);
  padding-right: var(--space-lg);
}
.row-gap-lg {
  gap: var(--space-lg);
}
```

### 响应式断点
| 名称 | 宽度 | 用途 |
|------|------|------|
| sm | 576px | 手机竖屏 |
| md | 768px | 手机横屏 / 小平板 |
| lg | 992px | 平板 / 小笔记本 |
| xl | 1200px | 桌面标准 |
| xxl | 1400px | 大屏桌面 |

### 页面布局模板

**主内容区**:
```html
<div class="container-industrial py-4">
  <!-- 导航栏 (阶段1添加) -->
  <nav class="main-nav mb-4">...</nav>

  <!-- 页面标题 -->
  <div class="main-header mb-4">
    <div class="header-content">
      <h1>页面标题</h1>
      <p class="subtitle">副标题 / 说明文字</p>
    </div>
  </div>

  <!-- 主要内容 -->
  <div class="row g-4">
    <div class="col-lg-8">
      <!-- 主工作区 -->
    </div>
    <div class="col-lg-4">
      <!-- 侧边栏 -->
    </div>
  </div>
</div>
```

---

## 6. Interaction Patterns

### 拖拽上传区域
```css
.upload-zone {
  border: 3px dashed var(--gray-300);
  border-radius: var(--radius-lg);
  padding: 3rem;
  text-align: center;
  transition: all var(--transition-base);
  background: var(--gray-50);
}
.upload-zone:hover,
.upload-zone.drag-over {
  border-color: var(--primary);
  background: var(--primary-light);
  transform: scale(1.01);
}
```

### 加载状态
```css
.btn.loading {
  position: relative;
  pointer-events: none;
  opacity: 0.7;
}
.btn.loading::after {
  content: '';
  position: absolute;
  width: 1rem;
  height: 1rem;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
}
@keyframes spin {
  to { transform: translateY(-50%) rotate(360deg); }
}
```

### 结果展示区
```css
.result-section {
  background: var(--gray-50);
  border-left: 4px solid var(--primary);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}
.result-image {
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  max-width: 100%;
  height: auto;
}
```

---

## 7. Accessibility

- 色彩对比度: 所有文本满足 WCAG AA 标准 (4.5:1)
- 焦点状态: `:focus-visible` 提供 2px 蓝色外框
- 键盘导航: Tab 键顺序符合逻辑
- 跳过链接: 提供 "跳至主内容" 链接

---

## 8. Icons

使用 **Bootstrap Icons** (已引入):
- `bi-upload` - 上传
- `bi-graph-up-arrow` - 统计分析
- `bi-file-earmark-pdf` - PDF报告
- `bi-download` - 下载
- `bi-check-circle-fill` - 完成状态
- `bi-exclamation-triangle` - 警告

---

## 9. Animation & Motion

**原则**: 短暂、微妙、有目的

| 类型 | 时长 | 缓动 | 用途 |
|------|------|------|------|
| Fast | 150ms | ease | 按钮悬停、标签切换 |
| Base | 250ms | ease | 卡片出现、页面切换 |
| Slow | 350ms | ease | 模态框打开 |

**示例**: 结果区淡入
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.result-section {
  animation: fadeInUp 0.3s ease-out;
}
```

---

## 10. Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

使用 Autoprefixer 自动处理浏览器前缀。

---

## 11. Advanced Components

### Data Card (数据卡片)
用于展示关键指标（KPI），支持图标、数值、趋势指示。

**样式**:
```css
.data-card {
  background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}
.data-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 4px;
  background: var(--gradient-hero);
}
.data-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.25);
}

.data-card .label {
  font-size: 0.875rem;
  color: var(--gray-400);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.data-card .value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-primary-400);
  line-height: 1.2;
  font-family: 'JetBrains Mono', monospace;
}
.data-card .trend {
  margin-top: 0.75rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.data-card .trend.up { color: var(--success); }
.data-card .trend.down { color: var(--danger); }
```

**HTML 结构**:
```html
<div class="data-card">
  <div class="label"><i class="bi bi-activity"></i> 过程能力指数 (Cpk)</div>
  <div class="value">1.42</div>
  <div class="trend up"><i class="bi bi-arrow-up-short"></i> +0.12 较上周</div>
</div>
```

### Glass Panel (玻璃拟态面板)
用于模态框、侧边栏、浮层，增强层次感。

```css
.glass-panel {
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  padding: 24px;
}
```

### Advanced Table (数据表格)
高密度、悬停高亮的表格。

```css
.data-table {
  width: 100%;
  border-spacing: 0 8px;
  border-collapse: separate;
}
.data-table thead th {
  background: var(--color-primary-600);
  color: white;
  font-weight: 600;
  padding: 12px 16px;
  position: sticky;
  top: 0;
  z-index: 10;
  border: none;
}
.data-table tbody tr {
  background: rgba(255,255,255,0.03);
  transition: background 0.15s, transform 0.15s;
}
.data-table tbody tr:hover {
  background: rgba(0,226,255,0.08);
  transform: scale(1.005);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.data-table td {
  padding: 12px 16px;
  border: none;
}
.data-table .numeric {
  text-align: right;
  font-family: 'JetBrains Mono', monospace;
}
```

---

## 12. Data Visualization (ECharts Theme)

### Industrial Dark Theme
使用基于 PostHog 暗色并增强工业蓝调。

```javascript
// static/js/chart-theme.js
const industrialDark = {
  backgroundColor: 'transparent',
  textStyle: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    color: '#e0e0e0'
  },
  title: {
    textStyle: { color: '#ffffff', fontWeight: 600 },
    subtextStyle: { color: '#a0a0a0' }
  },
  legend: {
    textStyle: { color: '#a0a0a0' },
    inactiveColor: '#5a5a5a'
  },
  tooltip: {
    backgroundColor: 'rgba(15, 23, 42, 0.9)',
    borderColor: '#333',
    borderWidth: 1,
    textStyle: { color: '#e0e0e0' },
    padding: [12, 16],
    extraCssText: 'backdrop-filter: blur(8px);'
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#3a3d45' } },
    axisTick: { lineStyle: { color: '#3a3d45' } },
    axisLabel: { color: '#a0a0a0' },
    splitLine: { show: false }
  },
  valueAxis: {
    splitLine: {
      lineStyle: { color: '#2a2d35', type: 'dashed' }
    },
    axisLabel: { color: '#a0a0a0' }
  },
  series: [
    {
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#0052cc' },
          { offset: 0.5, color: '#2979ff' },
          { offset: 1, color: '#00e5ff' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      lineStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#0052cc' },
          { offset: 1, color: '#00e5ff' }
        ]),
        width: 3
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0,82,204,0.4)' },
          { offset: 1, color: 'rgba(0,82,204,0.05)' }
        ])
      }
    }
  ],
  toolbox: {
    iconStyle: { borderColor: '#a0a0a0' },
    emphasis: { iconStyle: { borderColor: '#ffffff' } }
  }
};

// 使用: echarts.init(dom, industrialDark);
```

### 动画规则
- 入场动画时长: `800ms`
- 缓动: `'cubicOut'`
- 数据更新: 平滑过渡 `500ms`
- 悬停高亮: `200ms`

---

## 13. User Experience Enhancements

### 骨架屏 (Skeleton Screens)

**目的**: 数据加载期间保持布局稳定，减少感知等待时间。

**HTML 模板**:
```html
<div class="skeleton-card">
  <div class="skeleton-header shimmer"></div>
  <div class="skeleton-metrics shimmer"></div>
  <div class="skeleton-text shimmer"></div>
  <div class="skeleton-chart shimmer"></div>
</div>
```

**CSS**:
```css
.skeleton-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 16px;
  padding: 24px;
}
.skeleton-header {
  height: 28px;
  width: 60%;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.skeleton-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.skeleton-metrics > div {
  height: 48px;
  border-radius: 8px;
}
.skeleton-text {
  height: 16px;
  width: 90%;
  margin-bottom: 0.75rem;
}
.skeleton-chart {
  height: 300px;
  border-radius: 12px;
}
.skeleton-text:last-child,
.skeleton-metrics:last-child {
  width: 40%;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.skeleton-card > div {
  background: linear-gradient(90deg, 
    rgba(255,255,255,0.05) 0%, 
    rgba(255,255,255,0.1) 50%, 
    rgba(255,255,255,0.05) 100%);
  background-size: 200% 100%;
  animation: shimmer 1.8s infinite linear;
}
```

### 微交互 (Micro-interactions)

1. **按钮点击反馈**: `transform: scale(0.97)` 持续 120ms
2. **输入框聚焦**: 边框色 + 阴影扩散 `0 0 0 3px rgba(0,82,204,0.2)`
3. **卡片悬停**: 上移 4px + 阴影加深
4. **Tab 切换**: 下划线滑动动画，时长 250ms

---

## Version

- **v1.1.0** (2026-04-12) - 新增高级组件、ECharts 工业暗色主题、骨架屏与微交互规范
