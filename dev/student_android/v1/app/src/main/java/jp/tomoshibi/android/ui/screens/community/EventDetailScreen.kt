package jp.tomoshibi.android.ui.screens.community

import jp.tomoshibi.android.data.store.LocalAppStore

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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import java.time.LocalDate

// 行事详情 — 对齐 iOS EventDetailView（规格 §4.4）：
//   PageHeader「活動詳細」level 2 + 浅青渐变 hero 日期大卡 + 标题 + 📍场所 + 描述卡 + 「カレンダーに追加」按钮
//   按 id 在 MockData.DEFAULT_EVENTS 里找；找不到 → EmptyState
@Composable
fun EventDetailScreen(
    navController: NavHostController,
    id: Int,
) {
    val store = LocalAppStore.current
    val t = SuzuT.current
    val ctx = LocalContext.current
    val event = MockData.DEFAULT_EVENTS.find { it.id == id }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "活動詳細", level = 2, onLeft = { navController.popBackStack() })

            if (event == null) {
                // 取不到行事（id 不存在）→ 空态
                EmptyState(icon = SuzuIcons.Cal, title = "活動が見つかりません")
            } else {
                // 从 ISO 日期串 "2026-04-23" 解析出 年 / 月 / 日 / 曜日
                val ld = LocalDate.parse(event.date)
                val year = ld.year // 纯整数，下面用字符串拼接显示，绝不过 NumberFormat（防「2,026」）
                val month = ld.monthValue
                val day = ld.dayOfMonth
                // dayOfWeek：MONDAY=1 … SUNDAY=7；映射到日语曜日单字「日月火水木金土」
                val weekdayChars = listOf("月", "火", "水", "木", "金", "土", "日")
                val weekday = weekdayChars[ld.dayOfWeek.value - 1]

                Column(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .verticalScroll(rememberScrollState())
                            .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(14.dp),
                ) {
                    Spacer(Modifier.height(4.dp))

                    // hero 日期卡：浅青渐变圆角大卡，居中「年 · 月」+ 超大日数 +「曜日 · 时刻」
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
                            "$year · $month", // 字符串拼接，年份原样显示不本地化
                            color = t.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                        )
                        Text(
                            "$day", // 超大日数：54sp heavy 等宽
                            color = t.ink,
                            style =
                                TextStyle(
                                    fontSize = 54.sp,
                                    fontWeight = FontWeight.Black,
                                    fontFamily = FontFamily.Monospace,
                                ),
                        )
                        Text(
                            "$weekday · ${event.time}",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
                        )
                    }

                    // 标题（22 heavy）
                    Text(
                        event.title,
                        color = t.ink,
                        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Black),
                    )

                    // 📍 场所（place 非空才画）
                    if (event.place.isNotEmpty()) {
                        Text(
                            "📍 ${event.place}",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
                        )
                    }

                    // 描述卡 = event.desc + 写死后缀
                    SuzuCard {
                        Text(
                            event.desc +
                                "。新入生の自己紹介、在学生との交流タイム、軽食とドリンクをご用意します。",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 14.sp, lineHeight = 22.sp),
                        )
                    }

                    // 「カレンダーに追加」按钮 → toast。Android 不能说 iPhone。
                    // TODO: 后续可接 Android 日历 Intent（ACTION_INSERT），本波最小版只弹 toast
                    PrimaryButton(title = "カレンダーに追加", icon = SuzuIcons.Cal) {
                        store.showToast("カレンダーに追加しました")
                    }

                    Spacer(Modifier.height(20.dp))
                }
            }
        }
    }
}
