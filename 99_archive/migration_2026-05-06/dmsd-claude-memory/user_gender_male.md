---
name: itsuki 是男生 — 中文代词用男字旁的「ta」
description: 2026-05-04 itsuki 明确指出。中文代词必须用男字旁（人字旁）「ta」，不要用女字旁「ta」。Tomoshibi 系统名 + itsuki 名字容易让人误判性别 — 这是历史误判，必须改正
type: user
originSessionId: 914c1dd9-9fd9-4789-931d-d6e59ae7ad9f
---

itsuki 是男生。中文代词全部用**男字旁**的「ta」（人字旁那个），不用女字旁的「ta」。

## 原话

「我是男生用 他」（2026-05-04）

## 历史误判原因

- itsuki 是日语 / 中文名，英文罗马字看不出性别
- Tomoshibi（灯火）是温暖意象，先入为主联想成女性
- CC 默认中文叙述用女字旁「ta」是历史误差

## 应用范围

所有 CC 写的文档、对话、注释、AC 素材 dump、CHANGELOG、TODO — 全部用男字旁「ta」。

## 已批量改的范围（2026-05-04）

全 DMSD 仓库 markdown（除 99_archive/ 历史快照）+ 全 memory 文件夹 sed 批量替换完成：
- DMSD 仓库 markdown 内 172 处替换
- memory 文件夹内 102 处替换
- 共 274 处

99_archive/ 是历史快照不动。

## 注意 sed 的副作用

sed 全替换有个边界场景 — **讨论代词对比时**（"用 X 不用 Y"）的语义会被破坏。已修：本文件 + MEMORY.md 顶部用「男字旁的 ta」「女字旁的 ta」描述法绕开。

## How to apply

- 所有第三人称指代 itsuki：用男字旁「ta」
- 老师 / 同学 / 妈妈 等真人是女性：用女字旁「ta」（按事实）
- 写规则讨论代词时：用「男字旁」「女字旁」描述法避免被工具误伤
