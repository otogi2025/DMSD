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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.FridgePurchaseRequest
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.theme.SuzuT

// 冷蔵庫購入届一覧（冷藏箱购买申请一览，L2 子页）— 对齐 iOS FridgePurchaseListView（DormLifeForms.swift 第 431 行起）
//   PageHeader「冷蔵庫購入届一覧」level 2 + 竖排卡列表，逐条 MockData.DEFAULT_FRIDGE
//   每条 SuzuCard：左竖排「購入製品」标签 + 製品名 + Spacer + 右状态 Pill
//   空列表走 EmptyState「提出済みの届はありません」
@Composable
fun FridgeListScreen(navController: NavHostController) {
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

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                val items = MockData.DEFAULT_FRIDGE
                if (items.isEmpty()) {
                    // 空状态 — iOS 用 snowflake 图标，Android 无对应令牌，沿用 EmptyState 默认图标
                    EmptyState(title = "提出済みの届はありません")
                } else {
                    items.forEach { item ->
                        FridgePurchaseCard(item)
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 单条冷蔵庫購入卡 — 左竖排「購入製品」标签 + 製品名 + 右状态 Pill（对齐 iOS FridgePurchaseRow）
@Composable
private fun FridgePurchaseCard(item: FridgePurchaseRequest) {
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
                // 製品名（A/B 款照 iOS fridgeProductText 展开）
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
