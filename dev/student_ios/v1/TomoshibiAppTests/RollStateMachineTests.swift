// RollStateMachineTests.swift
// 点呼时间窗状态机单元测试（iOS 首批单元测试，2026-06-11）
//
// 被测：AppStore.decideRollState(sessions:now:) —— R-1/R-2 实装的纯判定函数。
// 为什么能测：判定逻辑已从 refreshRollStateFromSessions 抽成纯函数，「现在几点」作为参数注入，
// 不读真实时钟 → 测试结果不随运行时刻变。
//
// 时间轴（以 base 为窗口开始）：
//   base            窗口开始 scheduled_window_start_at
//   base + 600s     「時間内」截止 scheduled_on_time_end_at（10 分）
//   base + 900s      迟到截止   scheduled_late_end_at（15 分）
//   base + 1800s     自动结束   scheduled_auto_end_at（30 分）

import Foundation
import Testing
@testable import TomoshibiApp

struct RollStateMachineTests {
    /// 固定基准时刻（不读真实时钟）。
    private let base = Date(timeIntervalSince1970: 1_700_000_000)

    /// 造一个「我寮今日点呼场次」。窗口固定 0 / +600 / +900 / +1800。
    private func makeSession(checkedInAt: Date? = nil, myStatus: String? = nil) -> MyRollCallTodaySession {
        MyRollCallTodaySession(
            session_id: UUID(),
            session_type: "evening",
            day_type: "weekday",
            session_status: "running",
            scheduled_window_start_at: base,
            scheduled_on_time_end_at: base.addingTimeInterval(600),
            scheduled_late_end_at: base.addingTimeInterval(900),
            scheduled_auto_end_at: base.addingTimeInterval(1800),
            my_status: myStatus,
            my_checked_in_at: checkedInAt
        )
    }

    @Test("本日无场次 → idle")
    func noSessionsIsIdle() {
        let d = AppStore.decideRollState(sessions: [], now: base)
        #expect(d.rollState == .idle)
        #expect(d.checkinKind == nil)
        #expect(d.countdownSec == nil)
    }

    @Test("窗口开始前 → idle（下次点呼预告）")
    func beforeWindowIsIdle() {
        let d = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(-60))
        #expect(d.rollState == .idle)
        #expect(d.checkedInAt == nil)
    }

    @Test("窗口内未签到 → active，倒计时到「時間内」截止")
    func inWindowUnsignedIsActive() {
        let now = base.addingTimeInterval(300) // 窗口内、距 on_time_end 还有 300s
        let d = AppStore.decideRollState(sessions: [makeSession()], now: now)
        #expect(d.rollState == .active)
        #expect(d.countdownSec == 300)
        #expect(d.checkinKind == nil)
    }

    @Test("过「時間内」截止仍在迟到段未签到 → active，倒计时夹到 0")
    func pastOnTimeStillActiveCountdownZero() {
        let now = base.addingTimeInterval(700) // on_time_end(600) < now <= late_end(900)
        let d = AppStore.decideRollState(sessions: [makeSession()], now: now)
        #expect(d.rollState == .active)
        #expect(d.countdownSec == 0) // max(0, 600-700) 夹到 0、不出现负倒计时
    }

    @Test("窗口内已签到且准时 → done，判定「時間内」")
    func signedOnTimeIsDone() {
        let now = base.addingTimeInterval(300)
        let session = makeSession(checkedInAt: now, myStatus: "present")
        let d = AppStore.decideRollState(sessions: [session], now: now)
        #expect(d.rollState == .done)
        #expect(d.checkinKind == "時間内")
        #expect(d.checkedInAt == now)
    }

    @Test("已签到但迟到 → done，判定「遅刻」")
    func signedLateIsDone() {
        let now = base.addingTimeInterval(800)
        let session = makeSession(checkedInAt: now, myStatus: "late")
        let d = AppStore.decideRollState(sessions: [session], now: now)
        #expect(d.rollState == .done)
        #expect(d.checkinKind == "遅刻")
    }

    @Test("过迟到截止仍未签到 → absent")
    func pastLateEndUnsignedIsAbsent() {
        let now = base.addingTimeInterval(1000) // late_end(900) < now <= auto_end(1800)
        let d = AppStore.decideRollState(sessions: [makeSession()], now: now)
        #expect(d.rollState == .absent)
        #expect(d.countdownSec == nil)
    }

    // MARK: - C2 #1-5：时间窗精确边界（防 < / <= 漂移 + 与后端判定口径漂移）

    // 说明：iOS「時間内 / 遅刻」的 checkinKind 由后端 my_status 决定（signed* 用例已覆盖），
    // 不由 now 与 on_time_end 的比较推出。故未签到时 on_time_end 这个精确点在纯函数里唯一
    // 主宰的是倒计时钳位 max(0, on_time_end - now)：countdown>0 = 「時間内」侧、==0 = 进入「遅刻」段。

    @Test("#1 now == on_time_end 精确点：仍 active，倒计时恰好钳到 0（時間内↔遅刻 侧界）")
    func atOnTimeEndCountdownClampsToZero() {
        // on_time_end 前一秒：倒计时 == 1（「時間内」侧、仍 > 0）
        let justBefore = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(599))
        #expect(justBefore.rollState == .active)
        #expect(justBefore.countdownSec == 1)
        // on_time_end 精确点：倒计时 == 0（进入「遅刻」段），状态仍 active（未过 late_end）
        let atPoint = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(600))
        #expect(atPoint.rollState == .active)
        #expect(atPoint.countdownSec == 0)
    }

    @Test("#2 now == late_end 精确点：active（含端点）；越过一秒 → absent")
    func atLateEndBoundaryActiveVsAbsent() {
        // late_end 精确点 900：判定用 now <= late_end → 仍 active（受付中含遅刻段末刻）
        let atLateEnd = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(900))
        #expect(atLateEnd.rollState == .active)
        #expect(atLateEnd.countdownSec == 0) // max(0, 600-900) 钳到 0
        // late_end + 1 秒 901：越过迟到截止 → 欠席
        let afterLateEnd = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(901))
        #expect(afterLateEnd.rollState == .absent)
        #expect(afterLateEnd.countdownSec == nil)
    }

    @Test("#3 now == window_start 精确点：active（含端点）；前一秒 → idle 预告")
    func atWindowStartBoundaryIdleVsActive() {
        // window_start 前一秒 -1：属未来场次 → idle 预告
        let justBefore = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(-1))
        #expect(justBefore.rollState == .idle)
        // window_start 精确点 0：now >= window_start → 进行中场次 → active，倒计时满窗 600
        let atStart = AppStore.decideRollState(sessions: [makeSession()], now: base)
        #expect(atStart.rollState == .active)
        #expect(atStart.countdownSec == 600)
    }

    @Test("#4 now == auto_end 端点 → absent；越过 auto_end → 回落 idle（不再 absent 挂死）")
    func afterAutoEndFallsBackToIdle() {
        // auto_end 精确点 1800：仍属当前场次（now <= auto_end），未签到已过 late_end → absent
        let atAutoEnd = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(1800))
        #expect(atAutoEnd.rollState == .absent)
        // auto_end + 1 秒 1801：场次已完全结束、又非未来场次 → 无当前/预告场次 → 回落 idle
        let afterAutoEnd = AppStore.decideRollState(sessions: [makeSession()], now: base.addingTimeInterval(1801))
        #expect(afterAutoEnd.rollState == .idle)
        #expect(afterAutoEnd.countdownSec == nil)
    }

    @Test("#5 多场次并存（早点呼已结束 + 晚点呼进行中）→ 选中进行中场次，与数组顺序无关")
    func multipleSessionsSelectsRunningOne() {
        let now = base.addingTimeInterval(10000) // 取一个远离固定窗口的绝对时刻当「现在」
        // 早场次 A：整段在 now 之前结束（auto_end 早于 now）→ 应被完全忽略（不是选它算 absent）
        let ended = MyRollCallTodaySession(
            session_id: UUID(),
            session_type: "morning",
            day_type: "weekday",
            session_status: "ended",
            scheduled_window_start_at: now.addingTimeInterval(-3600),
            scheduled_on_time_end_at: now.addingTimeInterval(-3000),
            scheduled_late_end_at: now.addingTimeInterval(-2700),
            scheduled_auto_end_at: now.addingTimeInterval(-1800),
            my_status: nil,
            my_checked_in_at: nil
        )
        // 晚场次 B：now 落在窗口内、距 on_time_end 还有 300s、未签到 → 应被选中判 active/countdown=300
        let running = MyRollCallTodaySession(
            session_id: UUID(),
            session_type: "evening",
            day_type: "weekday",
            session_status: "running",
            scheduled_window_start_at: now.addingTimeInterval(-300),
            scheduled_on_time_end_at: now.addingTimeInterval(300),
            scheduled_late_end_at: now.addingTimeInterval(600),
            scheduled_auto_end_at: now.addingTimeInterval(1500),
            my_status: nil,
            my_checked_in_at: nil
        )
        // 两种数组顺序都必须选中进行中的 B（若误选已结束的 A 会得到 absent，测试即红）
        for sessions in [[ended, running], [running, ended]] {
            let d = AppStore.decideRollState(sessions: sessions, now: now)
            #expect(d.rollState == .active)
            #expect(d.countdownSec == 300)
        }
    }
}
