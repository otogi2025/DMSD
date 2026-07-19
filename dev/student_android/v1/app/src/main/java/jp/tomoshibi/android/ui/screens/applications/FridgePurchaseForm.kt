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
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
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
import androidx.compose.ui.text.input.KeyboardType
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
import jp.tomoshibi.android.ui.components.RadioCard
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// ─────────────────────────────────────────────────────────────────────
// FridgePurchaseForm —— 冷蔵庫購入届
// 对齐 iOS DormLifeForms.swift FridgePurchaseForm；提交走 DormLifeAPI.submitFridgePurchase。
// ─────────────────────────────────────────────────────────────────────

@Composable
fun FridgePurchaseForm(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val user = state.user

    // 三态流程：edit（填写）→ preview（确认）→ done（完成）
    var stage by remember { mutableStateOf("edit") }
    var submitting by remember { mutableStateOf(false) }

    // ── §1 連絡先 ──
    var contactPhone by remember { mutableStateOf(user.phone) }
    var contactWechat by remember { mutableStateOf("") }

    // ── §2 購入製品（A / B）──
    var product by remember { mutableStateOf("A") }

    // 提交可否（iOS canSubmit）：携帯電話 trim 后非空 + product ∈ {A, B}
    val canSubmit by remember {
        derivedStateOf {
            contactPhone.trim().isNotEmpty() && (product == "A" || product == "B")
        }
    }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // PageHeader 标题「冷蔵庫購入届」；preview 阶段左键退回 edit，其它阶段出栈回上一屏
            PageHeader(
                title = "冷蔵庫購入届",
                level = 2,
                onLeft = {
                    if (stage == "preview") stage = "edit" else navController.popBackStack()
                },
            )

            when (stage) {
                "done" -> {
                    ApplyDoneBody(kindName = "冷蔵庫購入") {
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
                                contactPhone = contactPhone,
                                onContactPhone = { contactPhone = it },
                                contactWechat = contactWechat,
                                onContactWechat = { contactWechat = it },
                                product = product,
                                onProduct = { product = it },
                                canSubmit = canSubmit,
                                onList = {
                                    navController.navigate(jp.tomoshibi.android.nav.Route.FridgeList.path)
                                },
                                onConfirm = { stage = "preview" },
                            )
                        } else {
                            // preview：只读键值卡列出已填内容 + 戻る / 提出する
                            PreviewBody(
                                t = t,
                                contactPhone = contactPhone,
                                contactWechat = contactWechat,
                                product = product,
                                onSubmit = {
                                    if (submitting) return@PreviewBody
                                    scope.launch {
                                        submitting = true
                                        val tokenAtStart = store.snapshot().authToken
                                        try {
                                            DormLifeAPI.submitFridgePurchase(
                                                DormLifeAPI.FridgePurchaseBody(
                                                    contactPhone = contactPhone.trim(),
                                                    contactWechat = contactWechat.trim().takeIf { it.isNotEmpty() },
                                                    product = product,
                                                ),
                                            )
                                            if (store.snapshot().authToken != tokenAtStart) return@launch
                                            store.showToast("冷蔵庫購入届を提出しました")
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
// 编辑态正文（§1 連絡先 / §2 購入製品 / §3 注意事項 + 底部「確認する」）
// ════════════════════════════════════════════════════════════════════
@Composable
private fun EditBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    contactPhone: String,
    onContactPhone: (String) -> Unit,
    contactWechat: String,
    onContactWechat: (String) -> Unit,
    product: String,
    onProduct: (String) -> Unit,
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
        Icon(SuzuIcons.Doc, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(15.dp))
        Spacer(Modifier.width(8.dp))
        Text(
            "提出済み一覧",
            color = MaterialTheme.colorScheme.primary,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
        )
        Spacer(Modifier.weight(1f))
        Icon(SuzuIcons.ChevR, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(14.dp))
    }

    // ── §1 連絡先（携帯電話 必填 + WeChat 可选）──
    SectionLabel(t, "1", "連絡先")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "携帯電話", required = true) {
                TField(
                    value = contactPhone,
                    onValueChange = onContactPhone,
                    placeholder = "090-0000-0000",
                    keyboard = KeyboardType.Phone,
                )
            }
            Field(label = "WeChat") {
                TField(value = contactWechat, onValueChange = onContactWechat, placeholder = "WeChat ID")
            }
        }
    }

    // ── §2 購入製品（A / B 二选一 RadioCard）──
    SectionLabel(t, "2", "購入製品")
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        RadioCard(
            title = "A: BESTEK 小型 1ドア 47L",
            detail = "氷温室付き（BTMF107）約 1 万円",
            selected = product == "A",
            onClick = { onProduct("A") },
        )
        RadioCard(
            title = "B: Haier 2ドア 85L",
            detail = "直冷式（JR-N85A-W）約 2 万円。A にない小型冷凍室付き",
            selected = product == "B",
            onClick = { onProduct("B") },
        )
    }

    // ── §3 注意事項（只读 5 条带勾说明）──
    SectionLabel(t, "3", "注意事項")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            NoteLine(t, "指定された冷蔵庫のみ設置できます")
            NoteLine(t, "他の寮生との共用は禁止です")
            NoteLine(t, "庫内の衛生と賞味期限を管理してください")
            NoteLine(t, "コンセント周辺を整理し、防火に注意してください")
            NoteLine(t, "費用は原則として寮費から差し引かれます")
        }
    }

    // ── 底部「確認する」主按钮（iOS 直接「提出する」，本端三态流程改成先进确认页）──
    PrimaryButton(title = "確認する", enabled = canSubmit, onClick = onConfirm)
}

// ════════════════════════════════════════════════════════════════════
// 确认态正文（preview）—— 只读键值卡 + 顶部 info banner + 戻る / 提出する
// 対齐 iOS ApplyPreviewView
// ════════════════════════════════════════════════════════════════════
@Composable
private fun PreviewBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    contactPhone: String,
    contactWechat: String,
    product: String,
    onSubmit: () -> Unit,
    onEdit: () -> Unit,
) {
    // 蓝底信息条「ℹ 提出後は審査待ちとなります。承認されるまでは内容の変更が可能です。」
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

    // 只读键值卡（左标签 100 + 右值）
    SuzuCard(padding = 0) {
        KvRow(t, "種別", "冷蔵庫購入届", first = true)
        KvRow(t, "携帯電話", contactPhone)
        if (contactWechat.isNotBlank()) KvRow(t, "WeChat", contactWechat)
        KvRow(t, "購入製品", productText(product))
    }

    // 底部双按钮：戻る + 提出する
    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        GhostButton(title = "戻る", modifier = Modifier.weight(1f), onClick = onEdit)
        PrimaryButton(title = "提出する", modifier = Modifier.weight(1f), onClick = onSubmit)
    }
}

// ════════════════════════════════════════════════════════════════════
// 私有小组件（对齐 iOS 私有 ApplyFormSectionLabel / noteLine / KvRow）
// ════════════════════════════════════════════════════════════════════

// 区块编号标签（22×22 圆角 6 方块蓝底白字 + 区块名），对齐 iOS ApplyFormSectionLabel
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
                    .background(MaterialTheme.colorScheme.primary),
            contentAlignment = Alignment.Center,
        ) {
            Text(num, color = Color.White, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        }
        Text(label, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
    }
}

// 注意事項一条（左 primary 勾图标 + 右 12.5sp inkSub 说明），对齐 iOS noteLine
@Composable
private fun NoteLine(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    text: String,
) {
    Row(
        verticalAlignment = Alignment.Top,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Icon(
            SuzuIcons.CheckCirc,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(14.dp).padding(top = 1.dp),
        )
        Text(
            text,
            color = t.inkSub,
            style = TextStyle(fontSize = 12.5.sp, lineHeight = 17.sp),
        )
    }
}

// 确认页只读键值行（左标签固定宽 100 + 右值，支持多行）
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

// 製品代号 → 确认页显示名（对齐 iOS fridgeProductText）
private fun productText(product: String): String =
    when (product) {
        "A" -> "A: BESTEK 小型 1ドア 47L"
        "B" -> "B: Haier 2ドア 85L"
        else -> "製品$product"
    }
