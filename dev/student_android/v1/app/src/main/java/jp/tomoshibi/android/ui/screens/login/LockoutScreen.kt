package jp.tomoshibi.android.ui.screens.login

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.delay

// 登录失败锁定页 — 対齐 iOS LockoutView（规格 §2.11）：
//   100×100 红圆 + 🔒 锁图标 → 标题 → MM:SS 倒计时大字 → 说明 → 琥珀色阶梯警告框 → 底部解锁按钮
//
// 失败阶梯（规格 E 节，照抄）：
//   失败 1=30 秒 / 2=1 分 / 3=5 分 / 4=30 分 / 5=1 時間 / 6+=永久
//   秒数数组 [30,60,300,1800,3600]，第 6 次起 = 永久（不计时）。
//
// 演示版说明：当前 Android 还没接「锁定升级」状态（对应 iOS AppStore.loginFailCount），
//   这里本地 remember 一个失败次数固定为第 1 次（30 秒）演示倒计时升级提示。
//   接通后端后改为从共享 store 读 loginFailCount。— TODO 接 loginFailCount 真值

// 阶梯秒数（第 N 次失败对应的锁定秒数；下标从 0 起对应第 1 次）
private val LOCKOUT_SECONDS = listOf(30, 60, 300, 1800, 3600)

// 阶梯日语标签（照抄规格：30 秒 / 1 分 / 5 分 / 30 分 / 1 時間 / 永久）
private val LOCKOUT_LABELS = listOf("30 秒", "1 分", "5 分", "30 分", "1 時間", "永久")

@Composable
fun LockoutScreen(navController: NavHostController) {
    val t = SuzuT.current

    // 演示版：失败次数固定为第 1 次（演示阶段无后端，真值接通后从 store 读）
    // failCount = 1 表示这是第 1 次锁定，对应阶梯下标 0（30 秒）
    val failCount by remember { mutableStateOf(1) }

    // 失败 ≥6 次 = 永久锁（阶梯只有 5 段计时，超出即永久）
    val isPermanent = failCount > LOCKOUT_SECONDS.size

    // 本次锁定总秒数（永久时为 null）
    val totalSeconds = if (isPermanent) null else LOCKOUT_SECONDS[failCount - 1]

    // 当前阶梯标签 + 下一阶梯标签（用于琥珀框升级提示）
    val currentLabel = LOCKOUT_LABELS.getOrElse(failCount - 1) { "永久" }
    val nextLabel = LOCKOUT_LABELS.getOrNull(failCount) // 已是最后一段则 null

    // 剩余秒数本地 state；永久时直接 0（不会用到倒计时显示）
    var remaining by remember { mutableStateOf(totalSeconds ?: 0) }

    // 倒计时：协程每秒减 1（规格 E 节指定 while + delay(1000) 写法，不用 iOS Timer 直译）
    LaunchedEffect(isPermanent) {
        if (!isPermanent) {
            while (remaining > 0) {
                delay(1000)
                remaining -= 1
            }
        }
    }

    // 倒计时归零 → 解锁；按钮在此之前 disabled
    val unlocked = !isPermanent && remaining == 0

    // 秒数格式化成 MM:SS（如 90 秒 → 01:30）
    val mmss = run {
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
            // ── 100×100 红圆 + 🔒 锁图标 ──
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

            // ── 标题（非永久 / 永久 两文案，照抄规格 §2.11）──
            Text(
                if (isPermanent) "アカウントがロックされました" else "ログインに失敗しました",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
            )

            if (isPermanent) {
                // ── 永久分支：大字「永久」+ 联络寮監说明（不计时）──
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
                // ── 非永久分支：MM:SS 倒计时大字 + 说明 ──
                Text(
                    mmss,
                    color = t.danger,
                    style = TextStyle(fontSize = 48.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
                )
                Text(
                    if (unlocked) "再度ログインできます" else "セキュリティのため、しばらくログインできません。",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 14.sp),
                )

                // ── 琥珀色阶梯警告框（当前阶段 + 升级提示）──
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

            Spacer(Modifier.height(8.dp))

            // ── 底部解锁按钮：倒计时归零后才 enabled → 回登录页 ──
            // 永久分支保留按钮但恒 disabled（用户只能联络寮監，对应规格「不计时」）
            PrimaryButton(
                title = if (unlocked) "ログインに戻る" else "ログインに戻る",
                modifier = Modifier.fillMaxWidth(),
                enabled = unlocked,
                onClick = {
                    navController.navigate(Route.Login.path) {
                        popUpTo(Route.Lockout.path) { inclusive = true }
                    }
                },
            )
        }
    }
}
