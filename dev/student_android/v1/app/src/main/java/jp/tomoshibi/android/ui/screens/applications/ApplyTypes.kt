package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AcUnit
import androidx.compose.material.icons.outlined.Cottage
import androidx.compose.material.icons.outlined.Laptop
import androidx.compose.ui.graphics.vector.ImageVector
import jp.tomoshibi.android.ui.icons.SuzuIcons

// 申请类型元数据 — 12 种，对齐 iOS APPLY_TYPES（key 英文 / 名日语 / 副标题日语 / 图标）
internal data class ApplyType(
    val key: String,
    val name: String,
    val sub: String,
    val icon: ImageVector,
)

internal val APPLY_TYPES =
    listOf(
        ApplyType("outing", "外出", "当日帰寮の外出", SuzuIcons.Cal),
        ApplyType("stay", "外泊", "寮外での宿泊", SuzuIcons.House),
        ApplyType("holiday", "帰省", "実家帰省・長期休暇", Icons.Outlined.Cottage),
        ApplyType("returncountry", "帰国", "一時帰国（航空機利用）", SuzuIcons.Plane),
        ApplyType("repair", "修繕", "部屋・設備の修繕依頼", SuzuIcons.Wrench),
        ApplyType("parcel", "代理受取", "不在時の荷物代理受取", SuzuIcons.Box),
        ApplyType("guest", "来訪者", "家族・友人の来訪", SuzuIcons.People),
        ApplyType("studyAbsence", "夜学習欠席", "夜学習の欠席届（前半・後半・両方）", SuzuIcons.Book),
        ApplyType("studyOnline", "オンライン学習", "自室でのオンライン学習", Icons.Outlined.Laptop),
        ApplyType("event", "行事企画", "寮内イベントの企画申請", SuzuIcons.Sparkle),
        ApplyType("fridge", "冷蔵庫購入", "指定冷蔵庫の購入届", Icons.Outlined.AcUnit),
        ApplyType("item", "物品所持", "持込物品の許可願", SuzuIcons.Box),
    )

// 列表卡按类型日语名查图标（匹配不到取第 0 个 outing，对齐 iOS applyType 兜底）
internal fun iconForKind(kind: String): ImageVector = APPLY_TYPES.firstOrNull { it.name == kind }?.icon ?: SuzuIcons.Cal
