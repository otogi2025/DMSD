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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.AnnouncementBrief
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// お知らせ一覧 — 対齐 iOS AnnouncementListView（§5.3）：
//   自绘 header（返回箭头 +「お知らせ」标题，注意不是 PageHeader）
//   每行卡：左未读圆点 + 标题（未读加粗）+ 摘要 2 行 + 底行「老师名 · 相对时间」+ 有回复时右侧气泡 + 回复数
@Composable
fun AnnouncementsScreen(navController: NavHostController) {
    val t = SuzuT.current
    val list = MockData.DEFAULT_ANNOUNCEMENTS

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

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (list.isEmpty()) {
                    // 空态 —— bell.slash 等价图标 SuzuIcons.Bell
                    EmptyState(title = "お知らせはありません", icon = SuzuIcons.Bell)
                }
                list.forEach { brief ->
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

// 公告列表卡 — 左未读圆点 + 标题/摘要/底行，整卡点击进详情
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
                // 摘要：最多 2 行，超出省略
                Text(
                    brief.summary,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp, lineHeight = 18.sp),
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
                Spacer(Modifier.height(8.dp))
                // 底行：左「老师名 · 相对时间」灰字，右回复气泡 + 回复数
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        "${brief.author} · ${brief.time}",
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
