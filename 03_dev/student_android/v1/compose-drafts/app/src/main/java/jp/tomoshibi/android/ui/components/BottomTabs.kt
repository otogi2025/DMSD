package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

private data class TabItem(val id: String, val label: String, val route: String, val icon: androidx.compose.ui.graphics.vector.ImageVector, val raised: Boolean = false)

@Composable
fun BottomTabs(navController: NavHostController, active: String) {
    val tokens = SuzuT.current
    val tabs = listOf(
        TabItem("home", "ホーム", Route.Home.path, SuzuIcons.Home),
        TabItem("apply", "申請", Route.Applications.path, SuzuIcons.Doc),
        TabItem("nfc", "点呼", Route.Nfc.path, SuzuIcons.Nfc, raised = true),
        TabItem("notif", "通知", Route.Notifications.path, SuzuIcons.Bell),
        TabItem("me", "マイ", Route.MyPage.path, SuzuIcons.User)
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(tokens.paper.copy(alpha = 0.96f))
            .border(width = 1.dp, color = tokens.hair)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 8.dp, vertical = 6.dp),
            verticalAlignment = Alignment.Bottom,
            horizontalArrangement = Arrangement.SpaceAround
        ) {
            tabs.forEach { tab ->
                val isActive = active == tab.id
                val color = if (isActive) tokens.ink else tokens.inkMute

                if (tab.raised) {
                    // 中央 NFC 浮起按钮
                    Box(
                        modifier = Modifier
                            .size(56.dp)
                            .offset(y = (-22).dp)
                            .shadow(elevation = 6.dp, shape = CircleShape)
                            .clip(CircleShape)
                            .background(tokens.btnGrad)
                            .clickable { navController.navigate(tab.route) },
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = tab.icon,
                            contentDescription = tab.label,
                            tint = Color.White,
                            modifier = Modifier.size(26.dp)
                        )
                    }
                } else {
                    // 普通 tab
                    Column(
                        modifier = Modifier
                            .weight(1f)
                            .clickable {
                                navController.navigate(tab.route) {
                                    popUpTo(Route.Home.path)
                                    launchSingleTop = true
                                }
                            }
                            .padding(vertical = 4.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(3.dp)
                    ) {
                        Icon(
                            imageVector = tab.icon,
                            contentDescription = tab.label,
                            tint = color,
                            modifier = Modifier.size(22.dp)
                        )
                        Text(
                            text = tab.label,
                            color = color,
                            style = TextStyle(
                                fontSize = 10.sp,
                                fontWeight = if (isActive) FontWeight.Bold else FontWeight.Medium
                            )
                        )
                    }
                }
            }
        }
    }
}
