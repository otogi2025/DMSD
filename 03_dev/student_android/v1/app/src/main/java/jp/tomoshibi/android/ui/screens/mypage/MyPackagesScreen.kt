package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import jp.tomoshibi.android.data.model.PackageItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.theme.SuzuT

// 荷物受取履歴（包裹受取履历，L2 子页）— 対齐 iOS MyPackagesView（规格 §10）
//   PageHeader「荷物受取履歴」level 2 + 竖排卡列表，逐条 MockData.DEFAULT_PACKAGES
//   每条 SuzuCard：左 📦 + 竖排（寄件方 / 日期）+ Spacer + 右 Pill（待領=橙 / 領済=灰）
@Composable
fun MyPackagesScreen(navController: NavHostController) {
    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "荷物受取履歴",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                MockData.DEFAULT_PACKAGES.forEach { pkg ->
                    PackageHistoryCard(pkg)
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 单条包裹卡 — 📦 28sp + 寄件方/日期 竖排 + 受取状态 Pill
@Composable
private fun PackageHistoryCard(pkg: PackageItem) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Column(modifier = Modifier.fillMaxWidth()) {
            androidx.compose.foundation.layout.Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("📦", style = TextStyle(fontSize = 28.sp))
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        pkg.from,
                        color = t.ink,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                    )
                    Spacer(Modifier.height(2.dp))
                    Text(
                        pkg.date,
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                    )
                }
                Spacer(Modifier.width(8.dp))
                // 待領 → Warn（橙）/ 領済 → Neutral（灰）
                Pill(
                    text = pkg.status,
                    tone = if (pkg.status == "待領") PillTone.Warn else PillTone.Neutral,
                )
            }
        }
    }
}
