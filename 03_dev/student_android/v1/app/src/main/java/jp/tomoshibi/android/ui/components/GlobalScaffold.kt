package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.ui.theme.SuzuT

// 全屏统一 scaffold — 装 BottomTabs（3 按钮浮空 capsule + 中央 ⭐点呼 raised）+ 全局 sheet
//
// API 契约:
//   activeTab: "apply" | "me" | "" (Home / 其他无 nav 屏传空字符串)
//   content: 屏内容（自动留底部 92dp 给 BottomTabs + raised 按钮）
//
// 中央 ⭐点呼 → 弹 RollCallSheet（不走 nav，不切 tab）
@Composable
fun GlobalScaffold(
    activeTab: String,
    navController: NavHostController,
    content: @Composable () -> Unit
) {
    var rollSheetOpen by remember { mutableStateOf(false) }
    val tokens = SuzuT.current

    Box(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        // 内容层 — 留 92dp 底部空间给 BottomTabs（capsule 62 + 边距 16 + raised 凸起 22）
        Box(modifier = Modifier.fillMaxSize().padding(bottom = 92.dp)) {
            content()
        }
        // BottomTabs 浮在底部
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
        ) {
            BottomTabs(
                navController = navController,
                active = activeTab,
                onRollClick = { rollSheetOpen = true }
            )
        }
        // 点呼 sheet — 中央按钮触发后覆盖
        if (rollSheetOpen) {
            RollCallSheet(onDismiss = { rollSheetOpen = false })
        }
    }
}
