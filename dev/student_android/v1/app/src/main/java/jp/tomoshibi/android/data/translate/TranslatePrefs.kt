package jp.tomoshibi.android.data.translate

import android.content.Context

/**
 * 公告翻译默认语言偏好。
 * 键名与 iOS @AppStorage("translate_default_lang") 对齐；空串 = 每次弹语言选择窗。
 */
object TranslatePrefs {
    private const val PREFS = "tomoshibi_translate_prefs"
    private const val KEY_DEFAULT_LANG = "translate_default_lang"

    fun getDefaultLang(context: Context): String =
        context
            .getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(KEY_DEFAULT_LANG, "")
            .orEmpty()

    fun setDefaultLang(
        context: Context,
        code: String,
    ) {
        context
            .getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_DEFAULT_LANG, code)
            .apply()
    }
}
