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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.data.network.ApiErrorPresenter
import jp.tomoshibi.android.data.network.endpoints.StudentRenewalAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.data.store.SessionMapper
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// ───────────────────────────────────────────────────────────────
// RenewStudentNoSheet — 学籍番号「再設定」弹窗
// 对齐 iOS Features/Home/HomeStubs.swift 行 2163–2298（struct RenewStudentNoSheet）。
// 用途：新学年开学时学生重新选「学年・組・出席番号」三段，系统自动拼出新学籍番号。
// iOS 用 GlassSheet；Android 走 GlassBottomSheet 近似。
// 提交：POST /api/v1/students/me/renew-number；422 撞号原样弹后端日语提示。
// ───────────────────────────────────────────────────────────────

// 学年：中高一貫 6 年制（01→中1 … 06→高3），label 是 chip 上显示的文字
private val GRADES =
    listOf(
        "01" to "中1",
        "02" to "中2",
        "03" to "中3",
        "04" to "高1",
        "05" to "高2",
        "06" to "高3",
    )

// 组：A→01 / B→02
private val CLASSES =
    listOf(
        "01" to "A組",
        "02" to "B組",
    )

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun RenewStudentNoSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()

    // 三段选择 state：学年 code / 组 code / 出席番号输入（字符串，只留数字）
    var gradeCode by remember { mutableStateOf("") }
    var classCode by remember { mutableStateOf("") }
    var seatInput by remember { mutableStateOf("") }
    var submitting by remember { mutableStateOf(false) }

    // 出席番号转 Int（输入非法则为 null）
    val seatNo: Int? = seatInput.toIntOrNull()
    // 三段齐 + 出席番号在 1–99 才允许提交（对齐 iOS canSubmit）
    val canSubmit =
        !submitting &&
            gradeCode.isNotEmpty() &&
            classCode.isNotEmpty() &&
            (seatNo != null && seatNo in 1..99)

    GlassBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(),
    ) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp)
                    .padding(bottom = 40.dp),
            horizontalAlignment = Alignment.Start,
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            // 1. 标题「学籍番号の再設定」（20sp heavy，ink）
            Text(
                text = "学籍番号の再設定",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )

            // 2. 说明「新学年の 学年・組・出席番号 を選んでください。学籍番号は自動で計算されます。」（13sp，inkSub）
            Text(
                text = "新学年の 学年・組・出席番号 を選んでください。学籍番号は自動で計算されます。",
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp),
            )

            // 3.「学年」必填 radio chips（中1..高3）
            FieldLabel("学年")
            FlowRow(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                GRADES.forEach { (code, label) ->
                    RadioChip(title = label, selected = gradeCode == code) { gradeCode = code }
                }
            }

            // 4.「組」必填 radio chips（A組 / B組）
            FieldLabel("組")
            FlowRow(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                CLASSES.forEach { (code, label) ->
                    RadioChip(title = label, selected = classCode == code) { classCode = code }
                }
            }

            // 5.「出席番号」必填 — 数字键盘，只留数字、最多 2 桁
            FieldLabel("出席番号")
            TField(
                value = seatInput,
                onValueChange = { raw ->
                    val digits = raw.filter { it.isDigit() }
                    seatInput = digits.take(2)
                },
                placeholder = "例: 18",
                keyboard = KeyboardType.Number,
            )

            // 6. 实时预览新学号（三段齐了才显示）「新しい学籍番号: {学年}{组}{出席番号2位}」primary 色
            if (gradeCode.isNotEmpty() && classCode.isNotEmpty() && seatNo != null && seatNo in 1..99) {
                Text(
                    text = "新しい学籍番号: %s%s%02d".format(gradeCode, classCode, seatNo),
                    color = cs.primary,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                )
            }

            // 7.「更新する」主按钮（三段齐才可点）→ POST renew-number
            PrimaryButton(
                title = if (submitting) "更新中…" else "更新する",
                enabled = canSubmit,
            ) {
                val seat = seatNo ?: return@PrimaryButton
                submitting = true
                scope.launch {
                    try {
                        val me =
                            StudentRenewalAPI.renewNumber(
                                gradeCode = gradeCode,
                                classCode = classCode,
                                seatNo = "%02d".format(seat),
                            )
                        val mapped = SessionMapper.mapMeToUser(me)
                        // 保留已有扣分统计（renew 响应不含 summary）
                        store.update { cur ->
                            cur.copy(
                                user =
                                    mapped.copy(
                                        points = cur.user.points,
                                        lateCount = cur.user.lateCount,
                                        absentCount = cur.user.absentCount,
                                        needsCleaning = cur.user.needsCleaning,
                                    ),
                                needsRenewal = me.needsRenewal ?: false,
                                myStudentId = me.id,
                            )
                        }
                        store.showToast("アカウント番号を更新しました")
                        onDismiss()
                    } catch (e: Exception) {
                        store.showToast(
                            ApiErrorPresenter.userMessage(e, fallback = "更新に失敗しました"),
                        )
                    } finally {
                        submitting = false
                    }
                }
            }
        }
    }
}

// 字段标签：13sp semibold inkSub + 红色「*」必填记号（对齐 iOS fieldLabel）
@Composable
private fun FieldLabel(text: String) {
    val t = SuzuT.current
    Row(verticalAlignment = Alignment.CenterVertically) {
        Text(text, color = t.inkSub, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
        Text(" *", color = t.danger, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
    }
}

// 单选 chip（对齐 iOS radioChip）：
//   选中 = primary 文字 bold + primary 描边 1.5 + primary 6% 底
//   未选 = ink 文字 medium + hair 描边 1 + pearl 底
@Composable
private fun RadioChip(
    title: String,
    selected: Boolean,
    onTap: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
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
