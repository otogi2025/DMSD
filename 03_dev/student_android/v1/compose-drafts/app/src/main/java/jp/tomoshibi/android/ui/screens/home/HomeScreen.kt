package jp.tomoshibi.android.ui.screens.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.BottomTabs
import jp.tomoshibi.android.ui.theme.MonoNumeralStyle
import jp.tomoshibi.android.ui.theme.SuzuT

@Composable
fun HomeScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    val totalDeduction = state.deductions.sumOf { it.points }

    Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        Column(
            modifier = Modifier
                .weight(1f)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp)
                .padding(top = 24.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ── greeting ──
            Column {
                Text(
                    text = "おかえりなさい",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium)
                )
                Text(
                    text = "${state.user.name.ifEmpty { "リュウイヒ" }}さん",
                    color = tokens.ink,
                    style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold)
                )
                Text(
                    text = "${MockData.DEFAULT_USER.dorm}寮 ${MockData.DEFAULT_USER.room}",
                    color = tokens.inkMute,
                    style = TextStyle(fontSize = 12.sp)
                )
            }

            // ── amber Card：減点 hero ──
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(tokens.amberGrad)
                    .clickable { navController.navigate(Route.Deduction.path) }
                    .padding(20.dp)
            ) {
                Column {
                    Text(
                        text = "今月の減点",
                        color = tokens.inkSub,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                    )
                    Spacer(Modifier.height(8.dp))
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(
                            text = totalDeduction.toString(),
                            color = tokens.ink,
                            style = MonoNumeralStyle.copy(fontSize = 56.sp)
                        )
                        Spacer(Modifier.width(4.dp))
                        Text(
                            text = "/ 4.0",
                            color = tokens.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium)
                        )
                    }
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = if (totalDeduction >= 4.0) "⚠ 罰掃 ライン到達" else "順調です",
                        color = if (totalDeduction >= 4.0) tokens.warnDeep else tokens.okDeep,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                    )
                }
            }

            // ── Quick action grid ──
            Text(
                text = "メニュー",
                color = tokens.inkSub,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
            )
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                QuickAction("申請", "外泊·外出", Modifier.weight(1f)) {
                    navController.navigate(Route.Applications.path)
                }
                QuickAction("通知", "${state.notifications.count { !it.read }} 件", Modifier.weight(1f)) {
                    navController.navigate(Route.Notifications.path)
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                QuickAction("音楽", "リクエスト", Modifier.weight(1f)) {
                    navController.navigate(Route.Music.path)
                }
                QuickAction("バス", "次便案内", Modifier.weight(1f)) {
                    navController.navigate(Route.Bus.path)
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                QuickAction("失物", "落し物", Modifier.weight(1f)) {
                    navController.navigate(Route.LostFound.path)
                }
                QuickAction("学習", "履歴", Modifier.weight(1f)) {
                    navController.navigate(Route.Study.path)
                }
            }

            // ── notif preview ──
            if (state.notifications.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "最近の通知",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                )
                state.notifications.take(3).forEach { n ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(tokens.paper)
                            .clickable { navController.navigate(Route.Notifications.path) }
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(99.dp))
                                .background(tokens.pill)
                                .padding(horizontal = 8.dp, vertical = 3.dp)
                        ) {
                            Text(n.tag, color = tokens.ink,
                                style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold))
                        }
                        Spacer(Modifier.width(10.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(n.title, color = tokens.ink,
                                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
                            Text(n.ts, color = tokens.inkMute, style = TextStyle(fontSize = 11.sp))
                        }
                    }
                }
            }
        }

        BottomTabs(navController = navController, active = "home")
    }
}

@Composable
private fun QuickAction(title: String, subtitle: String, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val tokens = SuzuT.current
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(16.dp))
            .background(tokens.paper)
            .clickable(onClick = onClick)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Text(title, color = tokens.ink, style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
        Text(subtitle, color = tokens.inkSub, style = TextStyle(fontSize = 11.sp))
    }
}
