package jp.tomoshibi.android.data.format

import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

// JstDate — 日期/时刻格式化纯逻辑，时区锁死 JST（対齐 iOS 全 App 用 JST 显示点呼时刻）。
//
// 为什么锁 Asia/Tokyo：点呼履歴原本用 SimpleDateFormat 直接格式化、跟随「设备时区」——
// 学生把手机时区设成非日本（或系统误判）时，同一条点呼记录 iOS 显 JST、Android 显别的时刻 = 双端漂移。
// 真实用户全在日本、设备时区本就是 JST，锁死后对真实用户显示不变，只堵住时区异常这条缝。
object JstDate {
    private val TOKYO: ZoneId = ZoneId.of("Asia/Tokyo")

    // 点呼履歴单条时刻格式："yyyy-MM-dd HH:mm"（JST）。等价原 RollCallScreen 的 SimpleDateFormat，只是时区锁死。
    private val historyFormatter: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm", Locale.JAPAN).withZone(TOKYO)

    // / unix 毫秒 → "yyyy-MM-dd HH:mm"（JST）。
    fun formatHistory(epochMillis: Long): String = historyFormatter.format(Instant.ofEpochMilli(epochMillis))
}
