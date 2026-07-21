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
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import jp.tomoshibi.android.data.model.ThemeMode
import jp.tomoshibi.android.data.store.AppStore
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.theme.TomoshibiTheme
import kotlinx.coroutines.flow.map

class MainActivity : ComponentActivity() {
    private lateinit var appStore: AppStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        appStore = AppStore(applicationContext)

        setContent {
            CompositionLocalProvider(LocalAppStore provides appStore) {
                // 只映射 themeMode，避免与 TomoshibiApp 内会话门双份全量 collect。
                // 复审：mapped Flow 必须 remember 固定实例——否则每次重组 new 一个 Flow，collectAsState
                // 以新实例为 key 重启订阅、先回落 initial（浅色），切换主题时会闪一帧浅色（回归）。
                val themeFlow = remember(appStore) { appStore.state.map { it.themeMode } }
                val themeMode by themeFlow.collectAsState(
                    initial = jp.tomoshibi.android.data.seed.MockData.INITIAL_STATE.themeMode,
                )
                TomoshibiTheme(darkTheme = themeMode == ThemeMode.DARK) {
                    Box(modifier = Modifier.fillMaxSize().systemBarsPadding()) {
                        TomoshibiApp()
                    }
                }
            }
        }
    }

    // TODO P6：NFC 前台分发（ForegroundDispatch）
    // override fun onResume() { super.onResume(); nfcAdapter?.enableForegroundDispatch(...) }
    // override fun onPause() { super.onPause(); nfcAdapter?.disableForegroundDispatch(this) }
}
