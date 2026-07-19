package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
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
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.DormLifeAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ApplyDoneBody
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GhostButton
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// ─────────────────────────────────────────────────────────────────────
// ItemPossessionForm —— 物品所持許可願（学生申请「持有某件物品」的许可）
// 1:1 对齐 iOS DormLifeForms.swift 第 525-838 行 struct ItemPossessionForm。
// iOS 原版只有「填写 → POST → 跳独立完成页」一条线；本 Android 屏按范本 StayForm.kt
// 的「内置三段」结构改写：edit（填写）→ preview（确认）→ done（完成），不开新路由。
// 字段：部屋番号 / 所持物品 / 所持理由 / 保護者氏名，4 项全必填。
// 提交走 DormLifeAPI.submitItemPossession。
// ─────────────────────────────────────────────────────────────────────

@Composable
fun ItemPossessionForm(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val user = state.user

    // 三态流程：edit（填写）→ preview（确认）→ done（完成）
    var stage by remember { mutableStateOf("edit") }
    var submitting by remember { mutableStateOf(false) }

    // ── 申請内容 4 字段 ──
    // 部屋番号：用本地 user.room 预填（对齐 iOS onAppear）
    var roomNo by remember { mutableStateOf(user.room) }
    var item by remember { mutableStateOf("") } // 所持物品
    var reason by remember { mutableStateOf("") } // 所持理由
    var guardianName by remember { mutableStateOf("") } // 保護者氏名

    // 提交可否（对齐 iOS canSubmit 第 535-540 行）：4 项 trim 后全非空
    val canSubmit by remember {
        derivedStateOf {
            roomNo.trim().isNotEmpty() &&
                item.trim().isNotEmpty() &&
                reason.trim().isNotEmpty() &&
                guardianName.trim().isNotEmpty()
        }
    }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // PageHeader 标题「物品所持許可願」（对齐 iOS 第 544 行）
            PageHeader(
                title = "物品所持許可願",
                level = 2,
                onLeft = {
                    // preview 阶段返回退回 edit；其它阶段直接出栈回列表
                    if (stage == "preview") stage = "edit" else navController.popBackStack()
                },
            )

            when (stage) {
                "done" -> {
                    ApplyDoneBody(kindName = "物品所持") {
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
                                roomNo = roomNo,
                                onRoomNo = { roomNo = it },
                                item = item,
                                onItem = { item = it },
                                reason = reason,
                                onReason = { reason = it },
                                guardianName = guardianName,
                                onGuardianName = { guardianName = it },
                                canSubmit = canSubmit,
                                onList = {
                                    navController.navigate(jp.tomoshibi.android.nav.Route.ItemList.path)
                                },
                                onConfirm = { stage = "preview" },
                            )
                        } else {
                            // preview：只读键值卡 + 戻る/提出する 双按钮
                            PreviewBody(
                                t = t,
                                roomNo = roomNo,
                                item = item,
                                reason = reason,
                                guardianName = guardianName,
                                onSubmit = {
                                    if (submitting) return@PreviewBody
                                    scope.launch {
                                        submitting = true
                                        val tokenAtStart = store.snapshot().authToken
                                        try {
                                            DormLifeAPI.submitItemPossession(
                                                DormLifeAPI.ItemPossessionBody(
                                                    roomNo = roomNo.trim(),
                                                    item = item.trim(),
                                                    reason = reason.trim(),
                                                    guardianName = guardianName.trim(),
                                                ),
                                            )
                                            if (store.snapshot().authToken != tokenAtStart) return@launch
                                            store.showToast("物品所持許可願を提出しました")
                                            stage = "done"
                                        } catch (e: ApiError) {
                                            if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                            store.showToast(e.display)
                                        } catch (e: Exception) {
                                            store.showToast("申請の提出に失敗しました")
                                        } finally {
                                            submitting = false
                                        }
                                    }
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
// 编辑态正文（§1 申請内容 + §2 確認事項 + 底部确认按钮）
// 对齐 iOS body 第 547-582 行
// ════════════════════════════════════════════════════════════════════
@Composable
private fun EditBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    roomNo: String,
    onRoomNo: (String) -> Unit,
    item: String,
    onItem: (String) -> Unit,
    reason: String,
    onReason: (String) -> Unit,
    guardianName: String,
    onGuardianName: (String) -> Unit,
    canSubmit: Boolean,
    onList: () -> Unit,
    onConfirm: () -> Unit,
) {
    // ── 顶部「提出済み一覧」入口（对齐 iOS listButton）──
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
            tint = androidx.compose.material3.MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(15.dp),
        )
        Spacer(Modifier.width(8.dp))
        Text(
            "提出済み一覧",
            color = androidx.compose.material3.MaterialTheme.colorScheme.primary,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
        )
        Spacer(Modifier.weight(1f))
        androidx.compose.material3.Icon(
            SuzuIcons.ChevR,
            contentDescription = null,
            tint = androidx.compose.material3.MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(14.dp),
        )
    }

    // ── §1 申請内容（4 字段全必填）──
    SectionLabel(t, "1", "申請内容")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "部屋番号", required = true) {
                TField(value = roomNo, onValueChange = onRoomNo, placeholder = "M101")
            }
            Field(label = "所持物品", required = true) {
                TField(value = item, onValueChange = onItem, placeholder = "所持したい物品")
            }
            Field(label = "所持理由", required = true) {
                TArea(value = reason, onValueChange = onReason, placeholder = "理由を入力してください", rows = 4)
            }
            Field(label = "保護者氏名", required = true) {
                TField(value = guardianName, onValueChange = onGuardianName, placeholder = "保護者氏名")
            }
        }
    }

    // ── §2 確認事項（3 条勾选提示句，只读）──
    SectionLabel(t, "2", "確認事項")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            NoteLine(t, "寮のルールを守って使用してください")
            NoteLine(t, "自分や他人の生活を妨げないようにしてください")
            NoteLine(t, "故障・紛失などの事故は本人の責任となります")
        }
    }

    PrimaryButton(title = "確認する", enabled = canSubmit, onClick = onConfirm)
}

// ════════════════════════════════════════════════════════════════════
// 确认态正文（preview）—— 只读键值卡 + 戻る / 提出する
// 对齐 iOS ApplyPreviewView（顶部 info banner + 键值卡 + 底部双按钮）
// ════════════════════════════════════════════════════════════════════
@Composable
private fun PreviewBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    roomNo: String,
    item: String,
    reason: String,
    guardianName: String,
    onSubmit: () -> Unit,
    onEdit: () -> Unit,
) {
    // 蓝底信息条（对齐 iOS ApplyPreviewView 顶部 banner）
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

    // 只读键值卡（左标签固定宽 100 + 右值）
    SuzuCard(padding = 0) {
        KvRow(t, "種別", "物品所持許可願", first = true)
        KvRow(t, "部屋番号", roomNo)
        KvRow(t, "所持物品", item)
        KvRow(t, "所持理由", reason)
        KvRow(t, "保護者氏名", guardianName)
    }

    // 底部双按钮（对齐 iOS ApplyPreviewView 底部「戻る」+「提出する」）
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        GhostButton(title = "戻る", modifier = Modifier.weight(1f), onClick = onEdit)
        PrimaryButton(title = "提出する", modifier = Modifier.weight(1f), onClick = onSubmit)
    }
}

// ════════════════════════════════════════════════════════════════════
// 私有小组件
// ════════════════════════════════════════════════════════════════════

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
                    .background(androidx.compose.material3.MaterialTheme.colorScheme.primary),
            contentAlignment = Alignment.Center,
        ) {
            Text(num, color = Color.White, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        }
        Text(label, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
    }
}

@Composable
private fun NoteLine(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    text: String,
) {
    Row(verticalAlignment = Alignment.Top, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        androidx.compose.material3.Icon(
            SuzuIcons.CheckCirc,
            contentDescription = null,
            tint = androidx.compose.material3.MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(14.dp).padding(top = 1.dp),
        )
        Text(
            text,
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
        )
    }
}

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
