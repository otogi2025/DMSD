package jp.tomoshibi.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import jp.tomoshibi.android.data.model.ThemeMode
import jp.tomoshibi.android.data.store.AppStore
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.theme.TomoshibiTheme

class MainActivity : ComponentActivity() {
    private lateinit var appStore: AppStore

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        appStore = AppStore(applicationContext)

        setContent {
            CompositionLocalProvider(LocalAppStore provides appStore) {
                val state by appStore.state.collectAsState(initial = jp.tomoshibi.android.data.seed.MockData.INITIAL_STATE)
                TomoshibiTheme(darkTheme = state.themeMode == ThemeMode.DARK) {
                    TomoshibiApp()
                }
            }
        }
    }

    // TODO P6: NFC ForegroundDispatch
    // override fun onResume() { super.onResume(); nfcAdapter?.enableForegroundDispatch(...) }
    // override fun onPause() { super.onPause(); nfcAdapter?.disableForegroundDispatch(this) }
}
