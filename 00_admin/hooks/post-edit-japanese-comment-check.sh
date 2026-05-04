#!/usr/bin/env bash
# DMSD CC PostToolUse hook — 代码注释日语漂移检测
#
# 配置位置：.claude/settings.json hooks.PostToolUse[matcher="Write|Edit"]
# 触发时机：CC 调 Write/Edit 完成后（命中代码文件）
#
# 工作流：
# 1. 读 stdin 提取 file_path
# 2. 判断是否代码文件（.swift / .py / .kt / .ts / .tsx / .js / .jsx）
# 3. 提取「新增注释行」：
#    - tracked 文件：git diff HEAD 看 ^+ 行
#    - untracked 新文件：grep 全文
# 4. 注释行检测：
#    - .swift / .kt / .ts(x) / .js(x)：行内 `//` 后面有日语
#    - .py：行内 `#` 后面有日语
# 5. 日语判定：包含 hiragana（U+3040-309F）或 katakana（U+30A0-30FF）
#    - 不算日语：纯汉字（中日共用）+ ASCII + 标点
# 6. 命中 → hookSpecificOutput.additionalContext 注入提醒
#
# 中文铁律来源：memory feedback_code_comments_chinese_strict.md
# 例外：UI 字符串里的日语保留（这是 UI 内容，不是注释）
#
# 2026-05-04 itsuki 拍板新建（5 hook 一波加）

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

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/itsuki/dev/DMSD}"
RELATIVE_PATH="${FILE_PATH#$PROJECT_DIR/}"

# 不在项目内 → skip
if [[ "$RELATIVE_PATH" == /* ]]; then
  exit 0
fi

# ============================================================
# 文件类型判断 + 注释模式
# ============================================================

COMMENT_PREFIX=""
case "$RELATIVE_PATH" in
  *.swift|*.kt|*.ts|*.tsx|*.js|*.jsx)
    COMMENT_PREFIX="//"
    ;;
  *.py)
    COMMENT_PREFIX="#"
    ;;
  *)
    exit 0  # 非代码文件 — skip
    ;;
esac

# ============================================================
# 提取「新增内容」
# ============================================================

cd "$PROJECT_DIR" 2>/dev/null || exit 0

if [ ! -f "$RELATIVE_PATH" ]; then
  exit 0
fi

NEW_CONTENT=""
if git ls-files --error-unmatch -- "$RELATIVE_PATH" &>/dev/null; then
  # tracked — 看 git diff 新增行
  NEW_CONTENT=$(git diff HEAD -- "$RELATIVE_PATH" 2>/dev/null \
    | grep '^+' | grep -v '^+++' \
    | sed 's/^+//' || true)
else
  # untracked 新文件 — 整文件视为新增
  NEW_CONTENT=$(cat "$RELATIVE_PATH" 2>/dev/null || true)
fi

if [ -z "$NEW_CONTENT" ]; then
  exit 0
fi

# ============================================================
# 找含日语 hiragana / katakana 的注释行
# ============================================================

# 算法：每行扫一遍，找注释起始位置（COMMENT_PREFIX），看后面是否有日语
# Hiragana: U+3040-309F = ぁ-ゟ (实际 ぁ-ん 范围 3041-3093 + 浊音半浊音)
# Katakana: U+30A0-30FF = ァ-ヿ (实际 ァ-ヴ 范围 30A1-30F6 + ー長音 30FC)
JAPANESE_RANGE='[ぁ-ゟ]|[ァ-ヿ]'

VIOLATIONS=""
LINE_NUM=0

# 注：bash IFS=read 不丢空行（用 -r）
while IFS= read -r line; do
  LINE_NUM=$((LINE_NUM + 1))

  # 提取注释部分（COMMENT_PREFIX 后的内容）
  # 简单版本：grep -E "$COMMENT_PREFIX" 然后看是否有日语
  # 注意 // 在 string literal 里也存在，简单检测会 false positive — 接受这个权衡（让 itsuki 看到提醒后判断）

  if echo "$line" | grep -qE "$COMMENT_PREFIX"; then
    # 取 COMMENT_PREFIX 后的内容
    if [ "$COMMENT_PREFIX" = "//" ]; then
      comment_part=$(echo "$line" | sed 's|.*//||')
    else
      comment_part=$(echo "$line" | sed 's|.*#||')
    fi

    # 检测日语 hiragana / katakana
    if echo "$comment_part" | grep -qE "$JAPANESE_RANGE"; then
      # 截断长度 80 显示
      preview=$(echo "$line" | cut -c1-80)
      VIOLATIONS="${VIOLATIONS}     [新行 ${LINE_NUM}] ${preview}
"
    fi
  fi
done <<< "$NEW_CONTENT"

# ============================================================
# 输出
# ============================================================

if [ -n "$VIOLATIONS" ]; then
  ADDITIONAL_CONTEXT="🇨🇳 中文铁律违反检测（${RELATIVE_PATH}）

新增的代码注释里发现日语 hiragana / katakana 字眼 — 违反中文铁律。

| 文件 | ${RELATIVE_PATH}
| 注释符号 | ${COMMENT_PREFIX}
| 违反行（前几条）|
${VIOLATIONS}

📜 中文铁律：代码注释 + 内部文档 100% 中文 / UI 字符串保持日语。
出处：memory feedback_code_comments_chinese_strict.md（2026-05-03 itsuki 拍板）
例外：UI 内容字符串（如 \"今日の出席\"）保持日语 ✅，但 // 注释里写日语 ❌。

→ 修复：把日语注释改成中文。

⚠️ false positive 可能：如果 // 出现在字符串字面量里（比如 URL: \"https://...\"），grep 可能误报，看上下文判断。"

  jq -n \
    --arg ctx "$ADDITIONAL_CONTEXT" \
    '{
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: $ctx
      }
    }'
fi

exit 0
