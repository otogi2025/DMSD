package jp.tomoshibi.android.ui.screens.applications

import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.model.StayStatus
import org.junit.Assert.assertEquals
import org.junit.Test

// 申请状态 → 显示 chip 映射测试（C2 Android #16）。
// 守两条契约：① 后端 status 英语字符串 → UI 枚举（后端加/改状态时这里先炸）；② 枚举 → 徽章日语文案。
class ApplicationStatusMapTest {
    // ── 后端 status 字符串 → ApplicationStatus（4 值，7→4 压缩）──

    @Test
    fun `mapApplicationStatus4 全值正映射`() {
        assertEquals(ApplicationStatus.PENDING, mapApplicationStatus4("pending"))
        assertEquals(ApplicationStatus.APPROVED, mapApplicationStatus4("approved"))
        assertEquals(ApplicationStatus.APPROVED, mapApplicationStatus4("approved_partial")) // 一部承認也归 APPROVED
        assertEquals(ApplicationStatus.RETURNED, mapApplicationStatus4("returned"))
        assertEquals(ApplicationStatus.REJECTED, mapApplicationStatus4("rejected"))
        assertEquals(ApplicationStatus.REJECTED, mapApplicationStatus4("withdrawn")) // 兜底归 REJECTED
    }

    @Test
    fun `mapApplicationStatus4 未知字符串走兜底不崩`() {
        // 后端先行加新状态时旧版 App 不该崩，走 else → REJECTED
        assertEquals(ApplicationStatus.REJECTED, mapApplicationStatus4("some_new_backend_status"))
    }

    // ── 后端 status 字符串 → StayStatus（7 值，申請履歴用）──

    @Test
    fun `mapStayStatus 全值正映射`() {
        assertEquals(StayStatus.PENDING, mapStayStatus("pending"))
        assertEquals(StayStatus.APPROVED_PARTIAL, mapStayStatus("approved_partial"))
        assertEquals(StayStatus.APPROVED, mapStayStatus("approved"))
        assertEquals(StayStatus.REJECTED, mapStayStatus("rejected"))
        assertEquals(StayStatus.RETURNED, mapStayStatus("returned"))
        assertEquals(StayStatus.WITHDRAWN, mapStayStatus("withdrawn"))
        assertEquals(StayStatus.PENDING, mapStayStatus("unknown")) // 兜底 PENDING
    }

    // ── ApplicationStatus 枚举 → 徽章 chip 文案 ──

    @Test
    fun `applicationStatusLabel 各态文案`() {
        assertEquals("審査中", applicationStatusLabel(ApplicationStatus.PENDING))
        assertEquals("承認済", applicationStatusLabel(ApplicationStatus.APPROVED))
        assertEquals("要修正", applicationStatusLabel(ApplicationStatus.RETURNED))
        assertEquals("差戻", applicationStatusLabel(ApplicationStatus.REJECTED)) // iOS 对齐：差戻 不是 却下
    }
}
