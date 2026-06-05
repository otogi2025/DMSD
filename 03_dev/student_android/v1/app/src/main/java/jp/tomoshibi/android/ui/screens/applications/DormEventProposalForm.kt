package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.components.TimeField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// ─────────────────────────────────────────────────────────────────────
// DormEventProposalForm —— 行事企画書（寮内イベント企画申請）
// 1:1 对齐 iOS DormLifeForms.swift 第 6-289 行 struct DormEventProposalForm。
// 种类固定为「行事企画」（无 kind 参数）。
// 三段内部流程（不开新路由）：edit（填写）→ preview（确认）→ done（完成），
// 跟 StayForm.kt 同一套 stage state 切换骨架。本屏不接后端、不发网络，
// 「提出する」只把 stage 切到 done（真实 POST 待后端 —— iOS 走 DormLifeAPI.submitEventProposal）。
// 区块（对齐 iOS ApplyFormSectionLabel 编号）：
//   §1 企画（起案団体名 / 企画名*）
//   §2 実施情報（実施日時* / 実施場所* / 予想参加人数* / 参加対象*）
//   §3 内容（目的* / 企画内容*）
//   §4 確認事項（予想問題点と解決策* / 予想経費* / その他）
// ─────────────────────────────────────────────────────────────────────

@Composable
fun DormEventProposalForm(navController: NavHostController) {
    val t = SuzuT.current

    // 种类名（PageHeader 标题 + 完成页都用）—— 固定为「行事企画」
    val kindName = "行事企画"

    // 三态流程：edit（填写）→ preview（确认）→ done（完成）
    var stage by remember { mutableStateOf("edit") }

    // ── §1 企画 ──
    var teamName by remember { mutableStateOf("") } // 起案団体名（个人时可空，对齐 iOS team_name nilIfBlank）
    var title by remember { mutableStateOf("") } // 企画名（必填）

    // ── §2 実施情報 ──
    var heldDate by remember { mutableStateOf("") } // 実施日（DateField 回传 ISO「yyyy-MM-dd」）
    var heldTime by remember { mutableStateOf("19:00") } // 実施時刻（iOS 默认 parseHM("19:00")）
    var place by remember { mutableStateOf("") } // 実施場所（必填）
    var expectedCountText by remember { mutableStateOf("") } // 予想参加人数（必填，数字）
    var target by remember { mutableStateOf("") } // 参加対象（必填）

    // ── §3 内容 ──
    var purpose by remember { mutableStateOf("") } // 目的（必填）
    var content by remember { mutableStateOf("") } // 企画内容（必填）

    // ── §4 確認事項 ──
    var riskSolution by remember { mutableStateOf("") } // 予想問題点と解決策（必填）
    var expectedCost by remember { mutableStateOf("") } // 予想経費（必填）
    var note by remember { mutableStateOf("") } // その他（可空，对齐 iOS note nilIfBlank）

    // 予想参加人数 解析成整数（对齐 iOS expectedCount: Int?）—— 空 / 非数字 → null
    val expectedCount by remember {
        derivedStateOf { expectedCountText.trim().toIntOrNull() }
    }

    // 提交可否（对齐 iOS canSubmit）：企画名 / 実施場所 / 参加対象 / 目的 / 企画内容 /
    // 予想問題点と解決策 / 予想経費 全非空 + 予想参加人数为非负整数
    val canSubmit by remember {
        derivedStateOf {
            if (title.trim().isEmpty()) return@derivedStateOf false
            if (place.trim().isEmpty()) return@derivedStateOf false
            val cnt = expectedCount ?: return@derivedStateOf false
            if (cnt < 0) return@derivedStateOf false
            if (target.trim().isEmpty()) return@derivedStateOf false
            if (purpose.trim().isEmpty()) return@derivedStateOf false
            if (content.trim().isEmpty()) return@derivedStateOf false
            if (riskSolution.trim().isEmpty()) return@derivedStateOf false
            if (expectedCost.trim().isEmpty()) return@derivedStateOf false
            true
        }
    }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // PageHeader 标题「行事企画申請」（对齐 iOS PageHeader title）
            PageHeader(
                title = "行事企画申請",
                level = 2,
                onLeft = {
                    // preview 阶段返回退回 edit；其它阶段直接出栈回列表
                    if (stage == "preview") stage = "edit" else navController.popBackStack()
                },
            )

            when (stage) {
                "done" -> {
                    DoneBody(kindName = kindName) {
                        // 「一覧へ」→ 回申请一覧（对齐 prompt：navigate Route.Applications.path）
                        navController.navigate(jp.tomoshibi.android.nav.Route.Applications.path)
                    }
                }

                else -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                    ) {
                        Spacer(Modifier.height(2.dp))

                        if (stage == "edit") {
                            EditBody(
                                t = t,
                                teamName = teamName,
                                onTeamName = { teamName = it },
                                title = title,
                                onTitle = { title = it },
                                heldDate = heldDate,
                                onHeldDate = { heldDate = it },
                                heldTime = heldTime,
                                onHeldTime = { heldTime = it },
                                place = place,
                                onPlace = { place = it },
                                expectedCountText = expectedCountText,
                                onExpectedCountText = { expectedCountText = it },
                                target = target,
                                onTarget = { target = it },
                                purpose = purpose,
                                onPurpose = { purpose = it },
                                content = content,
                                onContent = { content = it },
                                riskSolution = riskSolution,
                                onRiskSolution = { riskSolution = it },
                                expectedCost = expectedCost,
                                onExpectedCost = { expectedCost = it },
                                note = note,
                                onNote = { note = it },
                                onList = {
                                    // 「提出済み一覧」→ 行事企画一覧（已就绪路由 DormEventList，对齐 iOS router.go(.dormEventList)）
                                    navController.navigate(jp.tomoshibi.android.nav.Route.DormEventList.path)
                                },
                                canSubmit = canSubmit,
                                onConfirm = { stage = "preview" },
                            )
                        } else {
                            // preview：只读键值卡列出已填内容 + 戻る/提出する 双按钮
                            PreviewBody(
                                t = t,
                                kindName = kindName,
                                teamName = teamName,
                                title = title,
                                heldDate = heldDate,
                                heldTime = heldTime,
                                place = place,
                                expectedCountText = expectedCountText,
                                target = target,
                                purpose = purpose,
                                content = content,
                                riskSolution = riskSolution,
                                expectedCost = expectedCost,
                                note = note,
                                onSubmit = {
                                    // 提出する：本地完成（不发网络）—— 真实 POST 待后端，进 done
                                    stage = "done"
                                },
                                onEdit = { stage = "edit" },
                            )
                        }

                        Spacer(Modifier.height(40.dp))
                    }
                }
            }
        }
    }
}

// ════════════════════════════════════════════════════════════════════
// 编辑态正文（§1～§4 + 底部双按钮）
// ════════════════════════════════════════════════════════════════════
@Composable
private fun EditBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    teamName: String,
    onTeamName: (String) -> Unit,
    title: String,
    onTitle: (String) -> Unit,
    heldDate: String,
    onHeldDate: (String) -> Unit,
    heldTime: String,
    onHeldTime: (String) -> Unit,
    place: String,
    onPlace: (String) -> Unit,
    expectedCountText: String,
    onExpectedCountText: (String) -> Unit,
    target: String,
    onTarget: (String) -> Unit,
    purpose: String,
    onPurpose: (String) -> Unit,
    content: String,
    onContent: (String) -> Unit,
    riskSolution: String,
    onRiskSolution: (String) -> Unit,
    expectedCost: String,
    onExpectedCost: (String) -> Unit,
    note: String,
    onNote: (String) -> Unit,
    onList: () -> Unit,
    canSubmit: Boolean,
    onConfirm: () -> Unit,
) {
    // ── 顶部「提出済み一覧」链接卡（淡蓝底，对齐 iOS listButton）──
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.pill)
                .clickable(onClick = onList)
                .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        androidx.compose.material3.Icon(
            SuzuIcons.Doc,
            contentDescription = null,
            tint = MaterialPrimary(),
            modifier = Modifier.size(15.dp),
        )
        Spacer(Modifier.width(8.dp))
        Text("提出済み一覧", color = MaterialPrimary(), style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        Spacer(Modifier.weight(1f))
        androidx.compose.material3.Icon(
            SuzuIcons.ChevR,
            contentDescription = null,
            tint = MaterialPrimary(),
            modifier = Modifier.size(14.dp),
        )
    }

    // ── §1 企画 ──
    SectionLabel(t, "1", "企画")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "起案団体名") {
                TField(value = teamName, onValueChange = onTeamName, placeholder = "団体名（個人の場合は空欄）")
            }
            Field(label = "企画名", required = true) {
                TField(value = title, onValueChange = onTitle, placeholder = "企画名")
            }
        }
    }

    // ── §2 実施情報 ──
    SectionLabel(t, "2", "実施情報")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            // 実施日時（必填）—— 日 + 時刻 横排
            Field(label = "実施日時", required = true) {
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    DateField(label = "", value = heldDate, modifier = Modifier.weight(1f), onPick = onHeldDate)
                    TimeField(label = "", value = heldTime, modifier = Modifier.weight(1f), onPick = onHeldTime)
                }
            }
            Field(label = "実施場所", required = true) {
                TField(value = place, onValueChange = onPlace, placeholder = "実施場所")
            }
            Field(label = "予想参加人数", required = true) {
                TField(
                    value = expectedCountText,
                    onValueChange = onExpectedCountText,
                    placeholder = "0",
                    keyboard = KeyboardType.Number,
                )
            }
            Field(label = "参加対象", required = true) {
                TField(value = target, onValueChange = onTarget, placeholder = "例：寮生全員 / 高校生 / 希望者")
            }
        }
    }

    // ── §3 内容 ──
    SectionLabel(t, "3", "内容")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "目的", required = true) {
                TArea(value = purpose, onValueChange = onPurpose, placeholder = "企画の目的", rows = 4)
            }
            // 企画内容：iOS 带 hint「時間表も含めて入力してください」
            Field(label = "企画内容", required = true, hint = "時間表も含めて入力してください") {
                TArea(value = content, onValueChange = onContent, placeholder = "具体的な内容・時間表", rows = 6)
            }
        }
    }

    // ── §4 確認事項 ──
    SectionLabel(t, "4", "確認事項")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "予想問題点と解決策", required = true) {
                TArea(value = riskSolution, onValueChange = onRiskSolution, placeholder = "予想される問題と対応策", rows = 5)
            }
            Field(label = "予想経費", required = true) {
                TArea(value = expectedCost, onValueChange = onExpectedCost, placeholder = "必要な費用・内訳", rows = 3)
            }
            Field(label = "その他") {
                TArea(value = note, onValueChange = onNote, placeholder = "補足事項", rows = 3)
            }
        }
    }

    // ── 底部「確認する」主按钮（三态骨架：edit 段右键为「確認する」切到 preview）──
    PrimaryButton(title = "確認する", enabled = canSubmit, onClick = onConfirm)
}

// ════════════════════════════════════════════════════════════════════
// 确认态正文（preview）—— 顶部 info banner + 只读键值卡 + 戻る / 提出する
// 对齐 iOS ApplyPreviewView
// ════════════════════════════════════════════════════════════════════
@Composable
private fun PreviewBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    kindName: String,
    teamName: String,
    title: String,
    heldDate: String,
    heldTime: String,
    place: String,
    expectedCountText: String,
    target: String,
    purpose: String,
    content: String,
    riskSolution: String,
    expectedCost: String,
    note: String,
    onSubmit: () -> Unit,
    onEdit: () -> Unit,
) {
    // 蓝底信息条（对齐 iOS ApplyPreviewView 顶部 info banner）
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.pill)
                .padding(14.dp),
    ) {
        Text(
            "ℹ 提出後は審査待ちとなります。承認されるまでは内容の変更が可能です。",
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
        )
    }

    Text("申請内容の確認", color = t.ink, style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold))

    // 只读键值卡
    SuzuCard(padding = 0) {
        KvRow(t, "種別", "${kindName}申請", first = true)
        if (teamName.isNotBlank()) KvRow(t, "起案団体名", teamName)
        KvRow(t, "企画名", dash(title))
        KvRow(t, "実施日時", "${dash(heldDate)} ${dash(heldTime)}")
        KvRow(t, "実施場所", dash(place))
        KvRow(t, "予想参加人数", "${dash(expectedCountText)}名")
        KvRow(t, "参加対象", dash(target))
        KvRow(t, "目的", dash(purpose))
        KvRow(t, "企画内容", dash(content))
        KvRow(t, "予想問題点と解決策", dash(riskSolution))
        KvRow(t, "予想経費", dash(expectedCost))
        if (note.isNotBlank()) KvRow(t, "その他", note)
    }

    // 底部双按钮：戻る（修正回 edit）+ 提出する
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        GhostButton(title = "戻る", modifier = Modifier.weight(1f), onClick = onEdit)
        PrimaryButton(title = "提出する", modifier = Modifier.weight(1f), onClick = onSubmit)
    }
}

// ════════════════════════════════════════════════════════════════════
// 完成态正文（done）—— 居中绿勾徽章 + 大标题 + 预想审查时间卡 + 一覧へ
// 对齐 iOS ApplyDoneView
// ════════════════════════════════════════════════════════════════════
@Composable
private fun DoneBody(
    kindName: String,
    onBack: () -> Unit,
) {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Spacer(Modifier.height(40.dp))
        // 居中绿勾徽章（圆形渐变底 + 白勾，青→accent 渐变对齐 iOS ApplyDoneView）
        Box(
            modifier =
                Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(t.okBg),
            contentAlignment = Alignment.Center,
        ) {
            androidx.compose.material3.Icon(
                SuzuIcons.CheckCirc,
                contentDescription = null,
                tint = t.okDeep,
                modifier = Modifier.size(48.dp),
            )
        }
        Text("申請を提出しました", color = t.ink, style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold))
        Text(
            "${kindName}申請を受け付けました。\n審査完了時に通知でお知らせします。",
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center,
        )
        // 预想审查时间卡
        SuzuCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                androidx.compose.material3.Icon(
                    SuzuIcons.CalClock,
                    contentDescription = null,
                    tint = t.inkSub,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(Modifier.width(10.dp))
                Column {
                    Text("予想審査時間", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
                    Text("1〜2 時間", color = t.ink, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold))
                }
            }
        }
        Spacer(Modifier.height(8.dp))
        PrimaryButton(title = "一覧へ", onClick = onBack)
        Spacer(Modifier.height(40.dp))
    }
}

// ════════════════════════════════════════════════════════════════════
// 私有小组件（对齐 iOS ApplyFormSectionLabel + StayForm.kt 私有 KvRow）
// ════════════════════════════════════════════════════════════════════

// 区块编号标签（22×22 圆角 6 方块蓝底白字 + 区块名）
@Composable
private fun SectionLabel(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    num: String,
    label: String,
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(22.dp)
                    .clip(RoundedCornerShape(6.dp))
                    .background(MaterialPrimary()),
            contentAlignment = Alignment.Center,
        ) {
            Text(num, color = Color.White, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        }
        Text(label, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
    }
}

// 确认页只读键值行（左标签固定宽 100 + 右值，支持多行；非首行顶部 0.5 细线分隔）
@Composable
private fun KvRow(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    label: String,
    value: String,
    first: Boolean = false,
) {
    if (!first) {
        Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
    }
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Text(label, color = t.inkSub, modifier = Modifier.width(100.dp), style = TextStyle(fontSize = 12.sp))
        Text(value, color = t.ink, modifier = Modifier.weight(1f), style = TextStyle(fontSize = 14.sp, lineHeight = 19.sp))
    }
}

// 主色短手（区块编号方块 / 一覧链接 用，避免每处都写 MaterialTheme.colorScheme.primary）
@Composable
private fun MaterialPrimary(): Color = androidx.compose.material3.MaterialTheme.colorScheme.primary

// 预览空值占位（"" → "—"，null → "—"）
private fun dash(s: String?): String = if (s.isNullOrBlank()) "—" else s
