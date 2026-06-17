package jp.tomoshibi.android.ui.screens.applications

import android.widget.Toast
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
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
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

// 「夜学習欠席届」（夜间学习请假）— 対齐 iOS ApplyStubs.swift StudyAbsenceForm（规格 §3）
//   §1 欠席する日付（DateField，规格限今日～14 日后，演示不强制）
//   §2 欠席する範囲（前半節 / 後半節 / 両方 三选一，RadioCard）
//   §3 理由（必須，TArea）
// 三态流程：edit（填写）→ preview（只读确认）→ done（完成）— 不开新路由，靠本地 stage 状态切换。

// 欠席範囲：label = 日语显示文案；wire = 发后端的值（first_half / second_half / full）
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
    val t = SuzuT.current
    val ctx = LocalContext.current

    // 三态：edit=编辑 / preview=确认 / done=完成
    var stage by remember { mutableStateOf("edit") }

    // 表单字段（本地 state 收集，不接后端）
    var targetDate by remember { mutableStateOf("") } // ISO "yyyy-MM-dd"
    var range by remember { mutableStateOf<StudyLeaveRange?>(null) }
    var reason by remember { mutableStateOf("") }

    // 必填齐全（理由 trim 后非空 + 日付已选 + 范围已选）才能进确认
    val canSubmit = targetDate.isNotEmpty() && range != null && reason.trim().isNotEmpty()

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "夜学習欠席届",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            when (stage) {
                // ── 编辑态：表单字段 + 底部「確認する」 ──
                "edit" -> {
                    EditStage(
                        tokens = t,
                        targetDate = targetDate,
                        range = range,
                        reason = reason,
                        canSubmit = canSubmit,
                        onPickDate = { targetDate = it },
                        onPickRange = { range = it },
                        onReasonChange = { reason = it },
                        onConfirm = {
                            // 理由 trim 后非空才允许（否则提示，对齐 iOS 校验）
                            if (reason.trim().isEmpty()) {
                                Toast.makeText(ctx, "理由を入力してください", Toast.LENGTH_SHORT).show()
                            } else {
                                stage = "preview"
                            }
                        },
                    )
                }

                // ── 确认态：只读键值卡 + 「提出する」/「修正する」 ──
                "preview" -> {
                    PreviewStage(
                        tokens = t,
                        targetDate = targetDate,
                        range = range,
                        reason = reason,
                        onSubmit = { stage = "done" },
                        onEdit = { stage = "edit" },
                    )
                }

                // ── 完成态：绿勾 + 预想审查时间 + 「一覧に戻る」 ──
                "done" -> {
                    DoneStage(
                        tokens = t,
                        onBack = {
                            Toast.makeText(ctx, "夜学習欠席届を提出しました", Toast.LENGTH_SHORT).show()
                            navController.popBackStack()
                        },
                    )
                }
            }
        }
    }
}

// ───────────────────────────── 编辑态 ─────────────────────────────
@Composable
private fun EditStage(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    targetDate: String,
    range: StudyLeaveRange?,
    reason: String,
    canSubmit: Boolean,
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
        // §1 欠席する日付
        SuzuCard {
            DateField(
                label = "欠席する日付",
                value = targetDate,
                required = true,
                onPick = onPickDate,
            )
            Spacer(Modifier.height(7.dp))
            // 规格：可选范围 = 今日～14 日后（演示不强制限制，仅文字说明）
            Text(
                "※ 本日から 14 日後までの日付を選択してください",
                color = tokens.inkMute,
                style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp),
            )
        }

        // §2 欠席する範囲（前半 / 後半 / 両方 三选一）
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

        // §3 理由（必須）
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

        // 底部主按钮：必填齐了才启用
        PrimaryButton(
            title = "確認する",
            enabled = canSubmit,
            onClick = onConfirm,
        )
        Spacer(Modifier.height(20.dp))
    }
}

// ───────────────────────────── 确认态 ─────────────────────────────
@Composable
private fun PreviewStage(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    targetDate: String,
    range: StudyLeaveRange?,
    reason: String,
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
        // 蓝底提示条：提出後は審査待ち（对齐 iOS 确认页）
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

        // 只读键值卡：列出已填内容
        SuzuCard {
            PreviewRow(tokens, "欠席する日付", targetDate.ifEmpty { "—" }, first = true)
            PreviewRow(tokens, "欠席する範囲", range?.label ?: "—")
            PreviewRow(tokens, "理由", reason.ifBlank { "—" })
        }

        // 「提出する」→ 完成；「修正する」→ 回编辑
        PrimaryButton(title = "提出する", onClick = onSubmit)
        jp.tomoshibi.android.ui.components
            .GhostButton(title = "修正する", onClick = onEdit)
        Spacer(Modifier.height(20.dp))
    }
}

// 只读键值行：左标签固定宽 96 + 右值；非首行顶部细线分隔
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

// ───────────────────────────── 完成态 ─────────────────────────────
@Composable
private fun DoneStage(
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
    onBack: () -> Unit,
) {
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Spacer(Modifier.height(40.dp))

        // 居中绿勾
        Box(
            modifier =
                Modifier
                    .size(72.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(tokens.okBg),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                SuzuIcons.CheckCirc,
                contentDescription = null,
                tint = tokens.okDeep,
                modifier = Modifier.size(44.dp),
            )
        }

        // 大标题
        Text(
            "申請を提出しました",
            color = tokens.ink,
            style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
        )
        Text(
            "夜学習欠席届を受け付けました。\n審査完了時に通知でお知らせします。",
            color = tokens.inkSub,
            style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
        )

        Spacer(Modifier.height(4.dp))

        // 预想审查时间卡
        SuzuCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    SuzuIcons.CalClock,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(Modifier.width(10.dp))
                Column {
                    Text(
                        "予想審査時間",
                        color = tokens.inkSub,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                    )
                    Text(
                        "1〜2 時間",
                        color = tokens.ink,
                        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                    )
                }
            }
        }

        Spacer(Modifier.height(8.dp))

        // 「一覧に戻る」→ 弹 toast 后回列表
        PrimaryButton(title = "一覧に戻る", onClick = onBack)
        Spacer(Modifier.height(20.dp))
    }
}
