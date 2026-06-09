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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.DormEventProposalOut
import jp.tomoshibi.android.data.network.endpoints.DormLifeAPI
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 行事企画一覧（行事企划一览，L2 子页）— 对齐 iOS DormEventProposalListView（DormLifeForms.swift 187 行起）
//   PageHeader「行事企画一覧」level 2 + 竖排卡列表
//   每条 SuzuCard：上半 title + place 竖排 + Spacer + 状态 Pill；下半 开催日時 + 「N名」预想人数
//   空列表走 EmptyState（文案抄 iOS「提出済みの企画はありません」）
//
// 接真后端 DormLifeAPI.listMyEventProposals()（GET /api/v1/dorm-life/event-proposals/mine），
// 套 LoadState 三态（加载中 / 失败 / 空 / 成功）。失败必走 FailedBox，绝不退化成空列表。
@Composable
fun DormEventListScreen(navController: NavHostController) {
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Empty / Success(后端 DormEventProposalOut 列表)
    var ui by remember { mutableStateOf<LoadState<List<DormEventProposalOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val items = DormLifeAPI.listMyEventProposals()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

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
                // 三态渲染
                when (val s = ui) {
                    LoadState.Loading -> {
                        LoadingBox()
                    }

                    is LoadState.Failed -> {
                        FailedBox(s.message, onRetry = { scope.launch { load() } })
                    }

                    // 空状态 —「提出済みの企画はありません」（iOS 用 sparkles 图标）
                    LoadState.Empty -> {
                        EmptyState(
                            title = "提出済みの企画はありません",
                            icon = SuzuIcons.Sparkles,
                        )
                    }

                    is LoadState.Success -> {
                        s.value.forEach { item ->
                            DormEventRow(item)
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 单条行事企画卡 — 上半 title/place 竖排 + 状态 Pill；下半 开催日時 + 「N名」预想人数
// item 为后端 DTO DormEventProposalOut（字段名跟旧本地模型不同：状态在 result 不在 status）
@Composable
private fun DormEventRow(item: DormEventProposalOut) {
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
                // 状态徽章 — 吃后端 result 字段（对齐 iOS eventResultPair）
                val pair = eventResultPair(item.result)
                Pill(text = pair.first, tone = pair.second)
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                // 开催日時 — heldAt 原样显示（DTO 里是 String）
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

// 后端 result → 徽章文字 + 色调（对齐 iOS eventResultPair）
//   approved / approved_conditional → 「許可」绿
//   rejected → 「却下」红
//   pending / resubmit / 其他 → 「審査中」橙
private fun eventResultPair(result: String): Pair<String, PillTone> =
    when (result) {
        "approved", "approved_conditional" -> "許可" to PillTone.Ok
        "rejected" -> "却下" to PillTone.Danger
        else -> "審査中" to PillTone.Warn
    }
