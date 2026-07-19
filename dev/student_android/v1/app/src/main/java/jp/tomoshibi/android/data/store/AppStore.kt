package jp.tomoshibi.android.data.store

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import jp.tomoshibi.android.data.model.AppState
import jp.tomoshibi.android.data.seed.MockData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

// AppStore — 对应 React StoreProvider
// 把整个 AppState JSON 序列化存进 DataStore Preferences 一个 key
// （比拆 30+ keys 简单，性能也够 — v1.0 数据量 < 100KB）
//
// 令牌例外：authToken 单独走 SecureTokenStore（EncryptedSharedPreferences），
// DataStore JSON 不再落明文 JWT。对齐 iOS KeychainService。

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "tomoshibi-app-state-v1",
)

private val APP_STATE_KEY = stringPreferencesKey("app_state_json")

// 共享 JSON 编解码器。ignoreUnknownKeys = 解码时忽略 JSON 里有、但 AppState 已删掉的字段，
// 这样删字段（如本次删匿名建議的 feedback 字段）后，老用户本地存档不会解析失败回落、丢掉其余本地数据。
// internal（非 private）：TokenRoundtripTest 直接用这份真配置做往返测试——配置将来变了测试跟着变，不测副本。
internal val appJson = Json { ignoreUnknownKeys = true }

class AppStore(
    private val context: Context,
) {
    private val tokenStore = SecureTokenStore(context)

    // 启动时异步：旧版 DataStore JSON 里若还有明文 authToken → 写入加密存储 → 删明文
    private val migrateScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    init {
        migrateScope.launch {
            migratePlainTokenIfNeeded()
        }
    }

    val state: Flow<AppState> =
        context.dataStore.data.map { prefs ->
            val decoded = decodePrefs(prefs)
            // 读路径也做一次同步迁移（EncryptedSharedPreferences 是同步 API），
            // 保证 Splash 自动登录在异步 migrate 完成前也能拿到 token。
            val plain = decoded.authToken
            if (!plain.isNullOrEmpty() && tokenStore.get() == null) {
                tokenStore.save(plain)
            }
            decoded.copy(authToken = tokenStore.get())
        }

    suspend fun update(transform: (AppState) -> AppState) {
        context.dataStore.edit { prefs ->
            val current = decodePrefs(prefs).copy(authToken = tokenStore.get())
            val next = transform(current)
            // token 单独加密存；DataStore JSON 永不落明文
            if (next.authToken.isNullOrEmpty()) {
                tokenStore.clear()
            } else {
                tokenStore.save(next.authToken)
            }
            prefs[APP_STATE_KEY] = appJson.encodeToString(next.copy(authToken = null))
        }
    }

    suspend fun reset() {
        tokenStore.clear()
        context.dataStore.edit { it.remove(APP_STATE_KEY) }
    }

    suspend fun snapshot(): AppState {
        migratePlainTokenIfNeeded()
        return state.first()
    }

    // 读旧明文 → 写加密 → 删旧明文（幂等）
    private suspend fun migratePlainTokenIfNeeded() {
        context.dataStore.edit { prefs ->
            val current = decodePrefs(prefs)
            val plain = current.authToken
            if (!plain.isNullOrEmpty()) {
                if (tokenStore.get() == null) {
                    tokenStore.save(plain)
                }
                prefs[APP_STATE_KEY] = appJson.encodeToString(current.copy(authToken = null))
            }
        }
    }

    private fun decodePrefs(prefs: Preferences): AppState {
        val json = prefs[APP_STATE_KEY] ?: return MockData.INITIAL_STATE
        return try {
            appJson.decodeFromString<AppState>(json)
        } catch (e: Exception) {
            android.util.Log.e("AppStore", "AppState 解析失败，回落 MockData（本地数据可能丢失）", e)
            MockData.INITIAL_STATE
        }
    }

    // A-030 / A-034 (2026-05-21): cycleDemoRollState() 已删
    // memory project_demo_scaffolds_to_remove_before_v1.md #1, #15
    // 接 backend event 驱动后 rollState 由 server 推送，不再 demo 循环
}

// CompositionLocal 让任何 Composable 通过 LocalAppStore.current 拿到 AppStore 实例
// 在 Activity setContent 顶层 provide
val LocalAppStore =
    staticCompositionLocalOf<AppStore> {
        error("AppStore not provided — wrap your composable in CompositionLocalProvider(LocalAppStore provides ...)")
    }

object AppStoreAccess {
    val current: AppStore
        @Composable get() = LocalAppStore.current
}
