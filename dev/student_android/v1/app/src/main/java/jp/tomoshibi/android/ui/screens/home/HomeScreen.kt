package jp.tomoshibi.android.ui.screens.home

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.network.BusRouteOut
import jp.tomoshibi.android.data.network.EventOut
import jp.tomoshibi.android.data.network.endpoints.AnnouncementsAPI
import jp.tomoshibi.android.data.network.endpoints.BusAPI
import jp.tomoshibi.android.data.network.endpoints.CleaningAPI
import jp.tomoshibi.android.data.network.endpoints.EventsAPI
import jp.tomoshibi.android.data.network.endpoints.FrontDeskAPI
import jp.tomoshibi.android.data.network.endpoints.LostFoundAPI
import jp.tomoshibi.android.data.network.endpoints.LostFoundOut
import jp.tomoshibi.android.data.network.endpoints.NextCleaningInfo
import jp.tomoshibi.android.data.network.endpoints.SongRequestOut
import jp.tomoshibi.android.data.network.endpoints.SongsAPI
import jp.tomoshibi.android.data.notifications.NotificationMapper
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.AbsenceSheet
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.HealthSheet
import jp.tomoshibi.android.ui.components.RenewStudentNoSheet
import jp.tomoshibi.android.ui.components.SectionCard
import jp.tomoshibi.android.ui.components.TopRollBar
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import java.time.LocalDate
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale

// HomeScreen — 对齐 iOS HomeStubs.swift LifeTab + greeting + renewBanner + pointsCard
// 数据：已登录 → 真后端；失败保持空，绝不回退 MockData。

private val MusicPurple = Color(0xFF7C3AED)
private val LostFixedColor = Color(0xFF7C3AED)
private val CleaningIconBg = Color(0xFFFDF4E1)
private val CleaningIconFg = Color(0xFFB07A28)

private data class UpcomingBus(
    val time: String,
    val direction: String,
    val date: String,
    val weekday: String,
    val isToday: Boolean,
)

@Composable
fun HomeScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    // 铃铛未読：push + feed + 包裹三源（对齐 iOS unreadNotificationCount）
    val pushNotifs by store.pushNotifications.collectAsState()
    val feedNotifs by store.studentNotifications.collectAsState()
    val packageItems by store.packages.collectAsState()

    var showRenewSheet by remember { mutableStateOf(false) }
    var showAbsenceSheet by remember { mutableStateOf(false) }
    var showHealthSheet by remember { mutableStateOf(false) }

    // 首页卡片本地缓存（对齐 iOS LifeTab @State，失败保持空）
    var latestAnnouncementTitle by remember { mutableStateOf<String?>(null) }
    var upcomingBus by remember { mutableStateOf<UpcomingBus?>(null) }
    var pendingPackages by remember { mutableStateOf(0) }
    var homeEvents by remember { mutableStateOf<List<EventOut>>(emptyList()) }
    var songs by remember { mutableStateOf<List<SongRequestOut>>(emptyList()) }
    var lostItems by remember { mutableStateOf<List<LostFoundOut>>(emptyList()) }
    var nextCleaning by remember { mutableStateOf<NextCleaningInfo?>(null) }

    // 拉取首页卡片数据
    LaunchedEffect(state.authed, state.authToken) {
        if (!state.authed || state.authToken.isNullOrEmpty()) return@LaunchedEffect
        // android#69: 七个接口并行请求（各自 runCatching 容错），缩短首屏等待
        coroutineScope {
            listOf(
                async {
                    // 公告列表（副标题用最新标题）+ 未读数
                    runCatching {
                        val list = AnnouncementsAPI.list()
                        latestAnnouncementTitle = list.items.firstOrNull()?.title
                        val unread = AnnouncementsAPI.unreadCount().unreadCount
                        store.update { it.copy(announcementUnreadCount = unread) }
                    }
                },
                async {
                    runCatching {
                        val routes = BusAPI.listRoutes()
                        upcomingBus = pickUpcomingBus(routes)
                    }.onFailure { upcomingBus = null }
                },
                async {
                    runCatching {
                        val pkgs = FrontDeskAPI.listMine()
                        pendingPackages = pkgs.count { it.status == "pending" || it.status == "notified" }
                    }.onFailure { pendingPackages = 0 }
                },
                async {
                    runCatching {
                        val today = JstDate.today()
                        val to = "${today.year + 1}-12-31"
                        homeEvents = EventsAPI.listEvents(fromDate = today.toString(), toDate = to)
                    }.onFailure { homeEvents = emptyList() }
                },
                async {
                    runCatching { songs = SongsAPI.list() }.onFailure { songs = emptyList() }
                },
                async {
                    runCatching { lostItems = LostFoundAPI.list() }.onFailure { lostItems = emptyList() }
                },
                async {
                    runCatching {
                        val history = CleaningAPI.listMine()
                        nextCleaning = computeNextCleaning(history)
                    }.onFailure { nextCleaning = null }
                },
            ).awaitAll()
        }
    }

    // 点呼状态由 AppStore rollTicker 每秒重算（对齐 iOS tickCountdown）；此处不再本地 -1

    val deductionTotal = state.user.points
    val announcementSub =
        when {
            latestAnnouncementTitle != null -> latestAnnouncementTitle!!
            state.announcementUnreadCount > 0 -> "未読 ${state.announcementUnreadCount} 件"
            else -> "寮からのお知らせ"
        }
    val topSong = songs.firstOrNull()
    val musicSub =
        if (topSong != null) {
            "${topSong.songTitle} · ${topSong.artist.orEmpty()}"
        } else {
            "まだ投稿がありません"
        }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 20.dp)
                    .padding(top = 24.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            val unread =
                remember(pushNotifs, feedNotifs, packageItems, state.studentNotificationUnreadCount) {
                    NotificationMapper.unreadCount(
                        push = pushNotifs,
                        feed = feedNotifs,
                        feedUnreadFallback = state.studentNotificationUnreadCount,
                        packages = packageItems,
                    )
                }
            Row(verticalAlignment = Alignment.Top) {
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(3.dp),
                ) {
                    Text(
                        // android#112 相邻: 原 ifEmpty 兜底值是硬编码演示名「リュウイヒ」、且 DEFAULT_USER.name 非空恒不触发
                        //   → loadMe 未完成/失败时首页问候演示假人姓名(真人 PII 泄漏)。与 Welcome 同门闩：
                        //   myStudentId!=null(真资料已加载)才显真名，否则中性问候「おかえりなさい」，不泄漏演示假人。
                        text =
                            if (state.myStudentId != null) {
                                "おかえり、${state.user.name} さん"
                            } else {
                                "おかえりなさい"
                            },
                        color = tokens.ink,
                        style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.2.sp),
                    )
                    Text(
                        text = todayJstLabel(),
                        color = tokens.inkMute,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }
                BellButton(
                    unread = unread,
                    onClick = { navController.navigate(Route.Notifications.path) },
                )
            }

            // 学年更新横幅
            if (state.needsRenewal) {
                RenewBanner(onClick = { showRenewSheet = true })
            }

            TopRollBar(
                navController = navController,
                deductionTotal = deductionTotal,
                late = state.user.lateCount,
                absent = state.user.absentCount,
                needsCleaning = state.user.needsCleaning,
                rollState = state.rollState,
                countdownSec = state.rollCountdownSec,
                checkinAt = state.checkinAt,
                checkinKind = state.checkinKind,
                onAbsenceClick = { showAbsenceSheet = true },
                onHealthClick = { showHealthSheet = true },
                onContactSupervisor = {
                    store.showToast("寮監：田中先生（内線 101）へ直接ご連絡ください")
                },
            )

            // 次の罰則清掃小卡（有安排才显）
            nextCleaning?.let { info ->
                NextCleaningCard(info)
            }

            // お知らせ
            AnnouncementCard(
                subtitle = announcementSub,
                unread = state.announcementUnreadCount,
                onClick = { navController.navigate(Route.Announcements.path) },
            )

            // バス
            BusCard(
                bus = upcomingBus,
                onClick = { navController.navigate(Route.BusList.path) },
            )

            // 宅配
            SectionCard(
                icon = SuzuIcons.Pkg,
                iconBg = tokens.dangerBg,
                iconTint = tokens.danger,
                title = "宅配便 · $pendingPackages 件未受取",
                subtitle = "未受取あり",
                badge = pendingPackages.takeIf { it > 0 },
                onClick = { navController.navigate(Route.Delivery.path) },
            )

            // 活動 → Schedule（标题已去「今週」，与拉取范围一致）
            EventsCard(
                events = homeEvents,
                onClick = { navController.navigate(Route.Schedule.path) },
            )

            // リクエスト曲（最新投稿，不是投票最高）
            SectionCard(
                icon = SuzuIcons.Music,
                iconBg = MusicPurple,
                title = "リクエスト曲 · ${songs.size} 件",
                subtitle = musicSub,
                onClick = { navController.navigate(Route.Music.path) },
            )

            LostFoundGrid(
                items = lostItems.take(3),
                onClick = { navController.navigate(Route.LostFound.path) },
            )
        }
    }

    if (showRenewSheet) {
        RenewStudentNoSheet(onDismiss = { showRenewSheet = false })
    }
    if (showAbsenceSheet) {
        AbsenceSheet(onDismiss = { showAbsenceSheet = false })
    }
    if (showHealthSheet) {
        HealthSheet(onDismiss = { showHealthSheet = false })
    }
}

@Composable
private fun RenewBanner(onClick: () -> Unit) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(primary.copy(alpha = 0.06f))
                .border(1.dp, primary.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Icon(
            imageVector = SuzuIcons.ContactCard,
            contentDescription = null,
            tint = primary,
            modifier = Modifier.size(18.dp),
        )
        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(
                "アカウント番号の更新が必要です",
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
            )
            Text(
                "新学年の学年・組・出席番号を設定してください",
                color = t.inkMute,
                style = TextStyle(fontSize = 12.sp),
            )
        }
        Box(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(99.dp))
                    .background(primary)
                    .padding(horizontal = 14.dp, vertical = 8.dp),
        ) {
            Text("更新", color = Color.White, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        }
    }
}

@Composable
private fun NextCleaningCard(info: NextCleaningInfo) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(t.paper)
                .border(1.dp, t.hair, RoundedCornerShape(16.dp))
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(38.dp)
                    .clip(CircleShape)
                    .background(CleaningIconBg),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = SuzuIcons.Sparkles,
                contentDescription = null,
                tint = CleaningIconFg,
                modifier = Modifier.size(18.dp),
            )
        }
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(
                "次の罰則清掃",
                color = t.inkSub,
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
            )
            Text(
                "${info.dateText} ${info.timeText}",
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
            )
        }
    }
}

@Composable
private fun AnnouncementCard(
    subtitle: String,
    unread: Int,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Box(contentAlignment = Alignment.TopEnd) {
            Box(
                modifier =
                    Modifier
                        .size(44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(primary.copy(alpha = 0.07f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = SuzuIcons.Megaphone,
                    contentDescription = null,
                    tint = primary,
                    modifier = Modifier.size(20.dp),
                )
            }
            if (unread > 0) {
                Box(
                    modifier =
                        Modifier
                            .offset(x = 4.dp, y = (-4).dp)
                            .size(20.dp)
                            .clip(CircleShape)
                            .background(t.danger)
                            .border(2.dp, Color.White, CircleShape),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        "$unread",
                        color = Color.White,
                        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
                    )
                }
            }
        }
        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text("お知らせ", color = t.ink, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold))
            Text(
                subtitle,
                color = t.inkSub,
                style = TextStyle(fontSize = 12.sp),
                maxLines = 1,
            )
        }
        Icon(SuzuIcons.ChevR, contentDescription = null, tint = t.inkMute, modifier = Modifier.size(16.dp))
    }
}

@Composable
private fun BusCard(
    bus: UpcomingBus?,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(primary.copy(alpha = 0.07f)),
            contentAlignment = Alignment.Center,
        ) {
            Icon(SuzuIcons.Bus, contentDescription = null, tint = primary, modifier = Modifier.size(22.dp))
        }
        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            if (bus != null) {
                Text(
                    if (bus.isToday) "次のバス便" else "次回運行",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp),
                )
                Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(
                        bus.time,
                        color = t.ink,
                        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold, fontFamily = FontFamily.Monospace),
                    )
                    if (bus.isToday) {
                        Text(
                            "· ${bus.direction}",
                            color = t.inkMute,
                            style = TextStyle(fontSize = 12.sp),
                            maxLines = 1,
                        )
                    } else {
                        val md = bus.date.drop(5).replace("-", "/")
                        Text(
                            "· $md(${bus.weekday})",
                            color = t.inkMute,
                            style = TextStyle(fontSize = 12.sp),
                        )
                    }
                }
                if (!bus.isToday) {
                    Text(bus.direction, color = t.inkMute, style = TextStyle(fontSize = 11.sp), maxLines = 1)
                }
            } else {
                Text("次のバス便", color = t.inkSub, style = TextStyle(fontSize = 13.sp))
                Text("予定なし", color = t.inkMute, style = TextStyle(fontSize = 14.sp))
            }
        }
        Icon(SuzuIcons.ChevR, contentDescription = null, tint = t.inkMute, modifier = Modifier.size(16.dp))
    }
}

@Composable
private fun EventsCard(
    events: List<EventOut>,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier =
                    Modifier
                        .size(32.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(Color(0xFF5FBEC8).copy(alpha = 0.13f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = SuzuIcons.Cal,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(18.dp),
                )
            }
            Spacer(modifier = Modifier.width(10.dp))
            Text(
                // android#68: 对齐 iOS「活動 · N件」——数据范围是今天到明年年底，不写「今週」
                text = "活動 · ${events.size} 件",
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                modifier = Modifier.weight(1f),
            )
            Icon(SuzuIcons.ChevR, contentDescription = null, tint = t.inkMute, modifier = Modifier.size(16.dp))
        }
        events.take(2).forEach { e ->
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = e.eventDate.drop(5),
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                    modifier = Modifier.width(50.dp),
                )
                Text(
                    text = e.title,
                    color = t.ink,
                    style = TextStyle(fontSize = 13.sp),
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = formatEventTime(e.startAt),
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )
            }
        }
    }
}

@Composable
private fun LostFoundGrid(
    items: List<LostFoundOut>,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                text = "遺失物 · 最新",
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
            )
            Icon(SuzuIcons.ChevR, contentDescription = null, tint = t.inkMute, modifier = Modifier.size(16.dp))
        }
        if (items.isNotEmpty()) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items.forEach { item ->
                    LostTile(label = item.itemName, modifier = Modifier.weight(1f))
                }
                // 不足 3 格时补空白占位，保持格子宽度
                repeat(3 - items.size) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }
    }
}

@Composable
private fun LostTile(
    label: String,
    modifier: Modifier = Modifier,
) {
    val t = SuzuT.current
    Box(
        modifier =
            modifier
                .height(96.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(
                    Brush.linearGradient(
                        colors =
                            listOf(
                                LostFixedColor.copy(alpha = 0.40f),
                                LostFixedColor.copy(alpha = 0.13f),
                            ),
                    ),
                ).border(0.5.dp, t.hair, RoundedCornerShape(16.dp))
                .padding(8.dp),
        contentAlignment = Alignment.BottomStart,
    ) {
        Text(
            text = label.take(8),
            color = Color.White,
            style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}

@Composable
private fun BellButton(
    unread: Int,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(contentAlignment = Alignment.TopEnd) {
        Box(
            modifier =
                Modifier
                    .size(44.dp)
                    .shadow(4.dp, RoundedCornerShape(14.dp), ambientColor = t.ink, spotColor = t.ink)
                    .clip(RoundedCornerShape(14.dp))
                    .background(t.paper)
                    .border(0.5.dp, t.hair, RoundedCornerShape(14.dp))
                    .clickable(onClick = onClick),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = SuzuIcons.Bell,
                contentDescription = "通知",
                tint = t.ink,
                modifier = Modifier.size(22.dp),
            )
        }
        if (unread > 0) {
            Box(
                modifier =
                    Modifier
                        .offset(x = 4.dp, y = (-4).dp)
                        .defaultMinSize(minWidth = 16.dp, minHeight = 16.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(t.danger)
                        .border(1.5.dp, Color.White, RoundedCornerShape(percent = 50))
                        .padding(horizontal = 4.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "$unread",
                    color = Color.White,
                    style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
    }
}

private fun todayJstLabel(): String {
    val today = JstDate.today()
    val fmt = DateTimeFormatter.ofPattern("yyyy 年 M 月 d 日（E）", Locale.JAPANESE)
    return today.format(fmt)
}

private fun formatEventTime(startAt: String?): String {
    if (startAt.isNullOrBlank()) return ""
    return runCatching { startAt.substring(11, 16) }.getOrDefault("")
}

private fun pickUpcomingBus(routes: List<BusRouteOut>): UpcomingBus? {
    val today = JstDate.today()
    val nowHm = JstDate.nowTime().format(DateTimeFormatter.ofPattern("HH:mm"))
    val active =
        routes
            .filter { !it.deprecated && it.kind == "dorm_special" }
            .sortedBy { it.scheduleAt }
    // 今日且时刻未过
    active
        .firstOrNull { r ->
            val date = r.scheduleAt.take(10)
            val time = runCatching { r.scheduleAt.substring(11, 16) }.getOrDefault("")
            date == today.toString() && time > nowHm
        }?.let { r ->
            return UpcomingBus(
                time = r.scheduleAt.substring(11, 16),
                direction = r.direction,
                date = r.scheduleAt.take(10),
                weekday = weekdayOf(r.scheduleAt.take(10)),
                isToday = true,
            )
        }
    // 最近未来日
    active
        .firstOrNull { r -> r.scheduleAt.take(10) > today.toString() }
        ?.let { r ->
            return UpcomingBus(
                time = runCatching { r.scheduleAt.substring(11, 16) }.getOrDefault(""),
                direction = r.direction,
                date = r.scheduleAt.take(10),
                weekday = weekdayOf(r.scheduleAt.take(10)),
                isToday = false,
            )
        }
    return null
}

private fun weekdayOf(ymd: String): String =
    runCatching {
        LocalDate.parse(ymd).format(DateTimeFormatter.ofPattern("E", Locale.JAPANESE))
    }.getOrDefault("")

private fun computeNextCleaning(history: List<jp.tomoshibi.android.data.network.endpoints.CleaningAssignmentOut>): NextCleaningInfo? {
    val pending =
        history
            .filter { it.status == "assigned" || it.status == "done" }
            .sortedBy { it.scheduledAt }
    val first = pending.firstOrNull() ?: return null
    val odt =
        runCatching { OffsetDateTime.parse(first.scheduledAt) }.getOrNull()
            ?: return null
    val jst = odt.atZoneSameInstant(JstDate.TOKYO)
    return NextCleaningInfo(
        dateText = "%d月%d日".format(jst.monthValue, jst.dayOfMonth),
        timeText = "%d時%02d分".format(jst.hour, jst.minute),
        area = first.area,
    )
}
