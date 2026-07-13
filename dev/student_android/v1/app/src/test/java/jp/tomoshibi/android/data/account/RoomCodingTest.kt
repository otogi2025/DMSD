package jp.tomoshibi.android.data.account

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

// 房号编码 / 寮名 / 房号-寮-性别校验测试（C2 Android #15 房号前缀→寮 + #20 注册房号校验）。
class RoomCodingTest {
    // ── #15 性别 → 前缀 / 完整房号 / 寮名（对称 iOS #6）──

    @Test
    fun `男生前缀 M 女生前缀 W`() {
        assertEquals("M", RoomCoding.roomPrefix("male"))
        assertEquals("W", RoomCoding.roomPrefix("female"))
    }

    @Test
    fun `完整房号 = 前缀 + 数字`() {
        assertEquals("M101", RoomCoding.fullRoom("male", "101"))
        assertEquals("W205", RoomCoding.fullRoom("female", "205"))
    }

    @Test
    fun `寮名男寮女寮`() {
        assertEquals("男寮", RoomCoding.dormLabel("male"))
        assertEquals("女寮", RoomCoding.dormLabel("female"))
    }

    // ⚠️ 注：iOS 对首位是字母的房号(A5)会原样保留("A5")；Android 现行 fullRoom 会拼成 "MA5"。
    //   这条差异是已知的 2 寮场景双端不一致（见 RoomCoding 文件内注记），本次锁定 Android 现行行为、不改注册逻辑。
    @Test
    fun `锁定现行行为_A 前缀房号男生仍被加 M 前缀`() {
        assertEquals("MA5", RoomCoding.fullRoom("male", "A5"))
    }

    // ── #20 房号 ↔ 寮 ↔ 性别 一致性校验（与后端 validate_room_dorm_match 同口径：M/A/W 三前缀 + 非法）──

    @Test
    fun `合法组合 1寮M男 2寮A男 4寮W女`() {
        assertTrue(RoomCoding.validateRoomDormMatch("M101", 1, "male")) // 1 寮 = M*** male
        assertTrue(RoomCoding.validateRoomDormMatch("A5", 2, "male")) // 2 寮 = A[0-9]{1,2} male
        assertTrue(RoomCoding.validateRoomDormMatch("A12", 2, "male")) // A + 2 桁也合法
        assertTrue(RoomCoding.validateRoomDormMatch("W305", 4, "female")) // 4 寮 = W*** female
    }

    @Test
    fun `性别与寮不匹配 非法`() {
        assertFalse(RoomCoding.validateRoomDormMatch("M101", 1, "female")) // 1 寮期望 male
        assertFalse(RoomCoding.validateRoomDormMatch("W305", 4, "male")) // 4 寮期望 female
    }

    @Test
    fun `前缀与寮不匹配 非法`() {
        assertFalse(RoomCoding.validateRoomDormMatch("M101", 2, "male")) // 2 寮要 A 前缀，M 非法
        assertFalse(RoomCoding.validateRoomDormMatch("A5", 1, "male")) // 1 寮要 M 前缀，A 非法
        assertFalse(RoomCoding.validateRoomDormMatch("W101", 1, "male")) // 1 寮要 M，W 非法
    }

    @Test
    fun `位数不对或纯数字或未知寮 非法`() {
        assertFalse(RoomCoding.validateRoomDormMatch("M10", 1, "male")) // M 后必须 3 桁
        assertFalse(RoomCoding.validateRoomDormMatch("M1010", 1, "male")) // 超过 3 桁
        assertFalse(RoomCoding.validateRoomDormMatch("101", 1, "male")) // 无前缀
        assertFalse(RoomCoding.validateRoomDormMatch("A123", 2, "male")) // A 后最多 2 桁
        assertFalse(RoomCoding.validateRoomDormMatch("M101", 3, "male")) // 无 3 寮
    }
}
