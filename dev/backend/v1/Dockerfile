# Tomoshibi backend — App Store 上架版生产 Docker image
# 部署目标：日本 VPS（Sakura / Conoha / Vultr Tokyo）+ Ubuntu 24.04 + docker compose

# H-20：base image 用 @sha256 digest 钉死，保证可复现构建（tag 会被悄悄重推、digest 不会）。
# digest 对应 python:3.12-slim（用 `docker buildx imagetools inspect python:3.12-slim` 取，
# 升 Python 版本时同步换新 digest）。
ARG PYTHON_IMAGE=python:3.12-slim@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9

# ---------------------------------------------------------------
# H-20：多阶段构建 —— builder 阶段装编译工具 + 编译依赖，runtime 阶段只搬装好的包，
# build-essential / libpq-dev 这些编译期才需要的工具不进运行镜像（减小体积 + 缩攻击面）。
# ---------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS builder

# 编译期系统依赖（psycopg 等需要编译时用）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# H-11：所有 Python 依赖（含 gunicorn / psycopg）都从 requirements.txt 装，版本统一锁在那；
# 不再在 Dockerfile 里内联裸 pip install。装到 /install 前缀目录，runtime 阶段整包搬过去。
COPY requirements.txt /app/
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------------------------------------------------------------
# runtime 阶段 —— 只带运行期需要的：装好的 Python 包 + curl（健康检查用）+ libpq 运行库。
# ---------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runtime

# 运行期系统依赖：curl（HEALTHCHECK 用）+ libpq5（psycopg 运行时链接库，非编译工具）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 从 builder 搬已装好的依赖
COPY --from=builder /install /usr/local

# 应用代码
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/
COPY seed.py /app/

# 上传目录（在线学习契約書照片/PDF）先建好，随下面 chown -R /app 一起设成 tomoshibi 所有。
# 必须在镜像里预建：生产挂 uploads_data named volume 时，卷首次挂载会继承挂载点的属主；
# 若挂载点不存在则默认 root 所有，非 root 的 tomoshibi 用户 makedirs/写文件直接 Permission denied。
RUN mkdir -p /app/uploads

# 非 root 用户跑（生产安全）
RUN useradd -m -u 1000 tomoshibi \
    && chown -R tomoshibi:tomoshibi /app
USER tomoshibi

EXPOSE 8000

# 健康检查（Caddy / docker compose 用来判断 healthy）
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

# 生产用 gunicorn + uvicorn worker
# ⚠️ 必须保持 -w 1（单进程）：
#   WebSocket 连接表（ws_manager.py）存在单进程内存里，
#   多进程（-w 2+）时每个 worker 各自维护独立连接表，
#   跨 worker 的 WS 推送会丢失约一半。
#   要支持多 worker 需要引入 Redis pub/sub 共享推送通道，
#   在此之前必须保持单进程，用单进程换正确性。
#   1 vCPU / 2 GB 小服务器单进程完全够用。
# H-5：补 gunicorn 调优参数：
#   --timeout 120          worker 处理单请求超 120s 判定卡死并重启（默认 30s 对慢导出 / 大上传偏短）
#   --graceful-timeout 30  收到重启信号后给 worker 30s 处理完手头请求再退（平滑发布）
#   --max-requests 1000    每 worker 处理满 1000 请求后自动回收重建，防长期运行的内存泄漏累积
#   --max-requests-jitter 100  给回收点加随机抖动，避免多 worker 同一时刻一起重启
#   --keep-alive 5         keep-alive 连接空闲 5s 关闭
CMD ["gunicorn", "app.main:app", \
     "-w", "1", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
