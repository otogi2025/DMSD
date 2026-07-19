package jp.tomoshibi.android.nav

// 22 个 route 完整列表 — 对应 Tomoshibi App.html SCREENS object (line 110-134)
// 用 sealed class 而不是 enum 因为部分 route 带参数（如 detail 屏需要 id）

sealed class Route(
    val path: String,
) {
    // ── auth flow ─────────────
    data object Splash : Route("splash")

    data object Onboarding : Route("onboarding") // 内部 4 页用 page state 管理（不分 sub-route）

    data object Account : Route("account") // 内部 4 step 用 step state 管理

    data object Welcome : Route("welcome")

    data object Login : Route("login")

    // ── core 5 tab ────────────
    data object Home : Route("home")

    data object Applications : Route("applications")

    data object Notifications : Route("notifications")

    data object MyPage : Route("mypage")

    // ── second-level (pushed from tab screens) ──
    // ApplyNewSelect = 新規申請种类全屏选单（对齐 iOS ApplyNewView）；选完再进 ApplyNew?kind=
    data object ApplyNewSelect : Route("applications/select")

    // ApplyNew 接受 ?kind= query 参数（外出/外泊/帰省/帰国/修繕/夜学習欠席/代理受取/来訪者/…）
    // 默认 外泊（最常用）— 对齐 iOS：list FAB → 种类全屏页 → 该 kind 独立 form
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

    // 兼容旧 path「deduction」→ 现复用 MyPointsScreen（对齐 iOS .myPoints）
    data object Deduction : Route("deduction")

    // ── 个人页（「マイページ」）子页 (从 MyPage landing 进入) ──
    data object MyInfo : Route("my/info")

    data object MyInfoEdit : Route("my/info/edit")

    data object MyRollcall : Route("my/rollcall")

    // id 可空：对齐 iOS myRollcallDetail(entryId: String?)；导航时 null → 省略段用 "_"
    data class MyRollcallDetail(
        val id: String?,
    ) : Route("my/rollcall/${id ?: "_"}") {
        companion object {
            const val PATH = "my/rollcall/{id}"
            const val ARG_ID = "id"

            /** Nav 参数 → 可空 id（"_" / 空串视为 null） */
            fun parseId(raw: String?): String? = raw?.takeIf { it.isNotEmpty() && it != "_" }
        }
    }

    data object MyPoints : Route("my/points")

    data object MyPointsChart : Route("my/points/chart")

    data object MyDiscipline : Route("my/discipline")

    data object MyHealth : Route("my/health")

    data object MyClean : Route("my/clean")

    data object MyPackages : Route("my/packages")

    data object MyStudy : Route("my/study")

    data object MySettings : Route("my/settings")

    data object MyAbout : Route("my/about")

    // ── 杂项 / 公告 / 认证补全 ──
    data object BusList : Route("bus/list") // 特別運行便一覧

    // id 用 String：对齐 iOS homePackageDetail(id: String) + 后端 FrontDeskItemOut.id（UUID）
    data class PackageDetail(
        val id: String,
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

    data object PwReset : Route("pwreset") // 找回密码说明（登录页无入口，屏体保留备用）

    data object MusicNew : Route("music/new") // 点歌投稿屏「曲を投稿」

    // id 用 String：对齐 iOS homeMusicDetail(id: String) + 后端 SongRequestOut.id
    data class MusicDetail(
        val id: String,
    ) : Route("music/$id") {
        companion object {
            const val PATH = "music/{id}"
            const val ARG_ID = "id"
        }
    }

    // ── community（从 Home 进入）──
    data object Music : Route("music")

    data object LostFound : Route("lostfound")

    data object Schedule : Route("schedule")

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

    // 行事企画差戻再提出（可编辑表单，对齐 iOS .dormEventResubmit(id:)）
    data class DormEventResubmit(
        val id: String,
    ) : Route("apply/event/resubmit/$id") {
        companion object {
            const val PATH = "apply/event/resubmit/{id}"
            const val ARG_ID = "id"
        }
    }

    data object StudyOnlineList : Route("applylist/online") // 在线学习申請一覧

    data object FridgeList : Route("applylist/fridge") // 冷蔵庫購入一覧

    data object ItemList : Route("applylist/items") // 物品所持一覧

    // ── 遺失物投稿/详情 ──
    data object LostNew : Route("lostnew") // 遺失物投稿屏

    data class LostDetail(
        val id: String,
    ) : Route("lostdetail/$id") {
        companion object {
            const val PATH = "lostdetail/{id}"
            const val ARG_ID = "id"
        }
    }
}

/** 面包屑显示名 — 对齐 iOS Route.displayName（按 path 前缀匹配） */
fun routeDisplayName(route: String): String {
    val base = route.substringBefore("?").substringBefore("/{")
    // 去掉动态段后的具体 id，取前两段做匹配
    val parts = base.split("/").filter { it.isNotEmpty() }
    val key = parts.take(2).joinToString("/")
    return when {
        base == "home" || parts.firstOrNull() == "home" && parts.size == 1 -> {
            "ホーム"
        }

        key == "applications" && parts.size == 1 -> {
            "申し込み"
        }

        key.startsWith("applications") -> {
            "詳細"
        }

        key == "mypage" -> {
            "マイページ"
        }

        key == "my/info" -> {
            if (parts.getOrNull(2) == "edit") "個人情報編集" else "個人情報"
        }

        key == "my/rollcall" -> {
            if (parts.size > 2) "詳細" else "点呼履歴"
        }

        key == "my/points" -> {
            if (parts.getOrNull(2) == "chart") "グラフ" else "減点明細"
        }

        key == "my/discipline" -> {
            "処分履歴"
        }

        key == "my/health" -> {
            "体調報告履歴"
        }

        key == "my/clean" -> {
            "罰則清掃履歴"
        }

        key == "my/packages" -> {
            "宅配履歴"
        }

        key == "my/study" -> {
            "夜学習履歴"
        }

        key == "my/settings" -> {
            "設定"
        }

        key == "my/about" -> {
            "Tomoshibi について"
        }

        key == "announcements" -> {
            if (parts.size > 1) "お知らせ詳細" else "お知らせ"
        }

        key == "notifications" -> {
            if (parts.size > 1) "詳細" else "通知"
        }

        key == "music" -> {
            when {
                parts.getOrNull(1) == "new" -> "投稿"
                parts.size > 1 -> "詳細"
                else -> "リクエスト曲"
            }
        }

        key == "lostfound" || key.startsWith("lost") -> {
            when {
                base.contains("new") -> "投稿"
                base.contains("detail") || parts.size > 1 -> "詳細"
                else -> "遺失物"
            }
        }

        key == "packages" -> {
            "宅配詳細"
        }

        key == "schedule" -> {
            "行事予定"
        }

        key == "bus" || key == "bus/list" -> {
            "特別運行便"
        }

        key == "stayhistory" -> {
            when {
                base.endsWith("/edit") -> "変更届"
                parts.size > 1 -> "申請詳細"
                else -> "申請履歴"
            }
        }

        key == "applylist/events" -> {
            "行事企画一覧"
        }

        key == "applylist/online" -> {
            "オンライン学習申請一覧"
        }

        key == "applylist/fridge" -> {
            "冷蔵庫購入届一覧"
        }

        key == "applylist/items" -> {
            "物品所持許可願一覧"
        }

        key == "delivery" -> {
            "宅配"
        }

        else -> {
            parts.lastOrNull() ?: route
        }
    }
}
