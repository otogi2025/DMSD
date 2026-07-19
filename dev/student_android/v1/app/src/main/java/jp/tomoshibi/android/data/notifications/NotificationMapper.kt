package jp.tomoshibi.android.data.notifications

import jp.tomoshibi.android.data.model.Notification
import jp.tomoshibi.android.data.network.StudentNotificationItem
import jp.tomoshibi.android.data.network.endpoints.FrontDeskItemOut
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale

/**
 * 通知中心三源聚合（对齐 iOS AppStore.allNotifications）：
 * push + studentNotifications feed + 包裹。
 * 纯函数，方便单测。
 */
object NotificationMapper {
    private val jst: ZoneId = ZoneId.of("Asia/Tokyo")
    private val timeFmt: DateTimeFormatter =
        DateTimeFormatter
            .ofPattern("M/d HH:mm")
            .withLocale(Locale.JAPAN)
            .withZone(jst)

    /** feed kind → 通知中心 UI 分类标签（对齐 iOS feedNotifType）。 */
    fun feedNotifType(kind: String): String =
        when (kind) {
            "bus" -> "バス"
            "event" -> "カレンダー"
            else -> "お知らせ" // announcement
        }

    /** ISO 时刻 → JST「M/d HH:mm」。 */
    fun notifTimeLabel(iso: String): String {
        val instant =
            runCatching { Instant.parse(iso) }.getOrNull()
                ?: runCatching { OffsetDateTime.parse(iso).toInstant() }.getOrNull()
                ?: return iso
        return timeFmt.format(instant)
    }

    /** 把后端 feed 映射成通知卡（id 用负数，与 push 正数 / 包裹大负数不相撞）。 */
    fun feedNotifications(items: List<StudentNotificationItem>): List<Notification> =
        items.mapIndexed { idx, n ->
            Notification(
                id = "-${idx + 1}",
                tag = feedNotifType(n.kind),
                title = n.title,
                body = n.body,
                ts = notifTimeLabel(n.createdAt),
                read = n.isRead,
                kind = n.kind,
                refId = n.refId,
            )
        }

    /**
     * 包裹 → 宅配通知卡。
     * 未読 = pending / notified；picked_up 等终态视为已読。
     */
    fun packageNotifications(packages: List<FrontDeskItemOut>): List<Notification> =
        packages.mapIndexed { idx, p ->
            Notification(
                id = "-${10_000_000 + idx}",
                tag = "宅配",
                title =
                    if (p.status == "picked_up") {
                        "荷物を受け取りました"
                    } else {
                        "荷物が届いています（${p.itemCount}件）"
                    },
                ts = notifTimeLabel(p.notifiedAt ?: p.createdAt),
                body = p.description,
                read = p.status != "pending" && p.status != "notified",
            )
        }

    /** 生产版三源合计（Android 暂无真实 push，push 列表可为空）。 */
    fun allNotifications(
        push: List<Notification>,
        feed: List<StudentNotificationItem>,
        packages: List<FrontDeskItemOut>,
    ): List<Notification> = push + feedNotifications(feed) + packageNotifications(packages)

    /**
     * 铃铛未読数（对齐 iOS unreadNotificationCount）：
     * feed 未加载时用后端 unreadCount；已加载后用列表自身未読条数 + push + 包裹。
     */
    fun unreadCount(
        push: List<Notification>,
        feed: List<StudentNotificationItem>,
        feedUnreadFallback: Int,
        packages: List<FrontDeskItemOut>,
    ): Int {
        val feedUnread =
            if (feed.isEmpty()) {
                feedUnreadFallback
            } else {
                feed.count { !it.isRead }
            }
        val packageUnread = packages.count { it.status == "pending" || it.status == "notified" }
        return push.count { !it.read } + feedUnread + packageUnread
    }
}

/** 通知中心 feed 三态（对齐 iOS notificationsState / ListLoadState）。 */
sealed interface NotificationsLoadState {
    data object Idle : NotificationsLoadState

    data object Loading : NotificationsLoadState

    data object Loaded : NotificationsLoadState

    data class Failed(
        val message: String,
    ) : NotificationsLoadState
}
