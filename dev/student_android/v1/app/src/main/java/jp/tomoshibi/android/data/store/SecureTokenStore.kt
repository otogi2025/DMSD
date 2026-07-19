package jp.tomoshibi.android.data.store

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

// SecureTokenStore.kt
// data/store — JWT 登录令牌的加密持久化（对齐 iOS KeychainService）
//
// 用 androidx.security.crypto 的 EncryptedSharedPreferences（AES256-GCM），
// 替代原先嵌在 AppState JSON 里、经 DataStore 明文落盘的 authToken。
//
// 迁移：AppStore 读到旧明文 token 时 → save 进本类 → 从 DataStore JSON 删掉明文。

class SecureTokenStore(
    context: Context,
) {
    private val prefs: SharedPreferences

    init {
        val masterKey =
            MasterKey
                .Builder(context.applicationContext)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
        prefs =
            EncryptedSharedPreferences.create(
                context.applicationContext,
                PREFS_NAME,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
            )
    }

    fun get(): String? = prefs.getString(KEY_TOKEN, null)?.takeIf { it.isNotEmpty() }

    fun save(token: String) {
        prefs.edit().putString(KEY_TOKEN, token).apply()
    }

    fun clear() {
        prefs.edit().remove(KEY_TOKEN).apply()
    }

    companion object {
        private const val PREFS_NAME = "tomoshibi_secure_token"
        private const val KEY_TOKEN = "auth_token"
    }
}
