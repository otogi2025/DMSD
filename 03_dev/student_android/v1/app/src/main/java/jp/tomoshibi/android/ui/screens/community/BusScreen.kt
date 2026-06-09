package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.BusRouteOut
import jp.tomoshibi.android.data.network.endpoints.BusAPI
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.MonoNumeralStyle
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 巴士时刻表屏（UI 标题「バス時刻表」）— 接真后端 BusAPI.listRoutes()（spec §7.6 GET /api/v1/bus/routes）。
//
// 数据来源从 MockData.WEEKDAY/SATURDAY/SUNDAY（假数据）换成后端 List<BusRouteOut>，套 LoadState 三态外壳。
//
// ⚠️ 结构差异说明：原假数据按「平日 / 土曜 / 日曜」三段分组，但后端 BusRouteOut 没有星期分组字段，
//    只给 scheduleAt（完整日期时间串）+ kind（daily_commute / dorm_special）。所以分组改成由 scheduleAt
//    推导星期，落到「平日 / 土曜 / 日曜」三段。「次回」高亮 = 列表里最早的一班（按 scheduleAt 字典序，
//    后端已是 ISO 串可直接比较），同一班同时填进 hero。
//
// 一行内显示项映射：
//   时刻「09:20」      ← scheduleAt 的 HH:mm 段
//   路线「高校棟 → 金川駅」← direction（DTO 的方向字段，语义对应原 BusRow.route）
//   hero 日期「05/06(水)」 ← scheduleAt 的 MM/dd + 星期（曜日）

// 屏内行模型 —— 把 BusRouteOut 抽成 UI 要的 3 个显示项 + 是否「次回」高亮。
private data class BusRow(
    val time: String, // HH:mm，来自 scheduleAt
    val route: String, // 方向，来自 direction
    val highlight: Boolean = false, // 是否「次回」（最早一班）
)

// 星期日文（0=日 … 6=土），用于 hero 日期「05/06(水)」里的曜日。
private val WEEKDAY_JP = listOf("日", "月", "火", "水", "木", "金", "土")

// scheduleAt（如 "2026-05-06T09:20:00+09:00"）取 HH:mm 段。解析失败原样返回前 5 位兜底，不崩。
private fun timeOf(scheduleAt: String): String = runCatching { scheduleAt.substring(11, 16) }.getOrDefault(scheduleAt)

// scheduleAt 取 MM/dd 段（"05/06"）。解析失败兜底返回月日两段原文。
private fun mmddOf(scheduleAt: String): String =
    runCatching { "${scheduleAt.substring(5, 7)}/${scheduleAt.substring(8, 10)}" }.getOrDefault(scheduleAt)

// 由 scheduleAt 的 yyyy-MM-dd 算星期几（0=周日 … 6=周六）。用纯算术（Zeller 同类），不引日期库。
// 解析失败返回 -1（归到「平日」段，避免崩）。
private fun weekdayIndexOf(scheduleAt: String): Int =
    runCatching {
        var y = scheduleAt.substring(0, 4).toInt()
        var m = scheduleAt.substring(5, 7).toInt()
        val d = scheduleAt.substring(8, 10).toInt()
        // Zeller 公式要求 1、2 月算作上一年的 13、14 月
        if (m < 3) {
            m += 12
            y -= 1
        }
        val k = y % 100
        val j = y / 100
        val h = (d + (13 * (m + 1)) / 5 + k + k / 4 + j / 4 + 5 * j) % 7
        // Zeller 的 h：0=周六 … 6=周五，换算成 0=周日 … 6=周六
        (h + 6) % 7
    }.getOrDefault(-1)

@Composable
fun BusScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Empty / Success(后端 BusRouteOut 列表)
    var ui by remember { mutableStateOf<LoadState<List<BusRouteOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val items = BusAPI.listRoutes()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(tokens.pearl)
                    .verticalScroll(rememberScrollState()),
        ) {
            // 头部
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 18.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(44.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(SuzuIcons.ChevL, contentDescription = "戻る", tint = tokens.ink, modifier = Modifier.size(24.dp))
                }
                Spacer(Modifier.width(4.dp))
                Text(
                    "バス時刻表",
                    color = tokens.ink,
                    style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold),
                )
            }

            // 三态渲染
            when (val st = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(st.message, onRetry = { scope.launch { load() } })
                }

                // 空态 —— 巴士图标
                LoadState.Empty -> {
                    EmptyState(title = "運行予定はありません", icon = SuzuIcons.Bus)
                }

                is LoadState.Success -> {
                    BusContent(routes = st.value, tokens = tokens)
                }
            }
        }
    }
}

// 渲染成功态：hero（次回運行）+ 平日 / 土曜 / 日曜 三段时刻表。
// routes 直接吃后端 BusRouteOut，星期分组 / 时刻 / 方向都从 scheduleAt + direction 现算。
@Composable
private fun BusContent(
    routes: List<BusRouteOut>,
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
) {
    // 「次回」= 列表里 scheduleAt 字典序最早的一班（后端是 ISO 串，可直接比字符串）。
    val nextRoute = routes.minByOrNull { it.scheduleAt }

    // 按星期分三段：平日（周一~周五）/ 土曜 / 日曜，每段内按时刻排序，并标出「次回」那班。
    fun rowsFor(predicate: (Int) -> Boolean): List<BusRow> =
        routes
            .filter { predicate(weekdayIndexOf(it.scheduleAt)) }
            .sortedBy { it.scheduleAt }
            .map { r ->
                BusRow(
                    time = timeOf(r.scheduleAt),
                    route = r.direction,
                    highlight = nextRoute != null && r.id == nextRoute.id,
                )
            }

    val weekdayRows = rowsFor { it in 1..5 } // 周一~周五
    val saturdayRows = rowsFor { it == 6 } // 周六
    val sundayRows = rowsFor { it == 0 } // 周日（解析失败的 -1 也不会落进任何段，归 0 段需 == 0 才算）

    // 次回運行 hero —— 只在有最早一班时显示
    if (nextRoute != null) {
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(tokens.btnGrad)
                    .padding(20.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(SuzuIcons.Bus, contentDescription = null, tint = Color.White, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(8.dp))
                Text(
                    "次回運行",
                    color = Color.White.copy(alpha = 0.9f),
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium),
                )
            }
            Spacer(Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.Bottom) {
                Text(
                    timeOf(nextRoute.scheduleAt),
                    color = Color.White,
                    style = MonoNumeralStyle.copy(fontSize = 44.sp, lineHeight = 48.sp),
                )
                Spacer(Modifier.width(10.dp))
                // 日期「05/06(水)」：MM/dd + 曜日
                val wd = weekdayIndexOf(nextRoute.scheduleAt)
                val wdLabel = if (wd in 0..6) "(${WEEKDAY_JP[wd]})" else ""
                Text(
                    "${mmddOf(nextRoute.scheduleAt)}$wdLabel",
                    color = Color.White.copy(alpha = 0.9f),
                    modifier = Modifier.padding(bottom = 6.dp),
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
                )
            }
            Spacer(Modifier.height(4.dp))
            Text(
                nextRoute.direction,
                color = Color.White,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
            )
        }

        Spacer(Modifier.height(20.dp))
    }

    // 平日 / 土曜 / 日曜 三段（某段为空则不渲染那段）
    if (weekdayRows.isNotEmpty()) {
        ScheduleSection("平日", weekdayRows, tokens)
        Spacer(Modifier.height(16.dp))
    }
    if (saturdayRows.isNotEmpty()) {
        ScheduleSection("土曜", saturdayRows, tokens)
        Spacer(Modifier.height(16.dp))
    }
    if (sundayRows.isNotEmpty()) {
        ScheduleSection("日曜", sundayRows, tokens)
    }
    Spacer(Modifier.height(20.dp))
}

@Composable
private fun ScheduleSection(
    label: String,
    rows: List<BusRow>,
    tokens: jp.tomoshibi.android.ui.theme.SuzuTokens,
) {
    Column(modifier = Modifier.padding(horizontal = 16.dp)) {
        Text(
            label,
            color = tokens.inkSub,
            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium),
        )
        Spacer(Modifier.height(8.dp))
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            rows.forEach { r ->
                val borderColor = if (r.highlight) tokens.ink else tokens.hair
                Row(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(tokens.paper)
                            .border(if (r.highlight) 2.dp else 1.dp, borderColor, RoundedCornerShape(12.dp))
                            .padding(horizontal = 14.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        r.time,
                        color = tokens.ink,
                        style =
                            MonoNumeralStyle.copy(
                                fontSize = 16.sp,
                                lineHeight = 20.sp,
                                fontWeight = FontWeight.SemiBold,
                            ),
                    )
                    Spacer(Modifier.width(14.dp))
                    Text(
                        r.route,
                        color = tokens.inkSub,
                        style = TextStyle(fontSize = 13.sp),
                    )
                    Spacer(Modifier.weight(1f))
                    if (r.highlight) {
                        Box(
                            modifier =
                                Modifier
                                    .clip(RoundedCornerShape(99.dp))
                                    .background(tokens.pill)
                                    .padding(horizontal = 8.dp, vertical = 2.dp),
                        ) {
                            Text(
                                "次回",
                                color = tokens.ink,
                                style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold),
                            )
                        }
                    }
                }
            }
        }
    }
}
