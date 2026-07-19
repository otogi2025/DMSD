package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.LostFoundAPI
import jp.tomoshibi.android.data.network.endpoints.LostFoundOut
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

// 遺失物一覧 — 对齐 iOS LostView（CommunityStubs.swift）：
//   PageHeader「遺失物」（学生端无右上 +；仅寮監可投稿）
//   + 提示 Banner + 搜索（放大镜 +「検索…」；标题/场所/日期任一命中）
//   + 2 列网格（🎒 + 标题 +「场所 · 日期」）+ loading/failed/空/搜索无结果
@Composable
fun LostFoundScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var query by remember { mutableStateOf("") }
    var ui by remember { mutableStateOf<LoadState<List<LostFoundOut>>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = LostFoundAPI.list()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return
                LoadState.Failed(e.display)
            } catch (_: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    val allRows = (ui as? LoadState.Success)?.value.orEmpty()
    val filtered =
        remember(query, allRows) {
            val q = query.trim()
            if (q.isEmpty()) {
                allRows
            } else {
                allRows.filter { item ->
                    val title = item.itemName
                    val place = item.location.orEmpty()
                    val date = formatLostDate(item.createdAt)
                    title.contains(q, ignoreCase = true) ||
                        place.contains(q, ignoreCase = true) ||
                        date.contains(q, ignoreCase = true)
                }
            }
        }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 学生端无 +（iOS 生产已拔）
            PageHeader(
                title = "遺失物",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            // 提示：请将拾得物交给寮監
            val primary = MaterialTheme.colorScheme.primary
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .padding(top = 4.dp, bottom = 10.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(primary.copy(alpha = 0.06f))
                        .border(1.dp, primary.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
                        .padding(horizontal = 12.dp, vertical = 10.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Icon(
                    SuzuIcons.Info,
                    contentDescription = null,
                    tint = primary,
                    modifier = Modifier.size(13.dp).padding(top = 1.dp),
                )
                Text(
                    "拾得物・落とし物は必ず寮監に届けてください。一覧は寮監が管理しています。",
                    color = primary,
                    style = TextStyle(fontSize = 12.sp),
                    modifier = Modifier.weight(1f),
                )
            }

            // 搜索框：放大镜 +「検索…」（单字符省略号 U+2026）
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(tokens.pearl)
                        .padding(horizontal = 14.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Icon(
                    SuzuIcons.Search,
                    contentDescription = null,
                    tint = tokens.inkMute,
                    modifier = Modifier.size(18.dp),
                )
                Box(modifier = Modifier.weight(1f)) {
                    if (query.isEmpty()) {
                        Text(
                            "検索…",
                            color = tokens.inkFaint,
                            style = TextStyle(fontSize = 14.sp),
                        )
                    }
                    BasicTextField(
                        value = query,
                        onValueChange = { query = it },
                        singleLine = true,
                        textStyle = TextStyle(color = tokens.ink, fontSize = 14.sp),
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }
            Spacer(Modifier.height(14.dp))

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox(useSpinner = true)
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    EmptyState(icon = SuzuIcons.Search, title = "落とし物はありません")
                }

                is LoadState.Success -> {
                    if (filtered.isEmpty()) {
                        EmptyState(icon = SuzuIcons.Search, title = "見つかりません")
                    } else {
                        LazyVerticalGrid(
                            columns = GridCells.Fixed(2),
                            modifier =
                                Modifier
                                    .weight(1f)
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp),
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp),
                            contentPadding = PaddingValues(bottom = 24.dp),
                        ) {
                            items(filtered, key = { it.id }) { item ->
                                LostCell(
                                    item = item,
                                    onClick = {
                                        navController.navigate(Route.LostDetail(item.id).path)
                                    },
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

// 网格卡：渐变色块 + 🎒 + 标题 +「场所 · 日期」
@Composable
private fun LostCell(
    item: LostFoundOut,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val accent = Color(0xFF7C3AED) // 生产固定紫（后端无装饰色）
    val place = item.location?.takeIf { it.isNotBlank() } ?: "—"
    val date = formatLostDate(item.createdAt)

    Column(
        modifier =
            Modifier
                .clip(RoundedCornerShape(14.dp))
                .background(t.paper)
                .border(0.5.dp, t.hair, RoundedCornerShape(14.dp))
                .clickable(onClick = onClick),
    ) {
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f)
                    .background(
                        Brush.linearGradient(
                            listOf(accent.copy(alpha = 2f / 3f), accent.copy(alpha = 0.27f)),
                        ),
                    ),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                "🎒",
                style = TextStyle(fontSize = 32.sp),
                modifier = Modifier.shadow(6.dp, ambientColor = Color.Black.copy(alpha = 0.3f)),
            )
        }
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(10.dp),
            verticalArrangement = Arrangement.spacedBy(3.dp),
        ) {
            Text(
                item.itemName,
                color = t.ink,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
            )
            Text(
                "$place · $date",
                color = t.inkMute,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style = TextStyle(fontSize = 10.5.sp),
            )
        }
    }
}

/** created_at ISO →「MM-dd」（JST），对齐 iOS lostDateFmt */
internal fun formatLostDate(iso: String): String {
    val instant =
        runCatching { Instant.parse(iso) }.getOrNull()
            ?: runCatching { OffsetDateTime.parse(iso).toInstant() }.getOrNull()
            ?: return iso.take(10).drop(5) // 兜底截 "YYYY-MM-DD" → "MM-DD"
    val fmt = DateTimeFormatter.ofPattern("MM-dd").withZone(ZoneId.of("Asia/Tokyo"))
    return fmt.format(instant)
}
