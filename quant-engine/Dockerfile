FROM docker.1ms.run/library/python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# 安装系统依赖（包括 TA-Lib 编译依赖）
RUN set -eux; \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i \
            -e 's|http://deb.debian.org|http://mirrors.aliyun.com|g' \
            -e 's|https://deb.debian.org|https://mirrors.aliyun.com|g' \
            -e 's|http://security.debian.org|http://mirrors.aliyun.com|g' \
            -e 's|https://security.debian.org|https://mirrors.aliyun.com|g' \
            /etc/apt/sources.list.d/debian.sources; \
    fi; \
    if [ -f /etc/apt/sources.list ]; then \
        sed -i \
            -e 's|http://deb.debian.org|http://mirrors.aliyun.com|g' \
            -e 's|https://deb.debian.org|https://mirrors.aliyun.com|g' \
            -e 's|http://security.debian.org|http://mirrors.aliyun.com|g' \
            -e 's|https://security.debian.org|https://mirrors.aliyun.com|g' \
            /etc/apt/sources.list; \
    fi; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt /app/requirements.txt

# 先安装 numpy 1.x 版本（ta-lib 编译需要）
RUN pip install "numpy<2"

# 安装 ta-lib（使用 py3.12 可用 wheel，且不自动升级 numpy）
RUN pip install --no-cache-dir --no-deps ta-lib==0.6.7

# 安装其他依赖（会升级 numpy 到 requirements.txt 指定版本）
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# 复制 indicator 模块（内设因子依赖）- 需要在 docker-compose 中通过 volumes 挂载
# 或者在构建时通过 context 包含

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "4"]
