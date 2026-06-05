package jp.tomoshibi.android.ui.screens.announcements

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.AnnouncementReply
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// お知らせ詳細 — 対齐 iOS AnnouncementDetailView（规格 §5.4）：
//   PageHeader「お知らせ詳細」level 2 + 正文区（标题/作者·时间/正文/分隔线/返信列表）+ 底部固定回复输入栏
//   按 id 从 MockData.DEFAULT_ANNOUNCEMENT_DETAILS 取详情；取不到显空态
@Composable
fun AnnouncementDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val ctx = LocalContext.current

    // 按 id 查公告详情（演示数据，接后端前从 mock 读）
    val detail = MockData.DEFAULT_ANNOUNCEMENT_DETAILS.find { it.id == id }

    // 底部回复输入框本地 state（演示版不真发，只弹 toast + 清空）
    var replyText by remember { mutableStateOf("") }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "お知らせ詳細", level = 2, onLeft = { navController.popBackStack() })

            if (detail == null) {
                // 取不到详情：铃铛空态
                EmptyState(
                    title = "お知らせが見つかりません",
                    icon = SuzuIcons.Bell,
                    modifier = Modifier.fillMaxWidth(),
                )
                return@Column
            }

            // 正文区：可滚动（占满除底部输入栏外的剩余高度）
            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
            ) {
                Spacer(Modifier.height(4.dp))
                // 标题 20sp bold
                Text(
                    detail.title,
                    color = t.ink,
                    style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold, lineHeight = 28.sp),
                )
                Spacer(Modifier.height(6.dp))
                // 作者 · 创建时刻（弱字）
                Text(
                    "${detail.author} · ${detail.createdAt}",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 12.sp),
                )
                Spacer(Modifier.height(14.dp))
                // 正文（行高大，读着舒服）
                Text(
                    detail.body,
                    color = t.ink,
                    style = TextStyle(fontSize = 15.sp, lineHeight = 24.sp),
                )
                Spacer(Modifier.height(18.dp))
                HorizontalDivider(color = t.hair)
                Spacer(Modifier.height(14.dp))
                // 返信 (N)
                Text(
                    "返信 (${detail.replies.size})",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.height(10.dp))

                if (detail.replies.isEmpty()) {
                    // 空回复占位
                    Text(
                        "まだ返信はありません",
                        color = t.inkMute,
                        style = TextStyle(fontSize = 13.sp),
                    )
                } else {
                    // 回复列表（旧→新，mock 数据已按此顺序排列）
                    detail.replies.forEach { reply ->
                        AnnouncementReplyRow(reply = reply)
                        Spacer(Modifier.height(12.dp))
                    }
                }
                Spacer(Modifier.height(16.dp))
            }

            // 底部固定回复输入栏
            ReplyComposer(
                value = replyText,
                onValueChange = { replyText = it },
                onSend = {
                    // 演示版：弹 toast + 清空，不真发
                    Toast.makeText(ctx, "送信しました", Toast.LENGTH_SHORT).show()
                    replyText = ""
                },
            )
        }
    }
}

// 单条回复行（Slack 风）：作者名 + 教员蓝胶囊 + 时刻弱字 + 回复正文
@Composable
private fun AnnouncementReplyRow(reply: AnnouncementReply) {
    val t = SuzuT.current
    Column(modifier = Modifier.fillMaxWidth()) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                reply.authorName,
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
            )
            // 老师身份加「教員」蓝胶囊
            if (reply.authorKind == "teacher") {
                Spacer(Modifier.width(6.dp))
                Pill(text = "教員", tone = PillTone.Accent)
            }
            Spacer(Modifier.width(8.dp))
            Text(
                reply.createdAt,
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp),
            )
        }
        Spacer(Modifier.height(4.dp))
        Text(
            reply.body,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, lineHeight = 21.sp),
        )
    }
}

// 底部固定回复输入栏：圆角多行输入框（1~4 行）+ 圆形发送按钮（有内容才可点）
@Composable
private fun ReplyComposer(
    value: String,
    onValueChange: (String) -> Unit,
    onSend: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val canSend = value.isNotBlank()

    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .background(t.paper)
                .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.Bottom,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.weight(1f).heightIn(min = 48.dp),
            placeholder = {
                Text("返信を入力...", color = t.inkMute, style = TextStyle(fontSize = 15.sp))
            },
            textStyle = TextStyle(fontSize = 15.sp, color = t.ink),
            shape = RoundedCornerShape(12.dp),
            minLines = 1,
            maxLines = 4,
        )
        // 圆形发送按钮：有内容时主色，无内容时灰且禁用
        Box(
            modifier =
                Modifier
                    .size(48.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(if (canSend) cs.primary else t.inkFaint),
            contentAlignment = Alignment.Center,
        ) {
            IconButton(onClick = onSend, enabled = canSend) {
                Icon(
                    imageVector = Icons.Filled.Send,
                    contentDescription = "送信",
                    tint = Color.White,
                    modifier = Modifier.size(20.dp),
                )
            }
        }
    }
}
