---
name: demo-clean
description: DMSD v1.0 上线前 demo scaffold 清理 SOP — 全清单（手动维护 + 自动 grep 补充）/ 每条清理动作 / 测试验证 / 留 v1.0-pre-cleanup tag。⭐ 一次性极致重要任务（漏删 = 生产环境安全漏洞，比如 RegisterStep5 demo bypass / 长按切点呼状态 / 假数据假端点）。
when_to_use: ⭐ 触发 — itsuki 说「v1.0 准备 / 上线前检查 / demo 清理 / 发版前 / 准备发布 / 删 demo」/ 当前版本号即将 bump 到 v1.0.0 之前 / 上线前 1-2 周节点。
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Demo Clean Skill — v1.0 上线前 demo scaffold 清理

> **核心理念**：DMSD demo 阶段为了快速演示加了一堆 bypass / 假数据 / 长按切状态等 scaffold。**这些东西 v1.0 上线前必须全删** — 否则：
> - RegisterStep5 demo bypass 留着 → 用户随便点个按钮就跳过认证
> - 长按切点呼状态留着 → 学生长按伪造已签到
> - 假数据假端点留着 → 跟真后端 API 不一致，崩
>
> **本 skill 是上线前 1-2 周必跑的"地毯式清理 SOP"**。一次性任务但极致关键，CC 默认会漏。

---

## §0 前置安全网（开干前必做）

```bash
# 留 git tag 便于回滚
git tag v1.0-pre-cleanup
git tag --list | tail -5  # 确认建好

# 确认工作树干净（没未 commit 的活）
git status

# 确认 main 是最新的
git log --oneline -3
```

**铁律**：清理过程发现「这个 scaffold 删了好像功能就崩了」→ **不要硬删** → 报告 itsuki 这个 scaffold 实际是依赖项（不是 demo 一次性），需要重新设计。

---

## §1 已知 demo scaffold 全清单

### 1.1 主清单源

`02_design/system_features.md` **末尾「v1.0 上线前必删 demo scaffold 集中清单」**段（2026-05-03 d9e3f48 commit 加的）。

每次跑本 skill 第一步：

```bash
sed -n '/v1.0 上线前必删 demo scaffold/,/^## /p' 02_design/system_features.md
```

### 1.2 截至 2026-05-04 已知项（可能过时，以 system_features.md 末尾为准）

| 文件 | scaffold 内容 | 删除动作 |
|---|---|---|
| `03_dev/student_ios/v1/TomoshibiApp/Features/Register/RegisterStep5View.swift` | demo bypass（itsuki backend 没开时直接进 App） | 删 bypass 分支 + 还原真实 backend 调用 |
| `03_dev/student_ios/v1/TomoshibiApp/Features/Home/HomeStubs.swift` | 假数据（学生列表 / 点呼状态） | 删整个 Stubs 文件 + grep 引用替换为真 API |
| `03_dev/student_ios/v1/TomoshibiApp/Features/CheckIn/...` | 长按切点呼状态（demo 演示用） | 删 long-press handler |
| `03_dev/student_ios/v1/TomoshibiApp/Foundation/AppState/AppStore.swift` | 可能有 demo flag / mock state | grep `demo` `mock` `stub` `fake` 全删 |

**这个表必须每次跑本 skill 时跟 system_features.md 末尾对账更新** — 单源是 system_features.md。

---

## §2 自动 grep 补充扫描

手动清单总会漏。跑这些 grep 找漏网的：

```bash
# Swift 端
grep -rn -E "(demo|mock|stub|fake|bypass|TODO|FIXME|HACK|XXX)" \
  03_dev/student_ios/v1/TomoshibiApp/ \
  --include="*.swift" \
  | grep -v "// " | grep -v "/\*"   # 过滤注释（视情况）

# Backend 端
grep -rn -E "(demo|mock|stub|fake|bypass|TODO|FIXME|HACK)" \
  03_dev/backend/app/ \
  --include="*.py"

# 文档端
grep -rn -E "(demo|mock|stub|TODO|FIXME)" \
  02_design/ 01_specs/ \
  --include="*.md"
```

每个匹配项**都要逐条评估**：
- 是 demo scaffold → 删
- 是合理的 TODO 注释（标记未来迭代） → 保留
- 是测试用 mock（在 tests/ 目录下） → 保留
- 不确定 → 报告 itsuki 决定

---

## §3 每条清理动作模板

对每个 demo scaffold 走这 5 步：

```
Step 1: 读文件确认 scaffold 上下文
Step 2: 找所有调用 / 引用（grep 文件名 / 函数名 / 变量名）
Step 3: 决定删除 vs 替换
   - 纯 demo（演示完没用）→ 直接删
   - 临时替换真实逻辑 → 还原真实调用（如 RegisterStep5）
Step 4: 改完跑 build / test
   - iOS: Xcode build (Cmd+B) 确认编译过
   - Backend: pytest 跑测试（如果有）
Step 5: git diff 自看一遍 + commit
```

### 3.1 commit message 模板

```
chore(cleanup): 删 X demo scaffold（v1.0 上线前清理）

- 删: <文件:行号> <一句话原文>
- 替换: <文件:行号> <从假数据到真 API>
- 验证: Xcode build pass / pytest pass

清单源: system_features.md §v1.0 上线前必删 demo scaffold
```

---

## §4 删除后测试验证

### 4.1 iOS

```bash
# 在 Xcode 跑：
# Product → Build (Cmd+B) — 编译过
# Product → Test (Cmd+U) — 单元测试过（如果有）
# Product → Run — 跑模拟器，手动过一遍主流程：
#   - 注册 5 步
#   - 登录
#   - 点呼签到
#   - 查看记录
```

任何一步炸 → **回滚到 v1.0-pre-cleanup tag**，告诉 itsuki 删错了哪一项。

### 4.2 Backend

```bash
cd 03_dev/backend
pytest                                  # 跑全套测试
uvicorn app.main:app --reload           # 起服务
curl http://localhost:8000/health       # 基本可用性
```

### 4.3 集成测试

iOS 模拟器 + backend 本地起 → 跑端到端流程（注册 → 登录 → 签到 → 后端真收到记录）。

---

## §5 完成后清单

- [ ] 所有手动清单项 ✅
- [ ] 所有 grep 补充项 ✅
- [ ] iOS Xcode build pass + 主流程手动过
- [ ] Backend pytest pass + 端到端跑通
- [ ] 文档（system_features.md / IOS_DESIGN_LOG.md）相关章节更新
- [ ] system_features.md 末尾「v1.0 上线前必删 demo scaffold 清单」段标 ✅ 完成日期
- [ ] git log --oneline 最近 commit 都是 chore(cleanup) 类
- [ ] git tag v1.0-rc1 (release candidate)
- [ ] 报告 itsuki：清理完成 + 准备 bump v1.0.0

---

## §6 反模式

### ❌ 反模式 1: 不留 v1.0-pre-cleanup tag 直接开干
**后果**：删错了无法快速回滚到清理前状态。

### ❌ 反模式 2: 看到 grep 出 demo 就直接删
**后果**：可能误删测试 mock / 文档示例 / 命名巧合。**每条逐条评估**。

### ❌ 反模式 3: 删完不跑 build / test
**后果**：编译炸 / 端到端炸 / 上线后用户炸。

### ❌ 反模式 4: 一个大 commit 删所有
**后果**：出问题不能 bisect 找到具体哪一项删错。**每个 scaffold 一个 commit**。

### ❌ 反模式 5: 不更新 system_features.md 末尾清单
**后果**：清单显示「待删」但实际已删，下个会话 CC 看清单又开始找。

---

## §7 配套文件 / skill

- `02_design/system_features.md` 末尾段 — 主清单单源
- `.claude/skills/version-bump/SKILL.md` — 清理完后 bump v1.0.0 走 version-bump skill
- `.claude/skills/release-checklist/SKILL.md` — 清理完后走发版动作
- memory `project_demo_scaffolds_to_remove_before_v1.md` — 项目级提醒

---

**最后更新**：2026-05-04 itsuki 拍板新建（v1.0 上线前 1-2 周必跑）
