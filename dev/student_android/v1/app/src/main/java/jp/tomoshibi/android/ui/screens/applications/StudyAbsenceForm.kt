package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.StudyAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ApplyDoneBody
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.RadioCard
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.format.DateTimeFormatter

// 「夜学習欠席届」— 对齐 iOS ApplyStubs.swift StudyAbsenceForm
//   §1 欠席日期（今天〜14 日后，DateField min/max 硬限制）
//   §2 欠席范围（前半节 / 后半节 / 両方）
//   §3 理由（必填）
// 提交走 StudyAPI.submitAbsenceRequest。

private enum class StudyLeaveRange(
    val label: String,
    val wire: String,
) {
    FIRST("前半節（19:40〜20:40）", "first_half"),
    SECOND("後半節（20:45〜21:45）", "second_half"),
    BOTH("両方", "full"),
}

@Composable
fun StudyAbsenceForm(navController: NavHostController) {
    val store = LocalAppStore.current
    val t = SuzuT.current
    val scope = rememberCoroutineScope()

    var stage by remember { mutableStateOf("edit") }
    var submitting by remember { mutableStateOf(false) }

    var targetDate by remember { mutableStateOf("") }
    var range by remember { mutableStateOf<StudyLeaveRange?>(null) }
    var reason by remember { mutableStateOf("") }

    val today = remember { JstDate.today().format(DateTimeFormatter.ISO_LOCAL_DATE) }
    val maxDate =
        remember {
            JstDate.today().plusDays(14).format(DateTimeFormatter.ISO_LOCAL_DATE)
        }

    val canSubmit =
        targetDate.isNotEmpty() &&
            targetDate >= today &&
            targetDate <= maxDate &&
            range != null &&
            reason.trim().isNotEmpty()

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "夜学習欠席届",
                level = 2,
                onLeft = {
                    if (stage == "preview") stage = "edit" else navController.popBackStack()
                },
            )

            when (stage) {
                "edit" -> {
                    EditStage(
                        tokens = t,
                        targetDate = targetDate,
                        range = range,
                        reason = reason,
                        canSubmit = canSubmit,
                        today = today,
                        maxDate = maxDate,
                        onPickDate = { targetDate = it },
                        onPickRange = { range = it },
                        onReasonChange = { reason = it },
                        onConfirm = {
                            if (reason.trim().isEmpty()) {
                                store.showToast("理由を入力してください")
                            } else {
                                stage = "preview"
                            }
                        },
                    )
                }

                "preview" -> {
                    PreviewStage(
                        tokens = t,
                        targetDate = targetDate,
                        range = range,
                        reason = reason,
                        submitting = submitting,
                        onSubmit = {
                            val r = range ?: return@PreviewStage
                            if (submitting) return@PreviewStage
                            scope.launch {
                                submitting = true
                                val tokenAtStart = store.snapshot().authToken
                                try {
                                    StudyAPI.submitAbsenceRequest(
                                        targetDate = targetDate,
                                        period = r.wire,
                                        reason = reason.trim(),
                                    )
                                    if (store.snapshot().authToken != tokenAtStart) return@launch
                                    store.showToast("夜学習欠席届を提出しました")
                                    stage = "done"
                                } catch (e: ApiError) {
                                    if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                    store.showToast(e.display)
                                } catch (_: Exception) {
                                    store.showToast("申請の提出に失敗しました")
                                } finally {
                                    submitting = false
                                }
                            }
                        },
                        onEdit = { stage = "edit" },
                    )
                }

                "done" -> {
                    ApplyDoneBody(
                        kindName = "夜学習欠席",
                        messageOverride = "夜学習欠席届を受け付けました。\n審査完了時に通知でお知らせします。",
                    ) {
                        // 对齐 iOS「一覧へ」= 回申请列表根（不是上一页的选种页）。
                        navController.navigate(jp.tomoshibi.android.nav.Route.Applications.path) {
                            popUpTo(jp.tomoshibi.android.nav.Route.Applications.path) { inclusive = false }
                            launchSingleTop = true
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun EditStage(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    targetDate: String,
    range: StudyLeaveRange?,
    reason: String,
    canSubmit: Boolean,
    today: String,
    maxDate: String,
    onPickDate: (String) -> Unit,
    onPickRange: (StudyLeaveRange) -> Unit,
    onReasonChange: (String) -> Unit,
    onConfirm: () -> Unit,
) {
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        SuzuCard {
            DateField(
                label = "欠席する日付",
                value = targetDate,
                required = true,
                minDate = today,
                maxDate = maxDate,
                onPick = onPickDate,
            )
            Spacer(Modifier.height(7.dp))
            Text(
                "※本日から14日後までの日付を選択してください",
                color = tokens.inkMute,
                style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp),
            )
        }

        SuzuCard {
            Text(
                "欠席する範囲",
                color = tokens.inkSub,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            )
            Spacer(Modifier.height(10.dp))
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                StudyLeaveRange.entries.forEach { r ->
                    RadioCard(
                        title = r.label,
                        selected = range == r,
                        onClick = { onPickRange(r) },
                    )
                }
            }
        }

        SuzuCard {
            Field(label = "理由", required = true) {
                TArea(
                    value = reason,
                    onValueChange = onReasonChange,
                    placeholder = "欠席する理由を入力してください",
                    rows = 5,
                )
            }
        }

        PrimaryButton(title = "確認する", enabled = canSubmit, onClick = onConfirm)
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun PreviewStage(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    targetDate: String,
    range: StudyLeaveRange?,
    reason: String,
    submitting: Boolean,
    onSubmit: () -> Unit,
    onEdit: () -> Unit,
) {
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(tokens.pill)
                    .padding(14.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    SuzuIcons.Info,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    "提出後は審査待ちとなります。",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 12.sp, lineHeight = 16.sp),
                )
            }
        }

        SuzuCard {
            PreviewRow(tokens, "欠席する日付", targetDate.ifEmpty { "—" }, first = true)
            PreviewRow(tokens, "欠席する範囲", range?.label ?: "—")
            PreviewRow(tokens, "理由", reason.ifBlank { "—" })
        }

        PrimaryButton(
            title = if (submitting) "提出中…" else "提出する",
            enabled = !submitting,
            onClick = onSubmit,
        )
        jp.tomoshibi.android.ui.components
            .GhostButton(title = "修正する", onClick = onEdit)
        Spacer(Modifier.height(20.dp))
    }
}

@Composable
private fun PreviewRow(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    label: String,
    value: String,
    first: Boolean = false,
) {
    Column {
        if (!first) {
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(0.5.dp)
                        .background(tokens.hair),
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth().padding(vertical = 12.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Text(
                label,
                color = tokens.inkSub,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.width(96.dp),
            )
            Spacer(Modifier.width(8.dp))
            Text(
                value,
                color = tokens.ink,
                style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
                modifier = Modifier.weight(1f),
            )
        }
    }
}
