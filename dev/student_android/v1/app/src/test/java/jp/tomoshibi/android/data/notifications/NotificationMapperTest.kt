package jp.tomoshibi.android.data.notifications

import jp.tomoshibi.android.data.network.StudentNotificationItem
import jp.tomoshibi.android.data.network.endpoints.FrontDeskItemOut
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class NotificationMapperTest {
    @Test
    fun `feed kind 映射到 UI 标签`() {
        assertEquals("お知らせ", NotificationMapper.feedNotifType("announcement"))
        assertEquals("バス", NotificationMapper.feedNotifType("bus"))
        assertEquals("カレンダー", NotificationMapper.feedNotifType("event"))
    }

    @Test
    fun `feed 映射带 kind 与 refId 且未読取反 isRead`() {
        val items =
            listOf(
                StudentNotificationItem(
                    kind = "announcement",
                    refId = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                    title = "テスト",
                    body = "本文",
                    createdAt = "2026-07-19T12:00:00Z",
                    isRead = false,
                ),
            )
        val cards = NotificationMapper.feedNotifications(items)
        assertEquals(1, cards.size)
        assertEquals("お知らせ", cards[0].tag)
        assertEquals("announcement", cards[0].kind)
        assertEquals("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", cards[0].refId)
        assertFalse(cards[0].read)
    }

    @Test
    fun `包裹 pending 未読 picked_up 已読`() {
        val pkgs =
            listOf(
                FrontDeskItemOut(
                    id = "1",
                    kind = "parcel",
                    description = "Amazon",
                    itemCount = 2,
                    status = "pending",
                    createdAt = "2026-07-19T10:00:00Z",
                ),
                FrontDeskItemOut(
                    id = "2",
                    kind = "parcel",
                    description = "佐川",
                    itemCount = 1,
                    status = "picked_up",
                    createdAt = "2026-07-18T10:00:00Z",
                ),
            )
        val cards = NotificationMapper.packageNotifications(pkgs)
        assertEquals(2, cards.size)
        assertEquals("宅配", cards[0].tag)
        assertFalse(cards[0].read)
        assertTrue(cards[1].read)
        assertEquals("荷物を受け取りました", cards[1].title)
    }

    @Test
    fun `未読数 feed 空时用 fallback 已加载用列表`() {
        val pkgs =
            listOf(
                FrontDeskItemOut(
                    id = "1",
                    kind = "parcel",
                    description = "x",
                    status = "notified",
                    createdAt = "2026-07-19T10:00:00Z",
                ),
            )
        // feed 未加载：用 fallback=3 + 包裹 1
        assertEquals(
            4,
            NotificationMapper.unreadCount(
                push = emptyList(),
                feed = emptyList(),
                feedUnreadFallback = 3,
                packages = pkgs,
            ),
        )
        // feed 已加载：列表未読 1（忽略 fallback）+ 包裹 1
        val feed =
            listOf(
                StudentNotificationItem(
                    kind = "bus",
                    refId = "id-1",
                    title = "a",
                    body = "b",
                    createdAt = "2026-07-19T12:00:00Z",
                    isRead = false,
                ),
                StudentNotificationItem(
                    kind = "bus",
                    refId = "id-2",
                    title = "c",
                    body = "d",
                    createdAt = "2026-07-19T12:00:00Z",
                    isRead = true,
                ),
            )
        assertEquals(
            2,
            NotificationMapper.unreadCount(
                push = emptyList(),
                feed = feed,
                feedUnreadFallback = 99,
                packages = pkgs,
            ),
        )
    }
}
