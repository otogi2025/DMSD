package jp.tomoshibi.android.ui.components

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
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
import jp.tomoshibi.android.ui.haptics.HapticKind
import jp.tomoshibi.android.ui.haptics.rememberHaptics
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 浮空 capsule + 中央 ⭐点呼 raised — 对齐 iOS BottomNav.swift
//
// G6 对齐：
//   - active tab 背后 primary@12% 胶囊 + 切换滑动动画（matchedGeometry 近似）
//   - bar 背景 paper@0.78（对齐 iOS ultraThinMaterial 降级色）
//   - 图标 20dp（对齐 iOS 20pt）
//   - 中央按钮 offset y -10dp（对齐 iOS centerButton.offset(y: -10)）

@Composable
fun BottomTabs(
    navController: NavHostController,
    active: String,
    // 默认 noop 兜底 — 让既存 4 屏直接调用（旧签名）暂时不断；
    // 后续会话把屏改成 GlobalScaffold 包裹后，应去掉此默认让契约更明确
    onRollClick: () -> Unit = {},
) {
    val tokens = SuzuT.current
    val barShape = RoundedCornerShape(31.dp)
    val haptics = rememberHaptics()
    val primary = MaterialTheme.colorScheme.primary

    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(start = 16.dp, end = 16.dp, bottom = 16.dp),
    ) {
        // ── 底部 capsule bar ──
        BoxWithConstraints(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .height(62.dp)
                    .align(Alignment.BottomCenter)
                    .shadow(
                        elevation = 12.dp,
                        shape = barShape,
                        spotColor = Color.Black.copy(alpha = 0.15f),
                        ambientColor = Color.Black.copy(alpha = 0.15f),
                    ).clip(barShape)
                    // 磨砂近似：半透明 paper（Compose 无法 blur 背后内容，对齐 iOS <26 fallback）
                    .background(tokens.paper.copy(alpha = 0.78f))
                    .border(
                        width = 0.5.dp,
                        color = Color.White.copy(alpha = 0.5f),
                        shape = barShape,
                    ).padding(horizontal = 12.dp),
        ) {
            val tabSlotWidth = (maxWidth - 80.dp) / 2
            // active 胶囊水平偏移：apply=0 / me=右半 + 中央空档
            val targetOffset =
                when (active) {
                    "apply" -> 0.dp
                    "me" -> tabSlotWidth + 80.dp
                    else -> (-9999).dp // 藏到屏外（Home 等无 tab 高亮）
                }
            val indicatorX by animateDpAsState(
                targetValue = targetOffset,
                animationSpec = spring(dampingRatio = 0.78f, stiffness = 380f),
                label = "nav-capsule",
            )

            if (active == "apply" || active == "me") {
                Box(
                    modifier =
                        Modifier
                            .offset(x = indicatorX)
                            .width(tabSlotWidth)
                            .fillMaxHeight()
                            .padding(vertical = 6.dp)
                            .clip(RoundedCornerShape(percent = 50))
                            .background(primary.copy(alpha = 0.12f)),
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth().fillMaxHeight(),
                verticalAlignment = Alignment.CenterVertically,
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
                    },
                )

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
                    },
                )
            }
        }

        // ── 中央 ⭐点呼 raised（offset -10 对齐 iOS）──
        Column(
            modifier =
                Modifier
                    .align(Alignment.BottomCenter)
                    .offset(y = (-10).dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                modifier =
                    Modifier
                        .size(62.dp)
                        .shadow(
                            elevation = 10.dp,
                            shape = CircleShape,
                            spotColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.42f),
                            ambientColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.42f),
                        ).clip(CircleShape)
                        .background(tokens.rollGrad)
                        .clickable {
                            haptics(HapticKind.Light)
                            onRollClick()
                        },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = SuzuIcons.Shield,
                    contentDescription = "点呼",
                    tint = Color.White,
                    modifier = Modifier.size(26.dp),
                )
            }
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = "点呼",
                color = MaterialTheme.colorScheme.primary,
                style =
                    TextStyle(
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                    ),
            )
        }
    }
}

// 单个 tab — icon 20dp + label 10sp（对齐 iOS）
@Composable
private fun NavTab(
    icon: ImageVector,
    label: String,
    active: Boolean,
    modifier: Modifier,
    onClick: () -> Unit,
) {
    val tokens = SuzuT.current
    val color = if (active) MaterialTheme.colorScheme.primary else tokens.inkMute

    Column(
        modifier =
            modifier
                .fillMaxHeight()
                .clickable { onClick() },
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = color,
            modifier = Modifier.size(20.dp),
        )
        Spacer(modifier = Modifier.height(3.dp))
        Text(
            text = label,
            color = color,
            style =
                TextStyle(
                    fontSize = 10.sp,
                    fontWeight = if (active) FontWeight.Bold else FontWeight.SemiBold,
                ),
        )
    }
}
