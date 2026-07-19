package jp.tomoshibi.android.ui.screens.notifications

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.Notification
import jp.tomoshibi.android.data.notifications.NotificationMapper
import jp.tomoshibi.android.data.notifications.NotificationsLoadState
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.SuzuSkeleton
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

/**
 * 通知中心（对齐 iOS NotificationsView）。
 * 数据源 = push + StudentNotificationsAPI.feed + 包裹；点卡标已读、不跳详情。
 */
@Composable
fun NotificationsScreen(navController: NavHostController) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()

    // 三源内存态（不读 MockData.DEFAULT_NOTIFICATIONS）
    val push by store.pushNotifications.collectAsState()
    val feed by store.studentNotifications.collectAsState()
    val packages by store.packages.collectAsState()
    val notifState by store.notificationsState.collectAsState()
    // AppState 仅用于 collect 触发重组时的令牌守卫旁路；未読 fallback 走 snapshot 亦可
    val appState by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    var filter by remember { mutableStateOf("すべて") }
    val chips = listOf("すべて", "申請", "減点", "夜学習", "宅配", "活動", "リクエスト曲")

    val all =
        remember(push, feed, packages) {
            NotificationMapper.allNotifications(push, feed, packages)
        }
    val filtered =
        if (filter == "すべて") {
            all
        } else {
            all.filter { it.tag == filter }
        }

    // 进入通知中心刷新 feed + 包裹（对齐 iOS .task { refreshNotificationSources }）
    LaunchedEffect(appState.authToken) {
        if (!appState.authToken.isNullOrEmpty()) {
            store.refreshNotificationSources()
        }
    }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // iOS PageHeader 只有标题，无「すべて既読」
            PageHeader(
                title = "通知",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp, vertical = 4.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                chips.forEach { chip ->
                    val active = filter == chip
                    Box(
                        modifier =
                            Modifier
                                .clip(RoundedCornerShape(percent = 50))
                                .background(if (active) primary else t.paper)
                                .clickable { filter = chip }
                                .padding(horizontal = 14.dp, vertical = 7.dp),
                    ) {
                        Text(
                            chip,
                            color = if (active) Color.White else t.inkSub,
                            style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold),
                        )
                    }
                }
            }

            Spacer(Modifier.height(12.dp))

            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                if (filtered.isEmpty()) {
                    when (val s = notifState) {
                        NotificationsLoadState.Loading,
                        NotificationsLoadState.Idle,
                        -> {
                            // 3 条 72 高骨架（对齐 iOS Skeleton）
                            SuzuSkeleton(height = 72)
                            SuzuSkeleton(height = 72)
                            SuzuSkeleton(height = 72)
                        }

                        is NotificationsLoadState.Failed -> {
                            EmptyState(
                                icon = SuzuIcons.Warn,
                                title = "読み込みに失敗しました",
                                message = s.message,
                            )
                        }

                        NotificationsLoadState.Loaded -> {
                            EmptyState(
                                icon = SuzuIcons.Bell,
                                title = "通知はありません",
                            )
                        }
                    }
                } else {
                    filtered.forEach { n ->
                        NotifCard(
                            n = n,
                            primary = primary,
                            onClick = {
                                val kind = n.kind
                                val refId = n.refId
                                if (kind != null && refId != null && !n.read) {
                                    scope.launch {
                                        store.markStudentNotificationRead(kind, refId)
                                    }
                                }
                            },
                        )
                    }
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

@Composable
private fun NotifCard(
    n: Notification,
    primary: Color,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    SuzuCard(
        padding = 14,
        modifier = Modifier.clickable(onClick = onClick),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
            horizontalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Box(
                modifier =
                    Modifier
                        .padding(top = 6.dp)
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(if (n.read) Color.Transparent else primary),
            )
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Pill(text = n.tag, tone = pillToneFor(n.tag))
                    Spacer(Modifier.weight(1f))
                    Text(n.ts, color = t.inkMute, style = TextStyle(fontSize = 11.sp))
                }
                Spacer(Modifier.height(6.dp))
                Text(
                    n.title,
                    color = t.ink,
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    n.body,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp, lineHeight = 20.sp),
                )
            }
        }
    }
}

// Pill 色调：「減点」=warn / 「申請」=ok / 其余=accent
private fun pillToneFor(tag: String): PillTone =
    when (tag) {
        "減点" -> PillTone.Warn
        "申請" -> PillTone.Ok
        else -> PillTone.Accent
    }
