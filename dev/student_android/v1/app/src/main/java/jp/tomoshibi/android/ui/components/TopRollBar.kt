package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import jp.tomoshibi.android.ui.theme.SuzuTokens

// 对齐 iOS HomeStubs.swift pointsCard 四态（idle / active / absent / done）。
// 夜学習 study 模式（HomeStubs 319-576）标 DEMO-ONLY，本组件不移植。
//
// 点呼操作按钮（欠席申請 / 体調報告）只开 UI 弹窗；真点呼提交归 B07。

private val DeepBrown = Color(0xFF5C3410)
private val CleaningOrange = Color(0xFFB07A28)
private val AbsentGrad =
    Brush.linearGradient(
        colorStops =
            arrayOf(
                0.0f to Color(0xFFFFD6D0),
                0.55f to Color(0xFFEF6A58),
                1.0f to Color(0xFFC83B29),
            ),
    )

@Composable
fun TopRollBar(
    navController: NavHostController,
    deductionTotal: Double,
    late: Int,
    absent: Int,
    needsCleaning: Boolean,
    rollState: RollState,
    countdownSec: Int,
    checkinAt: String?,
    checkinKind: String?,
    onAbsenceClick: () -> Unit,
    onHealthClick: () -> Unit,
    onContactSupervisor: () -> Unit,
) {
    val t = SuzuT.current
    val cardBrush = if (rollState == RollState.ABSENT) AbsentGrad else t.amberGrad

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(22.dp))
                .background(cardBrush)
                .padding(horizontal = 22.dp, vertical = 20.dp),
    ) {
        when (rollState) {
            RollState.IDLE -> {
                IdleContent(
                    deductionTotal = deductionTotal,
                    late = late,
                    absent = absent,
                    needsCleaning = needsCleaning,
                    onDetail = { navController.navigate(Route.MyPoints.path) },
                    t = t,
                )
            }

            RollState.ACTIVE, RollState.ABSENT, RollState.DONE -> {
                RollActiveContent(
                    deductionTotal = deductionTotal,
                    rollState = rollState,
                    countdownSec = countdownSec,
                    checkinAt = checkinAt,
                    checkinKind = checkinKind,
                    onDetail = { navController.navigate(Route.MyPoints.path) },
                    onAbsenceClick = onAbsenceClick,
                    onHealthClick = onHealthClick,
                    onContactSupervisor = onContactSupervisor,
                    t = t,
                )
            }
        }
    }
}

@Composable
private fun IdleContent(
    deductionTotal: Double,
    late: Int,
    absent: Int,
    needsCleaning: Boolean,
    onDetail: () -> Unit,
    t: SuzuTokens,
) {
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clickable(onClick = onDetail),
    ) {
        Row(verticalAlignment = Alignment.Top) {
            Text(
                text = "今月の減点",
                color = DeepBrown.copy(alpha = 0.8f),
                style =
                    TextStyle(
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.98.sp,
                    ),
                modifier = Modifier.weight(1f),
            )
            // IDLE 专用 pill（仅在 RollState.IDLE 分支进入本函数）
            PointsPill()
        }
        Spacer(Modifier.height(6.dp))
        Row(verticalAlignment = Alignment.Bottom) {
            Text(
                text = "%.1f".format(deductionTotal),
                color = DeepBrown,
                style =
                    TextStyle(
                        fontSize = 56.sp,
                        fontWeight = FontWeight.Black,
                        fontFamily = FontFamily.Monospace,
                        lineHeight = 60.sp,
                    ),
            )
            Spacer(Modifier.width(6.dp))
            Text(
                text = "点",
                color = DeepBrown.copy(alpha = 0.75f),
                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.padding(bottom = 10.dp),
            )
        }
        Spacer(Modifier.height(12.dp))
        CleaningFlagRow(points = deductionTotal, needsCleaning = needsCleaning)
        ProgressWithMarkers(value = deductionTotal, max = 8.0)
        Spacer(Modifier.height(5.dp))
        Row(modifier = Modifier.fillMaxWidth()) {
            Text(
                "0",
                color = DeepBrown.copy(alpha = 0.7f),
                style = TextStyle(fontSize = 10.sp, fontFamily = FontFamily.Monospace),
                modifier = Modifier.weight(1f),
            )
            Text(
                "4 · 清掃",
                color = DeepBrown.copy(alpha = 0.7f),
                style = TextStyle(fontSize = 10.sp, fontFamily = FontFamily.Monospace),
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.Center,
            )
            Text(
                "8 · 外出禁止",
                color = DeepBrown.copy(alpha = 0.7f),
                style = TextStyle(fontSize = 10.sp, fontFamily = FontFamily.Monospace),
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.End,
            )
        }
        Spacer(Modifier.height(12.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = "遅刻 $late 回 · 欠席 $absent 回",
                color = DeepBrown.copy(alpha = 0.85f),
                style = TextStyle(fontSize = 12.sp),
                modifier = Modifier.weight(1f),
            )
            Text(
                text = "詳細",
                color = DeepBrown,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
            )
            Icon(
                imageVector = SuzuIcons.ChevR,
                contentDescription = null,
                tint = DeepBrown,
                modifier = Modifier.size(14.dp),
            )
        }
    }
}

@Composable
private fun RollActiveContent(
    deductionTotal: Double,
    rollState: RollState,
    countdownSec: Int,
    checkinAt: String?,
    checkinKind: String?,
    onDetail: () -> Unit,
    onAbsenceClick: () -> Unit,
    onHealthClick: () -> Unit,
    onContactSupervisor: () -> Unit,
    t: SuzuTokens,
) {
    val isAbsent = rollState == RollState.ABSENT
    val labelColor = if (isAbsent) Color.White.copy(alpha = 0.9f) else DeepBrown.copy(alpha = 0.8f)
    val valueColor = if (isAbsent) Color.White else DeepBrown
    val chevColor = if (isAbsent) Color.White.copy(alpha = 0.9f) else DeepBrown.copy(alpha = 0.85f)

    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clickable(onClick = onDetail),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text(
                text = "今月の減点",
                color = labelColor,
                style =
                    TextStyle(
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.98.sp,
                    ),
            )
            Text(
                text = "%.1f 点".format(deductionTotal),
                color = valueColor,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
            )
            Spacer(modifier = Modifier.weight(1f))
            Text(
                text = "詳細",
                color = chevColor,
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
            )
            Icon(
                imageVector = SuzuIcons.ChevR,
                contentDescription = null,
                tint = chevColor,
                modifier = Modifier.size(12.dp),
            )
        }
        Spacer(Modifier.height(10.dp))
        HeroStatus(
            rollState = rollState,
            countdownSec = countdownSec,
            checkinAt = checkinAt,
            checkinKind = checkinKind,
            t = t,
        )
        Spacer(Modifier.height(14.dp))
        if (isAbsent) {
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(Color.White)
                        .clickable(onClick = onContactSupervisor)
                        .padding(vertical = 12.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    imageVector = SuzuIcons.Phone,
                    contentDescription = null,
                    tint = t.danger,
                    modifier = Modifier.size(15.dp),
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = "寮監に連絡",
                    color = t.danger,
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                )
            }
        } else {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                RollActionButton(
                    label = "欠席申請",
                    onClick = onAbsenceClick,
                    modifier = Modifier.weight(1f),
                )
                RollActionButton(
                    label = "体調報告",
                    onClick = onHealthClick,
                    modifier = Modifier.weight(1f),
                )
            }
        }
    }
}

@Composable
private fun HeroStatus(
    rollState: RollState,
    countdownSec: Int,
    checkinAt: String?,
    checkinKind: String?,
    t: SuzuTokens,
) {
    when (rollState) {
        RollState.ACTIVE -> {
            if (countdownSec <= 0) {
                HeroBlock(
                    caption = "今回の点呼",
                    big = "遅刻",
                    sub = "欠席申請または体調報告で、判定の見直しを申請できます",
                    bigColor = t.danger,
                    captionColor = DeepBrown.copy(alpha = 0.7f),
                    subColor = DeepBrown.copy(alpha = 0.8f),
                )
            } else {
                val m = countdownSec / 60
                val s = countdownSec % 60
                HeroBlock(
                    caption = "点呼中 · 残り",
                    big = "%d:%02d".format(m, s),
                    sub = "NFC にタッチしてチェックイン",
                    bigColor = DeepBrown,
                    captionColor = DeepBrown.copy(alpha = 0.7f),
                    subColor = DeepBrown.copy(alpha = 0.8f),
                    bigMonospaced = true,
                )
            }
        }

        RollState.ABSENT -> {
            HeroBlock(
                caption = "欠席判定・要連絡",
                big = "欠席",
                sub = "寮監室まで直接お越しください",
                bigColor = Color.White,
                captionColor = Color.White.copy(alpha = 0.9f),
                subColor = Color.White.copy(alpha = 0.95f),
            )
        }

        RollState.DONE -> {
            // 契约收口（对齐 iOS Home 英雄卡）：exempt 无签到时刻→隐藏占位、default 不兜底「時間内」
            val isLate = checkinKind == "遅刻"
            val isExempt = checkinKind == "免除"
            HeroBlock(
                caption = if (isExempt) "" else (checkinAt ?: "--:--"),
                big = checkinKind ?: "記録あり",
                sub = if (isExempt) "本日は点呼免除です" else "今回の点呼は完了しました",
                bigColor = if (isLate) t.danger else Color(0xFF2C6048),
                captionColor = DeepBrown.copy(alpha = 0.7f),
                subColor = DeepBrown.copy(alpha = 0.8f),
            )
        }

        RollState.IDLE -> {
            Unit
        }
    }
}

@Composable
private fun HeroBlock(
    caption: String,
    big: String,
    sub: String,
    bigColor: Color,
    captionColor: Color,
    subColor: Color,
    bigMonospaced: Boolean = false,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(caption, color = captionColor, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold))
        Text(
            text = big,
            color = bigColor,
            style =
                TextStyle(
                    fontSize = 44.sp,
                    fontWeight = FontWeight.Black,
                    fontFamily = if (bigMonospaced) FontFamily.Monospace else FontFamily.Default,
                ),
        )
        Text(sub, color = subColor, style = TextStyle(fontSize = 12.sp))
    }
}

@Composable
private fun RollActionButton(
    label: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier =
            modifier
                .height(40.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(Color.White.copy(alpha = 0.55f))
                .border(1.dp, Color.White.copy(alpha = 0.7f), RoundedCornerShape(12.dp))
                .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = label,
            color = DeepBrown,
            style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}

/** 右上点呼状态 pill —— 仅 IdleContent（RollState.IDLE）使用。 */
@Composable
private fun PointsPill() {
    Box(
        modifier =
            Modifier
                .clip(RoundedCornerShape(99.dp))
                .background(Color.White.copy(alpha = 0.45f))
                .padding(horizontal = 10.dp, vertical = 3.dp),
    ) {
        Text(
            "点呼開始前",
            color = DeepBrown,
            style = TextStyle(fontSize = 11.5.sp, fontWeight = FontWeight.Bold),
        )
    }
}

/** 罰則清掃三档：<4 隐藏 / 4-7 橙 / ≥8 红。 */
@Composable
private fun CleaningFlagRow(
    points: Double,
    needsCleaning: Boolean,
) {
    when {
        points >= 8.0 -> {
            CleaningFlagLabel(icon = SuzuIcons.Warn, text = "外出禁止", tint = Color(0xFFC44848))
            Spacer(Modifier.height(12.dp))
        }

        needsCleaning || points >= 4.0 -> {
            CleaningFlagLabel(icon = SuzuIcons.Sparkles, text = "罰則清掃 対象", tint = CleaningOrange)
            Spacer(Modifier.height(12.dp))
        }
    }
}

@Composable
private fun CleaningFlagLabel(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    text: String,
    tint: Color,
) {
    Row(
        modifier =
            Modifier
                .clip(RoundedCornerShape(99.dp))
                .background(Color.White.copy(alpha = 0.5f))
                .padding(horizontal = 10.dp, vertical = 5.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Icon(imageVector = icon, contentDescription = null, tint = tint, modifier = Modifier.size(12.dp))
        Text(text, color = tint, style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.Bold))
    }
}

@Composable
private fun ProgressWithMarkers(
    value: Double,
    max: Double,
) {
    val ratio = (value / max).coerceIn(0.0, 1.0).toFloat()
    Canvas(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(12.dp),
    ) {
        val w = size.width
        val barH = 8.dp.toPx()
        val top = (size.height - barH) / 2
        drawRoundRect(
            color = Color.White.copy(alpha = 0.4f),
            topLeft = Offset(0f, top),
            size = Size(w, barH),
            cornerRadius = CornerRadius(4.dp.toPx(), 4.dp.toPx()),
        )
        drawRoundRect(
            brush =
                Brush.horizontalGradient(
                    colors = listOf(Color(0xFFD99F3E), Color(0xFFB07A28)),
                ),
            topLeft = Offset(0f, top),
            size = Size(w * ratio, barH),
            cornerRadius = CornerRadius(4.dp.toPx(), 4.dp.toPx()),
        )
        // 4 点 / 8 点阈值竖标
        drawRect(
            color = DeepBrown.copy(alpha = 0.4f),
            topLeft = Offset(w * 0.5f - 1.dp.toPx(), 0f),
            size = Size(2.dp.toPx(), size.height),
        )
        drawRect(
            color = DeepBrown.copy(alpha = 0.4f),
            topLeft = Offset(w - 2.dp.toPx(), 0f),
            size = Size(2.dp.toPx(), size.height),
        )
    }
}
