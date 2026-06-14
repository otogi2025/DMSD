package jp.tomoshibi.android.ui.theme

import androidx.compose.ui.unit.dp

// Suzu 尺寸常量 — 对齐 iOS TTokens.swift 的 T.Radius / T.Space 两个嵌套枚举
// iOS 真值：Radius(xs8 sm12 md16 lg22 pill9999) / Space(4/8/12/16/24/32)
// pill 圆角在 Compose 用 RoundedCornerShape(percent = 50) 表达（高度方向全圆 = Capsule），
// 这里只放 dp 数值常量；各组件按需引用。
object SuzuDim {
    // 圆角 Radius（单位 dp）
    val radiusXs = 8.dp // 最小圆角
    val radiusSm = 12.dp // 输入框 TField / textarea
    val radiusMd = 16.dp // 卡片 Card 默认 / 按钮 / RadioCard
    val radiusLg = 22.dp // GlassCard 默认

    // 间距 Space（单位 dp）
    val spaceXs = 4.dp
    val spaceSm = 8.dp
    val spaceMd = 12.dp
    val spaceLg = 16.dp
    val spaceXl = 24.dp
    val spaceXxl = 32.dp
}
