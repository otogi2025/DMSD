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
}
