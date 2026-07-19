package jp.tomoshibi.android.ui.haptics

import android.os.Build
import android.view.HapticFeedbackConstants
import android.view.View
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.platform.LocalView

// 触觉反馈三档 — 对齐 iOS UIImpactFeedbackGenerator 用法（轻点 / 成功 / 失败）
// Compose 自带 HapticFeedbackType 只有 LongPress / TextHandleMove，
// 成功/失败用 View.performHapticFeedback 的 CONFIRM / REJECT（API 30+）补齐。

enum class HapticKind {
    /** 轻点（tab 切换 / 长按触发面包屑）— 对齐 iOS .soft / .light */
    Light,

    /** 成功（提交完成 / 签到成功）— 对齐 iOS notification .success */
    Success,

    /** 失败（校验失败 / 扫卡失败）— 对齐 iOS notification .error */
    Error,
}

/** 在 Composable 里拿到三档触觉执行器。 */
@Composable
fun rememberHaptics(): (HapticKind) -> Unit {
    val composeHaptic = LocalHapticFeedback.current
    val view = LocalView.current
    return remember(composeHaptic, view) {
        { kind ->
            view.performTomoshibiHaptic(kind, composeHapticFallback = {
                composeHaptic.performHapticFeedback(HapticFeedbackType.LongPress)
            })
        }
    }
}

fun View.performTomoshibiHaptic(
    kind: HapticKind,
    composeHapticFallback: (() -> Unit)? = null,
) {
    val constant =
        when (kind) {
            HapticKind.Light -> {
                HapticFeedbackConstants.CLOCK_TICK
            }

            HapticKind.Success -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    HapticFeedbackConstants.CONFIRM
                } else {
                    HapticFeedbackConstants.CONTEXT_CLICK
                }
            }

            HapticKind.Error -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    HapticFeedbackConstants.REJECT
                } else {
                    HapticFeedbackConstants.LONG_PRESS
                }
            }
        }
    val handled = performHapticFeedback(constant)
    if (!handled) {
        composeHapticFallback?.invoke()
    }
}
