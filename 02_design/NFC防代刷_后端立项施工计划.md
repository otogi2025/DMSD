# NFC 防代刷 — 后端立项施工计划

> 立项日期：2026-05-31。起因：teacher_web v1.0 上线就绪审查（W8）发现「NFC 防代刷三件套后端零实装」是核心安全缺口，但它属于学生端 NFC 签到流程、不在 teacher_web 范围，需单独立项。
> 调研依据：`02_design/flow_design.md`（防代刷流程主源）+ `hardware_design.md` + `03_dev/backend/v1/app/routers/rollcall.py` + `03_dev/rollcall_device/`。
> 定位：本文是「查清楚要怎么做」的施工计划，**不是已实装**。

## 1. 一句话

防代刷 = 防止学生甲替学生乙刷卡冒充出席。设计上两条签到路径各管一层防御，**后端的签到端点框架已实装，但防代刷的核心校验（一次性随机数 nonce、椭圆曲线签名 ECDSA、卡片绑定）全是 0**。

## 2. 设计的两条路径（来自 flow_design.md §3）

**路径 A — 实体卡（NTAG215 卡 → 点呼机 PN532 读头）**
- 点呼机读卡拿 7 字节 UID（卡硬件固化、无法软件篡改）→ 带 `card_uid` POST 签到 → 后端用 UID 查学生绑定。
- 防代刷锚点：卡 UID 跟学生绑定存后端，卡无法复制；老师现场目视是制度补充。

**路径 B — 动态贴纸（ST25DV16K 贴纸 → 学生手机）**
- 点呼机每 10 秒向后端拿新 nonce（一次性随机数，10 秒失效），通过 I²C 写进 ST25DV16K 贴纸。
- 学生手机后台读到贴纸里的 URL（带 device_id + nonce）→ 唤起 App → App 用手机里 iOS Keychain 存的 ECDSA 私钥（P-256 曲线）对「学生ID+设备ID+nonce+session+时间」签名 → POST 签到带 nonce + signature。
- 后端依次校验：nonce 10 秒内有效且没用过 → ECDSA 用学生公钥验签 → 设备活跃 → session 进行中 → 时间窗内。
- 防代刷数学（flow_design.md §3.4）：nonce 10 秒失效，代签者物理上来不及在 10 秒内从点呼机跑回宿舍签到，攻击窗口≈0；ECDSA 私钥设备级硬件保护，甲无法用乙私钥签名。

## 3. 后端现状

**已实装**（`rollcall.py` + `models.py`）：
- 签到端点 `POST /rollcall/sessions/{id}/checkins`（处理路径 A 的 card_uid + 路径 B 的 idempotency_key 幂等去重）
- session 状态校验（rollcall.py:278）、时间窗判定 present/late（:358）、幂等去重（:336-355）、path_hint 一致性（:286-301）、WebSocket 推送（:391-403）
- `rollcall_events` 表有 card_uid / idempotency_key / path_type / device_id 字段（models.py:803-824）

**未实装**（设计标注 v1.1 推后）：
- nonce 端点 + nonce 状态表 —— 后端完全没有
- ECDSA 签名验证 —— schemas.py:627 注释「v1.1 起追加」，当前签到无 signature 字段、后端不验签
- 卡 UID 绑定表 —— models.py 没有，Student 表无 card_uid 字段；路径 A 现遇 card_uid 无 student_id 直接返 422 UNKNOWN_CARD
- 点呼机端代码 —— rollcall_device/src/main.py 标「实装 0%，placeholder」

## 4. 缺口 + 施工顺序（后端可独立先做）

按依赖排序，前 6 步后端能独立做完（用脚本模拟点呼机/手机测，不等硬件）：

| 顺序 | 缺口 | 做什么 | 层 |
|---|---|---|---|
| 1 | nonce 状态表 | 建表（device_id/nonce/issued_at/used_at），10 秒过期+用后作废 | 后端建表+迁移 |
| 2 | `POST /api/v1/nonce` | 点呼机每 10 秒来拿，生成随机串、写表、返回 {nonce, ttl} | 后端新端点 |
| 3 | nonce 校验 | 签到端点收 nonce 时查表校验有效期+是否已用，失败 INVALID_NONCE | 后端逻辑 |
| 4 | ECDSA 公钥存储 | Account 表加 public_key 字段，或独立 StudentKey 表；注册流程存学生公钥 | 后端建字段/表 |
| 5 | ECDSA 验签 | 签到收 signature 后用学生公钥做 P-256 验签（Python cryptography 库本地可测），失败 INVALID_SIGNATURE | 后端逻辑 |
| 6 | NFC 卡绑定 | 建 nfc_cards 表（uid/student_id/active）+ 老师绑卡/作废端点（POST /cards/bind、DELETE /cards/{uid}）；路径 A 通过 uid 查学生 | 后端建表+端点 |
| - | schema 加字段 | RollCallCheckinIn 加 nonce + signature（Optional，兼容旧 client 不破坏现有测试） | 后端 schemas.py |

## 5. 依赖关系（这几步后端做不完，要等别的）

- **点呼机硬件**：`POST /nonce` 联调要 Pi + ST25DV16K 实物（hardware_design §4.6 显示 5-27 已下单，首单约 19,800 日元）+ I²C 写贴纸；PN532 读 NTAG215 UID 要 Pi + PN532 接线 + nfcpy/libnfc 库。
- **iOS/Android**：ECDSA 端到端要 App 在 Keychain 生成 P-256 密钥对、注册公钥、签名 payload 的字节序/编码跟后端 verify 严格一致（`student_id‖device_id‖nonce‖session_id‖ts_local` 双端约定）；RollCallAPI.swift 现在没 nonce/signature 字段（:35-41）要加。

## 6. 建议

后端 1-6 步（约 2 表 + 2-3 端点 + 验签逻辑 + 迁移 + 测试）可在 teacher_web 之外独立排期先做，做完用 Python 脚本模拟点呼机和手机端到端自测。硬件/iOS 联调等贴纸到货 + iOS 加签名字段后再做。**这是 v1.0「真防代刷」的关键缺口，建议作为 v1.0 之后第一优先功能立项。**
