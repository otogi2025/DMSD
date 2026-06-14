# TASK D · Apply (申し込み 13 页 · StayForm 最复杂) · SwiftUI 实装

> **Dispatch**: Agent tool · subagent_type=`general-purpose`
> **工程**: `~/dev/TomoshibiiOSApp/TomoshibiApp/Features/Apply/ApplyStubs.swift`
> **翻译源**: `phaseB_src/100ba570__ApplyListPage_ApplyNewPage_ApplyFormPage.js`（demo 阶段 JSX 源，已归档、不在仓库）

## 产物

**Replace** `ApplyStubs.swift` 全部内容。13 页 + 1 ApplyStub 工具。保留文件名。

## 13 Views · 8 kind 申請類型

**APPLY_TYPES** 严格按 Phase B 源 8 种（不改 C3，itsuki 已定方案 iii）:
```
outing (外出) / stay (外泊) / holiday (帰省) / return (早帰) /
repair (修繕) / parcel (代理受取) / guest (来訪者) / other (その他)
```

### ⭐ 必做 6 页

1. **ApplyListView** (L1 · 左上 Home icon) — 顶部 4-tab (全て / 審査中 / 承認済 / 下書き) · SEED.applications list · 每 card type icon + name + status Pill + summary + date · FAB "+" → `.applyNew`
2. **ApplyNewView** (L2) — 8 APPLY_TYPES grid 2 column · Card with icon + name + desc · tap → `router.go(.applyForm(kind: "xxx"))`
3. **ApplyFormDispatcher** (L2) — 根据 kind 分派:
   ```swift
   if kind == "stay" || kind == "holiday" { StayForm(kind: kind) }
   else { GenericApplyForm(kind: kind) }
   ```
4. **StayForm** ⭐⭐⭐ (60-90 min · 最复杂单组件)
5. **GenericApplyForm** (7 kind 共用 L2 form)
6. **ApplyDetailView** (L2) — 从 SEED.applications.first(where: {$0.id == id}) · status pill + 各字段 InfoRow · workflow 4-段 card (担任 → 寮務課長 → 管理課長 → 国際交流部長)

### 💤 余 3 页 · 简 stub

ApplyPreviewView / ApplyDoneView (只 ApplyDoneView 要做简单 ✅ + 「ホームへ戻る」即可)

### StayForm 详细 spec（跟 JSX `StayForm` 对应 §92-292）

8 section 用 private SectionLabel (已 reference in JSX file 见 line 293):

**§1 申請者本人** (read-only from SEED.user): 氏名 / 学年・組 / 本人連絡先 input
**§2 同行者**: 氏名 TField + 連絡先 TField
**§3 外泊日時**: 出発 DatePicker + 帰舎 DatePicker
**§4 移動手段** (行き / 帰り 各 ChipGroup):
  choices = ["西口バス便", "金川バス便", "JR", "自家用車", "タクシー", "教員送迎", "飛行機"]
  + 飛行機时加 便番号 TField
**§5 宿泊先** (isStay only): 分類 RadioCard (日本人宅 / 留学生宅 / ホテル / その他) + 名称 / 住所 / 行先都市 TField
**§6 食事**: 朝 / 昼 / 夕 Stepper × 3 + 「自分で記入可」checkbox
**§7 外泊の理由** (isHoliday 显示 "帰省の理由"): TArea(rows:4) 必填
**§8 備考**: TArea(rows:3)
**§9 保護者許可**: checkbox + 保護者電話 TField

**holiday kind 时** 上部 amber banner: 「⏰ 帰省申請は毎週水曜日 18:00 が締切です」

底部 「下書き保存」GhostButton + 「次へ (確認)」PrimaryButton → `router.go(.applyPreview(kind: kind))`

内部工具（private in file）:

```swift
private struct SectionLabel: View { var n: String; var label: String; /* 圆 + 数字 + 标签 */ }
private struct InfoRow: View { var k: String; var v: String; /* 键值 pair */ }
private struct ChipGroup<Item: Hashable>: View { ... /* 单选 chip 组 */ }
private struct DateField: View { @Binding var date: Date; /* compact DatePicker wrap */ }
private struct TimeField: View { ... }
```

## Foundation API

- `Route`: `.apply / .applyNew / .applyForm(kind:) / .applyPreview(kind:) / .applyDone(kind:) / .applyDetail(id:)`
- `SEED`:
  - `.user: User` (account/name/dorm/room/category)
  - `.applications: [ApplicationItem]` (id/type/status/date/summary)
- `AppStore.showToast` · `RouterStore.go / back`
- `PageHeader(title:, level:, right:?)` / `Card / Pill / PrimaryButton / GhostButton / Field / TField / TArea / RadioCard / EmptyState / Ic / TToggle`
- T tokens · 全套

## APPLY_STATUS 映射

```swift
let statusPill: (String, Pill.Tone) = {
    switch item.status {
    case "pending": return ("審査中", .warn)
    case "approved": return ("承認済", .ok)
    case "rejected", "returned": return ("差戻", .danger)
    case "draft": return ("下書き", .neutral)
    case "cancelled": return ("取消済", .neutral)
    default: return (item.status, .neutral)
    }
}()
```

## APPLY_TYPES icon + desc

```swift
let types: [(k: String, name: String, icon: String, desc: String)] = [
    ("outing",  "外出",     "figure.walk",       "当日帰寮の外出"),
    ("stay",    "外泊",     "house",             "寮外での宿泊"),
    ("holiday", "帰省",     "house.lodge",       "実家帰省・長期休暇"),
    ("return",  "早帰",     "calendar.badge.clock", "門限前の早帰・遅帰"),
    ("repair",  "修繕",     "wrench.and.screwdriver","部屋・設備の修繕依頼"),
    ("parcel",  "代理受取", "shippingbox",       "不在時の荷物代理受取"),
    ("guest",   "来訪者",   "person.2",          "家族・友人の来訪"),
    ("other",   "その他",   "ellipsis.bubble",   "上記以外のご依頼"),
]
```

## 产出要求

1. Replace ApplyStubs.swift · 13 struct + private tools · 800-1200 行
2. 每 View `#Preview`
3. build pass
4. 完成 report

## 不要做

- ❌ 改 Foundation/ · Route.swift · 其他 feature folder
- ❌ git commit
