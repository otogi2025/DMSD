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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
import jp.tomoshibi.android.data.model.Deduction
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.theme.SuzuT

// ───────────────────────────────────────────────────────────────
// MyPointsScreen / MyPointsChartScreen — 对齐 iOS MyPointsView（§6）+ MyPointsChartView（§6b）
//   §6  減点明細：琥珀渐变总分卡 + 0→8 进度条 + 逐条明细 + 规则盒
//   §6b 減点グラフ：過去 12 ヶ月 折线图（Canvas 自绘）+ 阈值线 + 图例
// 数据全部来自 MockData.DEFAULT_DEDUCTIONS，无网络层（与 iOS 未接后端的屏一致）
// ───────────────────────────────────────────────────────────────

// §6 减点明细页（L2）
@Composable
fun MyPointsScreen(navController: NavHostController) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary

    val deductions = MockData.DEFAULT_DEDUCTIONS
    // 今月合計 = 逐条 points 求和（演示 = 4.5）
    val total = deductions.sumOf { it.points }
    // 进度比例：0→8 满刻度，封顶 1.0 防溢出
    val ratio = (total / 8.0).coerceIn(0.0, 1.0).toFloat()

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "減点明細",
                level = 2,
                onLeft = { navController.popBackStack() },
                right = {
                    // 右上「グラフ →」青绿可点 → 减点グラフ页
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

                // ── 琥珀渐变总分卡（amberGrad 底，深棕字）──
                AmberTotalCard(total = total)

                // ── 进度条 0→8（8 处红标 + 下方刻度行）──
                PointsProgressBar(ratio = ratio)

                // ── 明细列表（逐条 DEFAULT_DEDUCTIONS，padding 0 的白卡）──
                SuzuCard(padding = 0) {
                    deductions.forEachIndexed { index, item ->
                        DeductionRow(item)
                        if (index != deductions.lastIndex) {
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

                // ── 规则盒（pill 灰底）──
                RuleBox()

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 琥珀渐变总分卡：「今月合計」+ 大数字 + 「点」
@Composable
private fun AmberTotalCard(total: Double) {
    val t = SuzuT.current
    // 深棕字（对齐 iOS #5C3410），80% 透明给小标题
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
                formatPoints(total),
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

// 进度条：灰底胶囊 + amber→warn 渐变填充到 ratio + 8 红标 + 下方刻度行
@Composable
private fun PointsProgressBar(ratio: Float) {
    val t = SuzuT.current
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        // 轨道（Box 叠层：灰底 → 填充 → 竖标）
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .height(12.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(t.hair),
        ) {
            // 填充：从左填到 points/8
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth(ratio)
                        .height(12.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(t.warn),
            )
            // 8 处红竖标（位于最右端 8/8 = 100%）
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(12.dp),
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

        // 下方刻度行：0 / 8 外出禁止
        Row(modifier = Modifier.fillMaxWidth()) {
            Text(
                "0",
                color = t.inkMute,
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

// 明细单行：日期（80 宽等宽）+ reason + 右「+{points}」
@Composable
private fun DeductionRow(item: Deduction) {
    val t = SuzuT.current
    // ≥1 → danger 红 / <1 → warnDeep
    val pointColor = if (item.points >= 1.0) t.danger else t.warnDeep
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
        Spacer(Modifier.width(8.dp))
        Text(
            item.reason,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
            modifier = Modifier.weight(1f),
        )
        Spacer(Modifier.width(8.dp))
        Text(
            "+${formatPoints(item.points)}",
            color = pointColor,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
        )
    }
}

// 规则盒：pill 灰底圆角 12
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
            "月累計 8 点で外出禁止",
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp, lineHeight = 18.sp),
        )
    }
}

// §6b 减点グラフ页（L2）— 折线图外壳 + Canvas 本体
@Composable
fun MyPointsChartScreen(navController: NavHostController) {
    val t = SuzuT.current

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
                    // 小标题
                    Text(
                        "過去 12 ヶ月",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp),
                    )
                    Spacer(Modifier.height(16.dp))

                    // 折线图本体（高 200dp，y 轴 0→8）
                    PointsLineChart()

                    Spacer(Modifier.height(8.dp))

                    // x 轴月份标签：5,6,7,8,9,10,11,12,1,2,3,4（共 12 个）
                    Row(modifier = Modifier.fillMaxWidth()) {
                        chartMonths().forEach { m ->
                            Box(modifier = Modifier.weight(1f), contentAlignment = Alignment.Center) {
                                Text(
                                    m.toString(),
                                    color = t.inkMute,
                                    style = TextStyle(fontSize = 10.sp, fontFamily = FontFamily.Monospace),
                                )
                            }
                        }
                    }

                    Spacer(Modifier.height(16.dp))

                    // 图例：红线「外出禁止閾値」
                    LegendRow(color = t.danger, label = "外出禁止閾値")
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 折线图 Canvas：青绿折线 + 节点圆点 + y=8 红线，y 轴 0→8 映射高度
@Composable
private fun PointsLineChart() {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    // 演示数据（12 个月）
    val data = listOf(0.0, 0.0, 1.0, 0.0, 0.5, 1.0, 0.0, 2.0, 0.0, 1.0, 2.0, 4.5)
    val maxY = 8.0 // y 轴满刻度

    Canvas(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(200.dp),
    ) {
        val w = size.width
        val h = size.height

        // y 值（0→8）映射到画布高度：0 在底、8 在顶
        fun yPx(v: Double): Float = (h - (v / maxY) * h).toFloat()

        // x 均分到 12 个节点
        fun xPx(i: Int): Float = if (data.size <= 1) w / 2f else (i.toFloat() / (data.size - 1)) * w

        // y=8 红色实线阈值（外出禁止）
        drawLine(
            color = t.danger,
            start = Offset(0f, yPx(8.0)),
            end = Offset(w, yPx(8.0)),
            strokeWidth = 2f,
        )

        // 青绿折线（逐段连线）
        for (i in 0 until data.size - 1) {
            drawLine(
                color = primary,
                start = Offset(xPx(i), yPx(data[i])),
                end = Offset(xPx(i + 1), yPx(data[i + 1])),
                strokeWidth = 3f,
            )
        }

        // 节点圆点（白底 + 青绿描边）
        data.forEachIndexed { i, v ->
            val center = Offset(xPx(i), yPx(v))
            drawCircle(color = Color.White, radius = 5f, center = center)
            drawCircle(
                color = primary,
                radius = 5f,
                center = center,
                style = Stroke(width = 2.5f),
            )
        }
    }
}

// 图例单行：一截彩色短线 + 标签
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
                    .width(18.dp)
                    .height(3.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(color),
        )
        Spacer(Modifier.width(8.dp))
        Text(
            label,
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp),
        )
    }
}

// 点数格式化：整数去掉「.0」（4.5 → "4.5" / 1.0 → "1"），对齐 iOS 显示
private fun formatPoints(v: Double): String = if (v % 1.0 == 0.0) v.toInt().toString() else v.toString()

// x 轴月份标签序列：5..12 然后 1..4（共 12 个月）
private fun chartMonths(): List<Int> = (5..12).toList() + (1..4).toList()
