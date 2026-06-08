// ST25DVWriter.swift
// Foundation · Network · NFC — 手机点呼签到：用 CoreNFC 把学号写进墙上 ST25DV16K 的 Mailbox
//
// ⭐ 架构（2026-06-02 itsuki 拍板「架构反转」，权威文档 02_design/flow_design.md §3）：
//   手机全程不联网（开飞行模式也能完成）。学生点签到 → app 用 CoreNFC 把身份数据写进点呼机墙上
//   ST25DV16K 芯片的 Mailbox（邮箱 = 256 字节临时缓存区）→ 点呼机被动读走 → 点呼机 POST 后端 → 后端验证。
//   旧方案（手机读贴纸拿一次性随机码 nonce → 手机自己 POST 后端）已作废。
//
// 写进 Mailbox 的数据格式（v1.0，紧凑二进制；跟 flow_design.md §3 + 将来点呼机端
// 03_dev/rollcall_device/src/nfc/st25dv.py 对齐。点呼机读取侧尚未实装，本格式为提案，硬件到货后对齐定稿）：
//   第 1 字节：格式版本号 0x01
//   第 2 字节：类型（0x01=点呼签到 / 0x02=学習签到），让点呼机区分两种签到
//   接 16 字节：student_id（UUID 的 16 字节原始值）
//   v1.1 可选：再接私钥签名（v1.0 不做）

@preconcurrency import CoreNFC
import Foundation

/// 签到类型（写进 Mailbox 第 2 字节，让点呼机区分点呼 / 学習）。
enum CheckinType: UInt8 {
    case rollcall = 0x01
    case study = 0x02
}

enum ST25DVError: Error {
    case unavailable // 本机不支持 NFC / 模拟器（NFCReaderSession.readingAvailable == false）
    case wrongTagType // 检测到的不是 ISO15693（NFC Type 5）标签
    case writeFailed(String) // 连接 / 写 Mailbox 失败
}

/// 把学号写进墙上 ST25DV16K 的 Mailbox（手机不联网，点呼机读走）。
/// 用法：`try await ST25DVWriter().writeCheckin(studentId: uuid, type: .rollcall)`
/// @unchecked Sendable：NFC 一次签到全程串行（begin → didDetect → connect → 写 → invalidate），
/// continuation / payload 不存在真并发访问，故安全标注、压掉 CoreNFC completion 闭包的 Sendable 告警。
final class ST25DVWriter: NSObject, @unchecked Sendable {
    private var continuation: CheckedContinuation<Void, Error>?
    private var payload = Data()

    func writeCheckin(studentId: UUID, type: CheckinType) async throws {
        guard NFCReaderSession.readingAvailable else { throw ST25DVError.unavailable }

        // 拼 payload：版本 0x01 + 类型 + 16 字节 UUID 原始值
        var data = Data()
        data.append(0x01)
        data.append(type.rawValue)
        withUnsafeBytes(of: studentId.uuid) { data.append(contentsOf: $0) }
        payload = data

        try await withCheckedThrowingContinuation { (cont: CheckedContinuation<Void, Error>) in
            self.continuation = cont
            // ST25DV 是 NFC Type 5 / ISO15693 标签
            let session = NFCTagReaderSession(pollingOption: .iso15693, delegate: self, queue: nil)
            session?.alertMessage = "点呼機にタッチしてください"
            session?.begin()
        }
    }

    private func finish(_ result: Result<Void, Error>) {
        switch result {
        case .success: continuation?.resume()
        case let .failure(error): continuation?.resume(throwing: error)
        }
        continuation = nil
    }
}

extension ST25DVWriter: NFCTagReaderSessionDelegate {
    func tagReaderSessionDidBecomeActive(_: NFCTagReaderSession) {}

    func tagReaderSession(_: NFCTagReaderSession, didInvalidateWithError error: Error) {
        // 用户取消 / 超时 / 系统错误。若还没 finish 过就按失败结束。
        finish(.failure(error))
    }

    func tagReaderSession(_ session: NFCTagReaderSession, didDetect tags: [NFCTag]) {
        guard let first = tags.first, case let .iso15693(tag) = first else {
            session.invalidate(errorMessage: "対応していないタグです")
            finish(.failure(ST25DVError.wrongTagType))
            return
        }
        // 连接 + 写 Mailbox 用 completion handler 版（非 async），避开 Swift 6 把 async Task 闭包当
        // 'sending' parameter 报 data race 的检查（session / tag 是非 Sendable 的 CoreNFC 类型）。
        session.connect(to: first) { [weak self] connectError in
            guard let self else { return }
            if let connectError {
                session.invalidate(errorMessage: "接続に失敗しました")
                self.finish(.failure(ST25DVError.writeFailed(connectError.localizedDescription)))
                return
            }
            // 写 Mailbox 用 ISO15693 自定义命令（ST 厂商私有指令）。
            // TODO[硬件]: 对照 ST25DV16K datasheet 核实命令字节（Write Mailbox / Fast Transfer Mode）；
            //   现在的命令码是占位、结构搭对、硬件到货联调时坐实。
            let writeMailboxCommandCode = 0xAA // TODO[硬件]: 占位 — ST25DV「Write Message」自定义命令码待核实
            tag.customCommand(
                requestFlags: .highDataRate,
                customCommandCode: writeMailboxCommandCode,
                customRequestParameters: self.payload
            ) { [weak self] _, commandError in
                guard let self else { return }
                if let commandError {
                    session.invalidate(errorMessage: "書き込みに失敗しました")
                    self.finish(.failure(ST25DVError.writeFailed(commandError.localizedDescription)))
                } else {
                    session.alertMessage = "送信しました"
                    session.invalidate()
                    self.finish(.success(()))
                }
            }
        }
    }
}
