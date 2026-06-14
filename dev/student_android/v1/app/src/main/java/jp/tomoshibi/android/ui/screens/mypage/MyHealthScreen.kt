package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.HealthRecord
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.theme.SuzuT

// 体調報告履歴（L2）— 対齐 iOS MyHealthView：
//   PageHeader「体調報告履歴」level 2 + 竖排卡列表逐条 MockData.DEFAULT_HEALTH
//   每条卡：上行 左「{症状} {体温}°C」/ 右「{日付}」，下行 备注（非空时）
@Composable
fun MyHealthScreen(navController: NavHostController) {
    val t = SuzuT.current

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "体調報告履歴", level = 2, onLeft = { navController.popBackStack() })

            // 竖排卡列表（间距 10），逐条假数据
            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                MockData.DEFAULT_HEALTH.forEach { rec ->
                    HealthCard(rec)
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 体調報告 1 条卡 — 上行 症状+体温 / 日付，下行 备注
@Composable
private fun HealthCard(rec: HealthRecord) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        // 上行：左症状（+体温）／右日付
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                rec.symptom,
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
            )
            // 体温非空时：「{tempC}°C」13sp semibold 等宽红色
            if (rec.tempC != null) {
                Spacer(Modifier.width(6.dp))
                Text(
                    "${rec.tempC}°C",
                    color = t.danger,
                    style =
                        TextStyle(
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            fontFamily = FontFamily.Monospace,
                        ),
                )
            }
            Spacer(Modifier.weight(1f))
            Text(
                rec.date,
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
            )
        }
        // 下行：备注（非空时，12.5sp inkSub）
        if (rec.note != null) {
            Spacer(Modifier.height(6.dp))
            Text(
                rec.note,
                color = t.inkSub,
                style = TextStyle(fontSize = 12.5.sp),
            )
        }
    }
}
