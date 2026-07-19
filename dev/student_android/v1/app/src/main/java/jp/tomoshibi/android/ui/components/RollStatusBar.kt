package jp.tomoshibi.android.ui.components

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// ───────────────────────────────────────────────────────────────
// RollStatusBar — 顶部点呼状态条（胶囊横条），对齐 iOS Foundation/Components/TopRollBar.swift
// 规格：内部对齐规格 ① 顶部状态条 TopRollBar（4 态）+ Android 对齐要点 A
//
// 注意命名：iOS 叫 TopRollBar，但 Android 的「TopRollBar」名字已被主页 amber hero 占用，
//           所以这个全局顶部状态条改叫 RollStatusBar。
//
// 4 态：IDLE（不显示）/ ACTIVE（点呼中倒计时）/ ABSENT（欠席判定）/ DONE（签到完成）
// 调用方只在 rollState != IDLE 时才 compose 本组件；本组件内部对 IDLE 再给一层安全兜底（返回空 Box）。
// ───────────────────────────────────────────────────────────────

@Composable
fun RollStatusBar(
    rollState: RollState,
    checkinAt: String?,
    checkinKind: String?,
    countdownSec: Int,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val t = SuzuT.current

    // IDLE 安全兜底：调用方本就不该在 IDLE 时 compose 本组件，这里再保险一层 —— 啥也不画。
    if (rollState == RollState.IDLE) {
        Box(modifier)
        return
    }

    // ── 倒计时分秒：countdownSec 总秒数拆成「N分NN秒」，秒补零（对齐 iOS %02d）──
    val min = countdownSec / 60
    val sec = countdownSec % 60

    // ── 各态文案 + 配色，逐字对照 iOS TopRollBar.swift ──
    val icon: ImageVector
    val iconTint: Color
    val primaryText: String
    val secondaryText: String
    val fg: Color
    val bg: Color

    when (rollState) {
        RollState.ACTIVE -> {
            // 点呼中：实心圆点（dot.circle.fill），底浅橙，文字深橙
            icon = SuzuIcons.Dot
            iconTint = t.danger
            primaryText = String.format("点呼中 · 遅刻まであと %d分%02d秒", min, sec)
            secondaryText = "タップで欠席届・体調報告"
            fg = t.warnDeep
            bg = t.warnBg
        }

        RollState.ABSENT -> {
            // 欠席判定：警告三角白图标，整条实红底，文字纯白
            icon = SuzuIcons.Warn
            iconTint = Color.White
            primaryText = "欠席になりました · 寮監まで直接ご連絡ください"
            secondaryText = "寮監室までお越しください"
            fg = Color.White
            bg = t.danger
        }

        RollState.DONE -> {
            // 签到完成：绿对钩；checkinKind 由后端 my_status 派生（不許写死「時間内」）
            icon = SuzuIcons.CheckCirc
            iconTint = t.ok
            val kind = checkinKind ?: ""
            primaryText = "チェックイン済み ${checkinAt ?: ""} · $kind"
            secondaryText = "お疲れさまでした"
            fg = t.okDeep
            bg = t.okBg
        }

        RollState.IDLE -> {
            return
        } // 上面已兜底，编译器穷尽用
    }

    // ── ACTIVE 态图标脉冲：alpha 在 0.55↔0.9 之间循环（对齐 iOS symbolEffect(.pulse)）──
    val iconAlpha =
        if (rollState == RollState.ACTIVE) {
            val tr = rememberInfiniteTransition(label = "rollDotPulse")
            val a by tr.animateFloat(
                initialValue = 0.55f,
                targetValue = 0.9f,
                animationSpec = infiniteRepeatable(tween(700), RepeatMode.Reverse),
                label = "rollDotAlpha",
            )
            a
        } else {
            1f
        }

    // ── 胶囊横条本体 ──
    Row(
        modifier =
            modifier
                .clip(RoundedCornerShape(50))
                .background(bg)
                // DONE 态点了无反应（done 不可再点）；其余态回调上层
                .clickable { if (rollState != RollState.DONE) onClick() }
                .padding(horizontal = 14.dp, vertical = 10.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 左：状态图标（ACTIVE 带脉冲 alpha）
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = iconTint,
            modifier = Modifier.size(20.dp).alpha(iconAlpha),
        )
        // 中：两行文字（12sp semibold / 10sp 灰）
        Column {
            Text(
                text = primaryText,
                color = fg,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
            )
            Text(
                text = secondaryText,
                // ABSENT 实红底用白字 70% 透明做「灰」效果，其余态用半透明 fg
                color = fg.copy(alpha = 0.7f),
                style = TextStyle(fontSize = 10.sp),
            )
        }
        Spacer(Modifier.weight(1f))
        // 右：箭头 —— DONE 态不画（done 不可再点）
        if (rollState != RollState.DONE) {
            Icon(
                imageVector = SuzuIcons.ChevR,
                contentDescription = null,
                tint = fg.copy(alpha = 0.5f),
                modifier = Modifier.size(18.dp),
            )
        }
    }
}
