package jp.tomoshibi.android.ui.screens.deduction

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Divider
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.theme.SuzuT

@Composable
fun DeductionScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    val total = state.deductions.sumOf { it.points }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 顶部 ← + 減点明細 + グラフ →
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Text("←", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
                }
                Spacer(Modifier.width(8.dp))
                Text(
                    "減点明細",
                    color = tokens.ink,
                    modifier = Modifier.weight(1f),
                    style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold),
                )
                Text(
                    "グラフ →",
                    color = tokens.ok,
                    modifier = Modifier.clickable { /* TODO chart screen */ },
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                )
            }

            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                // 大数字卡（amber 渐变）
                Column(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(18.dp))
                            .background(tokens.amberGrad)
                            .padding(horizontal = 20.dp, vertical = 18.dp),
                ) {
                    Text(
                        "今月合計",
                        color = tokens.warnDeep,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp),
                    )
                    Spacer(Modifier.height(2.dp))
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(
                            String.format("%.1f", total),
                            color = tokens.warnDeep,
                            style =
                                TextStyle(
                                    fontSize = 56.sp,
                                    fontWeight = FontWeight.Bold,
                                    fontFamily = FontFamily.Monospace,
                                    lineHeight = 60.sp,
                                ),
                        )
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "点",
                            color = tokens.warnDeep,
                            modifier = Modifier.padding(bottom = 10.dp),
                            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                        )
                    }
                }

                // threshold marks bar
                Box(
                    modifier = Modifier.fillMaxWidth().padding(top = 4.dp, bottom = 8.dp),
                ) {
                    Column {
                        Canvas(modifier = Modifier.fillMaxWidth().height(8.dp)) {
                            val w = size.width
                            val barH = size.height
                            // 灰底
                            drawRect(color = Color(0xFFE7E1D6), size = Size(w, barH))
                            // 进度（按 8 点封顶）
                            val ratio = (total / 8.0).coerceAtMost(1.0).toFloat()
                            drawRect(
                                color = Color(0xFFD4A05F),
                                size = Size(w * ratio, barH),
                            )
                            // 8 点 刻度
                            drawLine(
                                color = Color(0xFF8A6336),
                                start = Offset(w - 2f, -2f),
                                end = Offset(w - 2f, barH + 2f),
                                strokeWidth = 2f,
                            )
                        }
                        Spacer(Modifier.height(6.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("0", color = tokens.inkMute, style = TextStyle(fontSize = 10.sp))
                            Text(
                                "8 外出禁止",
                                color = tokens.danger,
                                style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold),
                            )
                        }
                    }
                }

                // 列表
                Column(
                    modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
                ) {
                    state.deductions.forEachIndexed { i, d ->
                        if (i > 0) Divider(color = tokens.hair, thickness = 0.5.dp)
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                d.date,
                                color = tokens.inkSub,
                                style = TextStyle(fontSize = 13.sp, fontFamily = FontFamily.Monospace),
                            )
                            Spacer(Modifier.width(14.dp))
                            Text(
                                d.reason,
                                color = tokens.ink,
                                modifier = Modifier.weight(1f),
                                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
                            )
                            Text(
                                "+" + String.format("%.1f", d.points),
                                color = if (d.points >= 1.0) tokens.danger else tokens.warnDeep,
                                style =
                                    TextStyle(
                                        fontSize = 14.sp,
                                        fontWeight = FontWeight.Bold,
                                        fontFamily = FontFamily.Monospace,
                                    ),
                            )
                        }
                    }
                }

                // ルール脚注
                Column(modifier = Modifier.padding(horizontal = 4.dp)) {
                    Text(
                        "現在のルール: 遅刻 0.5 点・欠席 1.0 点",
                        color = tokens.inkMute,
                        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                    )
                    Text(
                        "月累計 8 点で外出禁止",
                        color = tokens.inkMute,
                        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                    )
                }
                Spacer(Modifier.height(40.dp))
            }
        }
    }
}
