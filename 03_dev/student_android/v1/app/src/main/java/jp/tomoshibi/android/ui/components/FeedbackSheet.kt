package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// ───────────────────────────────────────────────────────────────
// FeedbackSheet — 反馈三选一分发弹窗
// 对齐 iOS Foundation/Features/Home/HomeStubs.swift 行 1863–1940（FeedbackSheet）。
// 入口：点顶部状态条 TopRollBar（非 done 态）弹出。
// 职责：只做「3 选 1」的分发框架 —— 点哪个选项就回调 onSelect(类型) + onDismiss 关窗，
//      具体子表单（身体状况报告 / 缺席申请 / 其他问题）归别处（health/absence/other），本文件不实装。
// 本波纯 UI，无状态机、无动画、不发网络。
// 规格真值：00_admin/iOS_Android_对齐规格.md 第 3007–3017 行（④ 反馈三选一）。
// ───────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeedbackSheet(
    onDismiss: () -> Unit,
    onSelect: (String) -> Unit,
) {
    val t = SuzuT.current
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = t.paper,
        sheetState = rememberModalBottomSheetState(),
    ) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 40.dp),
            horizontalAlignment = Alignment.Start,
        ) {
            // 1. 标题（20sp heavy，ink，下 6）
            Text(
                text = "反馈を送る",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )
            Spacer(Modifier.size(6.dp))
            // 2. 副标题（13sp，inkSub，下 18）
            Text(
                text = "どの種類の反馈を送りますか？",
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp),
            )
            Spacer(Modifier.size(18.dp))

            // 3. 3 个选项卡（VStack spacing 10）—— 点哪个回调对应类型 + 关窗
            // 🤒 体調問題 → "health"
            FeedbackOptionRow(
                emoji = "🤒",
                title = "体調問題を報告",
                subtitle = "発熱・頭痛・その他の症状を先生に通知",
                onClick = {
                    onSelect("health")
                    onDismiss()
                },
            )
            Spacer(Modifier.size(10.dp))
            // 📝 「今回欠席の申請」缺席申请 → "absence"
            FeedbackOptionRow(
                emoji = "📝",
                title = "今回欠席の申請",
                subtitle = "今回の点呼を欠席したい理由を申請",
                onClick = {
                    onSelect("absence")
                    onDismiss()
                },
            )
            Spacer(Modifier.size(10.dp))
            // 💬 其他问题 → "other"（含 NFC 故障一类，归 OtherSheet 分类处理）
            FeedbackOptionRow(
                emoji = "💬",
                title = "その他の問題",
                subtitle = "遅刻理由・外出中・NFC 不具合など",
                onClick = {
                    onSelect("other")
                    onDismiss()
                },
            )
        }
    }
    // TODO 真实装：onSelect 的三个类型 health/absence/other 应分别打开
    //   HealthSheet / AbsenceSheet / OtherSheet 三个表单弹窗（对齐 iOS .health/.absence/.other）。
    //   本波只做分发框架 —— 调用方先用 Toast 占位，子表单等「申请/反馈」那块对齐时再接。
}

// 单个选项卡（Row：白底 + t.hair 0.5dp 描边 + 圆角 16 + 内边距 16×14；
//          左 emoji 28sp + 中两行文字（标题 bold / 副灰）+ 右箭头 ChevR inkMute）
@Composable
private fun FeedbackOptionRow(
    emoji: String,
    title: String,
    subtitle: String,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(t.paper)
                .border(BorderStroke(0.5.dp, t.hair), RoundedCornerShape(16.dp))
                .clickable(onClick = onClick)
                .padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 左：emoji 28sp
        Text(text = emoji, style = TextStyle(fontSize = 28.sp))
        Spacer(Modifier.width(14.dp))
        // 中：两行文字 —— 标题 bold + 副灰
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            Text(
                text = title,
                color = t.ink,
                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
            )
            Text(
                text = subtitle,
                color = t.inkSub,
                style = TextStyle(fontSize = 12.sp),
            )
        }
        Spacer(Modifier.width(12.dp))
        // 右：箭头 ChevR（16dp，inkMute）
        Icon(
            imageVector = SuzuIcons.ChevR,
            contentDescription = null,
            tint = t.inkMute,
            modifier = Modifier.size(16.dp),
        )
    }
}
