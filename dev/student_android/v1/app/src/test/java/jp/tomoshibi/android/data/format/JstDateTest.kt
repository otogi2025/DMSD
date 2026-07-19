package jp.tomoshibi.android.data.format

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.ZoneId
import java.util.TimeZone

// JST 日期格式化测试（C2 Android #18 + B14 G24 扩展）。
// 守：时刻按 Asia/Tokyo 格式化，且不随「设备默认时区」漂移。
class JstDateTest {
    @Test
    fun `已知 epoch 按 JST 格式化`() {
        // 1970-01-01 00:00:00 UTC = 1970-01-01 09:00 JST
        assertEquals("1970-01-01 09:00", JstDate.formatHistory(0L))
        // 1_700_000_000_000ms = 2023-11-14 22:13:20 UTC = 2023-11-15 07:13 JST
        assertEquals("2023-11-15 07:13", JstDate.formatHistory(1_700_000_000_000L))
        assertEquals("07:13", JstDate.formatHm(1_700_000_000_000L))
    }

    @Test
    fun `结果不随设备默认时区漂移`() {
        val saved = TimeZone.getDefault()
        try {
            TimeZone.setDefault(TimeZone.getTimeZone("America/New_York"))
            assertEquals("2023-11-15 07:13", JstDate.formatHistory(1_700_000_000_000L))
            assertEquals(ZoneId.of("Asia/Tokyo"), JstDate.TOKYO)
            // today() 必须跟东京日历走，不能跟纽约
            assertEquals(JstDate.today(), java.time.LocalDate.now(JstDate.TOKYO))
        } finally {
            TimeZone.setDefault(saved)
        }
    }

    @Test
    fun `monthPrefix 为 yyyy-MM`() {
        val prefix = JstDate.monthPrefix()
        assertTrue(prefix.matches(Regex("""\d{4}-\d{2}""")))
    }

    @Test
    fun `formatCleaning 解析 ISO`() {
        val s = JstDate.formatCleaning("2026-04-14T15:30:00+09:00")
        assertEquals("4月14日 15時30分", s)
    }
}
