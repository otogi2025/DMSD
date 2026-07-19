package jp.tomoshibi.android.data.format

import java.time.Instant
import java.time.LocalDate
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.Locale

// JstDate — 日期/时刻格式化与「今天」基准，时区锁死 Asia/Tokyo（JST）。
//
// 对齐 iOS §22.1：绝对时刻 / 今天·月份判断 / 时间合成用 JST；
// date-only 民事日期（生日等）由调用方直接用字符串，不加时区转换。
//
// 为什么锁 Asia/Tokyo：原先各屏 LocalDate.now() / SimpleDateFormat 跟随设备时区，
// 非日本时区设备上「今天」「本月统计」「公告相对时间回落」会跟 iOS 差一天。
object JstDate {
    val TOKYO: ZoneId = ZoneId.of("Asia/Tokyo")

    private val historyFormatter: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm", Locale.JAPAN).withZone(TOKYO)

    private val hmFormatter: DateTimeFormatter =
        DateTimeFormatter.ofPattern("HH:mm", Locale.JAPAN).withZone(TOKYO)

    private val ymdHmFormatter: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm", Locale.JAPAN)

    private val cleaningFormatter: DateTimeFormatter =
        DateTimeFormatter.ofPattern("M月d日 H時mm分", Locale.JAPAN).withZone(TOKYO)

    private val monthDayFormatter: DateTimeFormatter =
        DateTimeFormatter.ofPattern("MM/dd", Locale.JAPAN).withZone(TOKYO)

    private val changeLogFormatter: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm", Locale.JAPAN).withZone(TOKYO)

    /** 东京时区「今天」的民事日期 */
    fun today(): LocalDate = LocalDate.now(TOKYO)

    /** 东京时区当前时刻 */
    fun nowTime(): LocalTime = LocalTime.now(TOKYO)

    /** 东京时区当前 ZonedDateTime */
    fun now(): ZonedDateTime = ZonedDateTime.now(TOKYO)

    /** 「yyyy-MM」本月前缀（点呼/扣分月统计口径） */
    fun monthPrefix(date: LocalDate = today()): String = date.format(DateTimeFormatter.ofPattern("yyyy-MM"))

    /** unix 毫秒 → "yyyy-MM-dd HH:mm"（JST）。点呼履歴等。 */
    fun formatHistory(epochMillis: Long): String = historyFormatter.format(Instant.ofEpochMilli(epochMillis))

    /** unix 毫秒 / Instant → "HH:mm"（JST） */
    fun formatHm(epochMillis: Long): String = hmFormatter.format(Instant.ofEpochMilli(epochMillis))

    fun formatHm(instant: Instant): String = hmFormatter.format(instant)

    /** 东京「现在」拼成 "yyyy-MM-dd HH:mm"（班车「次便」比较用） */
    fun nowYmdHm(): String = now().format(ymdHmFormatter)

    /** ISO 时刻 →「M月d日 H時mm分」（罰則清掃履歴） */
    fun formatCleaning(iso: String): String {
        val instant = parseInstant(iso) ?: return iso.take(16).replace('T', ' ')
        return cleaningFormatter.format(instant)
    }

    /** ISO 时刻 →「yyyy/MM/dd HH:mm」（変更履歴等） */
    fun formatChangeLog(iso: String): String {
        val instant = parseInstant(iso) ?: return iso
        return changeLogFormatter.format(instant)
    }

    /** unix 毫秒 →「yyyy/MM/dd HH:mm」（変更履歴本地条目） */
    fun formatChangeLogEpoch(epochMillis: Long): String = changeLogFormatter.format(Instant.ofEpochMilli(epochMillis))

    /** ISO →「MM-dd」（遺失物日期等） */
    fun formatMmDd(iso: String): String {
        val instant = parseInstant(iso) ?: return iso.take(10).drop(5)
        return DateTimeFormatter.ofPattern("MM-dd", Locale.JAPAN).withZone(TOKYO).format(instant)
    }

    /**
     * 公告列表相对时间（对齐 iOS）：
     * <60s たった今 / <1h N分前 / <24h N時間前 / 更早 MM/dd（JST）。
     */
    fun relativeOrMonthDay(iso: String): String {
        val instant =
            parseInstant(iso) ?: return runCatching {
                "${iso.substring(5, 10)} ${iso.substring(11, 16)}"
            }.getOrDefault(iso)
        val diffSec =
            java.time.Duration
                .between(instant, Instant.now())
                .seconds
        return when {
            diffSec < 60 -> "たった今"
            diffSec < 3600 -> "${diffSec / 60}分前"
            diffSec < 86400 -> "${diffSec / 3600}時間前"
            else -> monthDayFormatter.format(instant)
        }
    }

    /** ISO → Instant（OffsetDateTime / Instant 两种） */
    fun parseInstant(iso: String): Instant? =
        try {
            OffsetDateTime.parse(iso).toInstant()
        } catch (_: Exception) {
            try {
                Instant.parse(iso)
            } catch (_: Exception) {
                null
            }
        }
}
