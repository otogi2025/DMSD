#!/usr/bin/env bash
# 导出后端 API 接口总表（OpenAPI）→ 03_dev/backend/v1/openapi_snapshot.json
#
# 干嘛用：FastAPI 自带一份机器可读的「每个接口收什么字段、回什么字段」总表。
# 把它存进仓库后，改完后端重跑本脚本，git diff 直接显示字段层面的变化 —
# 跨端字段对齐（iOS / Android / 老师网页）从「读代码猜」变成「对着总表核」。
# itsuki 2026-06-11 拍板：收尾流程跟文件联动检查并行跑（改了 backend 才触发）。
#
# 用法：bash bin/export_openapi.sh   （任意目录可跑）
set -euo pipefail
cd "$(dirname "$0")/../03_dev/backend/v1"

# arch -arm64：强制原生 Apple 芯片架构跑（.venv 的编译包是 arm64，终端若在转译模式下会报架构不匹配）
arch -arm64 .venv/bin/python - <<'PY' > openapi_snapshot.json
import json
from app.main import app
# sort_keys 保证两次导出顺序一致 — diff 里只剩真实变化，没有排序噪音
print(json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True))
PY

echo "✅ 已导出 openapi_snapshot.json（$(grep -c '"operationId"' openapi_snapshot.json) 个接口）"
echo "   改动对比：git diff -- 03_dev/backend/v1/openapi_snapshot.json"
