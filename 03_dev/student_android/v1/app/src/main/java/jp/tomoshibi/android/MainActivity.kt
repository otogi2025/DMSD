package jp.tomoshibi.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import jp.tomoshibi.android.data.model.ThemeMode
import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.store.AppStore
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.theme.TomoshibiTheme
import kotlinx.coroutines.runBlocking

class MainActivity : ComponentActivity() {
    private lateinit var appStore: AppStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        appStore = AppStore(applicationContext)

        // 自动登录：启动时从 DataStore 恢复登录令牌给 ApiClient.token（之后所有请求自动带 Authorization: Bearer）。
        // runBlocking 在 onCreate 同步读一次（DataStore 读 < 100ms，可接受），保证 setContent 渲染前令牌已就绪。
        // 令牌为 null（未登录 / 已登出）时不 set；SplashScreen 仍按 authed flag 决定进登录页还是首页。
        runBlocking {
            appStore.snapshot().authToken?.let { ApiClient.token = it }
        }

        setContent {
            CompositionLocalProvider(LocalAppStore provides appStore) {
                val state by appStore.state.collectAsState(initial = jp.tomoshibi.android.data.seed.MockData.INITIAL_STATE)
                TomoshibiTheme(darkTheme = state.themeMode == ThemeMode.DARK) {
                    Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                        TomoshibiApp()
                    }
                }
            }
        }
    }

    // TODO P6: NFC ForegroundDispatch
    // override fun onResume() { super.onResume(); nfcAdapter?.enableForegroundDispatch(...) }
    // override fun onPause() { super.onPause(); nfcAdapter?.disableForegroundDispatch(this) }
}
