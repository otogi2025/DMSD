# Shared Decisions (pointer)

**所有跨会话 iOS/Web 共享决策在主工程：**

👉 **`~/dev/DMSD/00_admin/跨会话_ios_共享决策.md`**

任何 CC 会话（iOS-Swift-CC / Web-CC）开始前**必读**。

## 不要在这里重复规则

本文只是指针。决策 source of truth 在 DMSD 主工程。

## iOS Swift 特有

- 本工程（`~/dev/TomoshibiiOSApp/`）变更日志：`SESSION_CHANGELOG.md`
- 实装 fidelity 铁律（agent 用）：`REMOTE_AGENT_GUIDE.md`
- HTML 原型参照（只读）：`refs/Tomoshibi_iOS_PhaseB_v2.html` + `refs/phaseB_src/*.js`

## 会话结束时

1. 追加条目到 `SESSION_CHANGELOG.md`
2. 同步到 `~/dev/DMSD/00_admin/跨会话_ios_共享决策.md` §3（做完 / 待做）
