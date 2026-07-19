package jp.tomoshibi.android.ui.screens.notifications

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
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
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 通知中心（对齐 iOS NotificationsView，规格 §5.2）
// = 聚合视图：演示态读 MockData.DEFAULT_NOTIFICATIONS（已注入登录态 store.state.notifications）
// 顶部筛选 pill 行（横向滚动 7 项）+ 通知卡列表（未读圆点 + Pill + 时刻 + 标题 + 正文）
@Composable
fun NotificationsScreen(navController: NavHostController) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val store = LocalAppStore.current
    // 登录态 store 里的通知列表（INITIAL_STATE 已塞 DEFAULT_NOTIFICATIONS）
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    // 本地筛选 state — 默认「すべて」（不过滤）
    var filter by remember { mutableStateOf("すべて") }

    // 7 项筛选标签（对齐 iOS / 规格 §5.2 — 第 7 项是「リクエスト曲」而非「リクエスト」）
    val chips = listOf("すべて", "申請", "減点", "夜学習", "宅配", "活動", "リクエスト曲")

    // 按 tag 过滤；「すべて」直通不过滤
    val filtered =
        if (filter == "すべて") {
            state.notifications
        } else {
            state.notifications.filter { it.tag == filter }
        }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // 1. 子页头部 — 标题「通知」level 2（左键返回），右侧「すべて既読」一键全标已读
            PageHeader(
                title = "通知",
                level = 2,
                onLeft = { navController.popBackStack() },
                right = {
                    Box(
                        modifier =
                            Modifier.clickable {
                                scope.launch {
                                    store.update { s ->
                                        s.copy(notifications = s.notifications.map { it.copy(read = true) })
                                    }
                                }
                            },
                    ) {
                        Text(
                            "すべて既読",
                            color = t.ink,
                            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                        )
                    }
                },
            )

            // 2. 筛选 pill 行（横向滚动）— 选中 = 主色填充白字 / 未选 = paper 底描边
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

            // 3. 通知卡列表（卡间距 8）
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
                    // 4. 空态 — 铃铛图标 +「通知はありません」
                    EmptyState(
                        icon = SuzuIcons.Bell,
                        title = "通知はありません",
                    )
                }

                filtered.forEach { n ->
                    SuzuCard(
                        padding = 14,
                        modifier =
                            Modifier.clickable {
                                // 点卡 → 标该条已读 + 跳详情
                                scope.launch {
                                    store.update { s ->
                                        s.copy(
                                            notifications =
                                                s.notifications.map {
                                                    if (it.id == n.id) it.copy(read = true) else it
                                                },
                                        )
                                    }
                                }
                                navController.navigate(Route.NotifDetail(n.id).path)
                            },
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.Top,
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            // 左：未读时画 8dp 主色实心圆点；已读留空占位（保持对齐）
                            Box(
                                modifier =
                                    Modifier
                                        .padding(top = 6.dp)
                                        .size(8.dp)
                                        .clip(CircleShape)
                                        .background(if (n.read) Color.Transparent else primary),
                            )
                            // 右：顶行 Pill(tag) + 时刻弱字 / 中标题 bold / 下正文灰字 1.5 行高
                            Column(modifier = Modifier.weight(1f)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    // Pill tone：減点=Warn / 申請=Ok / 其余=Accent
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

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// Pill 色调映射（规格 §5.2）：減点=warn / 申請=ok / 其余=accent
private fun pillToneFor(tag: String): PillTone =
    when (tag) {
        "減点" -> PillTone.Warn
        "申請" -> PillTone.Ok
        else -> PillTone.Accent
    }
