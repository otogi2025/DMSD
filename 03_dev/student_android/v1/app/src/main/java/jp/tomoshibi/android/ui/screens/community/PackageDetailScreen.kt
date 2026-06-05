package jp.tomoshibi.android.ui.screens.community

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
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

// 宅配詳細 — 対齐 iOS PackageDetailView：
//   PageHeader「宅配詳細」level 2 + 📦 大 emoji + 4 行 meta 表 + 「受取確認」按钮
//   按 id 从 MockData.DEFAULT_PACKAGES 取，取不到显空态
@Composable
fun PackageDetailScreen(
    navController: NavHostController,
    id: Int,
) {
    val t = SuzuT.current
    val ctx = LocalContext.current

    // 按 id 取对应包裹；取不到为 null
    val pkg = MockData.DEFAULT_PACKAGES.find { it.id == id }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "宅配詳細", level = 2, onLeft = { navController.popBackStack() })

            if (pkg == null) {
                // 找不到对应包裹 → 空态
                EmptyState(title = "宅配が見つかりません", icon = SuzuIcons.Pkg)
            } else {
                Column(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .verticalScroll(rememberScrollState())
                            .padding(horizontal = 16.dp),
                ) {
                    SuzuCard(padding = 20) {
                        // 顶部 📦 emoji（56sp，居中）
                        Box56Center("📦")

                        Spacer(Modifier.height(16.dp))

                        // 4 行 meta：每行上 0.5dp 分隔线，左 label 灰 + 右 value 加粗
                        MetaRow("配送業者", pkg.from)
                        MetaRow("到着時刻", "${pkg.date} 14:22")
                        MetaRow("追跡番号", pkg.tracking ?: "―")
                        MetaRow("保管場所", "寮務室前棚 A-3") // iOS 端写死的演示文字
                    }

                    Spacer(Modifier.height(20.dp))

                    // 「受取確認」→ 弹 toast 后返回上层
                    PrimaryButton(title = "受取確認") {
                        Toast.makeText(ctx, "受取完了しました", Toast.LENGTH_SHORT).show()
                        navController.popBackStack()
                    }

                    Spacer(Modifier.height(20.dp))
                }
            }
        }
    }
}

// 顶部 56sp 的 📦 emoji，整行居中
@Composable
private fun Box56Center(emoji: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.Center,
    ) {
        Text(emoji, style = TextStyle(fontSize = 56.sp))
    }
}

// meta 单行 — 上边 0.5dp 分隔线 + 左 label 灰 + 右 value 加粗
@Composable
private fun MetaRow(
    label: String,
    value: String,
) {
    val t = SuzuT.current
    HorizontalDivider(color = t.hair, thickness = 0.5.dp)
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = t.inkMute, style = TextStyle(fontSize = 14.sp))
        Spacer(Modifier.weight(1f))
        Text(
            value,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
        )
    }
}
