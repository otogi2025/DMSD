# iOS App 界面截图（2026-06-05 实机）

itsuki 2026-06-05 提供的 iOS 学生 App 演示版实机截图 14 张，作为 **iOS↔Android 对齐**的视觉真值。
配套规格文档：`00_admin/iOS_Android_对齐规格.md`。

## 怎么放

把 14 个 PNG 按下表编号命名（`01_home.png` … `14_calendar.png`）拖进**本目录**。
CC 只能看到画面、拿不到原始文件，所以这步要 itsuki 手动放（或告诉 CC 截图文件路径，CC 来复制）。

## 14 张图对应的界面

| 编号 | 文件名 | 界面 | iOS 源 | 关键内容 |
|---|---|---|---|---|
| 01 | `01_home.png` | ホーム（主页） | `Features/Home/HomeStubs.swift` | おかえり问候 + 减点 4.5 卡 + 次のバス便 + 宅配便 1 件 + 今週の活動 14 件 + リクエスト曲 + 遺失物 + 底部 3 tab |
| 02 | `02_bus_special.png` | 特別運航便（巴士时刻表） | `Features/.../Bus*` | すべて/特別便/通学便 筛选 + 空港送迎便 開关 + 按日期分组的班次列表（空きあり/残N） |
| 03 | `03_delivery_pending.png` | 宅配 · 待領 tab | 宅配 view | 待領·1 / 領済·3 切换 + 宅配便卡 + 受取 按钮 |
| 04 | `04_delivery_done.png` | 宅配 · 領済 tab | 宅配 view | 已领列表（佐川/ヤマト/郵便局 + 日期） |
| 05 | `05_discipline_detail.png` | 減点明細 | `Features/MyPage/MyPageStubs.swift`（減点） | 今月合計 4.5 + 进度条 + 按日期扣分明细 + 规则脚注 |
| 06 | `06_home_scrolled.png` | ホーム（下滚） | 同 01 | 减点卡顶部 + 各功能卡 + 遺失物彩色卡（青い折りたたみ傘/黒の鍵/赤のペンケース） |
| 07 | `07_songs.png` | リクエスト曲（点歌） | 曲 view | 提示横幅 + 曲卡（曲名/歌手/号）+ 通報 按钮 + 右上 + |
| 08 | `08_applications_list.png` | 申し込み（申请列表） | `Features/Apply/ApplyStubs.swift` | すべて/審査中/承認済/下書き tab + 外泊/帰省/外出 卡 + 右下 + 悬浮按钮 |
| 09 | `09_apply_grid.png` | 新規申請（选类型） | `Features/Apply/*` | 外出/外泊/帰省/帰国/修繕/代理受取/来訪者/学習欠席 宫格 |
| 10 | `10_apply_grid_scrolled.png` | 新規申請（下滚） | 同 09 | オンライン学習/行事企画/冷蔵庫購入/物品所持 |
| 11 | `11_mypage.png` | マイページ | `Features/MyPage/MyPageStubs.swift` | 头像卡（リュウイヒ / アカウント 060218 / 男寮 A5 / 一般寮生）+ 行事予定 + 学習ステータス + 今月の点呼 + 減点明細 |
| 12 | `12_mypage_history.png` | マイページ（下滚） | 同 11 | 履歴 宫格（個人情報/処分履歴/体調報告履歴/申請履歴/掃除提出履歴/荷物受取履歴）+ 通知設定 + Tomoshibi について + ログアウト |
| 13 | `13_nfc_scan.png` | NFC 点呼弹窗 | `Features/.../Rollcall*` | スキャンの準備ができました + 点呼時間外提示 + NFC をかざす / キャンセル |
| 14 | `14_calendar.png` | カレンダー（行事予定） | 行事予定 view | 2026年4月 月历 + 4月23日 誕生日会 详情 |

> 注：这是**演示版**截图，数据是假的（リュウイヒ / 060218 等架空样本）。布局 / 配色 / 文案是真的，Android 对齐照这个来。
