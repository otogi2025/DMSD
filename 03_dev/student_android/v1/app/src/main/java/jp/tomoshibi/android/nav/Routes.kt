package jp.tomoshibi.android.nav

// 23 个 route 完整列表 — 对应 Tomoshibi App.html SCREENS object (line 110-134)
// 用 sealed class 而不是 enum 因为部分 route 带参数（如 detail 屏需要 id）

sealed class Route(val path: String) {
    // ── auth flow ─────────────
    data object Splash : Route("splash")
    data object Onboarding : Route("onboarding")     // 内部 3 页用 page state 管理（不分 sub-route）
    data object Account : Route("account")           // 内部 4 step 用 step state 管理
    data object Welcome : Route("welcome")
    data object Login : Route("login")

    // ── core 5 tab ────────────
    data object Home : Route("home")
    data object Applications : Route("applications")
    data object Nfc : Route("nfc")
    data object Notifications : Route("notifications")
    data object MyPage : Route("mypage")

    // ── second-level (pushed from tab screens) ──
    // ApplyNew 接受 ?kind= query 参数（外出/外泊/帰省/帰国/早帰/修繕/学習/代理受取/来訪者/その他）
    // 默认 外泊（最常用）— 对齐 iOS 流程：list FAB → kind 选择 sheet → 该 kind 独立 form 标题
    data object ApplyNew : Route("applications/new?kind=外泊") {
        const val PATH = "applications/new?kind={kind}"
        const val ARG_KIND = "kind"
        fun withKind(k: String) = "applications/new?kind=$k"
    }
    data class ApplicationDetail(val id: String) : Route("applications/$id") {
        companion object {
            const val PATH = "applications/{id}"
            const val ARG_ID = "id"
        }
    }
    data class NotifDetail(val id: String) : Route("notifications/$id") {
        companion object {
            const val PATH = "notifications/{id}"
            const val ARG_ID = "id"
        }
    }
    data object Deduction : Route("deduction")
    data object RollCall : Route("rollcall")
    data object Settings : Route("settings")

    // ── community 7 屏 (从 Home 进入) ──
    data object Music : Route("music")
    data object Study : Route("study")
    data object LostFound : Route("lostfound")
    data object Schedule : Route("schedule")
    data object Feedback : Route("feedback")
    data object Bus : Route("bus")
    data object Delivery : Route("delivery")
}
