package jp.tomoshibi.android.ui.screens.notifications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

@Composable
fun NotificationsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    var filter by remember { mutableStateOf("すべて") }

    // 7 类 chip filter（对应 iOS 截图 21.55.06 顶部 chip 行）
    val chips = listOf("すべて", "申請", "減点", "学習", "宅配", "活動", "リクエスト")

    val filtered = if (filter == "すべて") state.notifications
    else state.notifications.filter { it.tag == filter }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 顶部 ← + 通知
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center
                ) {
                    Text("←", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
                }
                Spacer(Modifier.width(8.dp))
                Text("通知", color = tokens.ink, modifier = Modifier.weight(1f),
                    style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
                Box(
                    modifier = Modifier.clickable {
                        scope.launch {
                            store.update { s -> s.copy(notifications = s.notifications.map { it.copy(read = true) }) }
                        }
                    }
                ) {
                    Text("すべて既読", color = tokens.ink,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold))
                }
            }

            // chip filter row（横スクロール）
            Row(
                modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                chips.forEach { chip ->
                    val active = filter == chip
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(99.dp))
                            .background(if (active) tokens.ink else tokens.paper)
                            .then(if (active) Modifier else Modifier.border(1.dp, tokens.hair, RoundedCornerShape(99.dp)))
                            .clickable { filter = chip }
                            .padding(horizontal = 14.dp, vertical = 7.dp)
                    ) {
                        Text(
                            chip, color = if (active) tokens.pearl else tokens.inkSub,
                            style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold)
                        )
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Column(
                modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                if (filtered.isEmpty()) {
                    Box(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 60.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("該当する通知はありません", color = tokens.inkMute, style = TextStyle(fontSize = 14.sp))
                    }
                }
                filtered.forEach { n ->
                    Row(
                        modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp))
                            .background(tokens.paper).clickable {
                                scope.launch {
                                    store.update { s ->
                                        s.copy(notifications = s.notifications.map {
                                            if (it.id == n.id) it.copy(read = true) else it
                                        })
                                    }
                                }
                                navController.navigate("notifications/${n.id}")
                            }.padding(14.dp),
                        verticalAlignment = Alignment.Top,
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Box(
                            modifier = Modifier.padding(top = 7.dp).size(8.dp)
                                .clip(CircleShape)
                                .background(if (n.read) Color.Transparent else tokens.ok)
                        )
                        Column(modifier = Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(
                                    modifier = Modifier.clip(RoundedCornerShape(6.dp))
                                        .background(tokens.pill).padding(horizontal = 8.dp, vertical = 2.dp)
                                ) {
                                    Text(n.tag, color = tokens.ink,
                                        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
                                }
                                Spacer(Modifier.weight(1f))
                                Text(n.ts, color = tokens.inkMute, style = TextStyle(fontSize = 11.sp))
                            }
                            Spacer(Modifier.height(6.dp))
                            Text(n.title, color = tokens.ink,
                                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold))
                            Spacer(Modifier.height(4.dp))
                            Text(n.body, color = tokens.inkSub,
                                style = TextStyle(fontSize = 13.sp, lineHeight = 20.sp))
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}
