package jp.tomoshibi.android.ui.screens.announcements

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.AnnouncementBrief
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.AnnouncementsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 公告一览（标题「お知らせ」）— 接真后端 AnnouncementsAPI.list()（§5.3）。
//
// ★★ 本屏是「列表屏接后端」的示范模板，其余列表屏照此结构改：
//    1. 三态 var ui by remember { mutableStateOf<LoadState<List<XxxOut>>>(LoadState.Loading) }
//    2. suspend fun load()：try 调 XxxAPI.yyy() → 空判 Empty/Success；catch ApiError → Failed(e.display)
//    3. LaunchedEffect(Unit) { load() } 进屏即拉
//    4. when (ui) { Loading -> LoadingBox; Failed -> FailedBox(重试); Empty -> EmptyState; Success -> 列表 }
//    5. 行卡直接吃后端 DTO 字段（不再经 MockData / data.model 本地模型）
@Composable
fun AnnouncementsScreen(navController: NavHostController) {
    val t = SuzuT.current
    val scope = rememberCoroutineScope()
    val store = LocalAppStore.current
    // 三态：Loading / Failed(消息) / Empty / Success(后端 AnnouncementBrief 列表)
    var ui by remember { mutableStateOf<LoadState<List<AnnouncementBrief>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表。
    // 401 → AppStore 统一清令牌，TomoshibiApp 会话门跳登录页（对齐 iOS handleIfUnauthorized）。
    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = AnnouncementsAPI.list().items
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) {
                    return
                }
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // 自绘 header（返回箭头 +「お知らせ」标题）—— 規格明确不用 PageHeader
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                Box(
                    modifier =
                        Modifier
                            .size(36.dp)
                            .clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        imageVector = SuzuIcons.ChevL,
                        contentDescription = null,
                        tint = t.ink,
                        modifier = Modifier.size(22.dp),
                    )
                }
                Text(
                    "お知らせ",
                    color = t.ink,
                    style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold),
                )
            }

            // 三态渲染
            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                // 空态 —— bell.slash 等价图标 SuzuIcons.Bell
                LoadState.Empty -> {
                    EmptyState(title = "お知らせはありません", icon = SuzuIcons.Bell)
                }

                is LoadState.Success -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        s.value.forEach { brief ->
                            AnnouncementRow(
                                brief = brief,
                                onClick = { navController.navigate(Route.Announcement(brief.id).path) },
                            )
                        }
                        Spacer(Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

// 公告列表卡 — 左未读圆点 + 标题/摘要/底行，整卡点击进详情（brief 为后端 DTO AnnouncementBrief）
@Composable
private fun AnnouncementRow(
    brief: AnnouncementBrief,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val unread = !brief.isRead
    SuzuCard(
        modifier = Modifier.clickable(onClick = onClick),
        padding = 14,
    ) {
        Row(verticalAlignment = Alignment.Top) {
            // 左未读圆点：未读时 8dp primary 实心圆，已读留空占位（保持对齐）
            Box(
                modifier = Modifier.size(8.dp).padding(top = 6.dp),
                contentAlignment = Alignment.Center,
            ) {
                if (unread) {
                    Box(
                        modifier =
                            Modifier
                                .size(8.dp)
                                .clip(RoundedCornerShape(percent = 50))
                                .background(MaterialTheme.colorScheme.primary),
                    )
                }
            }
            Spacer(Modifier.width(10.dp))
            Column(modifier = Modifier.weight(1f)) {
                // 标题：未读加粗，已读 Medium
                Text(
                    brief.title,
                    color = t.ink,
                    style =
                        TextStyle(
                            fontSize = 15.sp,
                            fontWeight = if (unread) FontWeight.Bold else FontWeight.Medium,
                        ),
                )
                Spacer(Modifier.height(4.dp))
                // 摘要：最多 2 行，超出省略（后端 body_summary）
                Text(
                    brief.bodySummary,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Spacer(Modifier.height(8.dp))
                // 底行：左「老师名 · 时刻」灰字，右回复气泡 + 回复数
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        "${brief.authorTeacherName} · ${fmtTime(brief.createdAt)}",
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp),
                    )
                    Spacer(Modifier.weight(1f))
                    if (brief.replyCount > 0) {
                        Icon(
                            imageVector = SuzuIcons.Chat,
                            contentDescription = null,
                            tint = t.inkMute,
                            modifier = Modifier.size(14.dp),
                        )
                        Spacer(Modifier.width(4.dp))
                        Text(
                            "${brief.replyCount}",
                            color = t.inkMute,
                            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
                        )
                    }
                }
            }
        }
    }
}

// ISO datetime（"2026-04-20T14:30:00+09:00"）→ 简洁显示「MM-dd HH:mm」。
// 解析失败（后端格式变化 / 串太短）原样返回，避免显示崩溃。
private fun fmtTime(iso: String): String = runCatching { "${iso.substring(5, 10)} ${iso.substring(11, 16)}" }.getOrDefault(iso)
