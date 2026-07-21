package jp.tomoshibi.android.data.rollcall

import jp.tomoshibi.android.data.model.RollState
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

// 点呼时间窗判定纯函数测试（C2 Android #13-14，对齐 iOS RollStateMachineTests.swift）。
//
// ⭐ 双端判定漂移防护：窗口数值跟 iOS RollStateMachineTests 用同一组（0 / +600 / +900 / +1800 秒），
//    同一时刻两端判定答案必须一致，否则学生看 iOS 是「時間内」、Android 是「遅刻」。
//
// 时间轴（毫秒，base 为窗口开始）：
//   base            windowStart
//   base + 600_000  onTimeEnd（10 分）
//   base + 900_000  lateEnd  （15 分）
//   base + 1_800_000 autoEnd （30 分）
class RollStateMachineTest {
    private val base = 1_700_000_000_000L

    private fun makeSession(
        checkedInAtMillis: Long? = null,
        myStatus: String? = null,
    ) = RollSession(
        windowStartMillis = base,
        onTimeEndMillis = base + 600_000,
        lateEndMillis = base + 900_000,
        autoEndMillis = base + 1_800_000,
        checkedInAtMillis = checkedInAtMillis,
        myStatus = myStatus,
    )

    // ── #13 窗口精确边界（对称 iOS #3 窗口开始 + #1 時間内截止）──

    @Test
    fun `now 等于 windowStart 精确点 未签到 归 ACTIVE 倒计时满`() {
        val d = RollStateMachine.decide(listOf(makeSession()), nowMillis = base)
        // 与 iOS 一致：now >= windowStart 用闭区间，窗口开启瞬间即 active（不是 idle）
        assertEquals(RollState.ACTIVE, d.state)
        assertEquals(600L, d.countdownSec) // (600_000-0)/1000
        assertNull(d.checkinKind)
    }

    @Test
    fun `now 等于 onTimeEnd 精确点 未签到 仍 ACTIVE 倒计时夹到 0`() {
        val d = RollStateMachine.decide(listOf(makeSession()), nowMillis = base + 600_000)
        // 比较符 <= 定死在「時間内截止仍算受付中」侧；倒计时 max(0, ...) 夹到 0、不出现负值
        assertEquals(RollState.ACTIVE, d.state)
        assertEquals(0L, d.countdownSec)
    }

    // ── #14 迟到截止精确边界（对称 iOS #2 迟到↔缺席分界）──

    @Test
    fun `now 等于 lateEnd 精确点 未签到 仍 ACTIVE`() {
        val d = RollStateMachine.decide(listOf(makeSession()), nowMillis = base + 900_000)
        // lateEnd 闭区间归 active 侧（跟 iOS now <= lateEnd 一致）
        assertEquals(RollState.ACTIVE, d.state)
        assertEquals(0L, d.countdownSec)
    }

    @Test
    fun `刚过 lateEnd 未签到 落 ABSENT`() {
        val d = RollStateMachine.decide(listOf(makeSession()), nowMillis = base + 900_001)
        assertEquals(RollState.ABSENT, d.state)
        assertNull(d.countdownSec)
    }

    // ── 支撑用例（确保边界判定放在完整状态机里也对，跟 iOS 逐条对齐）──

    @Test
    fun `本日无场次 归 IDLE`() {
        val d = RollStateMachine.decide(emptyList(), nowMillis = base)
        assertEquals(RollState.IDLE, d.state)
        assertNull(d.checkinKind)
        assertNull(d.countdownSec)
    }

    @Test
    fun `窗口开始前 归 IDLE`() {
        val d = RollStateMachine.decide(listOf(makeSession()), nowMillis = base - 60_000)
        assertEquals(RollState.IDLE, d.state)
        assertNull(d.checkedInAtMillis)
    }

    @Test
    fun `已签到且准时 归 DONE 判定時間内`() {
        val now = base + 300_000
        val d = RollStateMachine.decide(listOf(makeSession(checkedInAtMillis = now, myStatus = "present")), nowMillis = now)
        assertEquals(RollState.DONE, d.state)
        assertEquals("時間内", d.checkinKind)
        assertEquals(now, d.checkedInAtMillis)
    }

    @Test
    fun `已签到但迟到 归 DONE 判定遅刻`() {
        val now = base + 800_000
        val d = RollStateMachine.decide(listOf(makeSession(checkedInAtMillis = now, myStatus = "late")), nowMillis = now)
        assertEquals(RollState.DONE, d.state)
        assertEquals("遅刻", d.checkinKind)
    }

    @Test
    fun `已签到但被结算欠席 myStatus absent 归 ABSENT 不显 DONE 時間内 时刻`() {
        val now = base + 300_000
        val d = RollStateMachine.decide(listOf(makeSession(checkedInAtMillis = now, myStatus = "absent")), nowMillis = now)
        assertEquals(RollState.ABSENT, d.state)
        assertNull(d.checkinKind)
        assertNull(d.checkedInAtMillis)
    }

    @Test
    fun `承認済出寮願免除 myStatus exempt_range 归 DONE 免除 不显假签到时刻`() {
        val now = base + 300_000
        val d = RollStateMachine.decide(listOf(makeSession(checkedInAtMillis = now, myStatus = "exempt_range")), nowMillis = now)
        assertEquals(RollState.DONE, d.state)
        assertEquals("免除", d.checkinKind)
        assertNull(d.checkedInAtMillis)
    }

    @Test
    fun `多场次并存 选中进行中场次判定 与数组顺序无关`() {
        val ended =
            RollSession(
                windowStartMillis = base - 3_600_000,
                onTimeEndMillis = base - 3_000_000,
                lateEndMillis = base - 2_700_000,
                autoEndMillis = base - 1_800_000, // 已整体结束
            )
        val running = makeSession()
        val now = base + 300_000 // 落在 running 窗口内
        // 两种数组顺序都跑（对称 iOS #5）：锁死「选中进行中场次」跟场次在数组里的位置无关
        for (sessions in listOf(listOf(ended, running), listOf(running, ended))) {
            val d = RollStateMachine.decide(sessions, nowMillis = now)
            assertEquals(RollState.ACTIVE, d.state)
            assertEquals(300L, d.countdownSec) // (600_000-300_000)/1000
        }
    }

    // ── 自动结束边界（对称 iOS #4，防「点呼结束后主页残留错误状态」回归）──

    @Test
    fun `now 等于 autoEnd 精确点 未签到 仍 ABSENT`() {
        // autoEnd 闭区间：场次仍算「当前场次」，未签到且已过 lateEnd → 欠席
        val d = RollStateMachine.decide(listOf(makeSession()), nowMillis = base + 1_800_000)
        assertEquals(RollState.ABSENT, d.state)
        assertNull(d.countdownSec)
    }

    @Test
    fun `越过 autoEnd 且无后续场次 回落 IDLE 不残留 ABSENT`() {
        // 场次整体结束后主页必须回落 idle（下次点呼预告），不能把 ABSENT 挂死到半夜
        val d = RollStateMachine.decide(listOf(makeSession()), nowMillis = base + 1_800_001)
        assertEquals(RollState.IDLE, d.state)
        assertNull(d.countdownSec)
        assertNull(d.checkinKind)
    }
}
