package jp.tomoshibi.android.data.rollcall

import jp.tomoshibi.android.data.model.RollState

// RollStateMachine — 点呼时间窗判定纯函数（对齐 iOS AppStore.decideRollState）。
//
// 为什么存在：Android 学生端此前没有时间窗判定逻辑（rollState 由 RollCallSheet 模拟直写），
// 后端「我寮今日点呼场次」接真数据后需要跟 iOS 一字不差的同一套判定，否则同一时刻学生看
// iOS 是「時間内」、Android 是「遅刻」= 双端判定漂移。本文件把 iOS 的纯判定移植过来，
// 「现在几点」作为参数注入（不读真实时钟）→ 可单测、结果不随运行时刻变。
//
// 时间轴语义与 iOS 同源（毫秒）：
//   windowStart   窗口开始 scheduled_window_start_at
//   onTimeEnd     「時間内」截止 scheduled_on_time_end_at
//   lateEnd       迟到截止   scheduled_late_end_at
//   autoEnd       自动结束   scheduled_auto_end_at
//   checkedInAt   我已签到时刻（null = 未签到）
//   myStatus      后端判定（null=未签到；present→時間内；late→遅刻；absent→欠席；exempt_range→免除；其它保守 DONE 不猜文案）

// / 一个「我寮今日点呼场次」的时间窗 + 我方签到状态（对齐 iOS MyRollCallTodaySession 判定所需字段）。
data class RollSession(
    val windowStartMillis: Long,
    val onTimeEndMillis: Long,
    val lateEndMillis: Long,
    val autoEndMillis: Long,
    val checkedInAtMillis: Long? = null,
    val myStatus: String? = null,
)

// / 纯判定结果（不碰持久化 / 时钟 / 格式化）— 对齐 iOS RollStateDecision。
data class RollDecision(
    val state: RollState,
    val checkinKind: String? = null, // 「時間内」/「遅刻」/ null
    val checkedInAtMillis: Long? = null, // 已签到时刻原始值；未签到 null
    val countdownSec: Long? = null, // active 时到「時間内」截止的倒计时秒；其余态 null
)

object RollStateMachine {
    // / 纯函数：从场次列表 + 注入的「现在」派生点呼状态。无副作用、不读真实时钟 → 可单测。
    // / 选「当前进行中场次」(now 落在 windowStart..autoEnd)；否则最近的未来场次做预告(idle)。
    // / 判定分支与 iOS decideRollState 逐行对应，边界比较符（>= / <=）必须与 iOS 一致。
    fun decide(
        sessions: List<RollSession>,
        nowMillis: Long,
    ): RollDecision {
        val current =
            sessions.firstOrNull {
                nowMillis >= it.windowStartMillis && nowMillis <= it.autoEndMillis
            }
        val upcoming =
            sessions
                .filter { nowMillis < it.windowStartMillis }
                .minByOrNull { it.windowStartMillis }
        val s =
            current ?: upcoming
                ?: // 本日我寮无点呼 → 安全落 idle
                return RollDecision(state = RollState.IDLE)

        // 已签到/已结算 → 按后端 myStatus 完整映射（android#1 契约收口，与 iOS decideRollState 逐行对齐）。
        // 后端 _settle 给 absent/exempt_range 也写 checked_in_at，故不能只凭 checkedInAtMillis 非空就当签到。
        s.checkedInAtMillis?.let { at ->
            return when (s.myStatus) {
                "present" -> RollDecision(state = RollState.DONE, checkinKind = "時間内", checkedInAtMillis = at)

                "late" -> RollDecision(state = RollState.DONE, checkinKind = "遅刻", checkedInAtMillis = at)

                // 被结算欠席：欠席态，不显时刻
                "absent" -> RollDecision(state = RollState.ABSENT)

                // 承認済出寮願免除：良性完了，复用 DONE 但文案「免除」、不显假签到时刻
                "exempt_range" -> RollDecision(state = RollState.DONE, checkinKind = "免除")

                // 未知：保守 DONE 但不猜文案（绝不兜底時間内），仍显真实时刻
                else -> RollDecision(state = RollState.DONE, checkinKind = null, checkedInAtMillis = at)
            }
        }

        // 未签到，按时间窗判定（比较符与 iOS 完全一致）
        return when {
            // 窗口开始前 → idle（下次点呼预告）
            nowMillis < s.windowStartMillis -> {
                RollDecision(state = RollState.IDLE)
            }

            // 受付中（含遅刻段，含 lateEnd 精确点）→ active；倒计时夹到 0、不出现负值
            nowMillis <= s.lateEndMillis -> {
                RollDecision(
                    state = RollState.ACTIVE,
                    countdownSec = ((s.onTimeEndMillis - nowMillis) / 1000L).coerceAtLeast(0L),
                )
            }

            // 超过迟到截止仍未签到 → 欠席
            else -> {
                RollDecision(state = RollState.ABSENT)
            }
        }
    }
}
