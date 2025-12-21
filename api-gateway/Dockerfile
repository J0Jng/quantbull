FROM python:3.12-slim

# 生产优化的基础镜像配置
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# 安装系统依赖（包含用于时区与常见 Python build 的基础包）
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone && \
    pip install --upgrade pip setuptools wheel && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 复制并安装 Python 依赖（优先使用 requirements.txt，适配 CI/CD）
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制应用代码
COPY . /app

# 使用非 root 用户运行（更安全）
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# 服务端口（容器内）
EXPOSE 8000

# 启动命令（使用 uvicorn，生产可通过 --workers 调整）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
