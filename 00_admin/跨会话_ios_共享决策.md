# 跨会话 iOS 共享决策（Shared Cross-Session iOS Rules）

> **作用**：iOS CC 会话（`~/dev/TomoshibiiOSApp/` Swift）と Web CC 会话（`~/dev/DMSD/teacher_web/` + `~/dev/DMSD/03_dev/student_ios/` HTML 原型）间的短期协作スナップショット + 実装 TODO。
>
> **⚠ 長期権威源は `02_design/system_features.md`**（iOS + Web + 後端 共用機能マトリクス）。本文は **実装ワーク用の短期ビュー**（現時点の TODO 進捗 + 両会話の合意点の抜粋）。学号体系 / 房间号 / 改动履歴 の詳細仕様は system_features.md に置く、本文は「今ここまでやった / 次これやる」の作業メモ。
>
> **建立**：2026-04-23 by [iOS-Swift-CC]
> **最后更新**：2026-04-23（[Mac-demo-sprint] Web-CC が system_features.md 建立 + 本文との関係を明示）

---

## § 0 — 文件位置速查

| 目录 | 用途 | 负责 CC 会话 |
|---|---|---|
| `~/dev/DMSD/` | 主工程：规格 / 设计 / backend / teacher_web / iOS HTML 原型 / 决策文档 | Web-CC |
| `~/dev/DMSD/03_dev/student_ios/` | **iOS HTML 原型（Phase B）**（Claude Design 产出） | Web-CC |
| `~/dev/TomoshibiiOSApp/` | **iOS Swift App（SwiftUI）** | iOS-Swift-CC |

**HTML 原型是 Swift 实装的对等参照物**。Swift 必须对齐 HTML（fidelity 铁律 — 文字/颜色/尺寸/间距逐项对照）。

iOS Swift 会话的变更日志：`~/dev/TomoshibiiOSApp/SESSION_CHANGELOG.md`

---

## § 1 — 账号番号规则（2026-04-23 拍板）

### 规则

**番号 = 6 桁**：`年级码(2) + 组码(2) + 出席番号(2)`

**年级码**（6 年制中高一体校 · 中1→高3）：

| 年级 | 码 |
|---|---|
| 中1 | `01` |
| 中2 | `02` |
| 中3 | `03` |
| 高1 | `04` |
| 高2 | `05` |
| 高3 | `06` |

**组码**：A 组 = `01` / B 组 = `02`（**不存在 C 组**）

**出席番号**：2 位 zero-pad（1〜99）

### 例

- 高3 B組 18番 → `06` + `02` + `18` = **`060218`**
- 中1 A組 05番 → `01` + `01` + `05` = `010105`
- 高2 B組 36番 → `05` + `02` + `36` = `050236`

### Demo seed 用户

| Field | Value |
|---|---|
| account | **`060218`** |
| name | リュウ イヒ |
| grade | 高3 |
| classSuffix | B |
| seatNo | 18 |
| gender | 女 |
| dorm | 男寮 |
| room | M101 |
| email | otogi2025@gmail.com |

### 生成时机

- 注册时：学生输入 `grade` / `classSuffix` / `seatNo` → App 自动算 account
- 出席番号**不按注册顺序** — 完全由 grade + class + seatNo 决定
- 同一年级同组内 seatNo 唯一（由学校分配，学生自己填最后一位补位即可）

---

## § 2 — 可变字段 / 升学 / 分班 / 搬寮

### 哪些字段可变

| 字段 | 触发 | 频率 |
|---|---|---|
| `grade` | 升学（4 月） | 1 次/年 |
| `classSuffix` | 分班（学期开始） | 不定 |
| `seatNo` | 出席番号变更 | 不定 |
| `room` | 搬寮 | 一年一换 |
| `account` | **自动重算**（不是独立字段） | 任何上面变动都触发 |

### App 内入口

- **iOS Swift** → `MyPage → 設定 → 個人情報を編集`（**TODO 待实装**）
- **Web** → `teacher_web` 老师端统一看板（**TODO 待实装**）

### Change Log 审计（所有学生编辑必须记录）

每次变更必须记录一条：

```
{
  timestamp: ISO 8601,
  field: "grade" | "classSuffix" | "seatNo" | "room" | ...,
  old_value: string,
  new_value: string,
  source: "student_app" | "teacher_web" | "admin_backend"
}
```

老师在 teacher_web 可以查看**任何学生的变更历史**（合规审计）。

Demo 阶段：App 本地 mock（`AppStore.changeLog: [ChangeLogEntry]`）；上线版走 backend。

### 房间号（room）

- Register 时学生自填（默认从 seed 提示）
- 升学 / 搬寮时学生 App 内改（**TODO**）
- **未来**：老师后台「分配房间」功能（批量分配 → 推送给学生 App → 学生 `room` 字段自动更新）

---

## § 3 — iOS Swift 当前状态（2026-04-23）

### 做完

- Splash → Register1（アバター / 氏名 / 性別 / 生年月日 / 学年 / 組 / 出席番号）→ 2 → 3 → 4 → Done → Login → Home flow
- Register Step1 加了 **学年 / 組 / 出席番号** 3 字段 + 实时 preview「アカウント番号 060218」
- SEED.user 默认值 = itsuki 高3 B組 18番 / account `060218`
- Login magic seed 兼容 `"00"` / `"060218"` / 两个 email
- Foundation atoms 对齐 HTML：PrimaryButton · Field · TField · GhostButton（含 contentShape hit-test）
- RootView 用 `.safeAreaInset` 挂 TopRollBar / BottomNav（不再是 overlay cover）
- TopRollBar：idle 态不显示（只 active / done 显示）· 圆角 capsule
- BottomNav：圆角胶囊 + 直接 `.glassEffect(.regular, in: .capsule)` + 贴底
- 点数 Card pill 状态机：idle/active/done/late dynamic
- 日文自然化：`来月清掃罰則予定` → `来月より清掃対象` · `快递 · N 件待領` → `宅配便 · N 件未受取` · `快递領取履歴` → `荷物受取履歴` · `父方の叔父` → `叔父 / 祖父母`
- MyLanding 加 `PageHeader(level: 1)` 左上 Home icon → 回主页
- StayForm：本人連絡先用 SEED.user · 方法 ChipGroup FlowLayout（iOS 16 Layout protocol）· 宿泊先 radio 删掉改 TField · 食事 per-day checkbox 改期间范围
- AppIcon 1024×1024 灰火焰 + Splash 同图

### 待做 TODO

- [ ] **RegisterStep3 加 房间号 TField**（学生自填 `room`）← 即将做
- [ ] **MyPage 個人情報編集页面** — 改 grade/classSuffix/seatNo/room，保存后重算 account
- [ ] **Change Log 本地 mock** — 学生任何改动 → append 到 AppStore.changeLog
- [ ] **MyPage 老师端「分配房间」功能** —（web-CC 职责，iOS 只是 receive push 更新 room）
- [ ] Home / Community / MyPage 各页视觉继续对齐 HTML

---

## § 4 — 跨会话协作规则

1. **改账号规则 / SEED 字段 / 重大 UI 架构** → 同一 commit 里更新本文件 + 对方 session 变更日志
2. **会话结束时** 在本文 §3 追加「做完」条目，并 mark 相关 TODO 为完成
3. **新决策先写本文，再实装**
4. Web-CC 的变更日志位置：`~/dev/DMSD/05_logs/raw/YYYY-MM-DD.md`（itsuki 原有规则）
5. iOS-Swift-CC 的变更日志位置：`~/dev/TomoshibiiOSApp/SESSION_CHANGELOG.md`

---

## 参考

- `~/dev/DMSD/CLAUDE.md` — 主工程指令
- `~/dev/DMSD/00_admin/文件结构指南.md` — 文件组织
- `~/dev/DMSD/00_admin/文档同步点清单.md` — 单源真值表
- `~/dev/TomoshibiiOSApp/REMOTE_AGENT_GUIDE.md` — iOS Swift 实装 fidelity 铁律（agent 用）
