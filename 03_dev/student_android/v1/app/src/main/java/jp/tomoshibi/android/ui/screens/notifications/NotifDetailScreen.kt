package jp.tomoshibi.android.ui.screens.notifications

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Divider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.theme.SuzuT

// 通知詳細 — 单条通知详情页（对齐 iOS NotificationsView 通知卡 Pill tone）
// 数据来源：登录态 store 里的 notifications（演示假数据 MockData.DEFAULT_NOTIFICATIONS）
@Composable
fun NotifDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    // 从登录态读出全部通知，再按传进来的 id 取出本条；取不到返回 null
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val notif = state.notifications.firstOrNull { it.id == id }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            // 顶部统一头部（level=2 → 左键显示返回箭头），返回上一页
            PageHeader(
                title = "通知",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            if (notif == null) {
                // 取不到对应通知 → 空态占位
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    EmptyState(title = "通知が見つかりません")
                }
                return@GlobalScaffold
            }

            // Pill tone 映射：減点=warn / 申請=ok / 其余=accent（对齐 iOS 通知卡 Pill）
            val tone =
                when (notif.tag) {
                    "減点" -> PillTone.Warn
                    "申請" -> PillTone.Ok
                    else -> PillTone.Accent
                }

            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                // 类型 Pill + 时刻弱字（时刻用通知自身的 ts 字段，不写死）
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Pill(text = notif.tag, tone = tone)
                    Spacer(Modifier.width(10.dp))
                    Text(notif.ts, color = t.inkMute, style = TextStyle(fontSize = 12.sp))
                }

                // 标题（加粗）
                Text(
                    notif.title,
                    color = t.ink,
                    style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold, lineHeight = 32.sp),
                )

                Divider(color = t.hair, thickness = 0.5.dp)

                // 正文（用通知自身的 body 字段）
                Text(
                    notif.body,
                    color = t.ink,
                    style = TextStyle(fontSize = 15.sp, lineHeight = 24.sp),
                )

                Spacer(Modifier.height(40.dp))
            }
        }
    }
}
