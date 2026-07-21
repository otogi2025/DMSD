package jp.tomoshibi.android.ui.theme

import androidx.compose.ui.graphics.Color

// Suzu 涼 配色 — 直接 port 自 iOS TTokens.swift
// Light = iOS 原版 palette；Dark = 为 Android 设计的暗色补集（不是简单反色，是深 teal + paper-on-ink）

// ─── Suzu Light ───────────────────────────────────────────────
val SuzuPrimaryLight = Color(0xFF1F6B74)
val SuzuPrimaryDkLight = Color(0xFF0E3840)
val SuzuAccentLight = Color(0xFF5FBEC8)
val SuzuAccentSoftLight = Color(0xFFA8DCE2)
val SuzuPearlLight = Color(0xFFEFF2F3)
val SuzuPaperLight = Color(0xFFFFFFFF)
val SuzuInkLight = Color(0xFF0F1E22)
val SuzuInkSubLight = Color(0xFF56707A)
val SuzuInkMuteLight = Color(0xFF93A4AC)
val SuzuInkFaintLight = Color(0xFFC4D0D5)
val SuzuHairLight = Color(0x140F1E22) // alpha 0.08
val SuzuHairSoftLight = Color(0x0A0F1E22) // alpha 0.04

val SuzuWarnLight = Color(0xFFD1984A)
val SuzuWarnBgLight = Color(0xFFFDF4E1)
val SuzuWarnDeepLight = Color(0xFF7A4A0E)
val SuzuDangerLight = Color(0xFFC44848)
val SuzuDangerBgLight = Color(0xFFFDE8E8)
val SuzuOkLight = Color(0xFF4A9478)
val SuzuOkBgLight = Color(0xFFE3F1EA)
val SuzuOkDeepLight = Color(0xFF2C6048)

val SuzuPillLight = Color(0x141F6B74) // alpha 0.08

// amber 三段渐变对齐 iOS HomeStubs.swift cardGradient：0xFFEFC2 → 0xF4C677 → 0xD99F3E
val SuzuAmberALight = Color(0xFFFFEFC2)
val SuzuAmberBLight = Color(0xFFF4C677)
val SuzuAmberCLight = Color(0xFFD99F3E)

// ─── Suzu Dark ────────────────────────────────────────────────
val SuzuPrimaryDark = Color(0xFF5FBEC8) // 深色模式下更亮的 teal，对比更醒目
val SuzuPrimaryDkDark = Color(0xFF0E3840)
val SuzuAccentDark = Color(0xFF7ED0D8)
val SuzuAccentSoftDark = Color(0xFF1C4248)
val SuzuPearlDark = Color(0xFF0A181C) // canvas
val SuzuPaperDark = Color(0xFF142428) // card surface
val SuzuInkDark = Color(0xFFE6EEF0)
val SuzuInkSubDark = Color(0xFF9BB0B6)
val SuzuInkMuteDark = Color(0xFF6A8088)
val SuzuInkFaintDark = Color(0xFF3D5258)
val SuzuHairDark = Color(0x1AFFFFFF) // alpha 0.10
val SuzuHairSoftDark = Color(0x0DFFFFFF) // alpha 0.05

val SuzuWarnDark = Color(0xFFE0AA5E)
val SuzuWarnBgDark = Color(0x24E0AA5E) // alpha 0.14
val SuzuWarnDeepDark = Color(0xFFF4C677)
val SuzuDangerDark = Color(0xFFE57878)
val SuzuDangerBgDark = Color(0x24E57878) // alpha 0.14
val SuzuOkDark = Color(0xFF7CC7A3)
val SuzuOkBgDark = Color(0x247CC7A3) // alpha 0.14
val SuzuOkDeepDark = Color(0xFFA4DEC0)

val SuzuPillDark = Color(0x295FBEC8) // alpha 0.16

val SuzuAmberADark = Color(0xFF3A2E15)
val SuzuAmberBDark = Color(0xFF5A4520)
val SuzuAmberCDark = Color(0xFF7A5A20)
