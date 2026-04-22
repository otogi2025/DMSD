# Round 3 Handoff 文件夹

> **用途**：给 Claude Design (claude.ai/design) 的 Round 3 输入包。整个文件夹拖到对话框 → 发送 prompt → Claude Design 基于这些素材产出 Tomoshibi 教员 Web Round 3 原型。
> **建立**：2026-04-21 晚 by [Code-Agent]

## 文件清单

| 文件 | 用途 |
|---|---|
| `Round3_Prompt.md` | ⭐ 主输入。把这个文件整段内容贴到 Claude Design 对话框 |
| `01_tomoshibi_icon.png` | 新 app icon（火焰 + 中心黄球，"灯火"视觉化）。Shell 左上角 ◇ 菱形要换成这个 |
| `02_gaihaku_form_reference.jpeg` | 实在的「外泊許可願」纸质表原件。外泊申请 form 的字段设计要数字化这张表 |
| `03_current_header_before.png` | 现在的 header 状态（DMSD + 寮管理システム），给 Claude Design 看"改之前什么样" |

## 使用方法（itsuki 操作步骤）

1. 打开 Claude.ai 进入 DMSD 的 Claude Design project（已有 Round 1-2 产出的那个）
2. **把本文件夹（`round3_handoff/`）整体拖到对话输入框** —— 3 张图 + `Round3_Prompt.md` 都会上传
3. 再把 `Round3_Prompt.md` 的**内容**复制粘贴到消息正文（上传文件 + 粘贴 prompt 同一条消息发送）
4. 发送
5. Claude Design 会产出 Round 3 原型（基于 Round 2 `round2/*.jsx` 扩展 + 新组件）
6. 完成后让它调 `Save as standalone HTML` skill 打包成 `DMSD Round 3 Prototype.html`（命名保留 DMSD 代号，UI 文字已全改 Tomoshibi）
7. 下载 handoff bundle → [Code-Agent] 后续通过 Anthropic share link 导入到 `03_dev/demo_4-28/teacher_web/` 做前端 integration

## 注意事项

- **把 prompt 和图片**同一条消息一起发（如果分开发，Claude Design 可能看不到图）
- Claude Design 可能先问几个 clarifying question，按自己理解答即可（或回"都在 prompt 里，请直接开工"）
- Claude Design 可能 propose 替代方案（例如 late 色选别的 hex），接受即可
- 完成后的 Round 3 HTML 拿到后，[Code-Agent] 会负责把静态 seed 换成真 API fetch + WebSocket 订阅

## 想改 Prompt？

直接编辑 `Round3_Prompt.md`。如果是重大 scope 变动（加 / 砍功能），先更新 `../WEB_DESIGN_LOG.md` 保持决策档一致。
