package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.Canvas
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.model.ListLoadState
import jp.tomoshibi.android.data.network.endpoints.ProfileDemeritEntry
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 减点明细 + 折线图 — 对齐 iOS MyPointsView / MyPointsChartView 生产分支

private data class PointDisplay(
    val id: String,
    val date: String,
    val label: String,
    val valPoints: Double,
)

private fun ProfileDemeritEntry.toDisplay(): PointDisplay =
    PointDisplay(
        id = id,
        date = isoToYmd(createdAt),
        label = reason,
        valPoints = points,
    )

@Composable
fun MyPointsScreen(navController: NavHostController) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val demerits by store.myDemeritEvents.collectAsState()
    val profileState by store.profileState.collectAsState()

    LaunchedEffect(Unit) {
        store.loadMyProfile()
    }

    val placeholder = store.isProfilePlaceholder(state)
    val total = state.user.points
    val ratio = (total / 8.0).coerceIn(0.0, 1.0).toFloat()
    val rows = demerits.map { it.toDisplay() }

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "減点明細",
                level = 2,
                onLeft = { navController.popBackStack() },
                right = {
                    Text(
                        "グラフ →",
                        color = primary,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
                        modifier =
                            Modifier
                                .clip(RoundedCornerShape(8.dp))
                                .clickable { navController.navigate(Route.MyPointsChart.path) }
                                .padding(horizontal = 6.dp, vertical = 4.dp),
                    )
                },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                Spacer(Modifier.height(4.dp))

                AmberTotalCard(total = total, placeholder = placeholder)
                PointsProgressBar(ratio = ratio)

                Text(
                    "減点履歴（全期間）",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                )

                when {
                    rows.isNotEmpty() -> {
                        SuzuCard(padding = 0) {
                            rows.forEachIndexed { index, item ->
                                DeductionRow(item)
                                if (index != rows.lastIndex) {
                                    Box(
                                        modifier =
                                            Modifier
                                                .fillMaxWidth()
                                                .height(1.dp)
                                                .background(t.hairSoft),
                                    )
                                }
                            }
                        }
                    }

                    profileState is ListLoadState.Loading -> {
                        CircularProgressIndicator(
                            modifier =
                                Modifier
                                    .align(Alignment.CenterHorizontally)
                                    .padding(vertical = 16.dp),
                        )
                    }

                    profileState is ListLoadState.Failed -> {
                        val msg = (profileState as ListLoadState.Failed).message
                        EmptyState(
                            icon = SuzuIcons.Warn,
                            title = "読み込みに失敗しました",
                            message = msg,
                        )
                    }

                    else -> {
                        EmptyState(icon = SuzuIcons.CheckCirc, title = "減点なし")
                    }
                }

                RuleBox()
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

@Composable
private fun AmberTotalCard(
    total: Double,
    placeholder: Boolean,
) {
    val t = SuzuT.current
    val brown = Color(0xFF5C3410)
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(20.dp))
                .background(t.amberGrad)
                .padding(horizontal = 20.dp, vertical = 22.dp),
    ) {
        Text(
            "今月合計",
            color = brown.copy(alpha = 0.8f),
            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.7.sp),
        )
        Spacer(Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.Bottom) {
            Text(
                if (placeholder) "—" else String.format("%.1f", total),
                color = brown,
                style =
                    TextStyle(
                        fontSize = 48.sp,
                        fontWeight = FontWeight.Black,
                        fontFamily = FontFamily.Monospace,
                    ),
            )
            Spacer(Modifier.width(4.dp))
            Text(
                "点",
                color = brown,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
                modifier = Modifier.padding(bottom = 8.dp),
            )
        }
    }
}

@Composable
private fun PointsProgressBar(ratio: Float) {
    val t = SuzuT.current
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .height(12.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(t.hair),
        ) {
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth(ratio)
                        .height(12.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(t.warn),
            )
            // 4 点橙标（中点）
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) {
                Box(
                    modifier =
                        Modifier
                            .width(2.dp)
                            .height(12.dp)
                            .background(t.warn),
                )
            }
            // 8 点红标（右端）
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.CenterEnd,
            ) {
                Box(
                    modifier =
                        Modifier
                            .width(2.dp)
                            .height(12.dp)
                            .background(t.danger),
                )
            }
        }

        Row(modifier = Modifier.fillMaxWidth()) {
            Text(
                "0",
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
            )
            Spacer(modifier = Modifier.weight(1f))
            Text(
                "4 罰則清掃",
                color = t.warn,
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
            )
            Spacer(modifier = Modifier.weight(1f))
            Text(
                "8 外出禁止",
                color = t.danger,
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
            )
        }
    }
}

@Composable
private fun DeductionRow(item: PointDisplay) {
    val t = SuzuT.current
    val pointColor = if (item.valPoints >= 1.0) t.danger else t.warnDeep
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            item.date,
            color = t.inkMute,
            style = TextStyle(fontSize = 12.sp, fontFamily = FontFamily.Monospace),
            modifier = Modifier.width(80.dp),
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            item.label,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
            modifier = Modifier.weight(1f),
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            "+${formatPoints(item.valPoints)}",
            color = pointColor,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
        )
    }
}

@Composable
private fun RuleBox() {
    val t = SuzuT.current
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.pill)
                .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(
            "現在のルール: 遅刻 0.5 点 / 欠席 1.0 点",
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold, lineHeight = 18.sp),
        )
        Text(
            "月累計 4 点で罰則清掃、月累計 8 点で外出禁止",
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp, lineHeight = 18.sp),
        )
    }
}

@Composable
fun MyPointsChartScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val demerits by store.myDemeritEvents.collectAsState()

    LaunchedEffect(Unit) {
        store.loadMyProfile()
    }

    val (labels, values) = monthlyChartData(demerits)

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "減点グラフ",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
            ) {
                Spacer(Modifier.height(4.dp))

                SuzuCard(padding = 20) {
                    Text(
                        "過去 12 ヶ月",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp),
                    )
                    Spacer(modifier = Modifier.height(14.dp))

                    Row(modifier = Modifier.fillMaxWidth()) {
                        // y 轴数字标签 8/6/4/2/0
                        Column(
                            modifier =
                                Modifier
                                    .width(24.dp)
                                    .height(200.dp),
                            verticalArrangement = Arrangement.SpaceBetween,
                            horizontalAlignment = Alignment.End,
                        ) {
                            listOf("8", "6", "4", "2", "0").forEach { n ->
                                Text(
                                    n,
                                    color = t.inkMute,
                                    style = TextStyle(fontSize = 10.sp, fontFamily = FontFamily.Monospace),
                                )
                            }
                        }
                        Spacer(modifier = Modifier.width(6.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            PointsLineChart(values = values)
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(modifier = Modifier.fillMaxWidth()) {
                                labels.forEach { m ->
                                    Box(modifier = Modifier.weight(1f), contentAlignment = Alignment.Center) {
                                        Text(
                                            m,
                                            color = t.inkMute,
                                            style = TextStyle(fontSize = 10.sp, fontFamily = FontFamily.Monospace),
                                        )
                                    }
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center,
                    ) {
                        LegendRow(color = t.warn, label = "罰則清掃閾値")
                        Spacer(modifier = Modifier.width(16.dp))
                        LegendRow(color = t.danger, label = "外出禁止閾値")
                    }
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

private fun monthlyChartData(events: List<ProfileDemeritEntry>): Pair<List<String>, List<Double>> {
    val now = JstDate.today()
    val labels = mutableListOf<String>()
    val values = mutableListOf<Double>()
    for (offset in 11 downTo 0) {
        val d = now.minusMonths(offset.toLong())
        val key = String.format("%04d-%02d", d.year, d.monthValue)
        val sum = events.filter { it.month == key }.sumOf { it.points }
        labels.add("${d.monthValue}")
        values.add(sum)
    }
    return labels to values
}

@Composable
private fun PointsLineChart(values: List<Double>) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val maxY = 8.0
    val dashGrid = PathEffect.dashPathEffect(floatArrayOf(2f, 3f), 0f)
    val dashThreshold = PathEffect.dashPathEffect(floatArrayOf(3f, 2f), 0f)

    Canvas(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(200.dp),
    ) {
        val w = size.width
        val h = size.height

        fun yPx(v: Double): Float = (h - (v / maxY) * h).toFloat()

        fun xPx(i: Int): Float =
            if (values.size <= 1) {
                w / 2f
            } else {
                (i.toFloat() / (values.size - 1)) * w
            }

        // y 轴 0/2/4/6/8 网格
        listOf(0.0, 2.0, 4.0, 6.0, 8.0).forEach { v ->
            drawLine(
                color = t.hair,
                start = Offset(0f, yPx(v)),
                end = Offset(w, yPx(v)),
                strokeWidth = 1f,
                pathEffect = dashGrid,
            )
        }

        // 4 / 8 阈值虚线
        drawLine(
            color = t.warn,
            start = Offset(0f, yPx(4.0)),
            end = Offset(w, yPx(4.0)),
            strokeWidth = 1.5f,
            pathEffect = dashThreshold,
        )
        drawLine(
            color = t.danger,
            start = Offset(0f, yPx(8.0)),
            end = Offset(w, yPx(8.0)),
            strokeWidth = 1.5f,
            pathEffect = dashThreshold,
        )

        for (i in 0 until values.size - 1) {
            drawLine(
                color = primary,
                start = Offset(xPx(i), yPx(values[i])),
                end = Offset(xPx(i + 1), yPx(values[i + 1])),
                strokeWidth = 2.5f,
                cap = androidx.compose.ui.graphics.StrokeCap.Round,
            )
        }

        values.forEachIndexed { i, v ->
            val center = Offset(xPx(i), yPx(v))
            val isLast = i == values.lastIndex
            val radius = if (isLast) 5f else 3.5f
            val color = if (isLast) t.warn else primary
            drawCircle(color = Color.White, radius = radius, center = center)
            drawCircle(color = color, radius = radius, center = center, style = Stroke(width = 2f))
        }
    }
}

@Composable
private fun LegendRow(
    color: Color,
    label: String,
) {
    val t = SuzuT.current
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier =
                Modifier
                    .width(14.dp)
                    .height(2.dp)
                    .background(color),
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            label,
            color = t.inkSub,
            style = TextStyle(fontSize = 11.sp),
        )
    }
}

private fun formatPoints(v: Double): String = if (v % 1.0 == 0.0) v.toInt().toString() else String.format("%.1f", v)
