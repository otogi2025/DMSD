package jp.tomoshibi.android.nav

// 22 个 route 完整列表 — 对应 Tomoshibi App.html SCREENS object (line 110-134)
// 用 sealed class 而不是 enum 因为部分 route 带参数（如 detail 屏需要 id）

sealed class Route(
    val path: String,
) {
    // ── auth flow ─────────────
    data object Splash : Route("splash")

    data object Onboarding : Route("onboarding") // 内部 3 页用 page state 管理（不分 sub-route）

    data object Account : Route("account") // 内部 4 step 用 step state 管理

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

    data class ApplicationDetail(
        val id: String,
    ) : Route("applications/$id") {
        companion object {
            const val PATH = "applications/{id}"
            const val ARG_ID = "id"
        }
    }

    data class NotifDetail(
        val id: String,
    ) : Route("notifications/$id") {
        companion object {
            const val PATH = "notifications/{id}"
            const val ARG_ID = "id"
        }
    }

    data object Deduction : Route("deduction")

    data object RollCall : Route("rollcall")

    // ── 个人页（「マイページ」）子页 (从 MyPage landing 进入) ──
    data object MyInfo : Route("my/info")

    data object MyInfoEdit : Route("my/info/edit")

    data object MyRollcall : Route("my/rollcall")

    data class MyRollcallDetail(
        val id: String,
    ) : Route("my/rollcall/$id") {
        companion object {
            const val PATH = "my/rollcall/{id}"
            const val ARG_ID = "id"
        }
    }

    data object MyPoints : Route("my/points")

    data object MyPointsChart : Route("my/points/chart")

    data object MyDiscipline : Route("my/discipline")

    data object MyHealth : Route("my/health")

    data object MyPackages : Route("my/packages")

    data object MyStudy : Route("my/study")

    data object MySettings : Route("my/settings")

    data object MyAbout : Route("my/about")

    // ── 杂项 / 公告 / 认证补全 ──
    data object BusList : Route("bus/list") // 特別運行便一覧

    data class PackageDetail(
        val id: Int,
    ) : Route("packages/$id") {
        companion object {
            const val PATH = "packages/{id}"
            const val ARG_ID = "id"
        }
    }

    data object Announcements : Route("announcements") // お知らせ一覧

    data class Announcement(
        val id: String,
    ) : Route("announcements/$id") {
        companion object {
            const val PATH = "announcements/{id}"
            const val ARG_ID = "id"
        }
    }

    data object Lockout : Route("lockout") // 登录失败锁定页

    data object PwReset : Route("pwreset") // 找回密码说明

    data object MusicNew : Route("music/new") // 点歌投稿屏「曲を投稿」

    data class MusicDetail(
        val id: Int,
    ) : Route("music/$id") {
        companion object {
            const val PATH = "music/{id}"
            const val ARG_ID = "id"
        }
    }

    data class EventDetail(
        val id: Int,
    ) : Route("events/$id") {
        companion object {
            const val PATH = "events/{id}"
            const val ARG_ID = "id"
        }
    }

    // ── community 5 屏 (从 Home 进入) ──
    data object Music : Route("music")

    data object LostFound : Route("lostfound")

    data object Schedule : Route("schedule")

    data object Bus : Route("bus")

    data object Delivery : Route("delivery")

    // ── 申請履歴 family（老師38条#5；前缀 stayhistory 防撞 applications/{id}）──
    data object StayList : Route("stayhistory") // 申請履歴一覧

    data class StayDetail(
        val id: String,
    ) : Route("stayhistory/$id") {
        companion object {
            const val PATH = "stayhistory/{id}"
            const val ARG_ID = "id"
        }
    }

    data class StayEdit(
        val id: String,
    ) : Route("stayhistory/$id/edit") {
        companion object {
            const val PATH = "stayhistory/{id}/edit"
            const val ARG_ID = "id"
        }
    }

    // ── 4 类型申請一覧（前缀 applylist 唯一）──
    data object DormEventList : Route("applylist/events") // 行事企画一覧

    data object StudyOnlineList : Route("applylist/online") // 在线学习申請一覧

    data object FridgeList : Route("applylist/fridge") // 冷蔵庫購入一覧

    data object ItemList : Route("applylist/items") // 物品所持一覧

    // ── 遺失物投稿/详情 + 本周活动列表 ──
    data object LostNew : Route("lostnew") // 遺失物投稿屏

    data class LostDetail(
        val id: String,
    ) : Route("lostdetail/$id") {
        companion object {
            const val PATH = "lostdetail/{id}"
            const val ARG_ID = "id"
        }
    }

    data object Events : Route("events") // 本周活动列表（对齐 iOS homeEvents）
}
