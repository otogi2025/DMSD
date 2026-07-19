package jp.tomoshibi.android

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.navigation.compose.rememberNavController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.nav.TomoshibiNavGraph

// 顶层 composable — 装载 Navigation + 会话门（401 / 过期清令牌后自动回登录页）
@Composable
fun TomoshibiApp() {
    val navController = rememberNavController()
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    // 对齐 iOS RootView：authToken 被清掉 → 自动跳登录。
    // 只在「曾经已登录 → 变为未登录」时跳，避免冷启动 Splash 被抢导航。
    var wasAuthed by remember { mutableStateOf(false) }
    LaunchedEffect(state.authed, state.authToken) {
        val nowAuthed = state.authed && !state.authToken.isNullOrEmpty()
        if (wasAuthed && !nowAuthed) {
            navController.navigate(Route.Login.path) {
                popUpTo(0) { inclusive = true }
            }
        }
        wasAuthed = nowAuthed
    }

    TomoshibiNavGraph(navController = navController)
}
