package jp.tomoshibi.android.ui.screens.notifications

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Divider
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
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.theme.SuzuT

@Composable
fun NotifDetailScreen(navController: NavHostController, id: String) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val notif = state.notifications.firstOrNull { it.id == id }

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
                Text("通知", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }

            if (notif == null) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("該当する通知が見つかりません", color = tokens.inkMute, style = TextStyle(fontSize = 14.sp))
                }
                return@GlobalScaffold
            }

            Column(
                modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // tag pill + ts
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier.clip(RoundedCornerShape(6.dp))
                            .background(tokens.pill).padding(horizontal = 10.dp, vertical = 4.dp)
                    ) {
                        Text(notif.tag, color = tokens.ink,
                            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
                    }
                    Spacer(Modifier.width(10.dp))
                    Text(notif.ts, color = tokens.inkMute, style = TextStyle(fontSize = 12.sp))
                }

                // title 24sp
                Text(notif.title, color = tokens.ink,
                    style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold, lineHeight = 32.sp))

                Divider(color = tokens.hair, thickness = 0.5.dp)

                // body 15sp
                Text(notif.body, color = tokens.ink,
                    style = TextStyle(fontSize = 15.sp, lineHeight = 24.sp))

                Spacer(Modifier.height(8.dp))

                // 送信元 footer
                Column(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                        .background(tokens.paper).padding(14.dp)
                ) {
                    Text("送信元", color = tokens.inkMute,
                        style = TextStyle(fontSize = 11.sp, letterSpacing = 1.5.sp, fontWeight = FontWeight.Bold))
                    Spacer(Modifier.height(4.dp))
                    Text("寮監事務室", color = tokens.ink,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
                }

                Spacer(Modifier.height(40.dp))
            }
        }
    }
}
