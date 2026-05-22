# Tomoshibi backend — App Store 上架版生产 Docker image
# 部署目标：日本 VPS（Sakura / Conoha / Vultr Tokyo）+ Ubuntu 24.04 + docker compose

FROM python:3.12-slim

# 系统依赖（psycopg2 + 健康检查用 curl）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 依赖（先单独 COPY requirements.txt 用 Docker layer cache）
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir "psycopg[binary]" gunicorn

# 应用代码
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/
COPY seed.py /app/

# 非 root 用户跑（生产安全）
RUN useradd -m -u 1000 tomoshibi \
    && chown -R tomoshibi:tomoshibi /app
USER tomoshibi

EXPOSE 8000

# 健康检查（Caddy / docker compose 用来判断 healthy）
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

# 生产用 gunicorn + uvicorn worker（2 worker 适配 1 vCPU / 2 GB e2-small）
# 2026-05-08 修：原写 -w 4 在 e2-small 上 OOM，改成 -w 2。
# 公式：1 vCPU 跑多 worker 是反模式（CPU 切换开销 > 并行收益），FastAPI IO bound 1-2 worker 够。
# 升级到 4 vCPU+ 时可改回 -w 4 或按 (2*CPU)+1 调。
CMD ["gunicorn", "app.main:app", \
     "-w", "2", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
