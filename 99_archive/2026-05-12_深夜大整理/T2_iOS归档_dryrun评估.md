# T2 — iOS throwaway 代码归档 dry-run 评估

> **这是什么**：backlog T2 🔴 标注"`03_dev/Student/DMSDStudentApp(iOS)/` 未归档 + 方向错位"。本文件是 CC 对归档操作的**dry-run 评估**，**不执行**。等 itsuki 授权后执行。
>
> **为什么 dry-run 而不直接做**：归档是破坏性操作（改 git history / 文件路径 / memory），按 CLAUDE.md "执行行动要 careful" 原则需要 itsuki 明确授权。
>
> **最后更新**: 2026-04-20（本评估报告初版，对应 backlog T2）

---

## 📌 关键更新 — backlog T2 的诊断过期

**backlog T2 里说**："`.gitignore` 后加的没跑 `git rm --cached` → 个人环境污染"

**实际 check（2026-04-20）**：

```
git ls-files "03_dev/Student/DMSDStudentApp(iOS)/" | grep -iE "xcuserdata|xcuserstate"
→ (none)
```

`git ls-files` 显示 repo 里 **没有 xcuserdata / xcuserstate**。原始 `.gitignore` 第 7 行就包含 `**/xcuserdata/` + `**/*.xcuserstate`，所以这些文件从未被 tracked。

**结论**：T2 里"个人环境污染"这半个论点**不成立**。只有"throwaway 代码 + 方向错位 + 文件夹名带括号"这部分仍然成立。

---

## 📊 当前状态诊断

### 基础数据

| 指标 | 值 |
|---|---|
| tracked 文件总数 | 35 |
| Swift 源文件数 | 约 22-26（主要在 `DMSDStudentApp/` 下）|
| 测试模板文件 | 2 个（Tests + UITests，全 Xcode 默认，无真测试）|
| JSON mock 数据 | 4 个（`Mocks/v1/`）|
| Assets（图片 / 颜色）| 3 个 Contents.json |
| Xcode project 文件 | 2 个（project.pbxproj + contents.xcworkspacedata）|
| 原始行数（估计）| ~1658 行 Swift |
| Xcode 个人数据（xcuserdata / xcuserstate）| **0**（已被 .gitignore 排除）|

### 目录结构

```
03_dev/Student/DMSDStudentApp(iOS)/
├── DMSDStudentApp/                      应用本体
│   ├── Assets.xcassets/                 资源（图标 / 颜色）
│   ├── Core/
│   │   ├── Error/APIErrorMessageMap.swift
│   │   ├── Networking/APIEnvelope.swift
│   │   ├── Networking/MockJSONLoader.swift
│   │   └── Scanning/NFCScanService.swift
│   ├── Features/
│   │   ├── AppShell/StudentAppShellView.swift
│   │   ├── Application/ApplicationCenterView.swift
│   │   ├── Common/ScreenState.swift / StateContainerView.swift
│   │   ├── Discipline/ (3 View)
│   │   ├── Profile/MyPageView.swift
│   │   ├── RollCall/ (7 View + Store)
│   │   └── Settings/SettingsCenterView.swift
│   ├── Mocks/v1/ (3 JSON + README)
│   ├── ContentView.swift
│   └── DMSDStudentAppApp.swift          app entry
├── DMSDStudentApp.xcodeproj/            Xcode 项目
├── DMSDStudentAppTests/                 unit test 模板
└── DMSDStudentAppUITests/               UI test 模板
```

### 方向错位分析（backlog T2 原文正确部分）

1. **Phase 2 路径 B 原型**（iPhone 读被动 NFC 标签）—— 按 `NFCScanService.swift` 用 `NFCTagReaderSession` 读标签
2. **Phase 1 不需要 iOS App** —— 按 4-19 G2 决策，v1.0 一次上 iOS + Android + 卡，但**这份代码是 4 月早期做的 Phase 2 原型**，架构已经跟不上 4-19 G2 和 4-20 议题 A/B 的新方案（BTR + Universal Link + 动态 ST25DV）
3. **memory 明确标 "throwaway"**（`feedback_ios_early_code.md`）
4. **测试三件套全 Xcode 默认模板**，没一行真 test

---

## 🎯 归档方案（3 选 1，CC 推荐 A）

### 方案 A ⭐（推荐）— `git mv` 整体归档到 `99_archive/`

```bash
# 目标路径
99_archive/2026-04-20_Phase2_iOS_原型_throwaway/
  └── DMSDStudentApp(iOS)/          ← 整个原目录移进来

# 同时建一份 README 说明
99_archive/2026-04-20_Phase2_iOS_原型_throwaway/README.md
```

**好处**:
- git history 完全保留（`git log --follow` 追溯任何 Swift 文件）
- `03_dev/` 下干净，下次写 iOS 代码时不会被"已有类似文件"误导
- 未来开 iOS 时可以参考（但不直接用）归档里的结构

**坏处**:
- 归档路径里仍带括号 `(iOS)` —— 如果要同时解决文件夹名问题，改名要单独做

**预计 git mv 操作**:
- 1 次 `git mv` 动 35 个文件的路径
- 1 次 `git add` 新建 99_archive README
- 1 个 commit

### 方案 B — 删除（依靠 git history 存档）

```bash
rm -r "03_dev/Student/DMSDStudentApp(iOS)/"
git add -A
git commit
```

**好处**: repo 变小；最干净

**坏处**:
- 想看旧代码要 `git checkout v0.3.1 -- 03_dev/...`，不直观
- 对教授来说"删除 throwaway" 看起来像"删证据"（虽然 git 留了）

**不推荐**。

### 方案 C — 保留原位 + 加 README 标明 throwaway

```bash
# 什么都不动，只在目录下加
03_dev/Student/DMSDStudentApp(iOS)/README.md
  "⚠️ throwaway 代码。v1.0 iOS 开工时将基于 01_specs + 02_design 重写。不要在此基础上改动。"
```

**好处**: 零风险；改动最小

**坏处**:
- `03_dev/` 永远混着 throwaway + 未来正式代码
- 未来开 iOS 时 Xcode 会在 `03_dev/Student/` 下看到两份项目，容易选错
- T2 问题没实质解决

**不推荐**。

---

## 🔍 文件夹名 `(iOS)` 带括号的 POSIX-safety

### 现状

`03_dev/Student/DMSDStudentApp(iOS)/` 文件夹名里有**英文括号 `(` `)`**。

### 潜在问题

- **shell 命令不加引号会报错**：`cd 03_dev/Student/DMSDStudentApp(iOS)` 报 `syntax error near unexpected token (`
- **CI / CD 管道** 里某些工具（Jenkins / shell script / docker volume）对括号处理不一致
- **URL 里**：括号在部分 CDN / 下载链接里被转义成 `%28` `%29`，视觉不清
- **截图 / 文档引用**：带括号的路径读起来奇怪

### 改名建议

如果**走方案 A**（归档），顺便改名：

```
原: 99_archive/2026-04-20_Phase2_iOS_原型_throwaway/DMSDStudentApp(iOS)/
改: 99_archive/2026-04-20_Phase2_iOS_原型_throwaway/DMSDStudentApp_iOS/
```

**或直接不保留内层目录层**（把 `DMSDStudentApp/` 上提一层）：

```
99_archive/2026-04-20_Phase2_iOS_原型_throwaway/
├── DMSDStudentApp/
├── DMSDStudentApp.xcodeproj/
├── DMSDStudentAppTests/
├── DMSDStudentAppUITests/
└── README.md
```

**注意**：Xcode 的 `.xcodeproj` 内部有**绝对 / 相对路径引用**（`project.pbxproj` 里）。改目录名后 Xcode 打开可能看到"文件找不到"警告 —— 但 **throwaway 代码不用管**，因为不会再打开 Xcode 跑。

---

## 📋 执行命令（itsuki 授权后可直接跑）

**方案 A + 同时改名**：

```bash
cd /Users/kurekoduki/dev/DMSD

# 1. 建目标目录
mkdir -p 99_archive/2026-04-20_Phase2_iOS_原型_throwaway

# 2. git mv（整个目录）
git mv "03_dev/Student/DMSDStudentApp(iOS)" \
       "99_archive/2026-04-20_Phase2_iOS_原型_throwaway/DMSDStudentApp_iOS"

# 3. 检查 03_dev/Student/ 是否空
ls 03_dev/Student/ 2>&1
# 如果空 → git 不会自动删空目录，需要手动：
#   rmdir 03_dev/Student/ 2>&1
# 如果想保留 03_dev/Student/ 作为未来正式 iOS 代码目录 → 加 .gitkeep：
#   touch 03_dev/Student/.gitkeep
#   git add 03_dev/Student/.gitkeep

# 4. 新建 README 标明归档理由
# （CC 可以预先起草 README 放 draft 文件）

# 5. commit
git commit -m "$(cat <<'EOF'
chore(v0.3.1-post): 归档 Phase 2 iOS throwaway 原型 → 99_archive/

覆盖 backlog T2 🔴。

为什么归档：
- 这份代码是 4 月早期做的 Phase 2 路径 B 原型（iPhone 读静态 NFC
  标签，自己联网发后端）
- 4-19 G2 决策 + 4-20 议题 A/B 后，iPhone 方案改为 BTR + Universal
  Link + AASA + 动态 NFC 贴纸 ST25DV16K，架构和这份原型完全不同
- memory feedback_ios_early_code 明确标 "throwaway，iOS 将从零重写"
- 留在 03_dev/ 会让未来写正式 iOS 代码时被"已有类似文件"误导

归档后的命名：
- 原路径：03_dev/Student/DMSDStudentApp(iOS)/  （文件夹名带括号不
  POSIX-safe）
- 新路径：99_archive/2026-04-20_Phase2_iOS_原型_throwaway/
         DMSDStudentApp_iOS/  （去括号）

保留内容：
- 25+ 个 Swift 源文件（Features / Core / Mocks）
- Xcode project 文件（project.pbxproj 等）
- Tests + UITests 模板（Xcode 默认无真测试）
- git history 完整保留（git log --follow 可追溯）

不保留：
- xcuserdata / xcuserstate —— 原来就被 .gitignore 排除，不在 repo 里

03_dev/Student/ 保留为空目录（加 .gitkeep），未来正式 iOS 开工时
重新在此建目录。
EOF
)"
```

**方案 B（删除）**：

```bash
cd /Users/kurekoduki/dev/DMSD
git rm -r "03_dev/Student/DMSDStudentApp(iOS)"
touch 03_dev/Student/.gitkeep && git add 03_dev/Student/.gitkeep
git commit -m "chore: 删除 Phase 2 iOS throwaway 原型（git history 留存）"
```

**方案 C（仅加 README）**：

```bash
cd /Users/kurekoduki/dev/DMSD
# 手写 03_dev/Student/DMSDStudentApp(iOS)/README.md
# 内容：throwaway 警告 + 重写计划
git add ".../README.md"
git commit -m "docs: 标记 Phase 2 iOS 为 throwaway"
```

---

## 🚨 风险清单

### 方案 A 的风险

1. **git mv 35 个文件会产生大量 rename 记录** —— commit diff 会很长，但 github 会识别为 rename
2. **Xcode 项目绝对路径引用** —— `.xcodeproj/project.pbxproj` 里可能有 absolute path 引用，打开 Xcode 会报警告。但 throwaway 代码不会再打开，忽略即可
3. **归档路径里的中文** "Phase 2 iOS 原型 throwaway" —— CC 实测中文目录名和 `.gitignore` / `git ls-files` 工作正常，但少数 CI 工具可能有问题。可选：改为全英 `99_archive/2026-04-20_phase2_ios_throwaway/`
4. **未来万一想 un-archive** —— 可以再跑 `git mv` 移回来，不丢数据

### 方案 B 的风险

1. **教授看 commit log "删除 throwaway"** 心里可能对"是不是在藏错"产生疑问 —— 但有 git history 作证，可以解释

### 方案 C 的风险

1. 问题没解决，只是打了"警告标签"
2. 未来 6-12 个月内还会反复被提起"这块要归档"

---

## 📌 CC 推荐

**方案 A + 同时改名去括号 + 全英路径**:

```
99_archive/2026-04-20_phase2_ios_throwaway/
├── DMSDStudentApp_iOS/
│   ├── DMSDStudentApp/...
│   ├── DMSDStudentApp.xcodeproj/
│   ├── DMSDStudentAppTests/
│   └── DMSDStudentAppUITests/
└── README.md                    ← CC 可预先起草
```

**理由**:
- A 比 B/C 都更彻底、更显"我在主动清理历史堆积"（AC 视角加分）
- 改全英路径解决 POSIX 问题（未来 CI 启用时少一个踩坑点）
- 归档 README 里写"重写计划"给未来的 itsuki 看

---

## 下一步（等 itsuki 明确授权）

1. itsuki 说 "做 T2 方案 A" → CC 执行命令
2. itsuki 说 "做方案 B" → CC 执行方案 B
3. itsuki 说 "先不动" → T2 保持 ⬜，进入未来 patch 再做
4. itsuki 说 "改方案" → 告诉 CC 具体怎么改

**CC 本次会话不执行归档操作**。

---

**END**
