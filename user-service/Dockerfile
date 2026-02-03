FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

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
    apt-get install -y gcc libffi-dev; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
