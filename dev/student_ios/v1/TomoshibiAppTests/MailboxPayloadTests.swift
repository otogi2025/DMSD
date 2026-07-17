// MailboxPayloadTests.swift
// ST25DV Mailbox 载荷组装 纯函数单测
//
// 被测：ST25DV.buildPayload(type:studentId:idempotencyKey:) —— 手机写进点呼机 Mailbox 的 34 字节载荷。
// 契约真值：specs/rollcall/Device_Contract.md §7（双端逐字节对齐，写入端 iOS / 读取端 st25dv.py 都照此表）。
//   [0]      版本 0x01
//   [1]      类型 0x01=点呼 / 0x02=晚自习
//   [2..17]  student_id UUID 原始 16 字节（RFC 4122 字节序）
//   [18..33] idempotency_key UUID 原始 16 字节
// ⭐ 核心不变量：总长恒 34 + 两个 UUID 的字节序不能被 CoreFoundation 的字节翻转搅乱（点呼机按原始字节序解析）。

import Foundation
import Testing
@testable import TomoshibiApp

struct MailboxPayloadTests {
    // MARK: - 长度 + 头两字节（版本 / 类型）

    @Test("载荷恒 34 字节，[0]=版本 0x01，[1]=类型（点呼 0x01 / 学習 0x02）")
    func lengthAndHeader() {
        let sid = UUID()
        let key = UUID()

        let rollcall = ST25DV.buildPayload(type: .rollcall, studentId: sid, idempotencyKey: key)
        #expect(rollcall.count == 34)
        #expect(rollcall.count == ST25DV.payloadLength)
        #expect(rollcall[0] == 0x01) // 版本
        #expect(rollcall[0] == ST25DV.payloadVersion)
        #expect(rollcall[1] == 0x01) // 点呼

        let study = ST25DV.buildPayload(type: .study, studentId: sid, idempotencyKey: key)
        #expect(study.count == 34)
        #expect(study[1] == 0x02) // 晚自习
    }

    // MARK: - UUID 字节序 + 偏移（回归风险最高：字节翻转 / 偏移错位）

    @Test("student_id 写 [2..17]，按 RFC 4122 原始字节序（不翻转）")
    func studentIdByteOrder() throws {
        // 用可预测的递增字节 UUID，逐字节钉死顺序
        let sid = try #require(UUID(uuidString: "01020304-0506-0708-090A-0B0C0D0E0F10"))
        let key = try #require(UUID(uuidString: "11121314-1516-1718-191A-1B1C1D1E1F20"))
        let payload = ST25DV.buildPayload(type: .rollcall, studentId: sid, idempotencyKey: key)

        let sidBytes = Array(payload[2 ..< 18])
        #expect(sidBytes == [
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10,
        ])
    }

    @Test("idempotency_key 写 [18..33]，按 RFC 4122 原始字节序（不翻转）")
    func idempotencyKeyByteOrder() throws {
        let sid = try #require(UUID(uuidString: "01020304-0506-0708-090A-0B0C0D0E0F10"))
        let key = try #require(UUID(uuidString: "11121314-1516-1718-191A-1B1C1D1E1F20"))
        let payload = ST25DV.buildPayload(type: .rollcall, studentId: sid, idempotencyKey: key)

        let keyBytes = Array(payload[18 ..< 34])
        #expect(keyBytes == [
            0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
            0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20,
        ])
    }

    // MARK: - 两个 UUID 段互不串位

    @Test("student_id 与 idempotency_key 是两段独立 16 字节，不同 UUID 不会互相污染")
    func twoUuidSegmentsIndependent() throws {
        let sid = try #require(UUID(uuidString: "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA"))
        let key = try #require(UUID(uuidString: "BBBBBBBB-BBBB-BBBB-BBBB-BBBBBBBBBBBB"))
        let payload = ST25DV.buildPayload(type: .rollcall, studentId: sid, idempotencyKey: key)

        #expect(Array(payload[2 ..< 18]) == Array(repeating: UInt8(0xAA), count: 16))
        #expect(Array(payload[18 ..< 34]) == Array(repeating: UInt8(0xBB), count: 16))
    }

    // MARK: - Write Message 的 MSGlength 字段（数据长-1）

    @Test("Write Message 的 MSGlength = 载荷长-1 = 33（datasheet：写 N 字节时该字段填 N-1）")
    func writeMessageLengthField() {
        #expect(ST25DV.payloadLength - 1 == 33)
    }
}
