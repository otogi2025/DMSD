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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.FridgePurchaseRequestOut
import jp.tomoshibi.android.data.network.endpoints.DormLifeAPI
import jp.tomoshibi.android.data.store.LocalAppStore
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

// 冷蔵庫購入届一覧（冷藏箱购买申请一览，L2 子页）— 接真后端 DormLifeAPI.listMyFridgePurchases()（GET /api/v1/dorm-life/fridge-purchases/mine）。
//   PageHeader「冷蔵庫購入届一覧」level 2 + 竖排卡列表，逐条吃后端 DTO FridgePurchaseRequestOut
//   每条 SuzuCard：左竖排「購入製品」标签 + 製品名 + Spacer + 右状态 Pill
//   套三态外壳：Loading→LoadingBox / Failed→FailedBox(可重试) / Empty→EmptyState「提出済みの届はありません」/ Success→卡列表
@Composable
fun FridgeListScreen(navController: NavHostController) {
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Empty / Success(后端 FridgePurchaseRequestOut 列表)
    val store = LocalAppStore.current
    var ui by remember { mutableStateOf<LoadState<List<FridgePurchaseRequestOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表。
    suspend fun load() {
        // 401 → 清会话（对齐 iOS：令牌已死不留失败态误导）。
        val tokenAtStart = store.snapshot().authToken
        ui = LoadState.Loading
        ui =
            try {
                val items = DormLifeAPI.listMyFridgePurchases()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return
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
                title = "冷蔵庫購入届一覧",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            // 三态渲染
            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                // 空态 — iOS 用 snowflake 图标，Android 无对应令牌，沿用 EmptyState 默认图标
                LoadState.Empty -> {
                    EmptyState(title = "提出済みの届はありません")
                }

                is LoadState.Success -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        s.value.forEach { item ->
                            FridgePurchaseCard(item)
                        }
                        Spacer(Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

// 单条冷蔵庫購入卡 — 左竖排「購入製品」标签 + 製品名 + 右状态 Pill（对齐 iOS FridgePurchaseRow，item 为后端 DTO FridgePurchaseRequestOut）
@Composable
private fun FridgePurchaseCard(item: FridgePurchaseRequestOut) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                // 「購入製品」固定标签
                Text(
                    "購入製品",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp),
                )
                Spacer(Modifier.height(4.dp))
                // 製品名（A/B 款照 iOS fridgeProductText 展开，后端 product 字段同为 "A"/"B"）
                Text(
                    fridgeProductText(item.product),
                    color = t.ink,
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                )
            }
            Spacer(Modifier.width(10.dp))
            val pair = fridgeStatusPair(item.status)
            Pill(text = pair.first, tone = pair.second)
        }
    }
}

// 製品款名展开 — 对齐 iOS fridgeProductText（A=BESTEK 小型 / B=Haier 2 门，其余回退「製品X」）
private fun fridgeProductText(product: String): String =
    when (product) {
        "A" -> "製品A: BESTEK 小型 1ドア 47L"
        "B" -> "製品B: Haier 2ドア 85L"
        else -> "製品$product"
    }

// 状态 → (徽章文字, Pill 色调) — 对齐 iOS fridgeStatusPair
//   ordered→「注文済」Accent / delivered→「引渡済」Ok / rejected→「却下」Danger / 其余(pending)→「審査中」Warn
private fun fridgeStatusPair(status: String): Pair<String, PillTone> =
    when (status) {
        "ordered" -> "注文済" to PillTone.Accent
        "delivered" -> "引渡済" to PillTone.Ok
        "rejected" -> "却下" to PillTone.Danger
        else -> "審査中" to PillTone.Warn
    }
