package jp.tomoshibi.android.ui.screens.home

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.LostItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.SectionCard
import jp.tomoshibi.android.ui.components.TopRollBar
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// HomeScreen omnibus — 6 section 自上而下（对应 iOS HomeStubs.swift LifeTab）
//   1. TopRollBar (amber hero, 跳 Deduction)
//   2. 次回バス      → Bus
//   3. 宅配便 + badge → Delivery
//   4. 今週の活動    → Schedule + 2 行 preview
//   5. リクエスト曲  → Music (紫 iconBg)
//   6. 遺失物 3 色块  → LostFound
// Auth flow 5 屏 standalone（无 BottomTabs），唯独 HomeScreen 用 GlobalScaffold(activeTab="")
@Composable
fun HomeScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    val totalDeduction = state.deductions.sumOf { it.points }

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
            // ── greeting ──
            Column {
                Text(
                    text = "おかえりなさい",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
                )
                Text(
                    text = "${state.user.name.ifEmpty { "リュウイヒ" }}さん",
                    color = tokens.ink,
                    style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold),
                )
                Text(
                    text = "${state.user.dorm} ${state.user.room}",
                    color = tokens.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )
            }

            Spacer(Modifier.height(4.dp))

            // ── 1. TopRollBar (amber hero) ──
            TopRollBar(
                navController = navController,
                deductionTotal = totalDeduction,
            )

            // ── 2. 次回バス ──
            val bus = MockData.DEFAULT_BUS
            SectionCard(
                icon = SuzuIcons.Bus,
                iconBg = tokens.pill,
                title = "次回バス ${bus.time}",
                subtitle = "${bus.date} ・ ${bus.route}",
                onClick = { navController.navigate(Route.Bus.path) },
            )

            // ── 3. 宅配便（red badge）──
            val delivery = MockData.DEFAULT_DELIVERY
            SectionCard(
                icon = SuzuIcons.Pkg,
                iconBg = tokens.danger,
                title = "宅配便",
                subtitle = "${delivery.source}・${delivery.note}",
                badge = delivery.count,
                onClick = { navController.navigate(Route.Delivery.path) },
            )

            // ── 4. 今週の活動 + 2 行 preview ──
            EventsCard(navController = navController)

            // ── 5. リクエスト曲 (紫 iconBg) ──
            val topSong =
                state.musicRequests.maxByOrNull { it.votes }
                    ?: MockData.DEFAULT_MUSIC.first()
            SectionCard(
                icon = SuzuIcons.Music,
                iconBg = MusicPurple,
                title = "リクエスト曲",
                subtitle = "${topSong.title}・${topSong.artist}",
                onClick = { navController.navigate(Route.Music.path) },
            )

            // ── 6. 遺失物 3 色块 grid ──
            LostFoundGrid(
                items = MockData.DEFAULT_LOST_FOUND,
                onClick = { navController.navigate(Route.LostFound.path) },
            )
        }
    }
}

// 紫色 iconBg — iOS HomeStubs.swift 1021 行 0xa78bfa→0x7c3aed gradient
private val MusicPurple = Color(0xFF7C3AED)

// 今週の活動 card — title row + 2 行 EVENTS_PREVIEW
@Composable
private fun EventsCard(navController: NavHostController) {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .clickable { navController.navigate(Route.Schedule.path) }
                .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier =
                    Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(t.pill),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = SuzuIcons.Cal,
                    contentDescription = null,
                    tint = t.ink,
                    modifier = Modifier.size(20.dp),
                )
            }
            Spacer(Modifier.width(12.dp))
            Text(
                text = "今週の活動・${MockData.EVENTS_THIS_WEEK} 件",
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
            )
            Icon(
                imageVector = SuzuIcons.ChevR,
                contentDescription = null,
                tint = t.inkMute,
                modifier = Modifier.size(16.dp),
            )
        }
        // 2 行 preview — date(50dp) / title / time
        MockData.EVENTS_PREVIEW.forEach { e ->
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = e.date,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium),
                    modifier = Modifier.width(50.dp),
                )
                Text(
                    text = e.title,
                    color = t.ink,
                    style = TextStyle(fontSize = 13.sp),
                    modifier = Modifier.weight(1f),
                )
                Text(
                    text = e.time,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )
            }
        }
    }
}

// 遺失物 3 色块 grid — 96×96dp 圆 16dp，hex parse
@Composable
private fun LostFoundGrid(
    items: List<LostItem>,
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
                text = "遺失物・最新",
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                modifier = Modifier.weight(1f),
            )
            Icon(
                imageVector = SuzuIcons.ChevR,
                contentDescription = null,
                tint = t.inkMute,
                modifier = Modifier.size(16.dp),
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items.take(3).forEach { item ->
                LostTile(item = item, modifier = Modifier.weight(1f))
            }
        }
    }
}

@Composable
private fun LostTile(
    item: LostItem,
    modifier: Modifier = Modifier,
) {
    val t = SuzuT.current
    val baseColor = parseHexColor(item.colorHex) ?: t.inkFaint
    Box(
        modifier =
            modifier
                .height(96.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(
                    Brush.linearGradient(
                        colors =
                            listOf(
                                baseColor.copy(alpha = 0.40f),
                                baseColor.copy(alpha = 0.13f),
                            ),
                    ),
                ).border(
                    width = 0.5.dp,
                    color = t.hair,
                    shape = RoundedCornerShape(16.dp),
                ).padding(8.dp),
        contentAlignment = Alignment.BottomStart,
    ) {
        Text(
            text = item.label.take(8),
            color = Color.White,
            style =
                TextStyle(
                    fontSize = 10.sp,
                    fontWeight = FontWeight.SemiBold,
                ),
        )
    }
}

// "FFA9C8E8" → Color(0xFFA9C8E8)
private fun parseHexColor(hex: String): Color? =
    runCatching {
        Color(hex.toLong(16))
    }.getOrNull()
