package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT

// 対齐 iOS HomeStubs.swift TopRollBar (IDLE 简版):
//   ┌──────────────────────────────────────┐
//   │ 今月の減点              外出禁止 pill │
//   │                                      │
//   │   4.5 点  (大数字 hero)              │
//   │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
//   │   0              8・外出禁止     │
//   │                                      │
//   │ 遅刻 5 回 ・ 欠席 2 回      詳細 →   │
//   └──────────────────────────────────────┘
//
// API 契約:
//   deductionTotal: 当前月减点（用于大数字 + progress 填充）
//   late: 迟到次数 / absent: 缺席次数 (Home 计算后传入)
@Composable
fun TopRollBar(
    navController: NavHostController,
    deductionTotal: Double,
    late: Int = 5,
    absent: Int = 2,
) {
    val t = SuzuT.current
    val banThreshold = 8.0 // ≥8 → 外出禁止

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(22.dp))
                .background(t.amberGrad)
                .clickable { navController.navigate(Route.Deduction.path) }
                .padding(horizontal = 20.dp, vertical = 18.dp),
    ) {
        // 第 1 行：「今月の減点」 + pill「外出禁止 / 良好」
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = "今月の減点",
                color = t.inkSub,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
            )
            val (pillLabel, pillBg, pillFg) =
                when {
                    deductionTotal >= banThreshold -> Triple("外出禁止", t.dangerBg, t.danger)
                    else -> Triple("良好", t.okBg, t.okDeep)
                }
            Box(
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(99.dp))
                        .background(pillBg)
                        .padding(horizontal = 10.dp, vertical = 4.dp),
            ) {
                Text(
                    text = pillLabel,
                    color = pillFg,
                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
        Spacer(Modifier.height(6.dp))

        // 第 2 行：大数字 hero「4.5 点」
        Row(verticalAlignment = Alignment.Bottom) {
            Text(
                text = "%.1f".format(deductionTotal),
                color = t.ink,
                style =
                    TextStyle(
                        fontSize = 56.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Default,
                        lineHeight = 60.sp,
                    ),
            )
            Spacer(Modifier.width(4.dp))
            Text(
                text = "点",
                color = t.ink,
                style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.padding(bottom = 10.dp),
            )
        }
        Spacer(Modifier.height(10.dp))

        // 第 3 行：progress bar with 0 / 8·外出禁止 marker
        ProgressWithMarkers(
            value = deductionTotal,
            max = 8.0,
            banAt = banThreshold,
            t = t,
        )
        Spacer(Modifier.height(4.dp))
        Row(modifier = Modifier.fillMaxWidth()) {
            Text(
                "0",
                color = t.inkMute,
                style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
            )
            Text(
                "8・外出禁止",
                color = t.inkMute,
                style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
                textAlign = androidx.compose.ui.text.style.TextAlign.End,
            )
        }
        Spacer(Modifier.height(10.dp))

        // 第 4 行：「遅刻 5 回・欠席 2 回」 + 詳細 →
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = "遅刻 $late 回 ・ 欠席 $absent 回",
                color = t.ink,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
            )
            Text(
                text = "詳細 →",
                color = t.ink,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
            )
        }
    }
}

// 自绘 progress bar with 8 dot marker (跟 iOS shape：浅色背景 capsule + 深色填充段 + 白点 marker)
@Composable
private fun ProgressWithMarkers(
    value: Double,
    max: Double,
    banAt: Double,
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
) {
    val ratio = (value / max).coerceIn(0.0, 1.0).toFloat()
    val banRatio = (banAt / max).coerceAtMost(1.0).toFloat()

    Canvas(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(8.dp),
    ) {
        val w = size.width
        val h = size.height
        val r = h / 2
        // 背景 capsule
        drawRoundRect(
            color = Color.White.copy(alpha = 0.5f),
            cornerRadius =
                androidx.compose.ui.geometry
                    .CornerRadius(r, r),
        )
        // 填充
        drawRoundRect(
            color = t.warnDeep,
            size =
                androidx.compose.ui.geometry
                    .Size(w * ratio, h),
            cornerRadius =
                androidx.compose.ui.geometry
                    .CornerRadius(r, r),
        )
        // marker dot 8 (ban threshold)
        if (banRatio < 1.0f) {
            drawCircle(
                color = Color.White,
                radius = 2.dp.toPx(),
                center = Offset(w * banRatio, h / 2),
            )
        }
    }
}
