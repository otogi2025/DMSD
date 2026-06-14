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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
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
import jp.tomoshibi.android.data.network.AnnouncementDetail
import jp.tomoshibi.android.data.network.AnnouncementReplyOut
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.AnnouncementsAPI
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 公告详情（标题「お知らせ詳細」）— 接真后端 AnnouncementsAPI.detail(id)（规格 §5.4）。
//   三态加载详情（访问时后端自动写已读）；底部回复输入栏真调 postReply，发送成功后清空 + 刷新带出新回复。
@Composable
fun AnnouncementDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val ctx = LocalContext.current
    val scope = rememberCoroutineScope()

    // 三态：Loading / Failed / Success(单条公告详情)。详情屏单条，404 等异常一律走 Failed，不退化成假数据。
    var ui by remember { mutableStateOf<LoadState<AnnouncementDetail>>(LoadState.Loading) }
    // 底部回复输入框本地 state
    var replyText by remember { mutableStateOf("") }
    // 发送中标志，避免重复提交
    var sending by remember { mutableStateOf(false) }

    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                LoadState.Success(AnnouncementsAPI.detail(id))
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "お知らせ詳細", level = 2, onLeft = { navController.popBackStack() })

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                // 单条详情无 Empty 态，兜底按失败处理避免崩溃。
                LoadState.Empty -> {
                    FailedBox("読み込みに失敗しました", onRetry = { scope.launch { load() } })
                }

                is LoadState.Success -> {
                    val detail = s.value
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
                            "${detail.authorTeacherName} · ${fmtTime(detail.createdAt)}",
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
                        // 回复区标题「返信 (N)」
                        Text(
                            "返信 (${detail.replies.size})",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                        )
                        Spacer(Modifier.height(10.dp))
                        if (detail.replies.isEmpty()) {
                            Text("まだ返信はありません", color = t.inkMute, style = TextStyle(fontSize = 13.sp))
                        } else {
                            // 回复列表（后端按时序返回）
                            detail.replies.forEach { reply ->
                                AnnouncementReplyRow(reply = reply)
                                Spacer(Modifier.height(12.dp))
                            }
                        }
                        Spacer(Modifier.height(16.dp))
                    }

                    // 底部固定回复输入栏 —— 真调 postReply 发送，成功后清空 + 刷新详情带出新回复。
                    ReplyComposer(
                        value = replyText,
                        sending = sending,
                        onValueChange = { replyText = it },
                        onSend = {
                            if (!sending && replyText.isNotBlank()) {
                                sending = true
                                scope.launch {
                                    try {
                                        AnnouncementsAPI.postReply(id, replyText)
                                        replyText = ""
                                        load() // 刷新带出新回复
                                    } catch (e: ApiError) {
                                        Toast.makeText(ctx, e.display, Toast.LENGTH_SHORT).show()
                                    } catch (e: Exception) {
                                        Toast.makeText(ctx, "送信に失敗しました", Toast.LENGTH_SHORT).show()
                                    } finally {
                                        sending = false
                                    }
                                }
                            }
                        },
                    )
                }
            }
        }
    }
}

// 单条回复行（Slack 风）：作者名 + 教员蓝胶囊 + 时刻弱字 + 回复正文（reply 为后端 DTO AnnouncementReplyOut）
@Composable
private fun AnnouncementReplyRow(reply: AnnouncementReplyOut) {
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
                fmtTime(reply.createdAt),
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

// 底部固定回复输入栏：圆角多行输入框（1~4 行）+ 圆形发送按钮（有内容且不在发送中才可点）
@Composable
private fun ReplyComposer(
    value: String,
    sending: Boolean,
    onValueChange: (String) -> Unit,
    onSend: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val canSend = value.isNotBlank() && !sending

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
        // 圆形发送按钮：可发送时主色，否则灰且禁用
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

// ISO datetime（"2026-04-20T14:30:00+09:00"）→ 简洁显示「MM-dd HH:mm」。解析失败原样返回。
private fun fmtTime(iso: String): String = runCatching { "${iso.substring(5, 10)} ${iso.substring(11, 16)}" }.getOrDefault(iso)
