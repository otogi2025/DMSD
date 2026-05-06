package jp.tomoshibi.android

import androidx.compose.runtime.Composable
import androidx.navigation.compose.rememberNavController
import jp.tomoshibi.android.nav.TomoshibiNavGraph

// 顶层 composable — 装载 Navigation
@Composable
fun TomoshibiApp() {
    val navController = rememberNavController()
    TomoshibiNavGraph(navController = navController)
}
