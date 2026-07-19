package jp.tomoshibi.android.ui.components

import android.app.Activity
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
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.data.nfc.CheckinType
import jp.tomoshibi.android.data.nfc.ST25DVError
import jp.tomoshibi.android.data.nfc.ST25DVWriter
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.UUID

// 点呼扫卡 sheet — 完全对齐 iOS RollcallSheet (HomeStubs.swift)
//
// 视觉结构（顶 → 底）:
//   ① drag handle (36×4dp)
//   ② 标题「スキャンの準備ができました」
//   ③ 操作说明 2 行
//   ④ 提示 pill（受付中=绿 / 時間外=黄，读真实 rollState）
//   ⑤ 大圆 NFC 视觉
//   ⑥ 「NFC をかざす」CTA → 真 NfcV 写 ST25DV Mailbox
//   ⑦ 「キャンセル」按钮
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RollCallSheet(onDismiss: () -> Unit) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    val activity = context as? Activity

    // 4 步状态机（idle → scanning → success → fail）
    var step by remember { mutableStateOf(Step.Idle) }
    var scanJob by remember { mutableStateOf<Job?>(null) }
    val writer =
        remember(activity) {
            activity?.let { ST25DVWriter(it) }
        }

    // 弹窗关掉 → 取消 NFC / 扫描任务（对齐 iOS onDisappear + writer.cancel）
    DisposableEffect(Unit) {
        onDispose {
            scanJob?.cancel()
            writer?.cancel()
        }
    }

    // success：停 2 秒 → 自动关窗 + toast（对齐 iOS）
    LaunchedEffect(step) {
        if (step == Step.Success) {
            delay(2000)
            store.showToast("点呼機に送信しました")
            onDismiss()
        }
    }

    fun dismiss() {
        scanJob?.cancel()
        writer?.cancel()
        onDismiss()
    }

    fun startNfcWrite() {
        val w = writer
        if (w == null) {
            store.showToast(ST25DVError.Unavailable.userMessageJP)
            step = Step.Fail
            return
        }
        step = Step.Scanning
        scanJob =
            scope.launch {
                try {
                    // 冷启动 token 已恢复但 loadMe 没跑完 → myStudentId 暂时 null，先补拉
                    if (store.snapshot().myStudentId == null) {
                        store.loadMe()
                    }
                    val sid =
                        store.snapshot().myStudentId?.let {
                            runCatching { UUID.fromString(it) }.getOrNull()
                        }
                    if (sid == null) {
                        step = Step.Fail
                        store.showToast("学生情報の取得に失敗しました")
                        return@launch
                    }
                    w.writeCheckin(studentId = sid, type = CheckinType.ROLLCALL)
                    // 生产版不本地置 DONE（伪判定会被 tickCountdown 覆盖）；
                    // 只显写卡成功绿勾，点呼状态由后端 my_checked_in_at 驱动。
                    step = Step.Success
                } catch (e: CancellationException) {
                    throw e // 协程取消必须上抛
                } catch (e: ST25DVError) {
                    step = Step.Fail
                    store.showToast(e.userMessageJP)
                } catch (_: Exception) {
                    step = Step.Fail
                }
            }
    }

    GlassBottomSheet(
        onDismissRequest = { dismiss() },
        sheetState = sheetState,
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
                    Text(
                        text = "スキャンの準備ができました",
                        color = tokens.ink,
                        style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
                        textAlign = TextAlign.Center,
                    )

                    Spacer(Modifier.height(14.dp))

                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalAlignment = Alignment.Start,
                    ) {
                        Text(
                            text = "① 入口の NFC マークにスマートフォンをかざす",
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

                    // 提示条：按真实 rollState 切绿/黄（对齐 iOS R-1）
                    val isActive = state.rollState == RollState.ACTIVE
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(if (isActive) tokens.okBg else tokens.warnBg)
                                .border(
                                    1.dp,
                                    (if (isActive) tokens.okDeep else tokens.warn).copy(alpha = 0.25f),
                                    RoundedCornerShape(12.dp),
                                ).padding(horizontal = 14.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            if (isActive) "✓" else "⚠",
                            color = if (isActive) tokens.okDeep else tokens.warnDeep,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                        )
                        Text(
                            text =
                                if (isActive) {
                                    "点呼受付中です。下のボタンでチェックインしてください。"
                                } else {
                                    "点呼時間外です。点呼開始まで少々お待ちください。"
                                },
                            color = if (isActive) tokens.okDeep else tokens.warnDeep,
                            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
                        )
                    }

                    Spacer(Modifier.height(28.dp))

                    PulseCircle()

                    Spacer(Modifier.height(28.dp))

                    Box(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(54.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(tokens.btnGrad)
                                .clickable { startNfcWrite() },
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "NFC をかざす",
                            color = Color.White,
                            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                        )
                    }

                    Spacer(Modifier.height(8.dp))

                    Box(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(48.dp)
                                .clickable { dismiss() },
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
                    RollSuccessBody(
                        checkinAt = state.checkinAt ?: "--:--",
                        checkinKind = state.checkinKind ?: "時間内",
                    )
                }

                Step.Fail -> {
                    FailBody(onRetry = { step = Step.Idle })
                }
            }
        }
    }
}

// ── Step 3 · success（点呼专属：绿圆 pop-in +「チェックイン完了」+ 时刻 pill）──
@Composable
private fun RollSuccessBody(
    checkinAt: String,
    checkinKind: String,
) {
    val t = SuzuT.current

    var popped by remember { mutableStateOf(false) }
    val scale by animateFloatAsState(
        targetValue = if (popped) 1f else 0.6f,
        animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy, stiffness = Spring.StiffnessMedium),
        label = "rollSuccessPop",
    )
    LaunchedEffect(Unit) { popped = true }

    Spacer(Modifier.height(8.dp))

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

    Row(
        modifier =
            Modifier
                .clip(RoundedCornerShape(999.dp))
                .background(t.okBg)
                .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = "$checkinAt · $checkinKind",
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
