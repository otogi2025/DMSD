package jp.tomoshibi.android.ui.screens.notifications

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
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

@Composable
fun NotificationsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("通知", color = tokens.ink, modifier = Modifier.weight(1f),
                style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
            Box(
                modifier = Modifier.clickable {
                    scope.launch {
                        store.update { s -> s.copy(notifications = s.notifications.map { it.copy(read = true) }) }
                    }
                }
            ) {
                Text("すべて既読", color = tokens.ink,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
            }
        }

        Column(
            modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()).padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            state.notifications.forEach { n ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(if (n.read) tokens.paper else tokens.pill)
                        .clickable {
                            scope.launch {
                                store.update { s ->
                                    s.copy(notifications = s.notifications.map {
                                        if (it.id == n.id) it.copy(read = true) else it
                                    })
                                }
                            }
                            navController.navigate("notifications/${n.id}")
                        }
                        .padding(14.dp),
                    verticalAlignment = Alignment.Top,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .padding(top = 7.dp)
                            .size(8.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .background(if (n.read) androidx.compose.ui.graphics.Color.Transparent else tokens.ink)
                    )
                    Column(modifier = Modifier.weight(1f)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(tokens.hair)
                                    .padding(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text(n.tag, color = tokens.inkSub,
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

        BottomTabs(navController = navController, active = "notif")
    }
}
