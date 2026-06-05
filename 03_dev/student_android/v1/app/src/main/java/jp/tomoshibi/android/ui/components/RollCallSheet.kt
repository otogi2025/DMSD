package jp.tomoshibi.android.ui.components

import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import java.time.LocalTime
import java.time.format.DateTimeFormatter

// 点呼扫卡 sheet — 完全对齐 iOS RollcallSheet (HomeStubs.swift §1136)
//
// 视觉结构（顶 → 底）:
//   ① drag handle (36×4dp)
//   ② 标题「スキャンの準備ができました」18sp Bold
//   ③ 操作说明 2 行：① 入口の NFC マークにスマホをかざす / ② 画面が光ったら完了
//   ④ amber 警告 pill「点呼時間外です。点呼開始まで少々お待ちください。」
//   ⑤ 大圆 NFC 视觉（180dp accentSoft 圆 + 内 100dp PhoneNfc icon primary）
//   ⑥ NFC をかざす CTA (52dp btnGrad)
//   ⑦ キャンセル text button（不再是 border button — iOS 风格）
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RollCallSheet(onDismiss: () -> Unit) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    // 4 步状态机（idle → scanning → success → fail），共用 StudyCheckinSheet 的 Step + 动画件
    var step by remember { mutableStateOf(Step.Idle) }
    // 本次签到时刻（success 步显示 + 写库用）
    var checkinTime by remember { mutableStateOf("") }

    // scanning：等 0.5 秒模拟扫卡完成 → 写 rollState=DONE + checkinAt → success（对齐 iOS simulate() 0.5s）
    LaunchedEffect(step) {
        if (step == Step.Scanning) {
            kotlinx.coroutines.delay(500)
            val now = LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm"))
            checkinTime = now
            store.update { it.copy(rollState = RollState.DONE, checkinAt = now) }
            step = Step.Success
        }
    }
    // success：停 2 秒 → 自动关窗（对齐 iOS simulate() 2s 后 closeSheet）
    LaunchedEffect(step) {
        if (step == Step.Success) {
            kotlinx.coroutines.delay(2000)
            onDismiss()
        }
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = tokens.paper,
        scrimColor = Color.Black.copy(alpha = 0.32f),
        dragHandle = {
            Box(
                modifier =
                    Modifier
                        .padding(top = 10.dp, bottom = 16.dp)
                        .size(width = 40.dp, height = 5.dp)
                        .clip(CircleShape)
                        .background(tokens.inkFaint),
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
                    // ② 标题
                    Text(
                        text = "スキャンの準備ができました",
                        color = tokens.ink,
                        style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
                        textAlign = TextAlign.Center,
                    )

                    Spacer(Modifier.height(14.dp))

                    // ③ 操作说明 2 行（左对齐 in 容器中央）
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.Start,
                    ) {
                        Text(
                            text = "① 入口の NFC マークにスマホをかざす",
                            color = tokens.inkSub,
                            style = TextStyle(fontSize = 13.sp, lineHeight = 20.sp),
                        )
                        Text(
                            text = "② 画面が光ったら完了",
                            color = tokens.inkSub,
                            style = TextStyle(fontSize = 13.sp, lineHeight = 20.sp),
                        )
                    }

                    Spacer(Modifier.height(16.dp))

                    // ④ amber 警告 pill「点呼時間外です」
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(tokens.warnBg)
                                .border(1.dp, tokens.warn.copy(alpha = 0.25f), RoundedCornerShape(12.dp))
                                .padding(horizontal = 14.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            "⚠",
                            color = tokens.warnDeep,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                        )
                        Text(
                            text = "点呼時間外です。点呼開始まで少々お待ちください。",
                            color = tokens.warnDeep,
                            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
                        )
                    }

                    Spacer(Modifier.height(28.dp))

                    // ⑤ 脉冲圆动画（复用 StudyCheckinSheet 的 PulseCircle，对齐 iOS idle 脉冲）
                    PulseCircle()

                    Spacer(Modifier.height(28.dp))

                    // ⑥ NFC をかざす CTA（demo 实际触发模拟扫描完成）
                    Box(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(54.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(tokens.btnGrad)
                                .clickable { step = Step.Scanning },
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "NFC をかざす",
                            color = Color.White,
                            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                        )
                    }

                    Spacer(Modifier.height(8.dp))

                    // ⑦ キャンセル ghost text button (无 border)
                    Box(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(48.dp)
                                .clickable { onDismiss() },
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "キャンセル",
                            color = tokens.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
                        )
                    }
                }

                Step.Scanning -> {
                    ScanningBody()
                }

                Step.Success -> {
                    RollSuccessBody(checkinTime)
                }

                Step.Fail -> {
                    FailBody(onRetry = { step = Step.Idle })
                }
            }
        }
    }
}

// ── Step 3 · success（点呼专属：绿圆 pop-in +「チェックイン完了」+ 时刻 pill +「お疲れさまでした」）──
@Composable
private fun RollSuccessBody(checkinAt: String) {
    val t = SuzuT.current

    // pop-in 弹入：进入瞬间从 0.6 弹到 1.0
    var popped by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (popped) 1f else 0.6f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
        label = "rollSuccessPop",
    )
    LaunchedEffect(Unit) { popped = true }

    Spacer(Modifier.height(8.dp))

    // 96dp 绿圆 + 内白 checkmark（套 pop-in scale）
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

    Text(
        text = "チェックイン完了",
        color = t.ink,
        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(12.dp))

    // 绿胶囊 pill「{时刻} · 時間内」
    Row(
        modifier =
            Modifier
                .clip(RoundedCornerShape(999.dp))
                .background(t.okBg)
                .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = "$checkinAt · 時間内",
            color = t.okDeep,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
        )
    }

    Spacer(Modifier.height(18.dp))

    Text(
        text = "お疲れさまでした",
        color = t.inkSub,
        style = TextStyle(fontSize = 13.sp),
        textAlign = TextAlign.Center,
    )

    Spacer(Modifier.height(8.dp))
}
