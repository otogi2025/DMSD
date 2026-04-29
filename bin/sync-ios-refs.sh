#!/usr/bin/env bash
# sync-ios-refs.sh · iOS refs/ 同步脚本
#
# 用途：DMSD（主工程 + 设计真值）的设计文档单向复制到 TomoshibiiOSApp/refs/
#       因为 Anthropic cloud agent 跑 Tomoshibi-iOS repo 拿不到 DMSD 文件，必须复制
#
# 用法：bash bin/sync-ios-refs.sh
# 前提：~/dev/DMSD/（本 repo） · ~/dev/TomoshibiiOSApp/（独立 Swift repo）均存在
#
# 建立：2026-04-23 by [iOS-Swift-CC]

set -e

DMSD="${DMSD:-$HOME/dev/DMSD}"
IOS="${IOS:-$HOME/dev/TomoshibiiOSApp}"

if [ ! -d "$DMSD" ] || [ ! -d "$IOS" ]; then
    echo "ERR: DMSD=$DMSD or IOS=$IOS not found"
    exit 1
fi

echo "🔄 Syncing iOS refs: $DMSD → $IOS/refs/"

mkdir -p "$IOS/refs/phaseB_src"

# iOS 设计真值
cp -v "$DMSD/03_dev/student_ios/IOS_DESIGN_LOG.md" \
      "$IOS/refs/IOS_DESIGN_LOG.md"

cp -v "$DMSD/03_dev/student_ios/designs/QA_Round1_PhaseB.md" \
      "$IOS/refs/QA_Round1_PhaseB.md" 2>/dev/null || echo "  (skip QA — not found)"

cp -v "$DMSD/03_dev/student_ios/designs/Tomoshibi_iOS_PhaseB_v2.html" \
      "$IOS/refs/Tomoshibi_iOS_PhaseB_v2.html"

# JSX 解包源
if [ -d "$DMSD/03_dev/student_ios/designs/phaseB_src" ]; then
    cp -v "$DMSD/03_dev/student_ios/designs/phaseB_src/"*.js \
          "$IOS/refs/phaseB_src/" 2>/dev/null || true
fi

# 跨会话共享决策（如果 web-CC 建了 system_features.md 就复制）
if [ -f "$DMSD/02_design/system_features.md" ]; then
    cp -v "$DMSD/02_design/system_features.md" \
          "$IOS/refs/system_features.md"
fi

# 临时决策文档（iOS-Swift-CC 会话建的）
if [ -f "$DMSD/00_admin/跨会话_ios_共享决策.md" ]; then
    cp -v "$DMSD/00_admin/跨会话_ios_共享决策.md" \
          "$IOS/refs/跨会话_ios_共享决策.md"
fi

echo "✅ Sync done."
echo "   Next: cd $IOS && git add refs/ && git commit -m 'sync: refs from DMSD'"
