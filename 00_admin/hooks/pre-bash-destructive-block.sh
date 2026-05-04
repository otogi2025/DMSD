#!/usr/bin/env bash
# DMSD CC PreToolUse hook — 拦截破坏性 Bash 命令
#
# 配置位置：.claude/settings.json hooks.PreToolUse[matcher="Bash"]
# 触发时机：CC 调 Bash 工具前（执行命令之前）
#
# 工作流：
# 1. 读 stdin PreToolUse JSON
# 2. 提取 tool_input.command
# 3. 匹配破坏性命令模式
# 4. 命中 → exit 2（block）+ stderr 错误消息让 CC 重新考虑
# 5. 没命中 → exit 0（让命令继续）
#
# 拦截清单（按破坏性排序）：
# - rm -rf <非临时路径>     ← 删除文件树（.git / repo 文件等）
# - git reset --hard         ← 丢弃工作树改动
# - git clean -f / -fd / -fx ← 删 untracked
# - git checkout --           ← 丢弃工作树改动（旧语法）
# - git restore --             ← 丢弃工作树改动（新语法）
# - git branch -D              ← 强删 branch
# - git push --force / -f      ← 覆盖 remote 历史
# - git push origin :refs      ← 删 remote ref
# - rm -f .git                  ← 灾难
#
# 设计原则：
# - 默认拦死，让 CC 解释为什么需要破坏性操作
# - 例外：rm -rf 到 /tmp/ 或 /var/tmp/ 或 ./node_modules / DerivedData 这种构建产物 → 放行
# - exit 2 = block（CC 看到 stderr 重新考虑）
# - exit 0 = allow（命令正常跑）
#
# 2026-05-04 itsuki 拍板新建（5 hook 一波加）

set -e
trap 'exit 0' ERR  # 脚本本身失败别影响 CC

INPUT=$(cat 2>/dev/null || echo "{}")

if [ -z "$INPUT" ] || [ "$INPUT" = "{}" ]; then
  exit 0
fi

# 提取命令字符串
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null || echo "")

if [ -z "$CMD" ]; then
  exit 0
fi

# ============================================================
# 检测函数
# ============================================================

block_with_reason() {
  local reason="$1"
  echo "❌ destructive-bash-block 拦截破坏性命令" >&2
  echo "" >&2
  echo "命令: $CMD" >&2
  echo "" >&2
  echo "原因: $reason" >&2
  echo "" >&2
  echo "→ 重新考虑：是否真需要这个破坏性操作？" >&2
  echo "→ 如果是，请要求 itsuki 明确授权后再跑（CC 自己不能擅自破坏 repo）" >&2
  echo "→ 如果只是 cleanup 临时文件，改用 /tmp/ 路径" >&2
  exit 2
}

# ============================================================
# Pattern 1: rm -rf 后跟非临时路径
# 放行: /tmp/ /var/tmp/ ./node_modules ./DerivedData ./.next ./dist ./build
# ============================================================

if echo "$CMD" | grep -qE '\brm\s+(-[rRf]+|-[rRf]+\s+-[rRf]+)\s+'; then
  # 提取 rm 后的路径参数
  RM_PATH=$(echo "$CMD" | grep -oE 'rm\s+(-[a-zA-Z]+\s+)+\S+' | awk '{print $NF}')

  # 临时路径白名单
  if echo "$RM_PATH" | grep -qE '^(/tmp/|/var/tmp/|/var/folders/|\./?(node_modules|DerivedData|\.next|dist|build|\.cache|\.parcel-cache|\.turbo)(/.*)?$|node_modules$|DerivedData$|dist$|build$)'; then
    : # 放行临时 / 构建产物
  else
    block_with_reason "rm -rf 到非临时路径会删除真实文件 — 这是不可逆操作"
  fi
fi

# ============================================================
# Pattern 2: git reset --hard
# ============================================================

if echo "$CMD" | grep -qE '\bgit\s+reset\s+(--hard|-[a-zA-Z]*\bhard\b)'; then
  block_with_reason "git reset --hard 丢弃工作树所有未 commit 改动 — 不可逆"
fi

# ============================================================
# Pattern 3: git clean -f
# ============================================================

if echo "$CMD" | grep -qE '\bgit\s+clean\s+(-[a-zA-Z]*f[a-zA-Z]*)'; then
  block_with_reason "git clean -f 删除 untracked 文件 — 可能误删 itsuki 在做的活"
fi

# ============================================================
# Pattern 4: git checkout -- / git restore --
# ============================================================

if echo "$CMD" | grep -qE '\bgit\s+(checkout|restore)\s+--\s+\S+'; then
  block_with_reason "git checkout/restore -- <file> 丢弃该文件未 commit 改动 — 不可逆"
fi

# ============================================================
# Pattern 5: git branch -D
# ============================================================

if echo "$CMD" | grep -qE '\bgit\s+branch\s+(-D|-[a-zA-Z]*D[a-zA-Z]*)\b'; then
  block_with_reason "git branch -D 强删 branch — 如果 branch 没合并到任何地方，commit 永久丢失"
fi

# ============================================================
# Pattern 6: git push --force / -f / +refspec
# ============================================================

if echo "$CMD" | grep -qE '\bgit\s+push\s+.*(-{1,2}force|-f\b|\s\+[a-zA-Z])'; then
  block_with_reason "git push --force 覆盖 remote 历史 — 可能毁掉别协作者 commit"
fi

# ============================================================
# Pattern 7: 删 remote ref（git push origin :refs/...）
# ============================================================

if echo "$CMD" | grep -qE '\bgit\s+push\s+\S+\s+:'; then
  block_with_reason "git push origin :ref 删除 remote ref — 不可逆"
fi

# ============================================================
# Pattern 8: rm 直接 .git 目录
# ============================================================

if echo "$CMD" | grep -qE '\brm\s.*\b\.git\b'; then
  block_with_reason "rm 涉及 .git 目录 — 会摧毁整个 git 历史"
fi

# 通过所有检测 → 放行
exit 0
