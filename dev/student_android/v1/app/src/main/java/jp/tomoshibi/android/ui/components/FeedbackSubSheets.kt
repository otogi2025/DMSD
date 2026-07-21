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
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.ApiErrorPresenter
import jp.tomoshibi.android.data.network.endpoints.RollCallReportsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// ───────────────────────────────────────────────────────────────
// FeedbackSubSheets — 上报三子表单（体调 / 缺席 / 其他）
// 对齐 iOS HomeStubs.swift：HealthSheet / AbsenceSheet / OtherSheet。
// 生产版 POST /api/v1/rollcall/reports（RollCallReportsAPI），成功 toast + 错误分支对齐 iOS。
// ───────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun HealthSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()

    var sym by remember { mutableStateOf("") }
    var temp by remember { mutableStateOf("") }
    var note by remember { mutableStateOf("") }
    var submitting by remember { mutableStateOf(false) }

    val symptoms = listOf("発熱", "頭痛", "腹痛", "吐き気", "風邪症状", "その他")

    fun submit() {
        val lines = mutableListOf("症状：$sym")
        val tVal = temp.trim()
        if (tVal.isNotEmpty()) lines.add("体温：$tVal℃")
        val nVal = note.trim()
        if (nVal.isNotEmpty()) lines.add("補足：$nVal")
        val bodyText = lines.joinToString("\n")
        scope.launch {
            val tokenAtStart = store.snapshot().authToken
            submitting = true
            try {
                RollCallReportsAPI.create(kind = "health", body = bodyText)
                if (store.snapshot().authToken != tokenAtStart) return@launch
                onDismiss()
                store.showToast("先生に通知しました")
            } catch (e: ApiError.Unprocessable) {
                submitting = false
                store.showToast(e.msg)
            } catch (e: ApiError.Unauthorized) {
                if (store.snapshot().authToken == tokenAtStart) {
                    store.clearSession()
                    onDismiss()
                }
            } catch (e: ApiError.Network) {
                submitting = false
                store.showToast("通信エラーが発生しました。電波を確認してください")
            } catch (e: Exception) {
                submitting = false
                store.showToast(
                    ApiErrorPresenter.userMessage(e, fallback = "送信に失敗しました"),
                )
            }
        }
    }

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
            Text(
                text = "体調不良を報告",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )

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

            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "体温（任意）", required = false)
                TField(
                    value = temp,
                    onValueChange = { temp = it },
                    placeholder = "体温（℃）",
                    keyboard = KeyboardType.Decimal,
                )
            }

            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "補足", required = false)
                TArea(
                    value = note,
                    onValueChange = { note = it },
                    placeholder = "具体的な症状があれば教えてください",
                    rows = 3,
                )
            }

            PrimaryButton(
                title = if (submitting) "送信中…" else "提出",
                enabled = sym.isNotEmpty() && !submitting,
                onClick = { submit() },
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AbsenceSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()

    var reason by remember { mutableStateOf("") }
    var submitting by remember { mutableStateOf(false) }

    fun submit() {
        val bodyText = reason.trim()
        scope.launch {
            val tokenAtStart = store.snapshot().authToken
            submitting = true
            try {
                RollCallReportsAPI.create(kind = "absence", body = bodyText)
                if (store.snapshot().authToken != tokenAtStart) return@launch
                onDismiss()
                store.showToast("審査中です")
            } catch (e: ApiError.Unprocessable) {
                submitting = false
                store.showToast(e.msg)
            } catch (e: ApiError.Unauthorized) {
                if (store.snapshot().authToken == tokenAtStart) {
                    store.clearSession()
                    onDismiss()
                }
            } catch (e: ApiError.Network) {
                submitting = false
                store.showToast("通信エラーが発生しました。電波を確認してください")
            } catch (e: Exception) {
                submitting = false
                store.showToast(
                    ApiErrorPresenter.userMessage(e, fallback = "送信に失敗しました"),
                )
            }
        }
    }

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
            // 标题逐字对照 iOS「今回の点呼を欠席する」（陈述句，无「たい」）
            Text(
                text = "今回の点呼を欠席する",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )

            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "理由", required = true)
                TArea(
                    value = reason,
                    onValueChange = { reason = it },
                    placeholder = "欠席の理由をお書きください",
                    rows = 5,
                )
            }

            PrimaryButton(
                title = if (submitting) "送信中…" else "提出",
                enabled = reason.trim().isNotEmpty() && !submitting,
                onClick = { submit() },
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun OtherSheet(onDismiss: () -> Unit) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()

    var cat by remember { mutableStateOf("") }
    var content by remember { mutableStateOf("") }
    var submitting by remember { mutableStateOf(false) }

    val categories = listOf("遅刻理由", "外出中", "NFC 不具合", "その他")

    fun submit() {
        val c = content.trim()
        val bodyText = "分類：$cat\n内容：$c"
        scope.launch {
            val tokenAtStart = store.snapshot().authToken
            submitting = true
            try {
                RollCallReportsAPI.create(kind = "other", body = bodyText)
                if (store.snapshot().authToken != tokenAtStart) return@launch
                onDismiss()
                store.showToast("送信しました")
            } catch (e: Exception) {
                // iOS OtherSheet 生产分支失败统一「送信に失敗しました」（比 health/absence 粗）
                submitting = false
                store.showToast("送信に失敗しました")
            }
        }
    }

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
            Text(
                text = "その他の問題",
                color = t.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Black),
            )

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

            Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
                FieldLabel(label = "内容", required = true)
                TArea(
                    value = content,
                    onValueChange = { content = it },
                    placeholder = "詳しく教えてください",
                    rows = 4,
                )
            }

            PrimaryButton(
                title = if (submitting) "送信中…" else "提出",
                enabled = cat.isNotEmpty() && content.trim().isNotEmpty() && !submitting,
                onClick = { submit() },
            )
        }
    }
}

// 字段标签 —— 13sp semibold inkSub + 必填时跟一个 danger 色「*」
// 同包共享（internal）：RenewStudentNoSheet 等应复用本份，勿再各写 private 副本
@Composable
internal fun FieldLabel(
    label: String,
    required: Boolean = false,
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

// radio 选项胶囊 —— 照抄 iOS radioChip；同包共享，见上方 FieldLabel 注释
@Composable
internal fun RadioChip(
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
