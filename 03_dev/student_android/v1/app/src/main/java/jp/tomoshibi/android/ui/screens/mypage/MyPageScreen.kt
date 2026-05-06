package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 5 个 emoji grid 块 — 对应 iOS 截图 21.55.41 的 2 列 × 3 行（最后一行只有 1 块）
private data class GridBlock(val emoji: String, val label: String, val route: String, val badge: String? = null)

// 列表行项 — 行事 / 特別運航便 / 通知設定 等
private data class ListRowItem(val label: String, val route: String? = null, val danger: Boolean = false, val onClick: (() -> Unit)? = null)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyPageScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    var showLogoutSheet by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState()

    val deductionTotal = state.deductions.sumOf { it.points }
    val grids = listOf(
        GridBlock("😷", "体調報告履歴", Route.Home.path),
        GridBlock("📄", "申請履歴", Route.Applications.path),
        GridBlock("🧹", "掃除提出履歴", Route.Home.path),
        GridBlock("📦", "荷物受取履歴", Route.Delivery.path, badge = "1"),
        GridBlock("📚", "学習履歴", Route.Study.path)
    )

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 顶部 Home icon + マイページ
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape).clickable {
                        navController.navigate(Route.Home.path) {
                            popUpTo(Route.Home.path) { inclusive = false }
                        }
                    },
                    contentAlignment = Alignment.Center
                ) {
                    Text("⌂", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
                }
                Spacer(Modifier.width(8.dp))
                Text("マイページ", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }

            Column(
                modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // ── profile card ──
                Column(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(18.dp))
                        .background(tokens.paper).padding(20.dp),
                    verticalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                        Box(
                            modifier = Modifier.size(64.dp).clip(CircleShape).background(tokens.btnGrad),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(state.user.avatar.ifEmpty { "リ" }, color = Color.White,
                                style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text(state.user.name.ifEmpty { "リュウイヒ" }, color = tokens.ink,
                                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold))
                            Spacer(Modifier.height(2.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("アカウント番号 ", color = tokens.inkMute, style = TextStyle(fontSize = 12.sp))
                                Text(state.user.studentNo, color = tokens.ink,
                                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold,
                                        fontFamily = FontFamily.Monospace))
                            }
                        }
                    }
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Pill("${state.user.dorm} ${state.user.room}", tokens.btnGrad, Color.White)
                        Pill(state.user.category, null, tokens.ink, bg = tokens.pill)
                    }
                }

                // ── 5 emoji grid（2 列 × 3 行，最后一行 1 块）──
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    grids.chunked(2).forEach { rowItems ->
                        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                            rowItems.forEach { block ->
                                GridCell(block, navController, modifier = Modifier.weight(1f))
                            }
                            if (rowItems.size == 1) {
                                Spacer(Modifier.weight(1f))
                            }
                        }
                    }
                }

                // ── 列表 rows ──
                Column(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper)
                ) {
                    val rows = listOf(
                        ListRowItem("行事予定", Route.Schedule.path),
                        ListRowItem("特別運航便", Route.Bus.path),
                        ListRowItem("通知設定", Route.Settings.path),
                        ListRowItem("Tomoshibi について"),
                        ListRowItem("ログアウト", danger = true, onClick = { showLogoutSheet = true })
                    )
                    rows.forEachIndexed { i, r ->
                        if (i > 0) Divider(color = tokens.hair, thickness = 0.5.dp)
                        Row(
                            modifier = Modifier.fillMaxWidth()
                                .clickable {
                                    r.onClick?.invoke()
                                        ?: r.route?.let { navController.navigate(it) }
                                }
                                .padding(horizontal = 18.dp, vertical = 16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                r.label,
                                color = if (r.danger) tokens.danger else tokens.ink,
                                modifier = Modifier.weight(1f),
                                style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium)
                            )
                            if (!r.danger) {
                                Text("›", color = tokens.inkMute, style = TextStyle(fontSize = 18.sp))
                            }
                        }
                    }
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }

    if (showLogoutSheet) {
        ModalBottomSheet(
            onDismissRequest = { showLogoutSheet = false },
            sheetState = sheetState,
            containerColor = tokens.paper
        ) {
            Column(modifier = Modifier.padding(24.dp).padding(bottom = 32.dp)) {
                Text("ログアウトしますか？", color = tokens.ink,
                    style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold))
                Spacer(Modifier.height(8.dp))
                Text("再度ログインが必要になります。", color = tokens.inkSub, style = TextStyle(fontSize = 13.sp))
                Spacer(Modifier.height(20.dp))
                Box(
                    modifier = Modifier.fillMaxWidth().height(52.dp).clip(RoundedCornerShape(16.dp))
                        .background(tokens.danger).clickable {
                            scope.launch {
                                store.update { it.copy(authed = false) }
                                showLogoutSheet = false
                                navController.navigate(Route.Login.path) {
                                    popUpTo(0) { inclusive = true }
                                }
                            }
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Text("ログアウト", color = Color.White,
                        style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
                }
                Spacer(Modifier.height(8.dp))
                Box(
                    modifier = Modifier.fillMaxWidth().height(52.dp).clip(RoundedCornerShape(16.dp))
                        .border(1.5.dp, tokens.hair, RoundedCornerShape(16.dp))
                        .clickable { showLogoutSheet = false },
                    contentAlignment = Alignment.Center
                ) {
                    Text("キャンセル", color = tokens.ink,
                        style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold))
                }
            }
        }
    }
}

@Composable
private fun GridCell(block: GridBlock, navController: NavHostController, modifier: Modifier = Modifier) {
    val t = SuzuT.current
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(t.paper)
            .border(0.5.dp, t.hair, RoundedCornerShape(16.dp))
            .clickable { navController.navigate(block.route) }
            .heightIn(min = 92.dp)
            .padding(horizontal = 14.dp, vertical = 14.dp)
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            Text(block.emoji, style = TextStyle(fontSize = 24.sp))
            Spacer(modifier = Modifier.weight(1f))
            Text(block.label, color = t.ink,
                style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Bold))
        }
        if (block.badge != null) {
            Box(
                modifier = Modifier.align(Alignment.TopEnd).clip(CircleShape).background(t.danger)
                    .padding(horizontal = 6.dp, vertical = 2.dp)
            ) {
                Text(block.badge, color = Color.White,
                    style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold))
            }
        }
    }
}

@Composable
private fun Pill(text: String, brush: androidx.compose.ui.graphics.Brush?, fg: Color, bg: Color = Color.Transparent) {
    val t = SuzuT.current
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(99.dp))
            .let { if (brush != null) it.background(brush) else it.background(bg) }
            .padding(horizontal = 10.dp, vertical = 4.dp)
    ) {
        Text(text, color = fg, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold))
    }
}
