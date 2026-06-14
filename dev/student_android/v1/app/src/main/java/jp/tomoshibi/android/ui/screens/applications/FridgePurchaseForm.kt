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
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
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

// ─────────────────────────────────────────────────────────────────────
// FridgePurchaseForm —— 冷蔵庫購入届
// 对齐 iOS Features/Apply/DormLifeForms.swift 第 290-429 行 struct FridgePurchaseForm。
// 字段：§1 連絡先（携帯電話 必填 + WeChat 可选）/ §2 購入製品（A・B 二选一 RadioCard）/ §3 注意事項（只读 5 条）。
// 本屏不接后端、不发网络：表单字段全用本地 state 收集，
// 提交走「编辑(edit) → 确认(preview) → 完成(done)」三个内部 stage（不开新路由），结构对齐范本 StayForm.kt。
// ─────────────────────────────────────────────────────────────────────

@Composable
fun FridgePurchaseForm(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val user = state.user

    // 三态流程：edit（填写）→ preview（确认）→ done（完成）
    var stage by remember { mutableStateOf("edit") }

    // ── §1 連絡先 ──
    // 携帯電話预填本人电话（iOS 在 .onAppear 预填 displayUser.phone；本地无冷启动假人问题，直接用 user.phone 初值）
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
                    DoneBody(navController = navController)
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
                                    // 提出する：本地完成（不发网络），切到 done。
                                    // TODO: 接后端时这里走 DormLifeAPI submitFridgePurchase POST（对齐 iOS submitAsync）。
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
    onConfirm: () -> Unit,
) {
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
            detail = "直冷式（JR-N85A-W）約 2 万円。A より小さな冷凍室があります",
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
            NoteLine(t, "費用は原則として学生納付金から差し引かれます")
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
// 完成态正文（done）—— 居中绿勾徽章 + 大标题 + 预想审查时间卡 + 一覧へ
// 対齐 iOS ApplyDoneView
// ════════════════════════════════════════════════════════════════════
@Composable
private fun DoneBody(navController: NavHostController) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 28.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        // 居中绿勾徽章（青 primary → accent secondary 对角渐变 + 白 checkmark），対齐 iOS check badge
        Box(
            modifier =
                Modifier
                    .size(96.dp)
                    .clip(RoundedCornerShape(28.dp))
                    .background(
                        Brush.linearGradient(colors = listOf(cs.primary, cs.secondary)),
                    ),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                SuzuIcons.CheckCirc,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(40.dp),
            )
        }
        Spacer(Modifier.height(22.dp))
        Text("申請を提出しました", color = t.ink, style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold))
        Spacer(Modifier.height(8.dp))
        Text(
            "冷蔵庫購入申請を受け付けました。\n審査完了時に通知でお知らせします。",
            color = t.inkSub,
            style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(28.dp))
        // 预想审查时间卡
        SuzuCard {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("予想審査時間", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
                Spacer(Modifier.weight(1f))
                Text("1〜2 時間", color = t.ink, style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold))
            }
        }
        Spacer(Modifier.height(28.dp))
        // 「一覧へ」跳申請一覧（对齐 iOS router.replace(.apply)）
        PrimaryButton(title = "一覧へ") {
            navController.navigate(jp.tomoshibi.android.nav.Route.Applications.path)
        }
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
