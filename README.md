# 工业质量统计工具

## 项目概述

工业质量统计工具是一个专业的企业级质量管理系统，提供完整的SPC控制图绘制、质量统计分析、过程能力分析等专业功能。系统采用现代Web技术栈，支持云原生部署，为企业提供完整的质量管理体系解决方案。

## 核心功能

### SPC控制图功能
- **X-bar R图**: 适用于子组大小2-10的过程控制
- **X-bar S图**: 适用于子组大小大于10的过程控制
- **I-MR图**: 单值移动极差图，适用于单个测量值
- **P图**: 不合格品率控制图
- **C图**: 缺陷数控制图
- **过程能力分析**: Cp/Cpk/Pp/Ppk计算和评估

### 质量统计分析
- **方差分析 (ANOVA)**: 单因素方差分析和多重比较
- **回归分析**: 多元线性回归和残差诊断
- **Gage R&R**: 测量系统分析
- **过程能力分析**: 全面的过程能力评估

### 数据管理
- **文件上传**: 支持CSV、Excel格式
- **数据解析**: 智能数据列识别
- **数据验证**: 完整性检查和异常值检测
- **结果导出**: Excel和PDF格式导出

### 实时监控
- **实时数据监控**: 持续监控质量指标
- **异常告警**: 自动检测异常情况
- **趋势分析**: 质量趋势预测

## 技术架构

### 后端技术栈
- **框架**: Python Flask 3.1.3
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **容器化**: Docker
- **编排**: Kubernetes
- **部署**: Gunicorn + Nginx

### 前端技术栈
- **基础**: HTML5/CSS3/JavaScript
- **框架**: Bootstrap 5
- **图表**: ECharts
- **主题**: 科技感深色主题
- **响应式**: 移动端适配

### 核心依赖
```
Flask==3.1.3
pandas==3.0.2
numpy==1.24.3
scipy==1.10.1
statsmodels==0.14.0
scikit-learn==1.2.2
openpyxl==3.1.2
reportlab==4.0.4
psycopg2-binary==2.9.6
redis==4.5.5
celery==5.2.7
```

## 安装和部署

### 本地开发环境

#### 1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库连接等
```

#### 4. 启动应用
```bash
python web/app.py
```

### Docker部署

#### 1. 构建镜像
```bash
docker build -t industrial-quality-stats:latest .
```

#### 2. 使用Docker Compose
```bash
docker-compose up -d
```

### Kubernetes部署

#### 1. 创建命名空间
```bash
kubectl create namespace quality-stats
```

#### 2. 部署应用
```bash
kubectl apply -f kubernetes/
```

#### 3. 验证部署
```bash
kubectl get pods -n quality-stats
kubectl get services -n quality-stats
```

## API接口文档

### 基础API

#### 健康检查
```
GET /api/health
```

#### 文件上传
```
POST /api/upload
Content-Type: multipart/form-data

参数:
- file: 上传的文件 (CSV/Excel)
```

#### 获取数据列
```
POST /api/columns
Content-Type: application/json

请求体:
{
  "file_path": "uploads/example.csv"
}
```

### SPC API

#### X-bar R图
```
POST /api/spc/xbar-r
Content-Type: application/json

请求体:
{
  "subgroup_col": "批次",
  "value_col": "测量值",
  "data": [...]
}
```

#### X-bar S图
```
POST /api/spc/xbar-s
Content-Type: application/json

请求体:
{
  "subgroup_col": "批次",
  "value_col": "测量值",
  "data": [...]
}
```

#### 单值移动极差图
```
POST /api/spc/individual-mr
Content-Type: application/json

请求体:
{
  "value_col": "测量值",
  "data": [...]
}
```

#### P控制图
```
POST /api/spc/p-chart
Content-Type: application/json

请求体:
{
  "subgroup_col": "批次",
  "defect_col": "不合格数",
  "data": [...]
}
```

#### C控制图
```
POST /api/spc/c-chart
Content-Type: application/json

请求体:
{
  "subgroup_col": "批次",
  "defect_count_col": "缺陷数",
  "data": [...]
}
```

#### 过程能力分析
```
POST /api/spc/process-capability
Content-Type: application/json

请求体:
{
  "data": [...],
  "usl": 10.0,
  "lsl": 0.0,
  "target": 5.0  // 可选
}
```

### 质量统计API

#### 方差分析
```
POST /api/quality/anova
Content-Type: application/json

请求体:
{
  "factor_col": "因子",
  "response_col": "响应变量",
  "data": [...]
}
```

#### 回归分析
```
POST /api/quality/regression
Content-Type: application/json

请求体:
{
  "x_cols": ["变量1", "变量2"],
  "y_col": "响应变量",
  "data": [...]
}
```

#### Gage R&R分析
```
POST /api/quality/gage-rnr
Content-Type: application/json

请求体:
{
  "part_col": "部件",
  "operator_col": "操作员",
  "measurement_col": "测量值",
  "data": [...]
}
```

#### 过程能力分析
```
POST /api/quality/capability
Content-Type: application/json

请求体:
{
  "data": [...],
  "usl": 10.0,
  "lsl": 0.0,
  "target": 5.0  // 可选
}
```

## 配置说明

### 应用配置

#### config.py
```python
class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = False
    
    # 文件上传配置
    UPLOAD_FOLDER = 'web/uploads'
    EXPORT_FOLDER = 'web/exports'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/quality_stats'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 应用配置
    HOST = '0.0.0.0'
    PORT = 5000
    WORKERS = 4
```

### Docker配置

#### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "web.app:app"]
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/quality_stats
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: quality_stats
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

### Kubernetes配置

#### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: industrial-quality-stats
  namespace: quality-stats
spec:
  replicas: 3
  selector:
    matchLabels:
      app: industrial-quality-stats
  template:
    metadata:
      labels:
        app: industrial-quality-stats
    spec:
      containers:
      - name: app
        image: industrial-quality-stats:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## 使用说明

### 1. 数据上传
1. 访问主页 `http://localhost:5000`
2. 点击"上传文件"按钮
3. 选择CSV或Excel文件
4. 系统自动解析文件并显示数据预览

### 2. SPC控制图
1. 选择SPC图类型 (X-bar R, X-bar S, I-MR, P图, C图)
2. 选择数据列
3. 点击"生成图表"
4. 查看控制图和分析结果

### 3. 质量统计分析
1. 选择分析类型 (ANOVA, 回归分析, Gage R&R)
2. 配置分析参数
3. 执行分析
4. 查看统计结果和解释

### 4. 结果导出
1. 在分析结果页面点击"导出"
2. 选择导出格式 (Excel/PDF)
3. 下载分析结果

## 性能优化

### 缓存策略
- Redis缓存频繁访问的数据
- 查询结果缓存
- 静态文件缓存

### 数据库优化
- 建立适当的索引
- 查询优化
- 连接池管理

### 应用优化
- Gunicorn多worker处理
- 异步任务处理
- 内存优化

## 安全特性

### 数据安全
- 文件上传验证
- 数据访问控制
- 敏感信息加密

### API安全
- 输入验证
- 错误处理
- 访问日志

### 网络安全
- HTTPS强制
- CORS配置
- 速率限制

## 监控和日志

### 应用监控
- 性能监控
- 错误监控
- 用户行为分析

### 日志管理
- 应用日志
- 访问日志
- 错误日志

## 故障排除

### 常见问题

#### 1. 文件上传失败
- 检查文件大小限制
- 验证文件格式
- 查看磁盘空间

#### 2. 数据库连接失败
- 检查数据库配置
- 验证网络连接
- 查看数据库日志

#### 3. 内存不足
- 增加内存限制
- 优化查询
- 清理缓存

### 诊断命令

```bash
# 查看应用状态
kubectl get pods -n quality-stats

# 查看应用日志
kubectl logs -f deployment/industrial-quality-stats -n quality-stats

# 查看数据库状态
kubectl exec -it deployment/postgresql -n quality-stats -- psql -U user -d quality_stats

# 检查Redis连接
kubectl exec -it deployment/redis -n quality-stats -- redis-cli ping
```

## 开发指南

### 代码结构
```
industrial-quality-stats/
├── web/
│   ├── app.py                 # Flask应用主文件
│   ├── config.py              # 配置文件
│   ├── api/                   # API接口
│   │   ├── spc.py             # SPC API
│   │   └── quality.py         # 质量统计API
│   ├── utils/                 # 工具类
│   │   ├── spc_charts.py      # SPC图表生成器
│   │   ├── quality_statistics.py  # 质量统计分析
│   │   └── ...                # 其他工具类
│   ├── templates/             # HTML模板
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   └── mobile.html
│   ├── static/               # 静态文件
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── uploads/              # 上传文件目录
│   └── exports/              # 导出文件目录
├── kubernetes/              # Kubernetes配置
├── scripts/                 # 脚本文件
├── requirements.txt         # Python依赖
├── Dockerfile              # Docker配置
├── docker-compose.yml      # Docker Compose配置
└── README.md               # 项目文档
```

### 开发流程

1. **需求定义**: 明确功能需求
2. **计划设定**: 制定开发计划
3. **任务拆解**: 分解为具体任务
4. **执行开发**: 编写代码
5. **审核测试**: 单元测试和集成测试
6. **阶段性总结**: 总结和优化

### 代码规范

- 遵循PEP 8规范
- 添加适当的注释
- 编写单元测试
- 文档化API接口

## 贡献指南

### 提交要求
- 代码审查
- 单元测试覆盖
- 文档更新
- 版本控制

### 分支管理
- main: 主分支
- develop: 开发分支
- feature/*: 功能分支
- bugfix/*: 修复分支

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请联系项目维护者。

## 版本历史

- **v1.0.0** (2026-05-09): 初始版本
  - 完整的SPC控制图功能
  - 质量统计分析工具
  - 云原生部署支持
  - 完整的API接口
  - 专业的文档体系