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
import jp.tomoshibi.android.data.network.ItemPossessionRequestOut
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
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 物品所持許可願一覧（物品持込许可申请一览，L2 子页）— 对齐 iOS ItemPossessionListView（DormLifeForms.swift 658 行起）
//   PageHeader「物品所持許可願一覧」level 2 + 竖排卡列表，逐条 后端 ItemPossessionRequestOut
//   每条 SuzuCard：左竖排（物品名「item」/ 部屋番号 / 申請理由 / 保護者 / 提出日時）+ 右上 状态 Pill
//   空列表 → EmptyState「提出済みの願はありません」（文案抄 iOS）
//
// 接真后端：DormLifeAPI.listMyItemPossessions()（GET /api/v1/dorm-life/item-possessions/mine）。
// 套「加载中 / 失败 / 空 / 成功」三态（AnnouncementsScreen 模板同款）。失败必落 FailedBox，绝不退化成空列表。
@Composable
fun ItemListScreen(navController: NavHostController) {
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Empty / Success(后端 ItemPossessionRequestOut 列表)
    var ui by remember { mutableStateOf<LoadState<List<ItemPossessionRequestOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val items = DormLifeAPI.listMyItemPossessions()
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
                title = "物品所持許可願一覧",
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

                    // 空态：图标 + 「提出済みの願はありません」（对齐 iOS EmptyState）
                    LoadState.Empty -> {
                        EmptyState(title = "提出済みの願はありません")
                    }

                    is LoadState.Success -> {
                        s.value.forEach { item ->
                            ItemPossessionCard(item)
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 单条物品申请卡 — 左竖排（物品名 / 部屋番号 / 理由 / 保護者 / 提出日時）+ 右上 状态 Pill
@Composable
private fun ItemPossessionCard(item: ItemPossessionRequestOut) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                // 物品名「item」— 标题行
                Text(
                    item.item,
                    color = t.ink,
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.height(4.dp))
                // 部屋番号 — iOS「部屋番号 \(room_no)」
                Text(
                    "部屋番号 ${item.roomNo}",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp),
                )
                Spacer(Modifier.height(4.dp))
                // 申請理由
                Text(
                    item.reason,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp),
                )
                Spacer(Modifier.height(4.dp))
                // 保護者名
                Text(
                    "保護者 ${item.guardianName}",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )
                Spacer(Modifier.height(2.dp))
                // 提出日時（等宽字体显示时间戳）
                Text(
                    item.submittedAt,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
            Spacer(Modifier.width(8.dp))
            // 状态徽章 — 对齐 iOS itemPossessionStatusPair：approved→「許可」Ok / rejected→「却下」Danger / 其余→「審査中」Warn
            val (label, tone) = itemStatusPair(item.status)
            Pill(text = label, tone = tone)
        }
    }
}

// 状态 → (日语徽章文案, Pill 色调) — 严格对齐 iOS DormLifeForms.swift itemPossessionStatusPair
private fun itemStatusPair(status: String): Pair<String, PillTone> =
    when (status) {
        "approved" -> "許可" to PillTone.Ok
        "rejected" -> "却下" to PillTone.Danger
        else -> "審査中" to PillTone.Warn
    }
