package jp.tomoshibi.android.ui.screens.community

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.PackageItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 宅配（包裹）一覧 — 対齐 iOS PackagesView：
//   PageHeader「宅配」level 2 + 待領/領済 segmented tab + 📦 卡列表（待領才显示「受取」按钮）
@Composable
fun DeliveryScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val ctx = LocalContext.current
    var tab by remember { mutableStateOf("pending") } // pending=待領 / done=領済
    var received by remember { mutableStateOf(setOf<Int>()) } // 本会话已点「受取」的 id

    val all = MockData.DEFAULT_PACKAGES
    val pending = all.filter { it.status == "待領" && it.id !in received }
    val done = all.filter { it.status == "領済" || it.id in received }
    val shown = if (tab == "pending") pending else done

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            PageHeader(title = "宅配", level = 2, onLeft = { navController.popBackStack() })

            // 待領 / 領済 segmented tab（浅灰底，选中格白底加粗）
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(tokens.hairSoft)
                        .padding(4.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                SegTab("待領 · ${pending.size}", tab == "pending", Modifier.weight(1f)) { tab = "pending" }
                SegTab("領済 · ${done.size}", tab == "done", Modifier.weight(1f)) { tab = "done" }
            }

            Spacer(Modifier.height(16.dp))

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (shown.isEmpty()) {
                    EmptyState(title = "なし", icon = SuzuIcons.Pkg)
                }
                shown.forEach { pkg ->
                    PackageRow(
                        pkg = pkg,
                        showReceive = tab == "pending",
                        onReceive = {
                            received = received + pkg.id
                            Toast.makeText(ctx, "受取しました", Toast.LENGTH_SHORT).show()
                        },
                    )
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// segmented tab 单格
@Composable
private fun SegTab(
    label: String,
    active: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            modifier
                .clip(RoundedCornerShape(9.dp))
                .background(if (active) t.paper else Color.Transparent)
                .clickable(onClick = onClick)
                .padding(vertical = 9.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            color = if (active) t.ink else t.inkMute,
            style = TextStyle(fontSize = 13.sp, fontWeight = if (active) FontWeight.Bold else FontWeight.Medium),
        )
    }
}

// 宅配卡 — 📦 emoji + 发货方 / 日期·追跡番号 + 待領时「受取」按钮
@Composable
private fun PackageRow(
    pkg: PackageItem,
    showReceive: Boolean,
    onReceive: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(t.paper)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("📦", style = TextStyle(fontSize = 28.sp))
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                "${pkg.from} 荷物",
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
            )
            Spacer(Modifier.height(2.dp))
            Text(
                if (pkg.tracking != null) "${pkg.date} · ${pkg.tracking}" else pkg.date,
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
            )
        }
        if (showReceive) {
            Spacer(Modifier.width(8.dp))
            Box(
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(99.dp))
                        .background(t.btnGrad)
                        .clickable(onClick = onReceive)
                        .padding(horizontal = 16.dp, vertical = 8.dp),
            ) {
                Text(
                    "受取",
                    color = Color.White,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
    }
}
