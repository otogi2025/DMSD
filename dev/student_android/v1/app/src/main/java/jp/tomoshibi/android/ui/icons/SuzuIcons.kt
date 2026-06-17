package jp.tomoshibi.android.ui.icons

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.*
import androidx.compose.ui.graphics.vector.ImageVector

// Suzu icon set — v1.0 阶段先用 Material Icons fallback 占位
// 对应 React tokens.jsx 的 Ic 组件，但不像 React SVG path 能直接 inline，
// Compose ImageVector DSL 写起来啰嗦 + path 数据来自 React 的 SVG 字符串需要解析。
//
// P1+ 切换方案：
// (A) 把 React 32 个 SVG path 转 res/drawable/ic_*.xml VectorDrawable，用 painterResource(R.drawable.ic_xxx)
// (B) 或者每个 icon 写一个 lazy ImageVector.Builder { path { moveTo... } } — 更"Compose native" 但代码量大
//
// 现在先用 Material Icons 让 nav 跑起来 — UI 还原度后续单独 PR 提升

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

    // Shield = iOS shield.checkered（带勾的盾）— Material Icons 用 Filled.GppGood (盾 + ✓) 最接近
    val Shield: ImageVector = Icons.Filled.GppGood
    val Person: ImageVector = Icons.Outlined.Person
}
