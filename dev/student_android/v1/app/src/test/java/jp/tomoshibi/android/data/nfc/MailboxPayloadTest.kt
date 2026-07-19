package jp.tomoshibi.android.data.nfc

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Test
import java.util.UUID

// MailboxPayloadTest — ST25DV Mailbox 载荷组装纯函数单测
//
// 被测：ST25DV.buildPayload —— 手机写进点呼机 Mailbox 的 34 字节载荷。
// 契约真值：specs/rollcall/Device_Contract.md §7（双端逐字节对齐）。
// 5 条用例对照 iOS MailboxPayloadTests.swift 逐条搬。

class MailboxPayloadTest {
    // MARK: - 长度 + 头两字节（版本 / 类型）

    @Test
    fun lengthAndHeader() {
        val sid = UUID.randomUUID()
        val key = UUID.randomUUID()

        val rollcall = ST25DV.buildPayload(CheckinType.ROLLCALL, sid, key)
        assertEquals(34, rollcall.size)
        assertEquals(ST25DV.PAYLOAD_LENGTH, rollcall.size)
        assertEquals(0x01.toByte(), rollcall[0]) // 版本
        assertEquals(ST25DV.PAYLOAD_VERSION, rollcall[0])
        assertEquals(0x01.toByte(), rollcall[1]) // 点呼

        val study = ST25DV.buildPayload(CheckinType.STUDY, sid, key)
        assertEquals(34, study.size)
        assertEquals(0x02.toByte(), study[1]) // 晚自习
    }

    // MARK: - UUID 字节序 + 偏移（回归风险最高：字节翻转 / 偏移错位）

    @Test
    fun studentIdByteOrder() {
        // 用可预测的递增字节 UUID，逐字节钉死顺序（同 iOS）
        val sid = UUID.fromString("01020304-0506-0708-090A-0B0C0D0E0F10")
        val key = UUID.fromString("11121314-1516-1718-191A-1B1C1D1E1F20")
        val payload = ST25DV.buildPayload(CheckinType.ROLLCALL, sid, key)

        val sidBytes = payload.copyOfRange(2, 18)
        assertArrayEquals(
            byteArrayOf(
                0x01,
                0x02,
                0x03,
                0x04,
                0x05,
                0x06,
                0x07,
                0x08,
                0x09,
                0x0A,
                0x0B,
                0x0C,
                0x0D,
                0x0E,
                0x0F,
                0x10,
            ),
            sidBytes,
        )
    }

    @Test
    fun idempotencyKeyByteOrder() {
        val sid = UUID.fromString("01020304-0506-0708-090A-0B0C0D0E0F10")
        val key = UUID.fromString("11121314-1516-1718-191A-1B1C1D1E1F20")
        val payload = ST25DV.buildPayload(CheckinType.ROLLCALL, sid, key)

        val keyBytes = payload.copyOfRange(18, 34)
        assertArrayEquals(
            byteArrayOf(
                0x11,
                0x12,
                0x13,
                0x14,
                0x15,
                0x16,
                0x17,
                0x18,
                0x19,
                0x1A,
                0x1B,
                0x1C,
                0x1D,
                0x1E,
                0x1F,
                0x20,
            ),
            keyBytes,
        )
    }

    // MARK: - 两个 UUID 段互不串位

    @Test
    fun twoUuidSegmentsIndependent() {
        val sid = UUID.fromString("AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA")
        val key = UUID.fromString("BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB")
        val payload = ST25DV.buildPayload(CheckinType.ROLLCALL, sid, key)

        assertArrayEquals(ByteArray(16) { 0xAA.toByte() }, payload.copyOfRange(2, 18))
        assertArrayEquals(ByteArray(16) { 0xBB.toByte() }, payload.copyOfRange(18, 34))
    }

    // MARK: - Write Message 的 MSGlength 字段（数据长-1）

    @Test
    fun writeMessageLengthField() {
        assertEquals(33, ST25DV.PAYLOAD_LENGTH - 1)
        assertEquals(33.toByte(), ST25DV.writeMessageLengthField)
    }
}
