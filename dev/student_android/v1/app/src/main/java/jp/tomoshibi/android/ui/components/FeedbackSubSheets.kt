package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.theme.SuzuT

// ───────────────────────────────────────────────────────────────
// FeedbackSubSheets — 反馈三子表单（体调 / 缺席 / 其他）
// 对齐 iOS Foundation/Features/Home/HomeStubs.swift 行 1947–2154：
//   HealthSheet（1947）/ AbsenceSheet（2038）/ OtherSheet（2083）。
// iOS 用 GlassSheet；Android 走 GlassBottomSheet（半透明 paper + ink@35% 遮罩近似）。
// 入口：FeedbackSheet 分发后，按选中的类型 health/absence/other 打开对应子表单（接线归主会话）。
// 本波纯 UI，无状态机、无网络。提交按钮点了只关窗（iOS 那边 closeSheet + showToast，Toast 由调用方接）。
// ───────────────────────────────────────────────────────────────

// ───────────────────────────────────────────────────────────────
// HealthSheet · 体调不良报告（症状必填 + 体温任意 + 补足）
// ───────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun HealthSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current

    // 已选症状（空串 = 未选；非空才允许提交）
    var sym by remember { mutableStateOf("") }
    // 体温（任意，数字键盘）
    var temp by remember { mutableStateOf("") }
    // 补足说明（任意多行）
    var note by remember { mutableStateOf("") }

    // 症状选项 —— 照抄 iOS symptoms 数组，「発熱」「頭痛」「腹痛」「吐き気」「風邪症状」「その他」
    val symptoms = listOf("発熱", "頭痛", "腹痛", "吐き気", "風邪症状", "その他")

    GlassBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(),
    ) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 40.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
            horizontalAlignment = Alignment.Start,
        ) {
            // 标题「体調不良を報告」（20sp heavy ink）
            Text(
                text = "体調不良を報告",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )

            // 字段「症状」必填 —— radio chip 横向换行组
            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "症状", required = true)
                FlowRow(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    symptoms.forEach { s ->
                        RadioChip(title = s, selected = sym == s) { sym = s }
                    }
                }
            }

            // 字段「体温（任意）」—— 数字键盘单行输入，placeholder「体温（℃）」
            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "体温（任意）", required = false)
                TField(
                    value = temp,
                    onValueChange = { temp = it },
                    placeholder = "体温（℃）",
                    keyboard = KeyboardType.Decimal,
                )
            }

            // 字段「補足」—— 多行输入，placeholder「具体的な症状があれば教えてください」
            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "補足", required = false)
                TArea(
                    value = note,
                    onValueChange = { note = it },
                    placeholder = "具体的な症状があれば教えてください",
                    rows = 3,
                )
            }

            // 「提出」—— 症状非空才可点
            PrimaryButton(
                title = "提出",
                enabled = sym.isNotEmpty(),
                onClick = { onDismiss() },
            )
        }
    }
}

// ───────────────────────────────────────────────────────────────
// AbsenceSheet · 缺席申请（理由必填多行）
// ───────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AbsenceSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current

    // 缺席理由（必填，去掉首尾空白后非空才允许提交）
    var reason by remember { mutableStateOf("") }

    GlassBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(),
    ) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 40.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
            horizontalAlignment = Alignment.Start,
        ) {
            // 标题「今回の点呼を欠席したい」（20sp heavy ink）
            Text(
                text = "今回の点呼を欠席したい",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )

            // 字段「理由」必填 —— 5 行多行输入，placeholder「欠席の理由をお書きください」
            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "理由", required = true)
                TArea(
                    value = reason,
                    onValueChange = { reason = it },
                    placeholder = "欠席の理由をお書きください",
                    rows = 5,
                )
            }

            // 「提出」—— 理由去空白后非空才可点
            PrimaryButton(
                title = "提出",
                enabled = reason.trim().isNotEmpty(),
                onClick = { onDismiss() },
            )
        }
    }
}

// ───────────────────────────────────────────────────────────────
// OtherSheet · 其他问题（分类必填 + 内容必填）
// ───────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun OtherSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current

    // 已选分类（空串 = 未选）
    var cat by remember { mutableStateOf("") }
    // 内容（必填，去空白后非空才允许提交）
    var content by remember { mutableStateOf("") }

    // 分类选项 —— 照抄 iOS categories 数组，「遅刻理由」「外出中」「NFC 不具合」「その他」
    val categories = listOf("遅刻理由", "外出中", "NFC 不具合", "その他")

    GlassBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(),
    ) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 40.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
            horizontalAlignment = Alignment.Start,
        ) {
            // 标题「その他の問題」（20sp heavy ink）
            Text(
                text = "その他の問題",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )

            // 字段「分類」必填 —— radio chip 横向换行组
            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "分類", required = true)
                FlowRow(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    categories.forEach { c ->
                        RadioChip(title = c, selected = cat == c) { cat = c }
                    }
                }
            }

            // 字段「内容」必填 —— 多行输入，placeholder「詳しく教えてください」
            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "内容", required = true)
                TArea(
                    value = content,
                    onValueChange = { content = it },
                    placeholder = "詳しく教えてください",
                    rows = 4,
                )
            }

            // 「提出」—— 分类非空 + 内容去空白后非空才可点
            PrimaryButton(
                title = "提出",
                enabled = cat.isNotEmpty() && content.trim().isNotEmpty(),
                onClick = { onDismiss() },
            )
        }
    }
}

// ───────────────────────────────────────────────────────────────
// 私有复用件
// ───────────────────────────────────────────────────────────────

// 字段标签 —— 13sp semibold inkSub + 必填时跟一个 danger 色「*」（对齐 iOS HStack(标签 + 红 *)）
@Composable
private fun FieldLabel(
    label: String,
    required: Boolean,
) {
    val t = SuzuT.current
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(
            text = label,
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
        )
        if (required) {
            Text(
                text = " *",
                color = t.danger,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            )
        }
    }
}

// radio 选项胶囊 —— 照抄 iOS radioChip：
//   选中 = primary 描边 1.5dp + primary 6% 底 + primary 字（bold）
//   未选 = t.hair 描边 1dp + t.pearl 底 + t.ink 字（medium）
@Composable
private fun RadioChip(
    title: String,
    selected: Boolean,
    onTap: () -> Unit,
) {
    val t = SuzuT.current
    val cs = androidx.compose.material3.MaterialTheme.colorScheme
    Row(
        modifier =
            Modifier
                .clip(RoundedCornerShape(12.dp))
                .background(if (selected) cs.primary.copy(alpha = 0.06f) else t.pearl)
                .border(
                    BorderStroke(if (selected) 1.5.dp else 1.dp, if (selected) cs.primary else t.hair),
                    RoundedCornerShape(12.dp),
                ).clickable(onClick = onTap)
                .padding(horizontal = 16.dp, vertical = 10.dp),
    ) {
        Text(
            text = title,
            color = if (selected) cs.primary else t.ink,
            style =
                TextStyle(
                    fontSize = 14.sp,
                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                ),
        )
    }
}
