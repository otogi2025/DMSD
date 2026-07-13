package jp.tomoshibi.android.data.network

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

// 关键网络模型 JSON 解码测试（C2 Android #17，对称 iOS #11）。
// 守：后端只返「帰省」必填字段、其余可选字段缺省 / 显式 null 时，ApiClient.json 能解出且可选字段落 null，
//     不因缺字段整段解码失败（字段可空性漂移的运行时保护）。用真实 ApiClient.json 配置解码。
class ModelDecodeTest {
    private val json = ApiClient.json

    @Test
    fun `ApplicationOut 帰省 缺全部可选字段仍解码成功且可选字段为 null`() {
        val body =
            """
            {
              "id": "app-1",
              "student_id": "stu-1",
              "kind": "帰省",
              "leave_date": "2026-05-03",
              "leave_method": "電車",
              "leave_time": "19:40:00",
              "return_date": "2026-05-05",
              "return_method": "電車",
              "return_time": "18:00:00",
              "submitted_at": "2026-05-01T10:00:00+09:00",
              "status": "pending",
              "approval_chain": []
            }
            """.trimIndent()

        val out = json.decodeFromString<ApplicationOut>(body)

        assertEquals("app-1", out.id)
        assertEquals("帰省", out.kind)
        assertEquals("2026-05-03", out.leaveDate)
        // 可选字段全落 null / 空
        assertNull(out.student)
        assertNull(out.reason)
        assertNull(out.destCities)
        assertNull(out.stayLocations)
        assertNull(out.mealsSkip)
        assertNull(out.flightDepAir)
        assertNull(out.taxiReservationTime)
        assertNull(out.busRouteId)
        assertNull(out.withdrawnAt)
        assertTrue(out.approvalChain.isEmpty())
    }

    @Test
    fun `ApplicationOut 显式 null 值也能解码`() {
        val body =
            """
            {
              "id": "app-2",
              "student_id": "stu-2",
              "kind": "帰省",
              "reason": null,
              "dest_cities": null,
              "taxi_reservation_time": null,
              "leave_date": "2026-05-03",
              "leave_method": "電車",
              "leave_time": "19:40:00",
              "return_date": "2026-05-05",
              "return_method": "電車",
              "return_time": "18:00:00",
              "submitted_at": "2026-05-01T10:00:00+09:00",
              "status": "pending",
              "approval_chain": [{ "approver_role": "担任" }]
            }
            """.trimIndent()

        val out = json.decodeFromString<ApplicationOut>(body)

        assertNull(out.reason)
        assertNull(out.destCities)
        // 承認链单步只给 approver_role，decision 等可选字段落 null
        assertEquals(1, out.approvalChain.size)
        assertEquals("担任", out.approvalChain[0].approverRole)
        assertNull(out.approvalChain[0].decision)
        assertNull(out.approvalChain[0].decidedAt)
    }

    @Test
    fun `未知多余字段被忽略不报错`() {
        // 后端多返字段（如新加的实验字段）时 ignoreUnknownKeys 让老 App 不崩
        val body =
            """
            {
              "id": "stu-x",
              "student_no": "060218",
              "name": "リュウイヒ",
              "dorm_unit": 1,
              "is_overseas": false,
              "room_no": "M101",
              "brand_new_field_from_backend": "ignore me"
            }
            """.trimIndent()

        val brief = json.decodeFromString<StudentBrief>(body)
        assertEquals("060218", brief.studentNo)
        assertEquals(1, brief.dormUnit)
        assertEquals("M101", brief.roomNo)
    }
}
