package jp.tomoshibi.android.ui.icons

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.automirrored.outlined.Undo
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Circle
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.GppGood
import androidx.compose.material.icons.outlined.ArrowDownward
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material.icons.outlined.ArrowUpward
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Build
import androidx.compose.material.icons.outlined.CalendarMonth
import androidx.compose.material.icons.outlined.Campaign
import androidx.compose.material.icons.outlined.ChatBubbleOutline
import androidx.compose.material.icons.outlined.Check
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.ContactPage
import androidx.compose.material.icons.outlined.DarkMode
import androidx.compose.material.icons.outlined.Description
import androidx.compose.material.icons.outlined.DirectionsBus
import androidx.compose.material.icons.outlined.Edit
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material.icons.outlined.Flag
import androidx.compose.material.icons.outlined.Flight
import androidx.compose.material.icons.outlined.Group
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material.icons.outlined.Inventory
import androidx.compose.material.icons.outlined.Inventory2
import androidx.compose.material.icons.outlined.KeyboardArrowDown
import androidx.compose.material.icons.outlined.KeyboardArrowLeft
import androidx.compose.material.icons.outlined.KeyboardArrowRight
import androidx.compose.material.icons.outlined.LibraryBooks
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Logout
import androidx.compose.material.icons.outlined.Menu
import androidx.compose.material.icons.outlined.MenuBook
import androidx.compose.material.icons.outlined.Mood
import androidx.compose.material.icons.outlined.MusicNote
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Phone
import androidx.compose.material.icons.outlined.PhoneAndroid
import androidx.compose.material.icons.outlined.PhotoCamera
import androidx.compose.material.icons.outlined.Public
import androidx.compose.material.icons.outlined.Scale
import androidx.compose.material.icons.outlined.Schedule
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.ShowChart
import androidx.compose.material.icons.outlined.Warning
import androidx.compose.material.icons.outlined.Wifi
import androidx.compose.ui.graphics.vector.ImageVector

// Suzu icon set — 对齐 iOS Foundation/Components/Icons/Ic.swift
// Material Icons 近似映射；UI 还原度后续可换自定义 VectorDrawable

object SuzuIcons {
    // ── nav bar 5 icon ────────────────────
    val Home: ImageVector = Icons.Outlined.Home
    val Doc: ImageVector = Icons.Outlined.Description // 申请类比 doc
    val Nfc: ImageVector = Icons.Outlined.Wifi // NFC 没有现成 — 用 wifi 占位（视觉接近"信号"）
    val Bell: ImageVector = Icons.Outlined.Notifications
    val User: ImageVector = Icons.Outlined.Person

    // ── 业务屏常用 ────────────────────
    val House: ImageVector = Icons.Outlined.Home
    val Plane: ImageVector = Icons.Outlined.Flight
    val Wrench: ImageVector = Icons.Outlined.Build
    val Box: ImageVector = Icons.Outlined.Inventory2
    val People: ImageVector = Icons.Outlined.Group
    val Chat: ImageVector = Icons.Outlined.ChatBubbleOutline
    val Book: ImageVector = Icons.Outlined.MenuBook
    val Cal: ImageVector = Icons.Outlined.CalendarMonth
    val CalClock: ImageVector = Icons.Outlined.Schedule
    val Bus: ImageVector = Icons.Outlined.DirectionsBus
    val Music: ImageVector = Icons.Outlined.MusicNote
    val Edit: ImageVector = Icons.Outlined.Edit

    // 取消 / 撤回操作用的「✕」图标（出寮届撤回按钮）— Material Outlined.Close 最贴近 iOS xmark
    val Close: ImageVector = Icons.Outlined.Close
    val Check: ImageVector = Icons.Outlined.Check
    val CheckCirc: ImageVector = Icons.Outlined.CheckCircle
    val Plus: ImageVector = Icons.Filled.Add
    val ChevR: ImageVector = Icons.Outlined.KeyboardArrowRight
    val ChevL: ImageVector = Icons.Outlined.KeyboardArrowLeft
    val ArrowR: ImageVector = Icons.Outlined.ArrowForward
    val Sparkle: ImageVector = Icons.Outlined.AutoAwesome
    val Graph: ImageVector = Icons.Outlined.ShowChart
    val Logout: ImageVector = Icons.Outlined.Logout
    val Menu: ImageVector = Icons.Outlined.Menu
    val Scale: ImageVector = Icons.Outlined.Scale
    val Face: ImageVector = Icons.Outlined.Mood
    val Books: ImageVector = Icons.Outlined.LibraryBooks
    val Info: ImageVector = Icons.Outlined.Info
    val Warn: ImageVector = Icons.Outlined.Warning
    val PhoneNfc: ImageVector = Icons.Outlined.PhoneAndroid
    val Sparkles: ImageVector = Icons.Outlined.AutoAwesome
    val Pkg: ImageVector = Icons.Outlined.Inventory
    val Envelope: ImageVector = Icons.Outlined.Email

    /** 公告卡 megaphone — Material Campaign 近似 iOS megaphone.fill */
    val Megaphone: ImageVector = Icons.Outlined.Campaign

    /** 学年更新横幅 — 近似 iOS person.text.rectangle */
    val ContactCard: ImageVector = Icons.Outlined.ContactPage

    /** 寮監に連絡 — phone.fill */
    val Phone: ImageVector = Icons.Outlined.Phone

    // Shield = iOS shield.checkered（带勾的盾）— Material Icons 用 Filled.GppGood (盾 + ✓) 最接近
    val Shield: ImageVector = Icons.Filled.GppGood
    val Person: ImageVector = Icons.Outlined.Person
    val Globe: ImageVector = Icons.Outlined.Public

    // ── G9：对齐 iOS Ic.swift 补齐的图标 ────────────────────

    /** Ic.chevD — chevron.down */
    val ChevD: ImageVector = Icons.Outlined.KeyboardArrowDown

    /** Ic.dot — circle.fill */
    val Dot: ImageVector = Icons.Filled.Circle

    /** Ic.search — magnifyingglass */
    val Search: ImageVector = Icons.Outlined.Search

    /** Ic.camera — camera */
    val Camera: ImageVector = Icons.Outlined.PhotoCamera

    /** Ic.heart(filled:false) — heart */
    val Heart: ImageVector = Icons.Outlined.FavoriteBorder

    /** Ic.heart(filled:true) — heart.fill */
    val HeartFilled: ImageVector = Icons.Filled.Favorite

    /** Ic.flag — flag */
    val Flag: ImageVector = Icons.Outlined.Flag

    /** Ic.up — arrow.up */
    val Up: ImageVector = Icons.Outlined.ArrowUpward

    /** Ic.down — arrow.down */
    val Down: ImageVector = Icons.Outlined.ArrowDownward

    /** Ic.lock — lock */
    val Lock: ImageVector = Icons.Outlined.Lock

    /** Ic.myMoon — moon.stars */
    val MyMoon: ImageVector = Icons.Outlined.DarkMode

    /** 面包屑行用（对齐 iOS arrow.uturn.backward） */
    val Undo: ImageVector = Icons.AutoMirrored.Outlined.Undo

    /** 返回箭头（AutoMirrored，RTL 友好） */
    val ArrowBack: ImageVector = Icons.AutoMirrored.Outlined.ArrowBack
}
