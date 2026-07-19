package jp.tomoshibi.android.data.account

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

// RoomCoding 纯函数单测 — 对齐 iOS RoomAssemblyTests + 后端 §5.0
class RoomCodingTest {
    @Test
    fun `纯数字房号按性别加 M_W 前缀`() {
        assertEquals("M101", RoomCoding.assembleRoomNo("101", "male"))
        assertEquals("W205", RoomCoding.assembleRoomNo("205", "female"))
        assertEquals(1, RoomCoding.dormUnit("101", "male"))
        assertEquals(4, RoomCoding.dormUnit("205", "female"))
    }

    @Test
    fun `A 前缀原样保留不被性别覆盖`() {
        // 2 寮男生：保持 A5，绝不拼成 MA5
        assertEquals("A5", RoomCoding.assembleRoomNo("A5", "male"))
        assertEquals("A12", RoomCoding.assembleRoomNo("A12", "male"))
        // 即便 gender=female，A 前缀也不被 W 覆盖（前缀由字母编码）
        assertEquals("A1", RoomCoding.assembleRoomNo("A1", "female"))
    }

    @Test
    fun `A 前缀男生判 2 寮`() {
        assertEquals(2, RoomCoding.dormUnit("A1", "male"))
        assertEquals(2, RoomCoding.dormUnit("A12", "male"))
        assertEquals(2, RoomCoding.dormUnit("a7", "male"))
        assertEquals(1, RoomCoding.dormUnit("301", "male"))
        // 女生一律 4 寮（现行：female 优先）
        assertEquals(4, RoomCoding.dormUnit("A1", "female"))
    }

    @Test
    fun `空后缀返回空串`() {
        assertEquals("", RoomCoding.assembleRoomNo("", "male"))
        assertEquals(1, RoomCoding.dormUnit("", "male"))
        assertEquals(4, RoomCoding.dormUnit("", "female"))
    }

    @Test
    fun `roomGenderMismatch 性别与前缀矛盾`() {
        assertTrue(RoomCoding.roomGenderMismatch("W101", "male"))
        assertTrue(RoomCoding.roomGenderMismatch("M101", "female"))
        assertTrue(RoomCoding.roomGenderMismatch("A5", "female"))
        assertFalse(RoomCoding.roomGenderMismatch("M101", "male"))
        assertFalse(RoomCoding.roomGenderMismatch("A5", "male"))
        assertFalse(RoomCoding.roomGenderMismatch("W205", "female"))
        // 纯数字尚未输前缀 → 不误挡
        assertFalse(RoomCoding.roomGenderMismatch("101", "male"))
    }

    @Test
    fun `dormLabel`() {
        assertEquals("男寮", RoomCoding.dormLabel("male"))
        assertEquals("女寮", RoomCoding.dormLabel("female"))
        assertEquals("男寮", RoomCoding.dormLabelFromUnit(1))
        assertEquals("男寮", RoomCoding.dormLabelFromUnit(2))
        assertEquals("女寮", RoomCoding.dormLabelFromUnit(4))
    }

    @Test
    fun `validateRoomDormMatch 合法组合`() {
        assertTrue(RoomCoding.validateRoomDormMatch("M101", 1, "male"))
        assertTrue(RoomCoding.validateRoomDormMatch("A5", 2, "male"))
        assertTrue(RoomCoding.validateRoomDormMatch("A12", 2, "male"))
        assertTrue(RoomCoding.validateRoomDormMatch("W305", 4, "female"))
    }

    @Test
    fun `validateRoomDormMatch 性别错`() {
        assertFalse(RoomCoding.validateRoomDormMatch("M101", 1, "female"))
        assertFalse(RoomCoding.validateRoomDormMatch("W305", 4, "male"))
    }

    @Test
    fun `validateRoomDormMatch 寮错`() {
        assertFalse(RoomCoding.validateRoomDormMatch("M101", 2, "male"))
        assertFalse(RoomCoding.validateRoomDormMatch("A5", 1, "male"))
        assertFalse(RoomCoding.validateRoomDormMatch("W101", 1, "male"))
    }

    @Test
    fun `validateRoomDormMatch 格式错`() {
        assertFalse(RoomCoding.validateRoomDormMatch("M10", 1, "male"))
        assertFalse(RoomCoding.validateRoomDormMatch("M1010", 1, "male"))
        assertFalse(RoomCoding.validateRoomDormMatch("101", 1, "male"))
        assertFalse(RoomCoding.validateRoomDormMatch("A123", 2, "male"))
        assertFalse(RoomCoding.validateRoomDormMatch("M101", 3, "male"))
    }
}
