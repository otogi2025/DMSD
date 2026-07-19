package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.EventOut
import jp.tomoshibi.android.data.network.endpoints.EventsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

// 行事详情 — 对齐 iOS EventDetailView 生产文案（CommunityStubs.swift）：
//   PageHeader「活動詳細」+ 浅青渐变 hero（年·零填充月 / 超大日 / 曜日全称·时刻）
//   + 标题 + 📍场所（有才显）+ 描述卡（仅 event.description，无写死后缀）
//   +「カレンダーに追加」toast（Android 不写 iPhone）
//   数据：GET /api/v1/events 后按 UUID 查找（后端无单条详情端点）
@Composable
fun EventDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val store = LocalAppStore.current
    val t = SuzuT.current
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<EventOut>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = EventsAPI.listEvents()
                val found = items.firstOrNull { it.id.equals(id, ignoreCase = true) }
                if (found == null) LoadState.Empty else LoadState.Success(found)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return
                LoadState.Failed(e.display)
            } catch (_: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(id) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "活動詳細", level = 2, onLeft = { navController.popBackStack() })

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    EmptyState(icon = SuzuIcons.Cal, title = "活動が見つかりません")
                }

                is LoadState.Success -> {
                    val event = s.value
                    // 从 ISO 日期串 "2026-04-23" 取年 / 零填充月 / 日 / 曜日全称
                    val parts = event.eventDate.split("-")
                    val year = parts.getOrNull(0) ?: ""
                    val month = parts.getOrNull(1) ?: "" // 已是两位零填充
                    val day = parts.getOrNull(2)?.toIntOrNull()?.toString() ?: ""
                    val weekday = weekdayFullJa(event.eventDate)
                    val time = fmtEventTime(event.startAt)

                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                    ) {
                        Spacer(Modifier.height(4.dp))

                        Column(
                            modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(20.dp))
                                    .background(
                                        Brush.linearGradient(
                                            listOf(Color(0xFFE8F4F6), Color(0xFFA8DCE2)),
                                        ),
                                    ).padding(vertical = 28.dp),
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(4.dp),
                        ) {
                            Text(
                                "$year · $month",
                                color = t.inkSub,
                                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                            )
                            Text(
                                day,
                                color = t.ink,
                                style =
                                    TextStyle(
                                        fontSize = 54.sp,
                                        fontWeight = FontWeight.Black,
                                        fontFamily = FontFamily.Monospace,
                                    ),
                            )
                            Text(
                                "$weekday · $time",
                                color = t.inkSub,
                                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
                            )
                        }

                        Text(
                            event.title,
                            color = t.ink,
                            style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Black),
                        )

                        // 后端无 place 字段；iOS 生产 place 恒空。有 description 外的场所信息时才画。
                        // EventOut 无 place → 本屏不画 📍 行（对齐生产）。

                        SuzuCard {
                            Text(
                                event.description.orEmpty().ifBlank { "（説明はありません）" },
                                color = t.inkSub,
                                style = TextStyle(fontSize = 14.sp, lineHeight = 22.sp),
                            )
                        }

                        PrimaryButton(title = "カレンダーに追加", icon = SuzuIcons.Cal) {
                            store.showToast("カレンダーに追加しました")
                        }

                        Spacer(Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

// 日语曜日全称（「木曜日」），对齐 iOS DateFormatter(EEEE, ja_JP)
private fun weekdayFullJa(dateIso: String): String =
    runCatching {
        val ld = LocalDate.parse(dateIso)
        val zdt = ld.atStartOfDay(ZoneId.of("Asia/Tokyo"))
        DateTimeFormatter.ofPattern("EEEE", Locale.JAPAN).format(zdt)
    }.getOrDefault("木曜日")

private fun fmtEventTime(startAt: String?): String {
    if (startAt == null) return "終日"
    return runCatching { startAt.substring(11, 16) }.getOrDefault("終日")
}
