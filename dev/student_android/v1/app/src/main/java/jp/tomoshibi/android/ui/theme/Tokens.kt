package jp.tomoshibi.android.ui.theme

import androidx.compose.runtime.Composable
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

// Suzu 専用 token — 超出 Material 3 ColorScheme 表达力的颜色 + 渐变
// 对应 React tokens.jsx 里 TT_LIGHT / TT_DARK 的 warn/danger/ok/amber/pill/gradient
// 通过 LocalSuzuTokens CompositionLocal 在子树消费（对应 React useSuzu() context hook）

@Immutable
data class SuzuTokens(
    val isDark: Boolean,
    // 状态色 — Material 3 没有的"温暖警告 / 安全成功"语义
    val warn: Color,
    val warnBg: Color,
    val warnDeep: Color,
    val danger: Color,
    val dangerBg: Color,
    val ok: Color,
    val okBg: Color,
    val okDeep: Color,
    // 表面 / 文字层级（5 层 ink + 2 层 hairline）
    val pearl: Color, // canvas / pageBg
    val paper: Color, // card surface
    val ink: Color, // primary text
    val inkSub: Color, // secondary text
    val inkMute: Color, // muted text / icon
    val inkFaint: Color, // disabled / placeholder
    val hair: Color, // 0.08 alpha divider
    val hairSoft: Color, // 0.04 alpha divider
    // pill chip 半透 primary
    val pill: Color,
    // amber Card 渐变（Home hero 减点卡）— iOS 招牌琥珀（三段停）
    val amberA: Color,
    val amberB: Color,
    val amberC: Color,
    // 三个签名渐变
    val btnGrad: Brush, // 主 CTA: accent → primary 135deg
    val amberGrad: Brush, // amber Card hero
    val rollGrad: Brush, // 点呼按钮 radial: accentSoft → accent → primary
)

// LocalSuzuTokens 默认值是 Light — 实际由 TomoshibiTheme 注入
val LocalSuzuTokens = staticCompositionLocalOf { lightSuzuTokens() }

fun lightSuzuTokens() =
    SuzuTokens(
        isDark = false,
        warn = SuzuWarnLight,
        warnBg = SuzuWarnBgLight,
        warnDeep = SuzuWarnDeepLight,
        danger = SuzuDangerLight,
        dangerBg = SuzuDangerBgLight,
        ok = SuzuOkLight,
        okBg = SuzuOkBgLight,
        okDeep = SuzuOkDeepLight,
        pearl = SuzuPearlLight,
        paper = SuzuPaperLight,
        ink = SuzuInkLight,
        inkSub = SuzuInkSubLight,
        inkMute = SuzuInkMuteLight,
        inkFaint = SuzuInkFaintLight,
        hair = SuzuHairLight,
        hairSoft = SuzuHairSoftLight,
        pill = SuzuPillLight,
        amberA = SuzuAmberALight,
        amberB = SuzuAmberBLight,
        amberC = SuzuAmberCLight,
        btnGrad =
            Brush.linearGradient(
                colors = listOf(SuzuAccentLight, SuzuPrimaryLight),
            ),
        // 三段对角渐变：对齐 iOS 0% / 55% / 100% stops
        amberGrad =
            Brush.linearGradient(
                colorStops =
                    arrayOf(
                        0.0f to SuzuAmberALight,
                        0.55f to SuzuAmberBLight,
                        1.0f to SuzuAmberCLight,
                    ),
            ),
        // 点呼按钮 radial: 中央深 primary → 中环 accent → 外缘浅 accentSoft
        // (Compose Brush.radialGradient: colors[0] = center, colors[N-1] = edge)
        // 对齐 iOS shield.checkered + 中央深外缘亮 halo 效果
        rollGrad =
            Brush.radialGradient(
                colors = listOf(SuzuPrimaryLight, SuzuAccentLight, SuzuAccentSoftLight),
            ),
    )

fun darkSuzuTokens() =
    SuzuTokens(
        isDark = true,
        warn = SuzuWarnDark,
        warnBg = SuzuWarnBgDark,
        warnDeep = SuzuWarnDeepDark,
        danger = SuzuDangerDark,
        dangerBg = SuzuDangerBgDark,
        ok = SuzuOkDark,
        okBg = SuzuOkBgDark,
        okDeep = SuzuOkDeepDark,
        pearl = SuzuPearlDark,
        paper = SuzuPaperDark,
        ink = SuzuInkDark,
        inkSub = SuzuInkSubDark,
        inkMute = SuzuInkMuteDark,
        inkFaint = SuzuInkFaintDark,
        hair = SuzuHairDark,
        hairSoft = SuzuHairSoftDark,
        pill = SuzuPillDark,
        amberA = SuzuAmberADark,
        amberB = SuzuAmberBDark,
        amberC = SuzuAmberCDark,
        btnGrad =
            Brush.linearGradient(
                colors = listOf(SuzuAccentDark, SuzuPrimaryDark),
            ),
        amberGrad =
            Brush.linearGradient(
                colorStops =
                    arrayOf(
                        0.0f to SuzuAmberADark,
                        0.55f to SuzuAmberBDark,
                        1.0f to SuzuAmberCDark,
                    ),
            ),
        rollGrad =
            Brush.radialGradient(
                colors = listOf(SuzuPrimaryDark, SuzuAccentDark, SuzuAccentSoftDark),
            ),
    )

// 短手访问器 — 屏幕里写 SuzuT.warn 比 LocalSuzuTokens.current.warn 短
object SuzuT {
    val current: SuzuTokens
        @Composable get() = LocalSuzuTokens.current
}
