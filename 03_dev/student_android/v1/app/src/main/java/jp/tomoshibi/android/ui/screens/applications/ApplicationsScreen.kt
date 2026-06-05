package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AcUnit
import androidx.compose.material.icons.outlined.Cottage
import androidx.compose.material.icons.outlined.Laptop
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 対齐 iOS ApplyListView (ApplyStubs.swift §57-145):
//   头部 = 「⌂ 申し込み」（home 图标前缀，点击回首页）
//   筛选 chip =「すべて」「審査中」「承認済」「下書き」，选中 primary 青底白字
//   申请卡 = 左类型图标块 + 类型名 + 状态徽章 / 摘要 / 细线 + 日期（等宽）
//   FAB = 右下浮 56dp 圆角 18 方形 primary 青 → 新規申請种类选择
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ApplicationsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    var filter by remember { mutableStateOf("all") }
    var kindSheetOpen by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    val filtered =
        state.applications.filter { app ->
            when (filter) {
                "all" -> true

                "pending" -> app.status == ApplicationStatus.PENDING

                // 承認済 tab 同时收「承認済」与「一部承認」（iOS 一致）
                "approved" -> app.status == ApplicationStatus.APPROVED

                "draft" -> false

                // demo 暂无「下書き」状态（接后端后按 status==draft 过滤）
                else -> true
            }
        }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Box(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            Column(modifier = Modifier.fillMaxSize()) {
                // ── 头部：⌂ home 图标 +「申し込み」（对应 iOS PageHeader level=1）──
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        modifier =
                            Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .clickable {
                                    navController.navigate(Route.Home.path) {
                                        popUpTo(Route.Home.path) { inclusive = true }
                                    }
                                },
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            imageVector = SuzuIcons.Home,
                            contentDescription = "ホームへ",
                            tint = tokens.ink,
                            modifier = Modifier.size(22.dp),
                        )
                    }
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "申し込み",
                        color = tokens.ink,
                        style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold),
                    )
                }

                // ── 4 个筛选 chip（选中 primary 青底白字 / 未选 pill 淡青底 primary 字）──
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(bottom = 16.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    listOf(
                        "all" to "すべて",
                        "pending" to "審査中",
                        "approved" to "承認済",
                        "draft" to "下書き",
                    ).forEach { (k, l) ->
                        val active = filter == k
                        Box(
                            modifier =
                                Modifier
                                    .clip(RoundedCornerShape(99.dp))
                                    .background(if (active) primary else tokens.pill)
                                    .clickable { filter = k }
                                    .padding(horizontal = 14.dp, vertical = 7.dp),
                        ) {
                            Text(
                                l,
                                color = if (active) Color.White else primary,
                                style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold),
                            )
                        }
                    }
                }

                // ── 列表 ──
                Column(
                    modifier =
                        Modifier
                            .weight(1f)
                            .fillMaxWidth()
                            .verticalScroll(rememberScrollState())
                            .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    if (filtered.isEmpty()) {
                        Column(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 60.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Text("📋", style = TextStyle(fontSize = 40.sp))
                            Text(
                                "申請はありません",
                                color = tokens.inkSub,
                                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                            )
                            Text(
                                "下の＋ボタンから新規作成できます",
                                color = tokens.inkMute,
                                style = TextStyle(fontSize = 12.sp),
                            )
                        }
                    }
                    filtered.forEach { app ->
                        ApplicationRow(
                            kind = app.kind,
                            summary = app.dest,
                            date = app.createdAt,
                            status = app.status,
                            onClick = { navController.navigate("applications/${app.id}") },
                        )
                    }
                    Spacer(Modifier.height(120.dp))
                }
            }

            // ── 右下浮 FAB（56dp 圆角 18 方形 + primary 青底，对齐 iOS）──
            Box(
                modifier =
                    Modifier
                        .align(Alignment.BottomEnd)
                        .padding(end = 18.dp, bottom = 96.dp)
                        .size(56.dp)
                        .shadow(
                            elevation = 12.dp,
                            shape = RoundedCornerShape(18.dp),
                            spotColor = primary.copy(alpha = 0.35f),
                            ambientColor = primary.copy(alpha = 0.35f),
                        ).clip(RoundedCornerShape(18.dp))
                        .background(primary)
                        .clickable { kindSheetOpen = true },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = SuzuIcons.Plus,
                    contentDescription = "新規申請",
                    tint = Color.White,
                    modifier = Modifier.size(24.dp),
                )
            }
        }
    }

    // ── 新規申請种类选择（TODO N-AND-01：iOS 是独立全屏页 ApplyNewView，此处暂用底部弹层）──
    if (kindSheetOpen) {
        ModalBottomSheet(
            onDismissRequest = { kindSheetOpen = false },
            sheetState = sheetState,
            containerColor = tokens.paper,
        ) {
            ApplyKindGrid(
                onPick = { picked ->
                    kindSheetOpen = false
                    navController.navigate(Route.ApplyNew.withKind(picked))
                },
            )
        }
    }
}

// 申请卡 — 左类型图标块 + 类型名 + 状态徽章 / 摘要 / 细线 + 日期（对齐 iOS ApplicationRow）
@Composable
private fun ApplicationRow(
    kind: String,
    summary: String,
    date: String,
    status: ApplicationStatus,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier =
                    Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(t.pill),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = iconForKind(kind),
                    contentDescription = null,
                    tint = primary,
                    modifier = Modifier.size(20.dp),
                )
            }
            Spacer(Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        kind,
                        color = t.ink,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                    )
                    Spacer(Modifier.width(8.dp))
                    ApplicationStatusPill(status)
                }
                Spacer(Modifier.height(3.dp))
                Text(
                    summary,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp),
                )
            }
        }
        Spacer(Modifier.height(8.dp))
        Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
        Spacer(Modifier.height(8.dp))
        Text(
            date,
            color = t.inkMute,
            style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
        )
    }
}

// 申请类型元数据 — 12 种，对齐 iOS APPLY_TYPES（key 英文路由用 / 名日语 / 副标题日语 / 图标）
private data class ApplyType(
    val key: String,
    val name: String,
    val sub: String,
    val icon: ImageVector,
)

private val APPLY_TYPES =
    listOf(
        ApplyType("outing", "外出", "当日帰寮の外出", SuzuIcons.Cal),
        ApplyType("stay", "外泊", "寮外での宿泊", SuzuIcons.House),
        ApplyType("holiday", "帰省", "実家帰省・長期休暇", Icons.Outlined.Cottage),
        ApplyType("returncountry", "帰国", "一時帰国（航空機利用）", SuzuIcons.Plane),
        ApplyType("repair", "修繕", "部屋・設備の修繕依頼", SuzuIcons.Wrench),
        ApplyType("parcel", "代理受取", "不在時の荷物代理受取", SuzuIcons.Box),
        ApplyType("guest", "来訪者", "家族・友人の来訪", SuzuIcons.People),
        ApplyType("studyAbsence", "学習欠席", "晚自习の欠席届（前半・後半・両方）", SuzuIcons.Book),
        ApplyType("studyOnline", "オンライン学習", "自室でのオンライン学習", Icons.Outlined.Laptop),
        ApplyType("event", "行事企画", "寮内イベントの企画申請", SuzuIcons.Sparkle),
        ApplyType("fridge", "冷蔵庫購入", "指定冷蔵庫の購入届", Icons.Outlined.AcUnit),
        ApplyType("item", "物品所持", "持込物品の許可願", SuzuIcons.Box),
    )

// 列表卡按类型日语名查图标（匹配不到取第 0 个 outing，对齐 iOS applyType 兜底）
private fun iconForKind(kind: String): ImageVector = APPLY_TYPES.firstOrNull { it.name == kind }?.icon ?: SuzuIcons.Cal

@Composable
private fun ApplyKindGrid(onPick: (String) -> Unit) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text(
            "申請の種類を選択してください",
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp),
            modifier = Modifier.padding(start = 4.dp, bottom = 14.dp),
        )
        // 6 行 × 2 列 = 12 种
        APPLY_TYPES.chunked(2).forEach { row ->
            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                row.forEach { k ->
                    Column(
                        modifier =
                            Modifier
                                .weight(1f)
                                .clip(RoundedCornerShape(16.dp))
                                .background(t.pearl)
                                .clickable { onPick(k.name) }
                                .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        Box(
                            modifier =
                                Modifier
                                    .size(52.dp)
                                    .clip(RoundedCornerShape(14.dp))
                                    .background(t.pill),
                            contentAlignment = Alignment.Center,
                        ) {
                            Icon(
                                imageVector = k.icon,
                                contentDescription = null,
                                tint = primary,
                                modifier = Modifier.size(22.dp),
                            )
                        }
                        Spacer(Modifier.height(10.dp))
                        Text(
                            k.name,
                            color = t.ink,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                        )
                        Spacer(Modifier.height(3.dp))
                        Text(
                            k.sub,
                            color = t.inkMute,
                            style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp),
                            textAlign = TextAlign.Center,
                        )
                    }
                }
                if (row.size == 1) Spacer(Modifier.weight(1f))
            }
        }
    }
}

@Composable
internal fun ApplicationStatusPill(status: ApplicationStatus) {
    val tokens = SuzuT.current
    val (label, bg, fg) =
        when (status) {
            ApplicationStatus.PENDING -> Triple("審査中", tokens.warnBg, tokens.warnDeep)

            ApplicationStatus.APPROVED -> Triple("承認済", tokens.okBg, tokens.okDeep)

            ApplicationStatus.RETURNED -> Triple("要修正", tokens.dangerBg, tokens.danger)

            // iOS rejected 标签是「差戻」（不是「却下」）
            ApplicationStatus.REJECTED -> Triple("差戻", tokens.dangerBg, tokens.danger)
        }
    Box(
        modifier =
            Modifier
                .clip(RoundedCornerShape(99.dp))
                .background(bg)
                .padding(horizontal = 10.dp, vertical = 4.dp),
    ) {
        Text(
            label,
            color = fg,
            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}
