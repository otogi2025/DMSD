package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.material3.ExperimentalMaterial3Api
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
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.BottomTabs
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

private data class MyMenuItem(val emoji: String, val label: String, val route: String)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MyPageScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    var showLogoutSheet by remember { mutableStateOf(false) }
    val sheetState = rememberModalBottomSheetState()

    val items = listOf(
        MyMenuItem("📊", "減点履歴", Route.Deduction.path),
        MyMenuItem("✅", "点呼履歴", Route.RollCall.path),
        MyMenuItem("📝", "申請履歴", Route.Applications.path),
        MyMenuItem("⚙️", "設定", Route.Settings.path)
    )

    Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        Column(
            modifier = Modifier.weight(1f).fillMaxWidth().padding(horizontal = 20.dp)
        ) {
            Text("マイページ", color = tokens.ink,
                modifier = Modifier.padding(top = 24.dp, bottom = 16.dp),
                style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))

            // ── profile card ──
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(tokens.paper)
                    .padding(20.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(tokens.btnGrad),
                    contentAlignment = Alignment.Center
                ) {
                    Text(state.user.avatar.ifEmpty { "リ" },
                        color = Color.White,
                        style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
                }
                Column(modifier = Modifier.weight(1f)) {
                    Text(state.user.name.ifEmpty { "リュウイヒ" },
                        color = tokens.ink,
                        style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold))
                    Text("${state.user.dorm}寮 ${state.user.room}号室",
                        color = tokens.inkSub,
                        style = TextStyle(fontSize = 12.sp))
                    Text(state.user.email.ifEmpty { "otogi2025@gmail.com" },
                        color = tokens.inkMute,
                        style = TextStyle(fontSize = 11.sp))
                }
            }

            Spacer(Modifier.height(20.dp))

            // ── menu items ──
            items.forEach { item ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(bottom = 8.dp)
                        .clip(RoundedCornerShape(14.dp))
                        .background(tokens.paper)
                        .clickable { navController.navigate(item.route) }
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(tokens.pill),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(item.emoji, style = TextStyle(fontSize = 18.sp))
                    }
                    Text(item.label, color = tokens.ink, modifier = Modifier.weight(1f),
                        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold))
                    Text("›", color = tokens.inkMute,
                        style = TextStyle(fontSize = 18.sp))
                }
            }

            Spacer(Modifier.height(16.dp))

            // ── logout ──
            Box(
                modifier = Modifier
                    .fillMaxWidth().height(52.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .border(1.5.dp, tokens.danger.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
                    .clickable { showLogoutSheet = true },
                contentAlignment = Alignment.Center
            ) {
                Text("ログアウト", color = tokens.danger,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold))
            }
        }

        BottomTabs(navController = navController, active = "me")
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
                Text("再度ログインが必要になります。", color = tokens.inkSub,
                    style = TextStyle(fontSize = 13.sp))
                Spacer(Modifier.height(20.dp))
                Box(
                    modifier = Modifier
                        .fillMaxWidth().height(52.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(tokens.danger)
                        .clickable {
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
                    modifier = Modifier
                        .fillMaxWidth().height(52.dp)
                        .clip(RoundedCornerShape(16.dp))
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
