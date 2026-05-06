package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 浮空 capsule + 中央 ⭐点呼 raised — 对齐 iOS BottomNav.swift（去 Liquid Glass）
//
// API 契约（GlobalScaffold 用）:
//   active: "apply" | "me" | ""  — Home / community / nfc 等都传 ""，中央按钮不算 tab
//   onRollClick: 中央 ⭐点呼 → 弹 RollCallSheet（不走 nav）
//
// 设计还原：
//   - bar capsule: 62dp 高 / 31dp 圆角 / paper alpha 0.92 / 0.5dp white border / 12dp shadow
//   - 中央按钮: 62dp 圆 + rollGrad radial + shadow primary 0.42 / 10dp y=6 + offset y -22dp 浮起
//   - 圆下"点呼" 9sp Bold primary 小标（跟 iOS 一样）
@Composable
fun BottomTabs(
    navController: NavHostController,
    active: String,
    // 默认 noop 兜底 — 让既存 4 屏直接调用（旧签名）暂时不断；
    // 后续会话把屏改成 GlobalScaffold 包裹后，应去掉此默认让契约更明确
    onRollClick: () -> Unit = {}
) {
    val tokens = SuzuT.current
    val barShape = RoundedCornerShape(31.dp)

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 16.dp, end = 16.dp, bottom = 16.dp)
    ) {
        // ── 底部 capsule bar（左右两个 tab，中间留 80dp 空给浮起按钮）──
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(62.dp)
                .align(Alignment.BottomCenter)
                .shadow(
                    elevation = 12.dp,
                    shape = barShape,
                    spotColor = Color.Black.copy(alpha = 0.15f),
                    ambientColor = Color.Black.copy(alpha = 0.15f)
                )
                .clip(barShape)
                .background(tokens.paper.copy(alpha = 0.92f))
                .border(
                    width = 0.5.dp,
                    color = Color.White.copy(alpha = 0.5f),
                    shape = barShape
                )
                .padding(horizontal = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            NavTab(
                icon = SuzuIcons.Envelope,
                label = "申し込み",
                active = active == "apply",
                modifier = Modifier.weight(1f),
                onClick = {
                    navController.navigate(Route.Applications.path) {
                        popUpTo(Route.Home.path)
                        launchSingleTop = true
                    }
                }
            )

            // 中央留空给浮起按钮 — 80dp 跟 iOS 一致
            Spacer(modifier = Modifier.width(80.dp))

            NavTab(
                icon = SuzuIcons.User,
                label = "マイページ",
                active = active == "me",
                modifier = Modifier.weight(1f),
                onClick = {
                    navController.navigate(Route.MyPage.path) {
                        popUpTo(Route.Home.path)
                        launchSingleTop = true
                    }
                }
            )
        }

        // ── 中央 ⭐点呼 raised 浮起按钮（不走 nav，触发 sheet）──
        // offset y -14dp (原 -22dp)：让按钮更贴 capsule 中心，
        // 跟 iOS BottomNav.swift centerButton.offset(y: -10) 对齐
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .offset(y = (-14).dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(62.dp)
                    .shadow(
                        elevation = 10.dp,
                        shape = CircleShape,
                        spotColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.42f),
                        ambientColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.42f)
                    )
                    .clip(CircleShape)
                    .background(tokens.rollGrad)
                    .clickable { onRollClick() },
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = SuzuIcons.Shield,
                    contentDescription = "点呼",
                    tint = Color.White,
                    modifier = Modifier.size(26.dp)
                )
            }
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = "点呼",
                color = MaterialTheme.colorScheme.primary,
                style = TextStyle(
                    fontSize = 9.sp,
                    fontWeight = FontWeight.Bold
                )
            )
        }
    }
}

// 单个 tab 项 — icon 22dp + label 10sp，active 时 ink + Bold，inactive 时 inkMute + Medium
@Composable
private fun NavTab(
    icon: ImageVector,
    label: String,
    active: Boolean,
    modifier: Modifier,
    onClick: () -> Unit
) {
    val tokens = SuzuT.current
    val color = if (active) MaterialTheme.colorScheme.primary else tokens.inkMute

    Column(
        modifier = modifier
            .fillMaxHeight()
            .clickable { onClick() },
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = color,
            modifier = Modifier.size(22.dp)
        )
        Spacer(modifier = Modifier.height(3.dp))
        Text(
            text = label,
            color = color,
            style = TextStyle(
                fontSize = 10.sp,
                fontWeight = if (active) FontWeight.Bold else FontWeight.SemiBold
            )
        )
    }
}
