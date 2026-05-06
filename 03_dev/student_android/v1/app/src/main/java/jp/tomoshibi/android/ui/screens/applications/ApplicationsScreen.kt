package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
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
//   header = 「⌂ 申し込み」(Home icon prefix, 点击 → nav Home)
//   chip   = すべて / 審査中 / 承認済 / 下書き  (NOT 却下/差戻 — 那是 detail 状态 pill)
//   + FAB  = 右下浮 56dp 圆 teal 渐变 → ApplyNew (NOT 右上 IconButton)
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ApplicationsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    var filter by remember { mutableStateOf("all") }
    var kindSheetOpen by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    val filtered = state.applications.filter { app ->
        when (filter) {
            "all" -> true
            "pending" -> app.status == ApplicationStatus.PENDING
            "approved" -> app.status == ApplicationStatus.APPROVED
            "draft" -> false  // demo 暂无下書き state
            else -> true
        }
    }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Box(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            Column(modifier = Modifier.fillMaxSize()) {
                // ── header: ⌂ home icon prefix + 「申し込み」── 对应 iOS PageHeader level=1
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .clickable {
                                navController.navigate(Route.Home.path) {
                                    popUpTo(Route.Home.path) { inclusive = true }
                                }
                            },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = SuzuIcons.Home,
                            contentDescription = "ホームへ",
                            tint = tokens.ink,
                            modifier = Modifier.size(22.dp)
                        )
                    }
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "申し込み", color = tokens.ink,
                        style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold)
                    )
                }

                // ── 4-tab pill filter — iOS chip style ──
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(bottom = 16.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    listOf(
                        "all" to "すべて",
                        "pending" to "審査中",
                        "approved" to "承認済",
                        "draft" to "下書き"
                    ).forEach { (k, l) ->
                        val active = filter == k
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(99.dp))
                                .background(if (active) tokens.ink else tokens.paper)
                                .then(if (active) Modifier else Modifier.border(1.dp, tokens.hair, RoundedCornerShape(99.dp)))
                                .clickable { filter = k }
                                .padding(horizontal = 14.dp, vertical = 8.dp)
                        ) {
                            Text(
                                l,
                                color = if (active) tokens.pearl else tokens.inkSub,
                                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                            )
                        }
                    }
                }

                // ── list ──
                Column(
                    modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    if (filtered.isEmpty()) {
                        Box(
                            modifier = Modifier.fillMaxWidth().padding(vertical = 60.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                "該当する申請はありません", color = tokens.inkMute,
                                style = TextStyle(fontSize = 14.sp)
                            )
                        }
                    }
                    filtered.forEach { app ->
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(14.dp))
                                .background(tokens.paper)
                                .clickable { navController.navigate("applications/${app.id}") }
                                .padding(16.dp)
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(6.dp))
                                        .background(tokens.pill)
                                        .padding(horizontal = 8.dp, vertical = 2.dp)
                                ) {
                                    Text(
                                        app.kind, color = tokens.ink,
                                        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                    )
                                }
                                Spacer(Modifier.width(8.dp))
                                ApplicationStatusPill(app.status)
                                Spacer(Modifier.weight(1f))
                                Text("#${app.id}", color = tokens.inkMute, style = TextStyle(fontSize = 11.sp))
                            }
                            Spacer(Modifier.height(8.dp))
                            Text(
                                app.dest, color = tokens.ink,
                                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold)
                            )
                            Spacer(Modifier.height(4.dp))
                            Text(
                                text = if (app.from == app.to) app.from else "${app.from} 〜 ${app.to}",
                                color = tokens.inkSub,
                                style = TextStyle(fontSize = 13.sp)
                            )
                        }
                    }
                    Spacer(Modifier.height(20.dp))
                }
            }

            // ── 右下浮 FAB（iOS 风格）──
            Box(
                modifier = Modifier
                    .align(Alignment.BottomEnd)
                    .padding(end = 20.dp, bottom = 20.dp)
                    .size(56.dp)
                    .shadow(
                        elevation = 8.dp,
                        shape = CircleShape,
                        spotColor = Color.Black.copy(alpha = 0.18f),
                        ambientColor = Color.Black.copy(alpha = 0.18f)
                    )
                    .clip(CircleShape)
                    .background(tokens.btnGrad)
                    .clickable { kindSheetOpen = true },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = SuzuIcons.Plus,
                    contentDescription = "新規申請",
                    tint = Color.White,
                    modifier = Modifier.size(26.dp)
                )
            }
        }
    }

    // ── Kind picker bottom sheet — iOS ApplyNewView 2-col grid ──
    if (kindSheetOpen) {
        ModalBottomSheet(
            onDismissRequest = { kindSheetOpen = false },
            sheetState = sheetState,
            containerColor = tokens.paper
        ) {
            ApplyKindGrid(
                onPick = { picked ->
                    kindSheetOpen = false
                    navController.navigate(Route.ApplyNew.withKind(picked))
                }
            )
        }
    }
}

private data class KindMeta(val key: String, val name: String, val desc: String)
private val APPLY_KINDS = listOf(
    KindMeta("外出", "外出", "当日帰寮の外出"),
    KindMeta("外泊", "外泊", "寮外での宿泊"),
    KindMeta("帰省", "帰省", "実家帰省・長期休暇"),
    KindMeta("帰国", "帰国", "一時帰国（航空機利用）"),
    KindMeta("早帰", "早帰", "門限前の早帰・遅帰"),
    KindMeta("修繕", "修繕", "部屋・設備の修繕依頼"),
    KindMeta("代理受取", "代理受取", "不在時の荷物代理受取"),
    KindMeta("来訪者", "来訪者", "家族・友人の来訪"),
    KindMeta("学習", "学習", "自習室・学習関連"),
    KindMeta("その他", "その他", "その他の申請")
)

@Composable
private fun ApplyKindGrid(onPick: (String) -> Unit) {
    val t = SuzuT.current
    Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
        Text(
            "申請の種類を選択してください", color = t.inkSub,
            style = TextStyle(fontSize = 13.sp),
            modifier = Modifier.padding(start = 4.dp, bottom = 14.dp)
        )
        // 5 行 × 2 列
        APPLY_KINDS.chunked(2).forEach { row ->
            Row(
                modifier = Modifier.fillMaxWidth().padding(bottom = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                row.forEach { k ->
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .clip(RoundedCornerShape(16.dp))
                            .background(t.pearl)
                            .clickable { onPick(k.key) }
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Box(
                            modifier = Modifier
                                .size(52.dp)
                                .clip(RoundedCornerShape(14.dp))
                                .background(t.pill),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                k.name.firstOrNull()?.toString() ?: "",
                                color = t.ink,
                                style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold)
                            )
                        }
                        Spacer(Modifier.height(10.dp))
                        Text(
                            k.name, color = t.ink,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold)
                        )
                        Spacer(Modifier.height(3.dp))
                        Text(
                            k.desc, color = t.inkMute,
                            style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp),
                            textAlign = androidx.compose.ui.text.style.TextAlign.Center
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
    val (label, bg, fg) = when (status) {
        ApplicationStatus.PENDING -> Triple("審査中", tokens.warnBg, tokens.warnDeep)
        ApplicationStatus.APPROVED -> Triple("承認済", tokens.okBg, tokens.okDeep)
        ApplicationStatus.RETURNED -> Triple("要修正", tokens.dangerBg, tokens.danger)
        ApplicationStatus.REJECTED -> Triple("却下", tokens.dangerBg, tokens.danger)
    }
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(6.dp))
            .background(bg)
            .padding(horizontal = 8.dp, vertical = 2.dp)
    ) {
        Text(
            label, color = fg,
            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold)
        )
    }
}
