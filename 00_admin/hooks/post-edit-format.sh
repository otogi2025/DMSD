#!/usr/bin/env bash
# DMSD CC PostToolUse hook — 多语言自动格式化
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 调 Write/Edit 完成后（命中代码文件）
#
# 工作流：
# 1. 读 stdin 提取 file_path
# 2. 按扩展名分发到对应格式化工具：
#    - .py            → ruff check --fix + ruff format
#    - .swift         → swiftformat
#    - .kt / .kts     → ktlint -F
#    - .ts/.tsx/.js/.jsx/.vue/.css/.scss/.html/.json → prettier --write
# 3. 格式化工具未装 → 静默 skip（不报错）
# 4. node_modules / build / 99_archive / DerivedData → skip
#
# 装的工具（2026-05-19 itsuki 一次装齐）：
#   - ruff 0.15.13       (brew install ruff)
#   - swiftformat 0.61.1 (brew install swiftformat)
#   - ktlint 1.8.0       (brew install ktlint)
#   - prettier 3.8.3     (npm install -g prettier prettier-plugin-tailwindcss)
#
# 2026-05-19 itsuki 拍板新建（claude-code-setup MCP 推荐后落地）

set -e
trap 'exit 0' ERR

INPUT=$(cat 2>/dev/null || echo "{}")

if [ -z "$INPUT" ] || [ "$INPUT" = "{}" ]; then
  exit 0
fi

FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/kurekoduki/dev/DMSD}"
RELATIVE_PATH="${FILE_PATH#$PROJECT_DIR/}"

# 不在项目内 → skip
if [[ "$RELATIVE_PATH" == /* ]]; then
  exit 0
fi

# 跳过第三方目录 / 构建产物
if [[ "$RELATIVE_PATH" == *"node_modules/"* ]] || \
   [[ "$RELATIVE_PATH" == *".git/"* ]] || \
   [[ "$RELATIVE_PATH" == *"99_archive/"* ]] || \
   [[ "$RELATIVE_PATH" == *"build/"* ]] || \
   [[ "$RELATIVE_PATH" == *"DerivedData/"* ]] || \
   [[ "$RELATIVE_PATH" == *".venv/"* ]] || \
   [[ "$RELATIVE_PATH" == *"venv/"* ]] || \
   [[ "$RELATIVE_PATH" == *"__pycache__/"* ]]; then
  exit 0
fi

# 文件必须存在（防 Write 写入失败 / 路径漂移）
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# ============================================================
# 按扩展名分发到对应工具
# ============================================================

case "$FILE_PATH" in
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      ruff check --fix "$FILE_PATH" >/dev/null 2>&1 || true
      ruff format "$FILE_PATH" >/dev/null 2>&1 || true
    fi
    ;;
  *.swift)
    if command -v swiftformat >/dev/null 2>&1; then
      swiftformat "$FILE_PATH" >/dev/null 2>&1 || true
    fi
    ;;
  *.kt|*.kts)
    if command -v ktlint >/dev/null 2>&1; then
      ktlint -F "$FILE_PATH" >/dev/null 2>&1 || true
    fi
    ;;
  *.ts|*.tsx|*.js|*.jsx|*.vue|*.css|*.scss|*.html|*.json)
    if command -v prettier >/dev/null 2>&1; then
      prettier --write "$FILE_PATH" >/dev/null 2>&1 || true
    fi
    ;;
esac

exit 0
