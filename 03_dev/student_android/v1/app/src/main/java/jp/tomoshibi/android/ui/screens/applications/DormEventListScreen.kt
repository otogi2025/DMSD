package jp.tomoshibi.android.ui.screens.applications

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
import jp.tomoshibi.android.data.model.DormEventProposal
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 行事企画一覧（行事企划一览，L2 子页）— 对齐 iOS DormEventProposalListView（DormLifeForms.swift 187 行起）
//   PageHeader「行事企画一覧」level 2 + 竖排卡列表，逐条 MockData.DEFAULT_DORM_EVENTS
//   每条 SuzuCard：上半 title + place 竖排 + Spacer + 状态 Pill；下半 开催日時 + 「N名」预想人数
//   空列表走 EmptyState（文案抄 iOS「提出済みの企画はありません」）
@Composable
fun DormEventListScreen(navController: NavHostController) {
    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "行事企画一覧",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                val items = MockData.DEFAULT_DORM_EVENTS
                if (items.isEmpty()) {
                    // 空状态 —「提出済みの企画はありません」（iOS 用 sparkles 图标）
                    EmptyState(
                        title = "提出済みの企画はありません",
                        icon = SuzuIcons.Sparkles,
                    )
                } else {
                    items.forEach { item ->
                        DormEventRow(item)
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 单条行事企画卡 — 上半 title/place 竖排 + 状态 Pill；下半 开催日時 + 「N名」预想人数
@Composable
private fun DormEventRow(item: DormEventProposal) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.Top,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        item.title,
                        color = t.ink,
                        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        item.place,
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }
                Spacer(Modifier.width(10.dp))
                // 状态徽章 — pending→「審査中」橙 / approved→「許可」绿 / rejected→「却下」红（对齐 iOS eventResultPair）
                val pair = eventResultPair(item.status)
                Pill(text = pair.first, tone = pair.second)
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                // 开催日時 — heldAt 原样显示（已是 "yyyy-MM-dd HH:mm"）
                Text(
                    item.heldAt,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
                Spacer(Modifier.weight(1f))
                // 预想参加人数 —「N名」
                Text(
                    "${item.expectedCount}名",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
        }
    }
}

// 状态 → 徽章文字 + 色调（对齐 iOS eventResultPair：审查中橙 / 许可绿 / 却下红）
private fun eventResultPair(status: String): Pair<String, PillTone> =
    when (status) {
        "approved" -> "許可" to PillTone.Ok
        "rejected" -> "却下" to PillTone.Danger
        else -> "審査中" to PillTone.Warn
    }
