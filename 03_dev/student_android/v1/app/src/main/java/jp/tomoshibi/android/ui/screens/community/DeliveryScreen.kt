package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import android.widget.Toast
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.MonoNumeralStyle
import jp.tomoshibi.android.ui.theme.SuzuT

// 宅配便 — 未受取 + 履歴
private data class DeliveryEntry(val source: String, val arriveDate: String, val received: Boolean)

private val MOCK_HISTORY = listOf(
    DeliveryEntry("Amazon", "04-22", true),
    DeliveryEntry("ヤマト", "04-18", true),
    DeliveryEntry("Amazon", "04-15", true),
    DeliveryEntry("佐川急便", "04-10", true)
)

@Composable
fun DeliveryScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val ctx = LocalContext.current
    var pendingReceived by remember { mutableStateOf(false) }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier = Modifier.fillMaxSize().background(tokens.pearl)
                .verticalScroll(rememberScrollState())
        ) {
            // 头部
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 18.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(44.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(SuzuIcons.ChevL, contentDescription = "戻る", tint = tokens.ink, modifier = Modifier.size(24.dp))
                }
                Spacer(Modifier.width(4.dp))
                Text("宅配便", color = tokens.ink,
                    style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
            }

            // 未受取统计
            Column(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(tokens.paper)
                    .padding(20.dp)
            ) {
                Text("未受取", color = tokens.inkSub,
                    style = TextStyle(fontSize = 12.sp))
                Spacer(Modifier.height(6.dp))
                Row(verticalAlignment = Alignment.Bottom) {
                    Text(if (pendingReceived) "0" else "1",
                        color = tokens.danger,
                        style = MonoNumeralStyle.copy(fontSize = 48.sp, lineHeight = 52.sp))
                    Spacer(Modifier.width(6.dp))
                    Text("件", color = tokens.inkSub,
                        modifier = Modifier.padding(bottom = 8.dp),
                        style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold))
                }
            }
            Spacer(Modifier.height(16.dp))

            // 未受取卡（1 件）
            if (!pendingReceived) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
                        .clip(RoundedCornerShape(14.dp))
                        .background(tokens.paper)
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier.size(40.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(tokens.warnBg),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(SuzuIcons.Pkg, contentDescription = null, tint = tokens.warnDeep,
                            modifier = Modifier.size(22.dp))
                    }
                    Spacer(Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Amazon 荷物", color = tokens.ink,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
                        Spacer(Modifier.height(2.dp))
                        Text("本日到着 / 寮管理員室", color = tokens.inkSub,
                            style = TextStyle(fontSize = 12.sp))
                    }
                    Spacer(Modifier.width(8.dp))
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(99.dp))
                            .background(tokens.btnGrad)
                            .clickable {
                                pendingReceived = true
                                Toast.makeText(ctx, "受取しました", Toast.LENGTH_SHORT).show()
                            }
                            .padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text("受取", color = Color.White,
                            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
                    }
                }
                Spacer(Modifier.height(20.dp))
            }

            // 履歴 section
            Text("受取済", color = tokens.inkSub,
                modifier = Modifier.padding(horizontal = 16.dp),
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium))
            Spacer(Modifier.height(8.dp))
            Column(
                modifier = Modifier.padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                MOCK_HISTORY.forEach { d ->
                    Row(
                        modifier = Modifier.fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(tokens.paper)
                            .alpha(0.6f)
                            .padding(horizontal = 14.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier.size(28.dp)
                                .clip(CircleShape)
                                .background(tokens.okBg),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(SuzuIcons.Check, contentDescription = null, tint = tokens.okDeep,
                                modifier = Modifier.size(16.dp))
                        }
                        Spacer(Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text("${d.source} 荷物", color = tokens.ink,
                                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
                            Text(d.arriveDate, color = tokens.inkSub,
                                style = MonoNumeralStyle.copy(fontSize = 11.sp, lineHeight = 14.sp,
                                    fontWeight = FontWeight.Medium))
                        }
                        Text("受取済", color = tokens.okDeep,
                            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
                    }
                }
            }
            Spacer(Modifier.height(20.dp))
        }
    }
}
