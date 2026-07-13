package jp.tomoshibi.android.data.format

import org.junit.Assert.assertEquals
import org.junit.Test
import java.util.TimeZone

// JST 日期格式化测试（C2 Android #18，对称 iOS #12）。
// 守：时刻按 Asia/Tokyo 格式化、Date 值精确，且不随「设备默认时区」漂移（时区/格式漂移会让全 App 时刻错位）。
class JstDateTest {
    @Test
    fun `已知 epoch 按 JST 格式化`() {
        // 1970-01-01 00:00:00 UTC = 1970-01-01 09:00 JST
        assertEquals("1970-01-01 09:00", JstDate.formatHistory(0L))
        // 1_700_000_000_000ms = 2023-11-14 22:13:20 UTC = 2023-11-15 07:13 JST
        assertEquals("2023-11-15 07:13", JstDate.formatHistory(1_700_000_000_000L))
    }

    @Test
    fun `结果不随设备默认时区漂移`() {
        val saved = TimeZone.getDefault()
        try {
            // 把设备默认时区改成纽约 —— 锁死 Asia/Tokyo 的话输出应完全不变
            TimeZone.setDefault(TimeZone.getTimeZone("America/New_York"))
            assertEquals("2023-11-15 07:13", JstDate.formatHistory(1_700_000_000_000L))
        } finally {
            TimeZone.setDefault(saved)
        }
    }
}
