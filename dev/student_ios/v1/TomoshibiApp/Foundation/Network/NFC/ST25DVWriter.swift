// ST25DVWriter.swift
// Foundation · Network · NFC — 手机点呼签到：用 CoreNFC 把学号写进墙上 ST25DV16K 的 Mailbox
//
// ⭐ 架构（2026-06-02 itsuki 拍板「架构反转」，权威文档 design/flow_design.md §3）：
//   手机全程不联网（开飞行模式也能完成）。学生点签到 → app 用 CoreNFC 把身份数据写进点呼机墙上
//   ST25DV16K 芯片的 Mailbox（邮箱 = 256 字节临时缓存区）→ 点呼机被动读走 → 点呼机 POST 后端 → 后端验证。
//   旧方案（手机读贴纸拿一次性随机码 nonce → 手机自己 POST 后端）已作废。
//
// 写进 Mailbox 的载荷格式 = specs/rollcall/Device_Contract.md §7（唯一真值，双端逐字节对齐）：
//   [0]     1 字节  格式版本 = 0x01
//   [1]     1 字节  签到类型（0x01=点呼 / 0x02=晚自习 v1.1）
//   [2..17] 16 字节 student_id UUID 原始值（RFC 4122 字节序）
//   [18..33]16 字节 idempotency_key UUID 原始值（每次写入尝试新生成）
//   总长恒 34 字节。点呼机读取侧 dev/rollcall_device/src/nfc/st25dv.py 依同表解析。
//
// 写入流程（ST25DV RF 自定义命令，厂商码 0x02 = STMicroelectronics）：
//   连接 → Read Dynamic Configuration 读 MB_CTRL_Dyn（确认邮箱使能 + 无未读宿主消息）→ Write Message 写 34 字节。
//   命令码 / 寄存器位集中在 ST25DV 常量枚举，逐个附 datasheet 出处；硬件未到货前无法坐实处标「待硬件联调核实」。

@preconcurrency import CoreNFC
import Foundation

/// 签到类型（写进 Mailbox 载荷第 2 字节 [1]，让点呼机区分点呼 / 学習）。
/// Device_Contract §7：0x01=点呼 / 0x02=晚自习（v1.1）。
enum CheckinType: UInt8 {
    case rollcall = 0x01
    case study = 0x02
}

/// ST25DV16K 的 RF 自定义命令码 / 动态寄存器 / 载荷格式常量集中处。
///
/// 出处：ST25DV16K datasheet（型号 DS12550）「Custom commands」节 + 「Dynamic registers」节；
///   常量以「命令 / 寄存器名称」为准（这些是 ST25DV 系列固定值），精确小节号待与手册核对。
///   凡标「待硬件联调核实」= 硬件到货前无法在真机上坐实的点。
enum ST25DV {
    // MARK: - 载荷格式（Device_Contract §7）

    /// 载荷第 0 字节：格式版本号。v1.1 若加 ECDSA 签名会升到 0x02，双端同步升级。
    static let payloadVersion: UInt8 = 0x01
    /// 载荷总长（恒定）。点呼机读取后校验「长度=34 且版本=0x01」，不符即丢弃。
    static let payloadLength = 34

    /// 组装 Mailbox 载荷（恒 34 字节）。抽成 static 纯函数供单测锁字节序 + 长度（不碰 CoreNFC，可在测试宿主里跑）。
    /// - Parameters:
    ///   - type: 签到类型（点呼 / 学習）。
    ///   - studentId: 学生 UUID，写 [2..17]。
    ///   - idempotencyKey: 幂等键 UUID，写 [18..33]，调用方每次写入尝试新生成。
    static func buildPayload(type: CheckinType, studentId: UUID, idempotencyKey: UUID) -> Data {
        var data = Data(capacity: payloadLength)
        data.append(payloadVersion) // [0] 版本
        data.append(type.rawValue) // [1] 类型
        withUnsafeBytes(of: studentId.uuid) { data.append(contentsOf: $0) } // [2..17] student_id 16 字节
        withUnsafeBytes(of: idempotencyKey.uuid) { data.append(contentsOf: $0) } // [18..33] idempotency_key 16 字节
        return data
    }

    // MARK: - 厂商码

    /// IC 厂商码：STMicroelectronics = 0x02（ISO/IEC 7816-6 注册值）。
    /// ⚠️ CoreNFC 的 customCommand 会依据检测到的标签自动把厂商码插进命令帧，故本值仅作文档说明，
    ///   不手动拼进 customRequestParameters（拼了反而多一字节导致命令被拒）。
    static let manufacturerCodeST: UInt8 = 0x02

    // MARK: - RF 自定义命令码（datasheet「Custom commands」节；ISO15693 自定义命令有效范围 0xA0–0xDF）

    /// Write Message：把一段数据写进 Mailbox（RF→缓存）。
    /// 自定义请求参数 = [MSGlength = 数据长度-1 的 1 字节] + [数据本体]（厂商码由 CoreNFC 自动插入）。
    static let cmdWriteMessage: UInt8 = 0xAA
    /// Read Dynamic Configuration：读一个动态寄存器。
    /// 自定义请求参数 = [寄存器指针 1 字节]；响应 = [寄存器值 1 字节]。
    static let cmdReadDynamicConfiguration: UInt8 = 0xAD

    // MARK: - 动态寄存器指针（datasheet「Dynamic registers」节）

    /// MB_CTRL_Dyn：邮箱控制动态寄存器。
    /// ⚠️ **RF 侧指针 ≠ I²C 侧地址，别照抄点呼机的常量**：同一个寄存器，I²C（点呼机
    ///   `st25dv.py`）走 `0x2006`，RF（本文件的 Read Dynamic Configuration）走 `0x0D`。
    ///   datasheet 的「Dynamic registers」表把两列并排，取错列会读到另一个寄存器，
    ///   于是邮箱状态判断全错、写入被无条件拒绝。原写成 `0x06`（= I²C 地址的低字节），
    ///   2026-07-29 真机联调前由异构审查按手册抓出并订正。
    static let regMBCtrlDyn: UInt8 = 0x0D

    // MARK: - MB_CTRL_Dyn 位定义（datasheet MB_CTRL_Dyn 寄存器表）

    /// bit0 MB_EN：邮箱（Fast Transfer Mode 快速传输模式）已使能。
    ///   0 = 点呼机侧未开启邮箱 → RF 写入无处可落，应报错。
    static let mbCtrlMailboxEnabled: UInt8 = 1 << 0
    /// bit1 HOST_PUT_MSG：宿主（I2C 侧 = 点呼机）已写入一条消息且未被读走 = 邮箱被占。
    ///   RF 写入前应为 0，否则会覆盖点呼机尚未处理的消息。
    static let mbCtrlHostPutMsg: UInt8 = 1 << 1
    /// bit2 RF_PUT_MSG：RF 侧（= 上一部手机）已写入一条消息、点呼机还没读走。
    ///   排队场景现实存在：前一个学生刚写完、点呼机 I2C 还没取，此时直接写会覆盖掉
    ///   他的签到（芯片不会拦，RF 侧有写入优先权）→ 必须软件侧自己挡。
    ///   位号与点呼机 `st25dv.py` 的 `MB_CTRL_RF_PUT_MSG` 保持一致，硬件联调时一并坐实。
    static let mbCtrlRFPutMsg: UInt8 = 1 << 2
}

enum ST25DVError: Error {
    case unavailable // 本机不支持 NFC / 模拟器（NFCReaderSession.readingAvailable == false）
    case wrongTagType // 检测到的不是 ISO15693（NFC Type 5）标签
    case tagLost(String) // 连接失败 / 标签中途走开
    case mailboxDisabled // MB_CTRL_Dyn.MB_EN=0：点呼机侧未开启邮箱（快速传输模式），无法接收
    case mailboxBusy // MB_CTRL_Dyn.HOST_PUT_MSG=1：邮箱里有未读宿主消息，被占用
    case commandRejected(String) // 标签拒绝命令（Read Config / Write Message 返回错误或空响应）
    case payloadInvalid // 载荷长度不是约定的 34 字节（编程期不变量，正常构建不会触发）

    /// 面向用户的日语文案（失败弹窗 / toast 用）。技术细节不外泄，只给学生可行动的提示。
    var userMessageJP: String {
        switch self {
        case .unavailable:
            return "この端末は NFC に対応していません"
        case .wrongTagType:
            return "点呼機の NFC ではありません"
        case .tagLost:
            return "スマートフォンが離れました。もう一度かざしてください"
        case .mailboxDisabled:
            return "点呼機が受付状態ではありません。しばらく待ってからお試しください"
        case .mailboxBusy:
            return "点呼機が処理中です。少し待ってからもう一度かざしてください"
        case .commandRejected:
            return "書き込みに失敗しました。もう一度お試しください"
        case .payloadInvalid:
            return "送信データの生成に失敗しました"
        }
    }
}

/// 把学号写进墙上 ST25DV16K 的 Mailbox（手机不联网，点呼机读走）。
/// 用法：`try await ST25DVWriter().writeCheckin(studentId: uuid, type: .rollcall)`
/// @unchecked Sendable：NFC 一次签到全程串行（begin → didDetect → connect → 读寄存器 → 写 → invalidate），
/// continuation / payload 不存在真并发访问，故安全标注、压掉 CoreNFC completion 闭包的 Sendable 告警。
final class ST25DVWriter: NSObject, @unchecked Sendable {
    // codex B-2: 锁保护 continuation / session 跨线程读写 —— NFC 回调在 session 内部队列、
    //   writeCheckin 在调用线程，无锁理论上有可见性 race，加锁让 @unchecked Sendable 名副其实。
    private let lock = NSLock()
    private var continuation: CheckedContinuation<Void, Error>?
    /// codex B-1: 强引用持有 session，防 ARC 在 await 等待期间把它提前释放（局部变量出作用域就没人持有了）。
    private var session: NFCTagReaderSession?
    // codex 三轮 M-1: 取消请求标志 —— cancel() 可能在 writeCheckin 创建 / begin session 之前就触发，
    //   靠它在锁内原子判断「该不该开 NFC」，封住「已取消却 begin」的空窗。
    private var cancelRequested = false
    private var payload = Data()

    func writeCheckin(studentId: UUID, type: CheckinType) async throws {
        guard NFCReaderSession.readingAvailable else { throw ST25DVError.unavailable }

        // 组装 34 字节载荷（Device_Contract §7）。idempotency_key 每次写入尝试新生成。
        let data = ST25DV.buildPayload(type: type, studentId: studentId, idempotencyKey: UUID())
        // 不变量：载荷恒 34 字节，异常则不开 NFC（防把畸形帧写进点呼机）。
        guard data.count == ST25DV.payloadLength else { throw ST25DVError.payloadInvalid }
        payload = data

        try await withCheckedThrowingContinuation { (cont: CheckedContinuation<Void, Error>) in
            lock.lock()
            // codex 三轮 M-1: 创建 + begin session 都在锁内，且先查 cancelRequested ——
            //   若取消已抢先发生（cancel() 在本闭包前 / 中跑过），直接以取消失败结束、绝不 begin 开 NFC。
            if cancelRequested {
                lock.unlock()
                cont.resume(throwing: CancellationError())
                return
            }
            self.continuation = cont
            // ST25DV 是 NFC Type 5 / ISO15693 标签
            let s = NFCTagReaderSession(pollingOption: .iso15693, delegate: self, queue: nil)
            self.session = s
            s?.alertMessage = "点呼機にかざしてください"
            s?.begin()
            lock.unlock()
        }
    }

    /// 取消（用户关签到弹窗时调，codex M-1）：invalidate session 会触发 didInvalidateWithError → finish(.failure)，
    /// continuation 正常以失败结束、不会泄漏；NFC 系统界面也随之关闭。
    func cancel() {
        lock.lock()
        cancelRequested = true // codex 三轮 M-1: 标记取消，writeCheckin 若还没 begin 就不会再开 NFC
        let s = session
        lock.unlock()
        s?.invalidate()
    }

    /// codex B-2: 幂等 + 线程安全地结束。原子取出 continuation 置 nil —— 成功路径 invalidate 会再触发
    /// didInvalidateWithError 二次调 finish，此时 continuation 已 nil → guard 直接返回，绝不双重 resume 崩溃。
    private func finish(_ result: Result<Void, Error>) {
        lock.lock()
        let cont = continuation
        continuation = nil
        session = nil
        lock.unlock()
        guard let cont else { return }
        switch result {
        case .success: cont.resume()
        case let .failure(error): cont.resume(throwing: error)
        }
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
        // 连接 + 收发用 completion handler 版（非 async），避开 Swift 6 把 async Task 闭包当
        // 'sending' parameter 报 data race 的检查（session / tag 是非 Sendable 的 CoreNFC 类型）。
        session.connect(to: first) { [weak self] connectError in
            guard let self else { return }
            if let connectError {
                session.invalidate(errorMessage: "接続に失敗しました")
                self.finish(.failure(ST25DVError.tagLost(connectError.localizedDescription)))
                return
            }
            // 步骤①：读 MB_CTRL_Dyn，确认邮箱可写（使能 + 无未读宿主消息），再写。
            self.readMailboxControl(session: session, tag: tag)
        }
    }

    // MARK: - 步骤① Read Dynamic Configuration → 检查 MB_CTRL_Dyn

    /// 发 Read Dynamic Configuration（0xAD）读 MB_CTRL_Dyn（邮箱控制寄存器），据其决定能否写入。
    private func readMailboxControl(session: NFCTagReaderSession, tag: NFCISO15693Tag) {
        tag.customCommand(
            requestFlags: .highDataRate,
            customCommandCode: Int(ST25DV.cmdReadDynamicConfiguration),
            customRequestParameters: Data([ST25DV.regMBCtrlDyn])
        ) { [weak self] response, commandError in
            guard let self else { return }
            if let commandError {
                session.invalidate(errorMessage: "点呼機の状態を確認できませんでした")
                self.finish(.failure(ST25DVError.commandRejected(commandError.localizedDescription)))
                return
            }
            // MB_CTRL_Dyn 的寄存器值。CoreNFC 已剥掉 CRC；用 last 取值可同时兼容
            //   CoreNFC「保留 / 剥掉响应 flags 字节」两种可能（寄存器值总是响应里最后一字节）。
            //   待硬件联调核实：若真机响应结构与此不符，需按实测调整取值下标。
            guard let mbctrl = response.last else {
                session.invalidate(errorMessage: "点呼機の状態を確認できませんでした")
                self.finish(.failure(ST25DVError.commandRejected("空応答")))
                return
            }
            if mbctrl & ST25DV.mbCtrlMailboxEnabled == 0 {
                // 邮箱未使能：点呼机侧没开快速传输模式，写了也没人收。
                session.invalidate(errorMessage: "点呼機が受付状態ではありません")
                self.finish(.failure(ST25DVError.mailboxDisabled))
                return
            }
            if mbctrl & ST25DV.mbCtrlHostPutMsg != 0 {
                // 邮箱被占：点呼机刚写入的消息还没被读走，此刻写会覆盖它。
                session.invalidate(errorMessage: "点呼機が処理中です")
                self.finish(.failure(ST25DVError.mailboxBusy))
                return
            }
            if mbctrl & ST25DV.mbCtrlRFPutMsg != 0 {
                // 前一个学生写入的签到点呼机还没读走 —— 现在写会把他的签到覆盖掉（他会
                // 以为签到成功、实际丢了）。让本次失败重试，比静默吃掉别人的签到好。
                session.invalidate(errorMessage: "前の人の処理中です。少し待ってからもう一度")
                self.finish(.failure(ST25DVError.mailboxBusy))
                return
            }
            // 邮箱空闲 → 写入。
            self.writeMailbox(session: session, tag: tag)
        }
    }

    // MARK: - 步骤② Write Message → 写 34 字节载荷

    /// 发 Write Message（0xAA）把 34 字节载荷写进 Mailbox。
    /// 自定义请求参数 = [MSGlength = 载荷长-1] + [34 字节载荷]（厂商码由 CoreNFC 自动插入）。
    private func writeMailbox(session: NFCTagReaderSession, tag: NFCISO15693Tag) {
        // MSGlength 字段：datasheet 规定「写入字节数 - 1」（0 表示写 1 字节，255 表示写 256 字节）。
        var params = Data(capacity: 1 + payload.count)
        params.append(UInt8(payload.count - 1)) // 34-1 = 33
        params.append(payload)

        tag.customCommand(
            requestFlags: .highDataRate,
            customCommandCode: Int(ST25DV.cmdWriteMessage),
            customRequestParameters: params
        ) { [weak self] _, commandError in
            guard let self else { return }
            if let commandError {
                session.invalidate(errorMessage: "書き込みに失敗しました")
                self.finish(.failure(ST25DVError.commandRejected(commandError.localizedDescription)))
            } else {
                session.alertMessage = "送信しました"
                session.invalidate()
                self.finish(.success(()))
            }
        }
    }
}
