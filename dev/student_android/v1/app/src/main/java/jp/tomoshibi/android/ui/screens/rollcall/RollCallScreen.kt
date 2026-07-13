package jp.tomoshibi.android.ui.screens.rollcall

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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.theme.SuzuT

@Composable
fun RollCallScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 顶部 ← + 点呼履歴
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Text("←", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
                }
                Spacer(Modifier.width(8.dp))
                Text("点呼履歴", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }

            if (state.rollCalls.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize().padding(bottom = 60.dp), contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("📋", style = TextStyle(fontSize = 40.sp))
                        Spacer(Modifier.height(8.dp))
                        Text(
                            "点呼履歴はまだありません",
                            color = tokens.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                        )
                        Spacer(Modifier.height(4.dp))
                        Text(
                            "点呼を完了すると、ここに表示されます",
                            color = tokens.inkMute,
                            style = TextStyle(fontSize = 12.sp),
                        )
                    }
                }
                return@GlobalScaffold
            }

            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Column(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
                ) {
                    state.rollCalls.forEachIndexed { i, r ->
                        if (i > 0) Divider(color = tokens.hair, thickness = 0.5.dp)
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            val (label, color) =
                                when (r.status) {
                                    "ok" -> "時間内" to tokens.ok
                                    "late" -> "遅刻" to tokens.warn
                                    "miss" -> "欠席" to tokens.danger
                                    else -> r.status to tokens.inkMute
                                }
                            Box(
                                modifier = Modifier.size(8.dp).clip(CircleShape).background(color),
                            )
                            Spacer(Modifier.width(12.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                // 时刻格式化抽到 data/format/JstDate（时区锁死 JST、可单测）
                                Text(
                                    JstDate.formatHistory(r.ts),
                                    color = tokens.ink,
                                    style =
                                        TextStyle(
                                            fontSize = 13.sp,
                                            fontWeight = FontWeight.SemiBold,
                                            fontFamily = FontFamily.Monospace,
                                        ),
                                )
                                Text(
                                    if (r.method == "nfc") "NFC スキャン" else "手動入力",
                                    color = tokens.inkMute,
                                    style = TextStyle(fontSize = 11.sp),
                                )
                            }
                            Box(
                                modifier =
                                    Modifier
                                        .clip(RoundedCornerShape(6.dp))
                                        .background(color.copy(alpha = 0.12f))
                                        .padding(horizontal = 8.dp, vertical = 2.dp),
                            ) {
                                Text(
                                    label,
                                    color = color,
                                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
                                )
                            }
                        }
                    }
                }
                Spacer(Modifier.height(40.dp))
            }
        }
    }
}
