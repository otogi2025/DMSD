package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.StayApplication
import jp.tomoshibi.android.data.model.StayKind
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ChipGroup
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT

// ─────────────────────────────────────────────────────────────────────
// StayEditScreen —— 出寮届 变更届（编辑已提交的出寮届）
// 1:1 对齐 iOS StayEditForm（StayListStubs.swift 行 1172-1786）。
// 用 id 从 MockData.DEFAULT_STAY_APPLICATIONS 取那条做初值预填。
// iOS 版接后端（PUT /applications/:id）；本屏只做本地 UI，提交后直接返回。
// 区块顺序照 iOS body：警告横幅 → 申請者本人（变更不可）→ 出寮/帰寮日 → 移動方法
//   →（外泊/帰国才有）宿泊先 →「変更の理由」（必填）→ 提交行。
// ─────────────────────────────────────────────────────────────────────

// 出寮方法（去程）选项 —— 跟 StayForm 的 LEAVE_METHODS 一致（iOS StayEditForm LEAVE_TRANSPORTS）
private val EDIT_LEAVE_TRANSPORTS =
    listOf(
        "西口1便",
        "西口2便",
        "金川1便",
        "金川2便",
        "寮生特別運行",
        "JR",
        "自家用車",
        "タクシー",
        "教員",
        "その他",
    )

// 帰寮方法（回程）选项 —— 跟 StayForm 的 RETURN_METHODS 一致（iOS StayEditForm RETURN_TRANSPORTS）
private val EDIT_RETURN_TRANSPORTS =
    listOf(
        "西口登校便",
        "金川登校便",
        "寮生特別運行",
        "JR",
        "自家用車",
        "タクシー",
        "教員",
        "その他",
    )

@Composable
fun StayEditScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val user = state.user

    // 用 id 取原届做初值；找不到就用一条占位（iOS 里是 original 的 nil 兜底）
    val original: StayApplication =
        remember(id) {
            MockData.DEFAULT_STAY_APPLICATIONS.firstOrNull { it.id == id }
                ?: StayApplication(
                    id = id,
                    kind = StayKind.STAY.label,
                    status = "PENDING",
                    leaveDate = "—",
                    returnDate = null,
                    summary = "—",
                    submittedAt = "—",
                )
        }

    // needsDestination：外泊 / 帰国 才填宿泊先（对齐 iOS needsDestination = kind == .stay || .return）
    val needsDestination = original.kind == StayKind.STAY.label || original.kind == StayKind.RETURN.label

    // ── 編集対象（从 original 预填）──
    var leaveDate by remember { mutableStateOf(original.leaveDate.takeIf { it != "—" } ?: "") }
    var returnDate by remember { mutableStateOf(original.returnDate ?: (original.leaveDate.takeIf { it != "—" } ?: "")) }
    var leaveMethod by remember { mutableStateOf(original.leaveMethod ?: "JR") }
    var returnMethod by remember { mutableStateOf(original.returnMethod ?: "JR") }
    var destination by remember { mutableStateOf(original.destination ?: "") }
    var amendReason by remember { mutableStateOf("") }

    // 可提交：变更理由非空 +（有帰寮日时）帰寮日不早于出寮日（对齐 iOS canSubmit）
    val canSubmit =
        amendReason.trim().isNotEmpty() &&
            (returnDate.isEmpty() || leaveDate.isEmpty() || returnDate >= leaveDate)

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            // 标题「外泊届の変更」（iOS：「\(kind)届の変更」level 3）
            PageHeader(
                title = "${original.kind}届の変更",
                level = 3,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp, vertical = 12.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp),
            ) {
                // ── 警告横幅 ──「変更届を提出すると、承認の流れが最初からやり直しになります。」
                WarningBanner()

                // ── 申請者本人（変更不可）──
                SectionLabel("申請者本人（変更不可）")
                SuzuCard(padding = 0) {
                    Column(modifier = Modifier.fillMaxWidth()) {
                        IdRow("学号", user.studentNo, isFirst = true)
                        IdRow("氏名", user.name)
                        IdRow("学年・組", user.gradeClass)
                        IdRow("寮・部屋", "${user.dorm} ${user.room}")
                        IdRow("区分", user.category)
                        IdRow("携帯電話", user.phone)
                    }
                }
                Text(
                    "※ 個人情報の変更は寮監にご連絡ください。変更届では変更できません。",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )

                // ── 出寮 / 帰寮日 ──
                SectionLabel("出寮 / 帰寮日")
                SuzuCard(padding = 14) {
                    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        DateField(
                            label = "出寮日",
                            value = leaveDate,
                            onPick = { leaveDate = it },
                        )
                        original.leaveDate.takeIf { it != "—" }?.let { OriginalNote("原値", it) }
                        DateField(
                            label = "帰寮日",
                            value = returnDate,
                            onPick = { returnDate = it },
                        )
                        original.returnDate?.let { OriginalNote("原値", it) }
                    }
                }

                // ── 移動方法 ──
                SectionLabel("移動方法")
                SuzuCard(padding = 14) {
                    Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Text(
                                "出寮方法",
                                color = t.inkSub,
                                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                            )
                            ChipGroup(
                                options = EDIT_LEAVE_TRANSPORTS,
                                selected = leaveMethod,
                                onSelect = { leaveMethod = it },
                            )
                            original.leaveMethod?.takeIf { it != leaveMethod }?.let { OriginalNote("原値", it) }
                        }
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Text(
                                "帰寮方法",
                                color = t.inkSub,
                                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                            )
                            ChipGroup(
                                options = EDIT_RETURN_TRANSPORTS,
                                selected = returnMethod,
                                onSelect = { returnMethod = it },
                            )
                            original.returnMethod?.takeIf { it != returnMethod }?.let { OriginalNote("原値", it) }
                        }
                    }
                }

                // ── 宿泊先（仅外泊 / 帰国）──
                if (needsDestination) {
                    SectionLabel("宿泊先")
                    SuzuCard(padding = 14) {
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            TField(
                                value = destination,
                                onValueChange = { destination = it },
                                placeholder = "宿泊先住所",
                            )
                            original.destination?.takeIf { it != destination }?.let { OriginalNote("原値", it) }
                        }
                    }
                }

                // ── 「変更の理由」（必填）──
                Row(verticalAlignment = Alignment.CenterVertically) {
                    SectionLabel("変更の理由")
                    Text(
                        " *",
                        color = t.danger,
                        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
                    )
                }
                TArea(
                    value = amendReason,
                    onValueChange = { amendReason = it },
                    placeholder = "変更の理由を入力してください",
                    rows = 4,
                )
                Text(
                    "※ 各役職の先生にこの理由が表示されます。",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )

                // ── 提交行：「キャンセル」（次按钮）+「変更届を提出」（主按钮）──
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    GhostButton(
                        title = "キャンセル",
                        modifier = Modifier.weight(1f),
                        onClick = { navController.popBackStack() },
                    )
                    PrimaryButton(
                        title = "変更届を提出",
                        modifier = Modifier.weight(1f),
                        enabled = canSubmit,
                        // 本地无网络：点了直接返回。
                        // TODO: 真接后端时改成 PUT /applications/:id（iOS StayEditForm.submitAsync 走 ApplicationsAPI.update）
                        onClick = { navController.popBackStack() },
                    )
                }

                Spacer(Modifier.height(8.dp))
            }
        }
    }
}

// 警告横幅 —「変更届を提出すると、承認の流れが最初からやり直しになります。」（iOS warningBanner）
@Composable
private fun WarningBanner() {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.warnBg)
                .border(1.dp, t.warn, RoundedCornerShape(12.dp))
                .padding(horizontal = 14.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.Top,
    ) {
        // 警告三角图标位（iOS 用 SF Symbol exclamationmark.triangle.fill；这里用同义 emoji 占位）
        Text("⚠️", color = t.warnDeep, style = TextStyle(fontSize = 13.sp))
        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text(
                "変更届を提出すると、承認の流れが最初からやり直しになります。",
                color = t.warnDeep,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
            )
            Text(
                "先にご承認いただいた先生にも、もう一度ご承認をお願いすることになります。",
                color = t.warnDeep,
                style = TextStyle(fontSize = 11.5.sp, lineHeight = 16.sp),
            )
        }
    }
}

// 区块小标题（iOS sectionLabel：13 bold inkSub）
@Composable
private fun SectionLabel(text: String) {
    val t = SuzuT.current
    Text(
        text,
        color = t.inkSub,
        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.5.sp),
    )
}

// 身份信息一行（iOS idRow：左 90 宽标签 inkSub + 右值 ink，行间细线）
@Composable
private fun IdRow(
    k: String,
    v: String,
    isFirst: Boolean = false,
) {
    val t = SuzuT.current
    Column(modifier = Modifier.fillMaxWidth()) {
        if (!isFirst) {
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(1.dp)
                        .background(t.hair),
            )
        }
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 13.dp),
            verticalAlignment = Alignment.Top,
        ) {
            Text(
                k,
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp),
                modifier = Modifier.width(90.dp),
            )
            Text(
                v,
                color = t.ink,
                style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Medium),
                modifier = Modifier.weight(1f),
            )
        }
    }
}

// 原値小标（iOS originalNote：左 pill 胶囊「原値」+ 右值 inkMute）
@Composable
private fun OriginalNote(
    label: String,
    text: String,
) {
    val t = SuzuT.current
    Row(
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(percent = 50))
                    .background(t.pill)
                    .padding(horizontal = 6.dp, vertical = 1.dp),
        ) {
            Text(
                label,
                color = t.inkMute,
                style = TextStyle(fontSize = 10.5.sp, fontWeight = FontWeight.SemiBold),
            )
        }
        Text(text, color = t.inkMute, style = TextStyle(fontSize = 11.sp))
    }
}
