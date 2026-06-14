package jp.tomoshibi.android.ui.components

import android.widget.Toast
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import java.time.LocalTime
import java.time.format.DateTimeFormatter

// ───────────────────────────────────────────────────────────────
// StudyCheckinSheet — 晚自习 NFC「2 次签到」弹窗
// 对齐 iOS Foundation/Features/Home/HomeStubs.swift 的 StudyCheckinSheet（simulate() 行 1805）。
// 规格真值：内部对齐规格 第 2978–3003 行（③ 学習 NFC 2 次签到）。
//
// 机制：一次晚自习要碰 NFC 2 次 —— 学習開始（受付 19:35–19:40）+ 学習終了（受付 21:40–21:50）。
// 本文件用本地变量 tapIndex（1=开始 / 2=结束）演示「这是第几次签到」，每开一次只走一次签到。
// 状态机 4 步 idle → scanning → success → fail，跟 RollCallSheet 同一套写法。
// 本波纯 UI + 动画 mock —— 不真碰 NFC、不发网络、不写本地状态库。
// ───────────────────────────────────────────────────────────────

// 4 步状态机（对齐 iOS idle/scanning/success/fail）— RollCallSheet 共用同一套，故 internal
internal enum class Step { Idle, Scanning, Success, Fail }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StudyCheckinSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current
    val ctx = LocalContext.current
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    // 当前在哪一步（默认从 idle 开始）
    var step by remember { mutableStateOf(Step.Idle) }
    // 这是本次晚自习的第几次签到 —— 1=学習開始 / 2=学習終了
    // 真实装时应由后端 / 本地状态库的「下一次未完成 tap」决定（对齐 iOS app.nextStudyTap），
    // 本波 mock 固定从 1 开始。
    var tapIndex by remember { mutableStateOf(1) }

    // 当前是第 1 次还是第 2 次签到的派生文案（随 tapIndex 变）
    val isStart = tapIndex == 1
    val tapName = if (isStart) "学習開始" else "学習終了" // 这次签到的中性名（用在 toast / success 跳转语）
    val timeWindow = if (isStart) "19:35〜19:40" else "21:40〜21:50" // 受付窗口

    // scanning 步：等 0.5 秒模拟扫卡完成 → success（对齐 iOS simulate() 0.5s 延时）
    LaunchedEffect(step) {
        if (step == Step.Scanning) {
            kotlinx.coroutines.delay(500)
            // 真后端 recordStudyTap：此处应调写库 ——
            // TODO 真实装：往 studyTaps 集合插入当前 tap（start/end）+ 往 studyHistory 插一条记录，
            //   对齐 iOS app.recordStudyTap()。本波 mock 直接进 success，不写任何状态。
            step = Step.Success
        }
    }

    // success 步：停 2 秒 → 关窗 + toast（对齐 iOS simulate() 2s 后 closeSheet + Toast）
    LaunchedEffect(step) {
        if (step == Step.Success) {
            kotlinx.coroutines.delay(2000)
            // 全 2 次都做完（这次是第 2 次）→ 整段完成 toast，否则只报这一次完成
            val toastText =
                if (tapIndex == 2) {
                    "学習出席完了 · 全 2 回 タップ済み"
                } else {
                    "$tapName 完了"
                }
            Toast.makeText(ctx, toastText, Toast.LENGTH_SHORT).show()
            onDismiss()
        }
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = t.paper,
        scrimColor = Color.Black.copy(alpha = 0.32f),
        dragHandle = {
            Box(
                modifier =
                    Modifier
                        .padding(top = 10.dp, bottom = 16.dp)
                        .size(width = 40.dp, height = 5.dp)
                        .clip(CircleShape)
                        .background(t.inkFaint),
            )
        },
    ) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
                    .padding(bottom = 28.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            when (step) {
                Step.Idle -> {
                    IdleBody(
                        tapIndex = tapIndex,
                        isStart = isStart,
                        timeWindow = timeWindow,
                        onScan = { step = Step.Scanning },
                        onCancel = onDismiss,
                    )
                }

                Step.Scanning -> {
                    ScanningBody()
                }

                Step.Success -> {
                    SuccessBody(tapIndex = tapIndex, isStart = isStart)
                }

                Step.Fail -> {
                    FailBody(onRetry = { step = Step.Idle })
                }
            }
        }
    }
}

// ── Step 1 · idle ───────────────────────────────────────────────
// 顶部小标号「{N} / 2 回目」+ 大标题 + 受付时间 pill + 两步说明 + 脉冲圆 + 主按钮 + 取消
@Composable
private fun IdleBody(
    tapIndex: Int,
    isStart: Boolean,
    timeWindow: String,
    onScan: () -> Unit,
    onCancel: () -> Unit,
) {
    val t = SuzuT.current

    // ① 小标号「{N} / 2 回目」（primary 色 11sp 加宽大写感）
    Text(
        text = "$tapIndex / 2 回目",
        color = MaterialTheme.colorScheme.primary,
        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Black, letterSpacing = 1.8.sp),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(6.dp))

    // ② 大标题 —— 第 1 次=学習開始のタップ / 第 2 次=学習終了のタップ
    Text(
        text = if (isStart) "学習開始のタップ" else "学習終了のタップ",
        color = t.ink,
        style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Black),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(12.dp))

    // ③ 受付时间 pill（pill 底圆角 10 + 时钟图标 +「受付時間: {窗口}」）
    Row(
        modifier =
            Modifier
                .clip(RoundedCornerShape(10.dp))
                .background(t.pill)
                .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Icon(
            imageVector = SuzuIcons.CalClock,
            contentDescription = null,
            tint = t.inkSub,
            modifier = Modifier.size(14.dp),
        )
        Text(
            text = "受付時間: $timeWindow",
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
        )
    }

    Spacer(Modifier.height(18.dp))

    // ④ 两步说明（左对齐在容器中央）
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.Start,
    ) {
        Text(
            text = "① 学習室入口の NFC マークにスマホをかざす",
            color = t.inkSub,
            style = TextStyle(fontSize = 14.sp, lineHeight = 21.sp),
        )
        Text(
            text = "② 画面が光ったら完了",
            color = t.inkSub,
            style = TextStyle(fontSize = 14.sp, lineHeight = 21.sp),
        )
    }

    Spacer(Modifier.height(22.dp))

    // ⑤ 脉冲圆动画（140dp，一圈淡圆持续放大淡出 + 中心实心圆 + NFC 图标）
    PulseCircle()

    Spacer(Modifier.height(24.dp))

    // ⑥ 主按钮「NFC をかざす」→ 切 scanning
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(54.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(t.btnGrad)
                .clickable { onScan() },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = "NFC をかざす",
            color = Color.White,
            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
        )
    }

    Spacer(Modifier.height(8.dp))

    // ⑦ 取消按钮「キャンセル」（无 border 的 ghost 文字按钮）
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(48.dp)
                .clickable { onCancel() },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = "キャンセル",
            color = t.inkSub,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
        )
    }
}

// ── Step 2 · scanning（与 RollCallSheet 一致：「スキャン中…」+ 旋转环 +「動かないでください」）──
@Composable
internal fun ScanningBody() {
    val t = SuzuT.current

    Spacer(Modifier.height(8.dp))

    // 标题「スキャン中…」
    Text(
        text = "スキャン中…",
        color = t.ink,
        style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(28.dp))

    // 旋转环 Canvas（一段弧无限旋转一圈）
    SpinnerRing()

    Spacer(Modifier.height(28.dp))

    // 副文案「動かないでください」
    Text(
        text = "動かないでください",
        color = t.inkSub,
        style = TextStyle(fontSize = 14.sp),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(8.dp))
}

// ── Step 3 · success ────────────────────────────────────────────
// 绿圆 pop-in + checkmark + 标题 + 下方（还有下一次=文字提示 / 全完成=绿胶囊 pill）
@Composable
private fun SuccessBody(
    tapIndex: Int,
    isStart: Boolean,
) {
    val t = SuzuT.current

    // pop-in 弹入动画：进入瞬间从 0.6 弹到 1.0（spring 带回弹）
    var popped by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (popped) 1f else 0.6f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
        label = "successPop",
    )
    LaunchedEffect(Unit) { popped = true }

    Spacer(Modifier.height(8.dp))

    // 96dp 绿圆 + 内白 checkmark（整体套 pop-in scale）
    Box(
        modifier =
            Modifier
                .size(96.dp)
                .scale(scale)
                .clip(CircleShape)
                .background(t.okDeep),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            imageVector = SuzuIcons.Check,
            contentDescription = null,
            tint = Color.White,
            modifier = Modifier.size(52.dp),
        )
    }

    Spacer(Modifier.height(20.dp))

    // 标题 —— 第 1 次完成=開始タップ完了 / 第 2 次完成=終了タップ完了
    Text(
        text = if (isStart) "開始タップ完了" else "終了タップ完了",
        color = t.ink,
        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(12.dp))

    // 下方分两种：还有下一次 → 文字提示；全部完成 → 绿胶囊 pill
    if (tapIndex == 1) {
        // 第 1 次完成 → 提示下次什么时候来碰第 2 次
        Text(
            text = "次は 学習終了 を 21:40〜21:50 に",
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp),
            textAlign = TextAlign.Center,
        )
    } else {
        // 第 2 次完成 → 整段学習出席完成，绿胶囊报当前时刻
        val now = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm"))
        Row(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(999.dp))
                    .background(t.okBg)
                    .padding(horizontal = 16.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "$now · 本日の学習出席は完了",
                color = t.okDeep,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
            )
        }
    }

    Spacer(Modifier.height(8.dp))
}

// ── Step 4 · fail（与 RollCallSheet 一致：「失敗。もう一度」+ 失败说明 +「再試行」→ idle）──
@Composable
internal fun FailBody(onRetry: () -> Unit) {
    val t = SuzuT.current

    Spacer(Modifier.height(8.dp))

    // 失败大标题（用 warn 系颜色）
    Text(
        text = "失敗。もう一度",
        color = t.warnDeep,
        style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(12.dp))

    // 失败说明
    Text(
        text = "NFC を読み取れませんでした",
        color = t.inkSub,
        style = TextStyle(fontSize = 14.sp),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(24.dp))

    // 「再試行」按钮 → 回到 idle 重来
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(54.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(t.btnGrad)
                .clickable { onRetry() },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = "再試行",
            color = Color.White,
            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
        )
    }

    Spacer(Modifier.height(8.dp))
}

// ── 脉冲圆（idle 步用）────────────────────────────────────────────
// 一圈淡色圆持续放大 + 淡出，中心是实心圆 + NFC 图标。整体 140dp。
@Composable
internal fun PulseCircle() {
    val t = SuzuT.current
    // 无限循环动画：0→1 往复，驱动外圈的缩放 + 透明度
    val transition = rememberInfiniteTransition(label = "pulse")
    val progress by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec =
            infiniteRepeatable(
                animation = tween(durationMillis = 1400, easing = LinearEasing),
                repeatMode = RepeatMode.Restart,
            ),
        label = "pulseProgress",
    )

    Box(
        modifier = Modifier.size(140.dp),
        contentAlignment = Alignment.Center,
    ) {
        // 外圈脉冲：随 progress 从 90dp 放大到 140dp，同时透明度 0.35 → 0 淡出
        val ringSize = (90 + 50 * progress).dp
        val ringAlpha = 0.35f * (1f - progress)
        Box(
            modifier =
                Modifier
                    .size(ringSize)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primary.copy(alpha = ringAlpha)),
        )
        // 中心实心圆（pill 底）+ NFC 图标
        Box(
            modifier =
                Modifier
                    .size(90.dp)
                    .clip(CircleShape)
                    .background(t.pill),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = SuzuIcons.PhoneNfc,
                contentDescription = "NFC scan",
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(48.dp),
            )
        }
    }
}

// ── 旋转环（scanning 步用）────────────────────────────────────────
// Canvas 画一段 270° 弧，无限旋转一整圈，做「扫描中」的转圈视觉。整体 120dp。
@Composable
internal fun SpinnerRing() {
    val transition = rememberInfiniteTransition(label = "spinner")
    // 旋转角度 0 → 360 无限循环
    val angle by transition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec =
            infiniteRepeatable(
                animation = tween(durationMillis = 1000, easing = LinearEasing),
                repeatMode = RepeatMode.Restart,
            ),
        label = "spinnerAngle",
    )
    val arcColor = MaterialTheme.colorScheme.primary
    val trackColor = SuzuT.current.pill

    androidx.compose.foundation.Canvas(modifier = Modifier.size(120.dp)) {
        val stroke = 6.dp.toPx()
        // 底轨（整圈淡色）
        drawCircle(
            color = trackColor,
            radius = (size.minDimension - stroke) / 2f,
            center = Offset(size.width / 2f, size.height / 2f),
            style = Stroke(width = stroke),
        )
        // 旋转的那段弧（270° 实色，随 angle 转）
        drawArc(
            color = arcColor,
            startAngle = angle,
            sweepAngle = 270f,
            useCenter = false,
            topLeft = Offset(stroke / 2f, stroke / 2f),
            size =
                androidx.compose.ui.geometry
                    .Size(size.width - stroke, size.height - stroke),
            style = Stroke(width = stroke, cap = StrokeCap.Round),
        )
    }
}
