package jp.tomoshibi.android.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider

// Material 3 ColorScheme — Suzu palette 映射到 M3 role
private val SuzuLightColorScheme = lightColorScheme(
    primary = SuzuPrimaryLight,
    onPrimary = SuzuPaperLight,
    primaryContainer = SuzuAccentSoftLight,
    onPrimaryContainer = SuzuPrimaryDkLight,

    secondary = SuzuAccentLight,
    onSecondary = SuzuPaperLight,
    secondaryContainer = SuzuPillLight,
    onSecondaryContainer = SuzuPrimaryLight,

    tertiary = SuzuAmberBLight,
    onTertiary = SuzuPaperLight,
    tertiaryContainer = SuzuAmberALight,
    onTertiaryContainer = SuzuWarnDeepLight,

    error = SuzuDangerLight,
    onError = SuzuPaperLight,
    errorContainer = SuzuDangerBgLight,
    onErrorContainer = SuzuDangerLight,

    background = SuzuPearlLight,
    onBackground = SuzuInkLight,
    surface = SuzuPaperLight,
    onSurface = SuzuInkLight,
    surfaceVariant = SuzuPearlLight,
    onSurfaceVariant = SuzuInkSubLight,

    outline = SuzuInkMuteLight,
    outlineVariant = SuzuHairLight
)

private val SuzuDarkColorScheme = darkColorScheme(
    primary = SuzuPrimaryDark,
    onPrimary = SuzuPearlDark,
    primaryContainer = SuzuAccentSoftDark,
    onPrimaryContainer = SuzuAccentDark,

    secondary = SuzuAccentDark,
    onSecondary = SuzuPearlDark,
    secondaryContainer = SuzuPillDark,
    onSecondaryContainer = SuzuAccentDark,

    tertiary = SuzuAmberBDark,
    onTertiary = SuzuPearlDark,
    tertiaryContainer = SuzuAmberADark,
    onTertiaryContainer = SuzuWarnDeepDark,

    error = SuzuDangerDark,
    onError = SuzuPearlDark,
    errorContainer = SuzuDangerBgDark,
    onErrorContainer = SuzuDangerDark,

    background = SuzuPearlDark,
    onBackground = SuzuInkDark,
    surface = SuzuPaperDark,
    onSurface = SuzuInkDark,
    surfaceVariant = SuzuPearlDark,
    onSurfaceVariant = SuzuInkSubDark,

    outline = SuzuInkMuteDark,
    outlineVariant = SuzuHairDark
)

// TomoshibiTheme — App 顶层 wrap，注入 Material3 + Suzu 専用 token
// 用法：setContent { TomoshibiTheme(darkTheme = userPref) { App() } }
@Composable
fun TomoshibiTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) SuzuDarkColorScheme else SuzuLightColorScheme
    val suzuTokens = if (darkTheme) darkSuzuTokens() else lightSuzuTokens()

    CompositionLocalProvider(LocalSuzuTokens provides suzuTokens) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = TomoshibiTypography,
            content = content
        )
    }
}
