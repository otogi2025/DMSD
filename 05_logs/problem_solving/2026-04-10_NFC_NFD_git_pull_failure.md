# 2026-04-10 — NFC vs NFD：跨平台 git pull 失败事件

**类型**：problem_solving / AC 入試材料
**触发场景**：一个月停滞后回到 Mac，想 `git pull` 把 VPS 上的 3 个新 commit 拉下来

---

## 发生了什么

`git pull --rebase` 一开始就报错：

```
error: The following untracked working tree files would be overwritten by checkout:
    01_specs/临时PDF/「API_CONVENTIONS_v1.0.md」のコピー
    01_specs/临时PDF/「API_Contract_v1.0.pages」のコピー
    01_specs/临时PDF/「IA_UI_v1.0.pages」のコピー
    01_specs/临时PDF/「Overview of Features to Be Implemented in Version1.0.pages」のコピー
    01_specs/临时PDF/「v1.0完整计划.pdf」のコピー.pdf
Aborting
```

字面意思是"这 5 个未追踪的工作区文件会被 checkout 覆盖，拒绝继续"。可这 5 个文件明明在 git 索引里 tracked，git 自己也承认。两边互相打架，pull 完全卡死。

## 根本原因

**Unicode normalization 在不同操作系统的处理差异。**

日文里有些字符可以用两种方式编码，比如 `ピ`：

- **NFC**（precomposed，组合形式）= 1 个码点 `ピ`
- **NFD**（decomposed，分解形式）= 2 个码点 `ヒ` + `゚`（combining semi-voiced mark）

我家的 VPS 是 Linux，git 索引把这些文件名按 NFD 存。Mac 这边的 git 索引按 NFC 存。文件**内容完全一样**（同一个 git blob 哈希），但**路径的字节序列**不同。macOS 的 APFS 文件系统又把 NFC 和 NFD 当成同一个文件名 → git 一边觉得"NFD 路径要新建文件"，一边发现"NFC 路径已经占了同一个 inode"，于是 abort。

可视化：

```
git 索引 (origin/main):  「...」のコピー   ← NFD 字节序列
git 索引 (本地 HEAD):    「...」のコピー   ← NFC 字节序列  ← 看起来一样!
APFS 磁盘:               「...」のコピー   ← 同一个 inode
```

## 怎么解决的

折腾了 4 步：

1. **`mv` 5 个文件到 `~/dmsd_pull_blockers_backup/`** → 失败。它们其实是 tracked 文件，移走之后 git 报"unstaged changes (deleted)"，pull 仍然拒绝跑。
2. **`git stash` 暂存"删除"** → stash 把删除回滚了，文件又出现在工作区。pull 卡同样的原始错误。
3. **`git rm` + commit 删除 + 再 pull** → rebase 这次跑起来了，但走到第 3 步时 git 把 origin 的"NFC 路径消失 + NFD 路径出现"识别成 **rename**，和我的"删除 NFC"打架，报 rename/delete conflict。
4. **`git rebase --skip`** → 跳过我那个多余的删除 commit。✅ rebase 成功完成。

最终 git 历史是干净的，3 个目标 commit 全部到位，CLAUDE.md / progress_overview.md / reflection_2026-04-10 都拉下来了。

## 遗留问题

`git status` 还会显示 5 个 NFC 路径的"untracked"文件——但我用 `ls` 数过 `01_specs/临时PDF/` 里的实际文件，**只有 5 个，不是 10 个**。这是 git 内部账本和 APFS 文件系统的标签错配，磁盘上没有真实重复，不影响项目使用。等我以后学会更多 git 操作再彻底清理。

两个备份目录 `~/dmsd_pull_blockers_backup/` 和 `~/dmsd_pull_blockers_backup/round2/` 暂时留着，等我确认 `01_specs/临时PDF/` 一切正常后可以删。

## 学到什么

1. **跨平台开发会有看不见的坑。** 同一个 git 仓库在 Linux 和 macOS 之间互相同步时，仅仅因为文件名 Unicode 编码不同，整个 pull 流程就会卡死。这种 bug 在单平台开发里永远遇不到——只有横跨多个系统的项目才会撞上。
2. **错误信息有时是误导。** git 说"untracked files would be overwritten"，但这些文件其实是 tracked 的。错误信息描述的是 git 内部判断的中间状态，不是事实。理解 bug 不能只看报错措辞，必须查证它的实际状态。
3. **零基础也能解决底层 bug——只要会和 AI 协作。** 一年前的我看到这种报错肯定就放弃了。今天我跟 Claude Code 一步一步定位到 NFC vs NFD 这种连资深开发者都不一定立刻能反应过来的根本原因，然后用 4 步 git 操作干净地修好。诀窍不是"我懂多少"，而是：**懂得怎么和 AI 一起找根本原因 + 始终保持非破坏性操作习惯**（全程 `mv` 到备份目录而不是 `rm`，每一步都先检查再行动）。
4. **诚实记录"半成功"也是 AC 材料。** 这个 bug 没有 100% 修干净，还遗留 5 个鬼影 untracked。我没把它假装成"完美修复"，而是诚实地把遗留状态写下来。AC 入試 看的是真实过程，包括"未完成的部分"——能识别并承认遗留问题，本身就是工程能力的一部分。

---

**文件状态**：草稿，待 itsuki 审阅
**关联 commit**：`d23322e` / `44ba713`（rebase 后的本地新 commit），以及被 skip 掉的临时删除 commit `4024418`
