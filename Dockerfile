# 工业质量统计工具 Docker 镜像
# 版本: 1.0
# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

# 安装系统依赖（包括中文字体和编译工具）
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 中文字体支持
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    # 编译依赖（某些Python包可能需要）
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p uploads web_output

# 设置Flask应用入口
ENV FLASK_APP=web.app
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "-m", "web.app", "--host", "0.0.0.0", "--port", "5000"]