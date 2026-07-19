package jp.tomoshibi.android.data.store

import jp.tomoshibi.android.data.network.endpoints.StudentMeOut
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

// SessionMapper 纯函数单测（B02：loadMe 映射 + 423 锁定文案解析）
class SessionMapperTest {
    @Test
    fun `mapMeToUser 年级班级性别寮映射正确`() {
        val me =
            StudentMeOut(
                id = "uuid-1",
                studentNo = "060218",
                name = "山田 太郎",
                nameKana = "やまだ たろう",
                gradeCode = "06",
                classCode = "02",
                seatNo = "18",
                gender = "male",
                category = "一般寮生",
                roomNo = "M101",
                dormUnit = 1,
                isOverseas = false,
                email = "a@example.com",
                phone = "090-1111-2222",
                status = "active",
                needsRenewal = true,
            )
        val u = SessionMapper.mapMeToUser(me)
        assertEquals("山田 太郎", u.name)
        assertEquals("やまだ たろう", u.kana)
        assertEquals("060218", u.studentNo)
        assertEquals("高3 B組 18番", u.gradeClass)
        assertEquals("男", u.gender)
        assertEquals("男寮", u.dorm)
        assertEquals("M101", u.room)
        assertEquals("山", u.avatar)
        assertEquals("a@example.com", u.email)
        assertEquals(0.0, u.points, 0.0)
    }

    @Test
    fun `mapMeToUser 女寮 female`() {
        val me =
            StudentMeOut(
                id = "uuid-2",
                studentNo = "050101",
                name = "佐藤",
                gradeCode = "05",
                classCode = "01",
                seatNo = "01",
                gender = "female",
                category = "一般寮生",
                roomNo = "W201",
                dormUnit = 4,
                isOverseas = false,
                status = "active",
            )
        val u = SessionMapper.mapMeToUser(me)
        assertEquals("女", u.gender)
        assertEquals("女寮", u.dorm)
        assertEquals("高2 A組 1番", u.gradeClass)
    }

    @Test
    fun `parseLockoutRemainingSec 解析后端 423 文案`() {
        val sec = SessionMapper.parseLockoutRemainingSec("アカウントロック中（残り約 15 分）")
        assertEquals(900, sec)
    }

    @Test
    fun `parseLockoutRemainingSec 无匹配返回 null`() {
        assertNull(SessionMapper.parseLockoutRemainingSec("入力エラー"))
    }

    @Test
    fun `parseInstantMillis ISO8601`() {
        val ms = SessionMapper.parseInstantMillis("2026-07-19T12:00:00Z")
        assertTrue(ms != null && ms > 0)
    }

    @Test
    fun `gradeLabel classLabel 边界`() {
        assertEquals("中1", SessionMapper.gradeLabel("01"))
        assertEquals("高3", SessionMapper.gradeLabel("06"))
        assertEquals("99", SessionMapper.gradeLabel("99"))
        assertEquals("A", SessionMapper.classLabel("01"))
        assertEquals("Z", SessionMapper.classLabel("26"))
        assertEquals("00", SessionMapper.classLabel("00"))
    }

    @Test
    fun `needsRenewal 可空字段不影响映射`() {
        val me =
            StudentMeOut(
                id = "u",
                studentNo = "010101",
                name = "A",
                gradeCode = "01",
                classCode = "01",
                seatNo = "1",
                gender = "male",
                category = "一般寮生",
                roomNo = "M101",
                dormUnit = 1,
                isOverseas = false,
                status = "active",
                needsRenewal = null,
            )
        // mapMeToUser 本身不写 needsRenewal（在 AppState）；只确认不崩
        val u = SessionMapper.mapMeToUser(me)
        assertFalse(u.needsCleaning)
        assertEquals("中1 A組 1番", u.gradeClass)
    }
}
