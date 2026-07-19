package jp.tomoshibi.android.ui.screens.login

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.delay

// 登录失败锁定页 — 对齐 iOS LockoutView（规格 §2.11）
//
// 真值来源（本工单 G6）：
//   1) 后端 423 → AppState.lockoutRemainingSec / lockoutMessage（优先）
//   2) DEBUG 本地阶梯 → AppState.loginFailCount（对齐 iOS DEMO loginFailCount）
// 禁止本地写死 failCount=1。

// DEBUG 阶梯秒数（第 N 次失败对应的锁定秒数；下标从 0 起对应第 1 次）
private val LOCKOUT_SECONDS = listOf(30, 60, 300, 1800, 3600)

// 阶梯日语标签（照抄规格：30 秒 / 1 分 / 5 分 / 30 分 / 1 時間 / 永久）
private val LOCKOUT_LABELS = listOf("30 秒", "1 分", "5 分", "30 分", "1 時間", "永久")

@Composable
fun LockoutScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    // 优先用后端 423 解析出的剩余秒数；否则用 DEBUG 本地阶梯
    val backendRemaining = state.lockoutRemainingSec
    val failCount = state.loginFailCount
    val backendMessage = state.lockoutMessage

    val fromBackend = backendRemaining != null || !backendMessage.isNullOrEmpty()

    val isPermanent =
        if (fromBackend) {
            // 后端当前实现是固定时长锁，不走永久；无剩余秒数且有文案时仍显示倒计时区用兜底
            false
        } else {
            failCount > LOCKOUT_SECONDS.size
        }

    val totalSeconds: Int? =
        when {
            backendRemaining != null -> backendRemaining

            isPermanent -> null

            failCount >= 1 && failCount <= LOCKOUT_SECONDS.size -> LOCKOUT_SECONDS[failCount - 1]

            // 既无后端剩余、也无有效 failCount → 兜底 30 秒（不应常态出现）
            else -> 30
        }

    val currentLabel =
        when {
            fromBackend -> formatDurationLabel(totalSeconds ?: 0)
            else -> LOCKOUT_LABELS.getOrElse(failCount - 1) { "永久" }
        }
    val nextLabel =
        if (fromBackend) {
            null
        } else {
            LOCKOUT_LABELS.getOrNull(failCount)
        }

    var remaining by remember(totalSeconds) { mutableIntStateOf(totalSeconds ?: 0) }

    LaunchedEffect(isPermanent, totalSeconds) {
        if (!isPermanent) {
            remaining = totalSeconds ?: 0
            while (remaining > 0) {
                delay(1000)
                remaining -= 1
            }
        }
    }

    val unlocked = !isPermanent && remaining == 0

    val mmss =
        run {
            val m = remaining / 60
            val s = remaining % 60
            "%02d:%02d".format(m, s)
        }

    Box(
        modifier =
            Modifier
                .fillMaxSize()
                .background(t.pearl)
                .padding(horizontal = 32.dp),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            Box(
                modifier =
                    Modifier
                        .size(100.dp)
                        .clip(RoundedCornerShape(50.dp))
                        .background(t.dangerBg),
                contentAlignment = Alignment.Center,
            ) {
                Text("🔒", style = TextStyle(fontSize = 44.sp))
            }

            Text(
                if (isPermanent) "アカウントがロックされました" else "ログインに失敗しました",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
            )

            if (isPermanent) {
                Text(
                    "永久",
                    color = t.danger,
                    style = TextStyle(fontSize = 48.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
                )
                Text(
                    "試行回数の上限を超えました。\n寮監にご連絡ください。",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 14.sp),
                )
            } else {
                Text(
                    mmss,
                    color = t.danger,
                    style = TextStyle(fontSize = 48.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
                )
                Text(
                    when {
                        unlocked -> "再度ログインできます"
                        !backendMessage.isNullOrEmpty() -> backendMessage
                        else -> "セキュリティのため、しばらくログインできません。"
                    },
                    color = t.inkSub,
                    style = TextStyle(fontSize = 14.sp),
                )

                // 琥珀色阶梯 / 后端锁定提示
                Column(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(t.warnBg)
                            .border(1.dp, t.warn.copy(alpha = 0.25f), RoundedCornerShape(12.dp))
                            .padding(14.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    if (fromBackend) {
                        Text(
                            "アカウントロック中（$currentLabel）",
                            color = t.warnDeep,
                            style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold),
                        )
                    } else {
                        Text(
                            "現在 $failCount 回目のロック（$currentLabel）",
                            color = t.warnDeep,
                            style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold),
                        )
                        if (nextLabel != null) {
                            Text(
                                "次回失敗で $nextLabel ロックに上がります",
                                color = t.warnDeep,
                                style = TextStyle(fontSize = 12.5.sp),
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            PrimaryButton(
                title = "ログインに戻る",
                modifier = Modifier.fillMaxWidth(),
                enabled = unlocked,
                onClick = {
                    // 解锁回登录；本地失败计数保留到下次成功再 reset（对齐 iOS）
                    navController.navigate(Route.Login.path) {
                        popUpTo(Route.Lockout.path) { inclusive = true }
                    }
                },
            )
        }
    }
}

private fun formatDurationLabel(totalSec: Int): String {
    if (totalSec >= 3600) {
        val h = totalSec / 3600
        return "$h 時間"
    }
    if (totalSec >= 60) {
        val m = (totalSec + 59) / 60 // 向上取整分钟，跟后端「残り約 N 分」同口径
        return "$m 分"
    }
    return "$totalSec 秒"
}
