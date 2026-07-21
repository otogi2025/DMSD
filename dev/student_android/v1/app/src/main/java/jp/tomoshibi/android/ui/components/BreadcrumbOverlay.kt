package jp.tomoshibi.android.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.routeDisplayName
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 长按返回按钮弹出的面包屑历史 — 对齐 iOS BreadcrumbOverlay.swift
// 首行固定「ホームへ戻る」+ 栈内路径；点外侧关闭；宽 240dp / 圆角 14。

@Composable
fun BreadcrumbOverlay(
    navController: NavHostController,
    modifier: Modifier = Modifier,
) {
    val store = LocalAppStore.current
    val open by store.breadcrumbOpen.collectAsState()
    val backStack by navController.currentBackStack.collectAsState()
    val t = SuzuT.current

    // breadcrumbChain = 除当前页外的栈（对齐 iOS router.breadcrumbChain）
    // 过滤 NavHost 合成的根 NavGraph entry（route=null），避免空文字可点击行
    val chain = backStack.dropLast(1).filter { it.destination.route != null }

    AnimatedVisibility(
        visible = open,
        enter = fadeIn() + scaleIn(transformOrigin = TransformOrigin(0f, 0f), initialScale = 0.85f),
        exit = fadeOut() + scaleOut(transformOrigin = TransformOrigin(0f, 0f), targetScale = 0.85f),
        modifier = modifier.fillMaxSize(),
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            // 几乎全透明遮罩 — 点外侧关闭（仿 iOS Safari）
            Box(
                modifier =
                    Modifier
                        .fillMaxSize()
                        .clickable(
                            interactionSource = remember { MutableInteractionSource() },
                            indication = null,
                        ) { store.closeBreadcrumb() },
            )

            Column(
                modifier =
                    Modifier
                        .padding(start = 12.dp, top = 50.dp)
                        .width(240.dp)
                        .shadow(
                            elevation = 18.dp,
                            shape = RoundedCornerShape(14.dp),
                            ambientColor = t.ink.copy(alpha = 0.08f),
                            spotColor = t.ink.copy(alpha = 0.18f),
                        ).clip(RoundedCornerShape(14.dp))
                        .background(t.paper)
                        .border(0.5.dp, t.hair, RoundedCornerShape(14.dp)),
            ) {
                BreadcrumbRow(
                    icon = {
                        Icon(
                            SuzuIcons.Home,
                            contentDescription = null,
                            tint = t.ink,
                            modifier = Modifier.size(16.dp),
                        )
                    },
                    label = "ホームへ戻る",
                ) {
                    navController.popBackStack(jp.tomoshibi.android.nav.Route.Home.path, inclusive = false)
                    store.closeBreadcrumb()
                }

                if (chain.isNotEmpty()) {
                    HorizontalDivider(color = t.hair)
                }

                chain.forEachIndexed { idx, entry ->
                    if (idx > 0) HorizontalDivider(color = t.hair)
                    val route = entry.destination.route ?: ""
                    BreadcrumbRow(
                        icon = {
                            Icon(
                                SuzuIcons.Undo,
                                contentDescription = null,
                                tint = t.ink,
                                modifier = Modifier.size(13.dp),
                            )
                        },
                        label = routeDisplayName(route),
                    ) {
                        // 跳回该级：pop 到该 entry 的 route（保留该页）
                        val target = entry.destination.route
                        if (target != null) {
                            navController.popBackStack(target, inclusive = false)
                        }
                        store.closeBreadcrumb()
                    }
                }
            }
        }
    }
}

@Composable
private fun BreadcrumbRow(
    icon: @Composable () -> Unit,
    label: String,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clickable(onClick = onClick)
                .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(modifier = Modifier.size(18.dp), contentAlignment = Alignment.Center) {
            icon()
        }
        Spacer(modifier = Modifier.width(12.dp))
        Text(
            text = label,
            color = t.ink,
            style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium),
            maxLines = 1,
            modifier = Modifier.weight(1f),
        )
    }
}
