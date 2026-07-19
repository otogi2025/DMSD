package jp.tomoshibi.android.data.translate

/**
 * 公告翻译目标语言（对齐 iOS HomeStubs.TranslateLang）。
 * rawValue 写入偏好键 translate_default_lang，与设置页 / 公告详情共用。
 */
enum class TranslateLang(
    val code: String,
    /** 语言选择窗显示名（母语原文 + 日语括注） */
    val pickerLabel: String,
    /** 状态条 / 设置页短名 */
    val shortLabel: String,
) {
    ENGLISH("en", "English（英語）", "English"),
    CHINESE("zh-Hans", "简体中文（中国語）", "简体中文"),
    THAI("th", "ไทย（タイ語）", "ไทย"),
    VIETNAMESE("vi", "Tiếng Việt（ベトナム語）", "Tiếng Việt"),
    ;

    companion object {
        fun fromCode(code: String): TranslateLang? = entries.firstOrNull { it.code == code }
    }
}
