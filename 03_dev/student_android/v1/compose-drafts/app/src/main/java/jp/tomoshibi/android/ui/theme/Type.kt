package jp.tomoshibi.android.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// 日语优先字体栈 — 对应 iOS Hiragino Sans / Noto Sans JP
// 实际字体文件需要后续放进 res/font/ 并在 fontFamilies 里 reference
// 现在先用 SansSerif fallback，等 Android Studio 工程建好后接入 Noto Sans JP
val NotoSansJp: FontFamily = FontFamily.SansSerif // TODO: 接入 Noto Sans JP CJK 字体文件
val RobotoMono: FontFamily = FontFamily.Monospace // 数字用（减点 4.5 / 时间 09:20）

// Material 3 Typography — 12 个 type role
// 数值参照 React tokens.jsx + iOS 系统体感 (display 大号，body 16sp，caption 12sp)
val TomoshibiTypography = Typography(
    // Display — splash logo 灯字、大号 hero 数字
    displayLarge = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Light,
        fontSize = 96.sp,
        lineHeight = 100.sp
    ),
    displayMedium = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Light,
        fontSize = 72.sp,
        lineHeight = 76.sp
    ),
    displaySmall = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Normal,
        fontSize = 48.sp,
        lineHeight = 52.sp
    ),

    // Headline — 屏幕标题
    headlineLarge = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp,
        lineHeight = 36.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 32.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp
    ),

    // Title — section / card 标题
    titleLarge = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 24.sp
    ),
    titleMedium = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 22.sp
    ),
    titleSmall = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),

    // Body — 正文
    bodyLarge = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.15.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.25.sp
    ),
    bodySmall = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp
    ),

    // Label — button / chip 文字
    labelLarge = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.SemiBold,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    labelMedium = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp
    ),
    labelSmall = TextStyle(
        fontFamily = NotoSansJp,
        fontWeight = FontWeight.Medium,
        fontSize = 10.sp,
        lineHeight = 14.sp
    )
)

// 数字专用样式（Roboto Mono，用于减点 4.5、bus time 09:20、account No 060218）
val MonoNumeralStyle = TextStyle(
    fontFamily = RobotoMono,
    fontWeight = FontWeight.SemiBold,
    fontSize = 56.sp,
    lineHeight = 64.sp
)
