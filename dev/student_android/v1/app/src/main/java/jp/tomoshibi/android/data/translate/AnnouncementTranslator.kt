package jp.tomoshibi.android.data.translate

import com.google.mlkit.common.model.DownloadConditions
import com.google.mlkit.nl.translate.TranslateLanguage
import com.google.mlkit.nl.translate.Translation
import com.google.mlkit.nl.translate.Translator
import com.google.mlkit.nl.translate.TranslatorOptions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext

/**
 * 公告正文设备端翻译（Google ML Kit on-device）。
 * 对齐 iOS AnnouncementTranslateRunner：源语言日语、目标语言按用户选择；
 * 模型按需下载，下载失败按翻译失败处理。
 * Translator 按目标语言进程级缓存，避免连点同语言重复建客户端 / 查模型。
 */
object AnnouncementTranslator {
    private val lock = Any()
    private val cache = mutableMapOf<TranslateLang, Translator>()

    /**
     * @return 译文；失败抛异常（调用方映到「翻訳に失敗しました」）
     */
    suspend fun translate(
        text: String,
        target: TranslateLang,
    ): String =
        withContext(Dispatchers.IO) {
            synchronized(lock) { cache[target] }?.let { cached ->
                return@withContext cached.translate(text).await()
            }

            val mlTarget = toMlKitLanguage(target)
            val options =
                TranslatorOptions
                    .Builder()
                    .setSourceLanguage(TranslateLanguage.JAPANESE)
                    .setTargetLanguage(mlTarget)
                    .build()
            val translator = Translation.getClient(options)
            try {
                // 不强制 Wi-Fi：宿舍 Wi-Fi 不稳定时蜂窝也可下；失败由调用方重试
                val conditions = DownloadConditions.Builder().build()
                translator.downloadModelIfNeeded(conditions).await()
                val result = translator.translate(text).await()
                // 下载成功才缓存；并发已有实例则关掉本实例复用已有
                synchronized(lock) {
                    val existing = cache[target]
                    if (existing != null) {
                        translator.close()
                    } else {
                        cache[target] = translator
                    }
                }
                result
            } catch (e: Exception) {
                // 下载 / 翻译失败不缓存
                translator.close()
                throw e
            }
        }

    /** 进程退出或不需要翻译时关闭并清空缓存。 */
    fun close() {
        synchronized(lock) {
            cache.values.forEach { it.close() }
            cache.clear()
        }
    }

    private fun toMlKitLanguage(lang: TranslateLang): String =
        when (lang) {
            TranslateLang.ENGLISH -> TranslateLanguage.ENGLISH
            TranslateLang.CHINESE -> TranslateLanguage.CHINESE
            TranslateLang.THAI -> TranslateLanguage.THAI
            TranslateLang.VIETNAMESE -> TranslateLanguage.VIETNAMESE
        }
}
