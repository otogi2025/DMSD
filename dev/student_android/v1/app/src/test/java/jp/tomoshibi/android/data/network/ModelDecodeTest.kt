package jp.tomoshibi.android.data.network

import jp.tomoshibi.android.data.network.endpoints.CleaningAssignmentOut
import jp.tomoshibi.android.data.network.endpoints.LostFoundOut
import jp.tomoshibi.android.data.network.endpoints.MiscRequestOut
import jp.tomoshibi.android.data.network.endpoints.MyRollCallTodaySession
import jp.tomoshibi.android.data.network.endpoints.OutingOut
import jp.tomoshibi.android.data.network.endpoints.ProfileDemeritEntry
import jp.tomoshibi.android.data.network.endpoints.ProfileRollCallEntry
import jp.tomoshibi.android.data.network.endpoints.RollCallReportOut
import jp.tomoshibi.android.data.network.endpoints.SongRequestOut
import jp.tomoshibi.android.data.network.endpoints.StudentProfileOut
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
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
        // G17：后端恒发非 null Bool；缺字段时默认 false（对齐 iOS 非 Optional）
        assertFalse(out.receiptSubmitted)
        assertFalse(out.isLongVacation)
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

    @Test
    fun `CleaningAssignmentOut 解码`() {
        val body =
            """
            {
              "id": "c1",
              "student_id": "s1",
              "area": "廊下 2F",
              "scheduled_at": "2026-05-20T19:00:00+09:00",
              "status": "assigned",
              "failure_reason": null
            }
            """.trimIndent()
        val out = json.decodeFromString<CleaningAssignmentOut>(body)
        assertEquals("廊下 2F", out.area)
        assertEquals("assigned", out.status)
        assertNull(out.failureReason)
    }

    @Test
    fun `LostFoundOut 解码`() {
        val body =
            """
            {
              "id": "lf1",
              "student_id": "s1",
              "post_type": "found",
              "item_name": "傘",
              "description": null,
              "location": "玄関",
              "status": "open",
              "created_at": "2026-05-01T10:00:00+09:00",
              "resolved_at": null
            }
            """.trimIndent()
        val out = json.decodeFromString<LostFoundOut>(body)
        assertEquals("found", out.postType)
        assertEquals("傘", out.itemName)
        assertEquals("open", out.status)
    }

    @Test
    fun `MiscRequestOut 解码`() {
        val body =
            """
            {
              "id": "mr1",
              "student_id": "s1",
              "kind": "repair",
              "subject": "蛇口漏れ",
              "detail": null,
              "target_date": "2026-05-10",
              "status": "pending",
              "created_at": "2026-05-01T10:00:00+09:00"
            }
            """.trimIndent()
        val out = json.decodeFromString<MiscRequestOut>(body)
        assertEquals("repair", out.kind)
        assertEquals("蛇口漏れ", out.subject)
    }

    @Test
    fun `OutingOut 解码`() {
        val body =
            """
            {
              "id": "o1",
              "student_id": "s1",
              "outing_date": "2026-06-05",
              "destination": "駅",
              "leave_time": "14:00",
              "return_time": "18:00",
              "taxi_reservation_time": null,
              "reason": null,
              "status": "pending",
              "submitted_at": "2026-06-05T10:00:00+09:00",
              "withdrawn_at": null,
              "confirmed_by_teacher_id": null,
              "confirmed_by_name": null,
              "confirmed_at": null
            }
            """.trimIndent()
        val out = json.decodeFromString<OutingOut>(body)
        assertEquals("2026-06-05", out.outingDate)
        assertEquals("pending", out.status)
        assertNull(out.student)
    }

    @Test
    fun `SongRequestOut 解码`() {
        val body =
            """
            {
              "id": "sg1",
              "student_id": "s1",
              "dorm_unit": 1,
              "song_title": "Lemon",
              "artist": "米津玄師",
              "note": null,
              "created_at": "2026-05-01T10:00:00+09:00"
            }
            """.trimIndent()
        val out = json.decodeFromString<SongRequestOut>(body)
        assertEquals("Lemon", out.songTitle)
        assertEquals(1, out.dormUnit)
    }

    @Test
    fun `StudentNotificationFeedOut 解码`() {
        val body =
            """
            {
              "items": [
                {
                  "kind": "announcement",
                  "ref_id": "a1",
                  "title": "お知らせ",
                  "body": "摘要",
                  "created_at": "2026-05-01T10:00:00+09:00",
                  "is_read": false
                }
              ],
              "unread_count": 1
            }
            """.trimIndent()
        val out = json.decodeFromString<StudentNotificationFeedOut>(body)
        assertEquals(1, out.unreadCount)
        assertEquals("announcement", out.items[0].kind)
        assertFalse(out.items[0].isRead)
    }

    @Test
    fun `StudentProfileOut 解码`() {
        val body =
            """
            {
              "rollcall_events": [
                {
                  "id": "e1",
                  "session_id": "ss1",
                  "session_type": "evening",
                  "base_status": "present",
                  "status_source": "auto_nfc",
                  "checked_in_at": "2026-05-01T22:05:00+09:00",
                  "scheduled_window_start_at": null,
                  "scheduled_on_time_end_at": null
                }
              ],
              "demerit_events": [
                {
                  "id": "d1",
                  "source_type": "late",
                  "points": 1.0,
                  "reason": "点呼遅刻",
                  "month": "2026-05",
                  "created_at": "2026-05-01T22:30:00+09:00"
                }
              ]
            }
            """.trimIndent()
        val out = json.decodeFromString<StudentProfileOut>(body)
        assertEquals(1, out.rollcallEvents.size)
        assertEquals("present", out.rollcallEvents[0].baseStatus)
        assertEquals(1.0, out.demeritEvents[0].points, 0.0)
        // 单条类型也能独立解
        json.decodeFromString<ProfileRollCallEntry>(
            """{"id":"e1","session_id":"ss1","session_type":"evening","base_status":"present","status_source":"auto_nfc","checked_in_at":"2026-05-01T22:05:00+09:00"}""",
        )
        json.decodeFromString<ProfileDemeritEntry>(
            """{"id":"d1","source_type":"late","points":1.0,"reason":"点呼遅刻","month":"2026-05","created_at":"2026-05-01T22:30:00+09:00"}""",
        )
    }

    @Test
    fun `MyRollCallTodaySession 解码`() {
        val body =
            """
            {
              "session_id": "ss1",
              "session_type": "evening",
              "day_type": "weekday",
              "session_status": "running",
              "scheduled_window_start_at": "2026-05-01T22:00:00+09:00",
              "scheduled_on_time_end_at": "2026-05-01T22:15:00+09:00",
              "scheduled_late_end_at": "2026-05-01T22:30:00+09:00",
              "scheduled_auto_end_at": "2026-05-01T23:00:00+09:00",
              "my_status": null,
              "my_checked_in_at": null
            }
            """.trimIndent()
        val out = json.decodeFromString<MyRollCallTodaySession>(body)
        assertEquals("evening", out.sessionType)
        assertNull(out.myStatus)
    }

    @Test
    fun `RollCallReportOut 解码`() {
        val body =
            """
            {
              "id": "r1",
              "student_id": "s1",
              "session_id": null,
              "kind": "health",
              "body": "発熱あり",
              "created_at": "2026-05-01T22:00:00+09:00",
              "resolved_at": null,
              "resolved_by_teacher_id": null
            }
            """.trimIndent()
        val out = json.decodeFromString<RollCallReportOut>(body)
        assertEquals("health", out.kind)
        assertEquals("発熱あり", out.body)
    }

    @Test
    fun `StudentAccountCreateBody validate 通过与拒绝`() {
        val ok =
            StudentAccountCreateBody(
                name = "山田太郎",
                gender = "male",
                gradeCode = "06",
                classCode = "02",
                seatNo = "18",
                category = "一般寮生",
                roomNo = "A1",
                dormUnit = 2,
                isOverseas = false,
                password = "secret1",
                registrationCode = "123456",
            )
        assertNull(ok.validate())

        val emptyName = ok.copy(name = "")
        assertEquals("氏名を入力してください", emptyName.validate())

        val shortRoom = ok.copy(roomNo = "A")
        assertEquals("部屋番号を正しく入力してください", shortRoom.validate())

        val badCode = ok.copy(registrationCode = "12ab56")
        assertEquals("登録コードは6桁の数字で入力してください", badCode.validate())
    }

    @Test
    fun `ApiErrorPresenter 统一文案`() {
        assertEquals(
            "ログインが必要です。再度ログインしてください。",
            ApiErrorPresenter.userMessage(ApiError.Unauthorized, "fallback"),
        )
        assertEquals(
            "サーバーエラー（コード 500）。時間をおいて再度お試しください。",
            ApiErrorPresenter.userMessage(ApiError.Server(500, "x"), "fallback"),
        )
        assertEquals(
            "入力が不正です",
            ApiErrorPresenter.userMessage(ApiError.Unprocessable("入力が不正です"), "fallback"),
        )
        assertEquals(
            "場面用文案",
            ApiErrorPresenter.userMessage(RuntimeException("boom"), "場面用文案"),
        )
    }
}
