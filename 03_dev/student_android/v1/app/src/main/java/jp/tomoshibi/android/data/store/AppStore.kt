package jp.tomoshibi.android.data.store

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import jp.tomoshibi.android.data.model.AppState
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.data.seed.MockData
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.time.LocalTime
import java.time.format.DateTimeFormatter

// AppStore — 对应 React StoreProvider
// 把整个 AppState JSON 序列化存进 DataStore Preferences 一个 key
// （比拆 30+ keys 简单，性能也够 — v1.0 数据量 < 100KB）

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "tomoshibi-app-state-v1",
)

private val APP_STATE_KEY = stringPreferencesKey("app_state_json")

class AppStore(
    private val context: Context,
) {
    val state: Flow<AppState> =
        context.dataStore.data.map { prefs ->
            val json = prefs[APP_STATE_KEY]
            if (json == null) {
                MockData.INITIAL_STATE
            } else {
                try {
                    Json.decodeFromString<AppState>(json)
                } catch (e: Exception) {
                    // schema 漂移时 fallback 默认 — v1.0 不做 migration
                    // 记日志：异常被吞会导致老用户升级后本地数据无声丢失，至少留排查线索
                    android.util.Log.e("AppStore", "AppState 解析失败，回落 MockData（本地数据可能丢失）", e)
                    MockData.INITIAL_STATE
                }
            }
        }

    suspend fun update(transform: (AppState) -> AppState) {
        context.dataStore.edit { prefs ->
            val current =
                prefs[APP_STATE_KEY]?.let {
                    try {
                        Json.decodeFromString<AppState>(it)
                    } catch (e: Exception) {
                        android.util.Log.e("AppStore", "update 时 AppState 解析失败，回落 MockData", e)
                        MockData.INITIAL_STATE
                    }
                } ?: MockData.INITIAL_STATE
            prefs[APP_STATE_KEY] = Json.encodeToString(transform(current))
        }
    }

    suspend fun reset() {
        context.dataStore.edit { it.remove(APP_STATE_KEY) }
    }

    suspend fun snapshot(): AppState = state.first()

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
