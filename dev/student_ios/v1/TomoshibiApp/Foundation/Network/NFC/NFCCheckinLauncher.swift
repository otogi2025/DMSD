// NFCCheckinLauncher.swift
// Foundation · Network · NFC — 「一按就扫」：按钮按下去就直接开 CoreNFC，中间不再插自制弹窗
//
// ⭐ 为什么有这个文件（2026-07-29 itsuki 真机实测后拍板）：
//   原流程要按两次 —— 先弹一个我们自己画的 SwiftUI 弹窗（「スキャンの準備ができました」），
//   用户再按弹窗里的「NFC をかざす」，这时才 session.begin()，于是苹果系统自己的 NFC 面板
//   （黑底 + 手机图标 + 「キャンセル」按钮）又盖在我们的弹窗上 —— 两层界面重叠、白按一次。
//   现在按钮 → 直接 begin()，全过程只剩苹果那一个面板；成功 / 失败的文字也全交给它显示
//   （成功：ST25DVWriter 设 alertMessage 后 invalidate()，面板出绿勾；
//     失败：invalidate(errorMessage:) 让面板出红叉 + 日语原因），面板自己消失。
//   失败重试 = 用户再按一次首页那个按钮，不再有「再試行」弹窗。
//
// 本文件只管「什么时候开扫描、扫完提示谁」，不碰写入逻辑本身 ——
//   载荷格式 / 寄存器 / 命令构造全在 ST25DVWriter.swift（唯一真值 = Device_Contract §7）。
//
// 仅生产 scheme 编译：演示 scheme（DEMO）没有真 NFC 可碰，仍走自制假动画弹窗
//   （Features/Home/HomeCheckinDemoSheets.swift）。

import Foundation

#if !DEMO
    @MainActor
    enum NFCCheckinLauncher {
        /// 是否已有一次写入在跑。CoreNFC 同一时刻只允许一个会话，连按两下按钮会让第二次直接失败，
        /// 所以自己先挡住（不是 UI 装饰，是硬件约束）。
        private static var isRunning = false

        /// 开始一次 NFC 签到写入。
        /// - Parameters:
        ///   - type: 签到类型（点呼 0x01 / 夜学習 0x02，写进载荷第 2 字节）。
        ///   - app: 全局状态，用来取学生编号 + 出 toast（轻提示条，不是弹窗）。
        ///   - onSuccess: 写入成功后在主线程回调，给调用方更新本地进度（如夜学習的 2 次打卡圆点）。
        ///     注意「写入成功」只等于载荷已交到墙上芯片，出席判定权威在点呼机 + 后端。
        static func start(
            type: CheckinType,
            app: AppStore,
            onSuccess: @escaping () -> Void = {}
        ) {
            guard !isRunning else { return }
            isRunning = true

            let writer = ST25DVWriter()
            Task { @MainActor in
                defer { isRunning = false }

                // 冷启动时登录令牌已恢复但 loadMe 还没跑完 → myStudentId 暂时为 nil，先补拉一次再判断
                if app.myStudentId == nil { await app.loadMe() }
                guard let sid = app.myStudentId, let uuid = UUID(uuidString: sid) else {
                    // 这一步失败时苹果面板还没弹出来，只能自己出提示
                    app.showToast("学生情報の取得に失敗しました")
                    return
                }

                do {
                    try await writer.writeCheckin(studentId: uuid, type: type)
                    // 成功画面已经由苹果面板显示（绿勾 +「送信しました」）；
                    // 这里只留一条 app 内的轻提示，方便面板消失后还能确认自己确实送出去了。
                    onSuccess()
                    app.showToast("点呼機に送信しました · 確認中…")
                    // ⭐ 写入成功 ≠ 签到成功（2026-07-29 真机实测暴露）：
                    //   载荷只是交到墙上芯片的邮箱，还要等点呼机读走 + 上报后端，本机才有资格显示「完了」。
                    //   以前到上一行就收工，首页永远停在「点呼中」—— 后端明明已经 200 了。
                    //   现在主动去后端确认，拿到结果由 AppStore 把首页卡片 + 顶部状态条切成完成态。
                    //   夜学習（.study）不走 /rollcall/me/today，没有可确认的场次，故只对点呼做。
                    if type == .rollcall {
                        // 不 await：确认要花几秒，await 会把下面 defer 里的 isRunning 一起卡住，
                        // 用户这段时间连按钮都按不动。丢给独立任务跑，重入由 AppStore 自己挡。
                        Task { @MainActor in
                            await app.confirmCheckinAfterNFCWrite()
                        }
                    }
                } catch let e as ST25DVError {
                    switch e {
                    case .unavailable, .payloadInvalid:
                        // 这两种是「面板还没弹出来就失败」（本机没 NFC / 载荷长度异常）→ 必须自己提示
                        app.showToast(e.userMessageJP)
                    case .wrongTagType, .tagLost, .mailboxDisabled, .mailboxBusy, .commandRejected:
                        // 其余失败原因 ST25DVWriter 已经通过 invalidate(errorMessage:) 打在苹果面板上，
                        // 这里再出一条就是重复提示 —— 不做。重试 = 用户再按一次按钮。
                        break
                    }
                } catch {
                    // 用户按了面板上的「キャンセル」、或系统超时 —— 面板自己已经收场，不再打扰用户。
                }
            }
        }
    }
#endif
