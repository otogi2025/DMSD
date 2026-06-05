package jp.tomoshibi.android.ui.components

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
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
    content: @Composable () -> Unit,
) {
    var rollSheetOpen by remember { mutableStateOf(false) }
    var feedbackSheetOpen by remember { mutableStateOf(false) }
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val ctx = LocalContext.current

    Box(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        // 内容层 — 留 92dp 底部空间给 BottomTabs（capsule 62 + 边距 16 + raised 凸起 22）
        Box(modifier = Modifier.fillMaxSize().padding(bottom = 92.dp)) {
            content()
        }
        // 顶部点呼状态条 — 仅 rollState != IDLE（点呼中 / 欠席 / 已签到）时浮在顶部
        if (state.rollState != RollState.IDLE) {
            RollStatusBar(
                rollState = state.rollState,
                checkinAt = state.checkinAt,
                countdownSec = state.rollCountdownSec,
                modifier =
                    Modifier
                        .align(Alignment.TopCenter)
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                onClick = { feedbackSheetOpen = true },
            )
        }
        // BottomTabs 浮在底部
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .align(Alignment.BottomCenter),
        ) {
            BottomTabs(
                navController = navController,
                active = activeTab,
                onRollClick = { rollSheetOpen = true },
            )
        }
        // 点呼 sheet — 中央按钮触发后覆盖
        if (rollSheetOpen) {
            RollCallSheet(onDismiss = { rollSheetOpen = false })
        }
        // 反馈三选一 sheet — 点顶部状态条（非 done 态）触发
        if (feedbackSheetOpen) {
            FeedbackSheet(
                onDismiss = { feedbackSheetOpen = false },
                onSelect = { kind ->
                    feedbackSheetOpen = false
                    // TODO: health/absence/other 子表单弹窗待建，先 toast 占位
                    Toast.makeText(ctx, "「$kind」の報告は後日対応", Toast.LENGTH_SHORT).show()
                },
            )
        }
    }
}
