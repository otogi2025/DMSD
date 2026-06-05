package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.CleaningRecord
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.theme.SuzuT

// 掃除提出履歴（扫除提出履历，L2）— 対齐 iOS MyCleanView（规格 §9）：
//   PageHeader「掃除提出履歴」level 2 + 竖排卡列表逐条 MockData.DEFAULT_CLEANING
//   每条卡：上行左竖排「范围 / 日期」+ 右 Pill（通過=绿 / 退回=红、有分数追加「· N点」）；退回时多一块红评语盒
@Composable
fun MyCleanScreen(navController: NavHostController) {
    val t = SuzuT.current

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "掃除提出履歴", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement =
                    androidx.compose.foundation.layout.Arrangement
                        .spacedBy(10.dp),
            ) {
                MockData.DEFAULT_CLEANING.forEach { record ->
                    CleanCard(record)
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 扫除提出单条卡 — 上行（左 范围/日期 竖排 + 右 状态 Pill）+ 退回时红评语盒
@Composable
private fun CleanCard(record: CleaningRecord) {
    val t = SuzuT.current
    // 退回 = 红，其余（通過）= 绿
    val tone = if (record.status == "退回") PillTone.Danger else PillTone.Ok
    // 有分数时追加「· N点」，无分数（退回）只显状态
    val pillText = if (record.score != null) "${record.status} · ${record.score}点" else record.status

    SuzuCard(padding = 14) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    record.scope,
                    color = t.ink,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.height(2.dp))
                Text(
                    record.date,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
            Pill(pillText, tone)
        }

        // 退回时多一块红色评语盒（dangerBg 底、圆角 8、评语文字红色）
        if (record.status == "退回" && record.comment != null) {
            Spacer(Modifier.height(10.dp))
            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(8.dp))
                        .background(t.dangerBg)
                        .padding(horizontal = 12.dp, vertical = 10.dp),
            ) {
                Text(
                    record.comment,
                    color = t.danger,
                    style = TextStyle(fontSize = 12.5.sp),
                )
            }
        }
    }
}
