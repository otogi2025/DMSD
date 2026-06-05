package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.StayApplication
import jp.tomoshibi.android.data.model.StayDecision
import jp.tomoshibi.android.data.model.StayKind
import jp.tomoshibi.android.data.model.StayStatus
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 申請履歴一覧（提出后给提交者展示承認状态，L2 子页）— 対齐 iOS StayListView（StayListStubs.swift 392-675）
//   PageHeader「申請履歴」level 2 + 顶部状态过滤标签 + 竖排卡列表，逐条 MockData.DEFAULT_STAY_APPLICATIONS
//   每条 StayRow：種別 icon +「{種別}届」+ 状态 Pill + summary + 承認 chain 进度点列 + 出寮日
//   静态列表（后端 GET /applications/mine 未接，先用 MockData 兜底）

// 顶部过滤标签 — 対齐 iOS tabs（4 个代表标签，按状态组匹配）
//   每个标签代表的 StayStatus name 集合：すべて = 全部 / 審査中 = PENDING / 承認済 = APPROVED+APPROVED_PARTIAL / 差戻 = REJECTED+RETURNED
private data class StayFilterTab(
    val label: String, // 标签 UI 文案（「すべて」「審査中」等）
    val statuses: Set<String>?, // null = すべて（不过滤）；否则该标签收的 StayStatus.name 集合
)

private val STAY_FILTER_TABS: List<StayFilterTab> =
    listOf(
        StayFilterTab("すべて", null),
        StayFilterTab("審査中", setOf(StayStatus.PENDING.name)),
        // IX-019:「承認済」标签同时收 承認済 和 一部承認
        StayFilterTab("承認済", setOf(StayStatus.APPROVED.name, StayStatus.APPROVED_PARTIAL.name)),
        // IX-019:「差戻」标签同时收 差戻 和 要修正 —— 被退回要修正的申请才不会消失
        StayFilterTab("差戻", setOf(StayStatus.REJECTED.name, StayStatus.RETURNED.name)),
    )

@Composable
fun StayListScreen(navController: NavHostController) {
    // 选中的过滤标签下标（默认 0 =「すべて」）
    var filterIndex by remember { mutableStateOf(0) }

    // 出寮日降序排列（最新在前），再按选中标签过滤
    val items =
        remember(filterIndex) {
            val sorted = MockData.DEFAULT_STAY_APPLICATIONS.sortedByDescending { it.leaveDate }
            val tab = STAY_FILTER_TABS[filterIndex]
            if (tab.statuses == null) sorted else sorted.filter { it.status in tab.statuses }
        }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "申請履歴",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
            ) {
                FilterTabs(
                    selectedIndex = filterIndex,
                    onSelect = { filterIndex = it },
                )
                Spacer(Modifier.height(14.dp))

                if (items.isEmpty()) {
                    EmptyState(
                        icon = SuzuIcons.Box,
                        title = "申請はありません",
                        // 「すべて」无申請时引导提交，过滤后无结果时提示条件不匹配
                        message =
                            if (STAY_FILTER_TABS[filterIndex].statuses == null) {
                                "外泊・帰省・帰国届を提出すると、ここに表示されます。"
                            } else {
                                "条件に一致する申請はありません。"
                            },
                        modifier = Modifier.fillMaxWidth(),
                    )
                } else {
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        items.forEach { item ->
                            StayRow(
                                item = item,
                                onClick = { navController.navigate(Route.StayDetail(item.id).path) },
                            )
                        }
                    }
                }
                Spacer(Modifier.height(28.dp))
            }
        }
    }
}

// 顶部状态过滤标签条（横向滚动 4 个胶囊；选中 = 白字+primary 底 / 未选 = primary 字+pill 底）
@Composable
private fun FilterTabs(
    selectedIndex: Int,
    onSelect: (Int) -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    Row(
        modifier = Modifier.horizontalScroll(rememberScrollState()),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        STAY_FILTER_TABS.forEachIndexed { index, tab ->
            val selected = index == selectedIndex
            Box(
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(percent = 50))
                        .background(if (selected) cs.primary else t.pill)
                        .clickable { onSelect(index) }
                        .padding(horizontal = 14.dp, vertical = 7.dp),
            ) {
                Text(
                    tab.label,
                    color = if (selected) Color.White else cs.primary,
                    style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold),
                )
            }
        }
    }
}

// 一覧 row — 対齐 iOS StayRow
//   1 段目：種別 icon（圆角 pill 底）+「{種別}届」+ 状态 Pill + summary（1 行）+ 右 chevron
//   2 段目：承認 chain 进度点列（链非空时显示）
//   3 段目：上分隔细线 + 日历图标 + 出寮日（等宽字体）
@Composable
private fun StayRow(
    item: StayApplication,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    SuzuCard(
        modifier = Modifier.clickable(onClick = onClick),
        padding = 14,
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            // 1 段目
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier =
                        Modifier
                            .size(40.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(t.pill),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        imageVector = kindIcon(item.kind),
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(17.dp),
                    )
                }
                Column(
                    modifier = Modifier.weight(1f),
                    verticalArrangement = Arrangement.spacedBy(3.dp),
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            "${item.kind}届",
                            color = t.ink,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                        )
                        // 状态徽章：StayStatus.label 已是日语 UI 文案，色调按映射表
                        val status = StayStatus.valueOf(item.status)
                        Pill(text = status.label, tone = statusTone(status))
                    }
                    Text(
                        item.summary,
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp),
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                    )
                }
                Icon(
                    imageVector = SuzuIcons.ChevR,
                    contentDescription = null,
                    tint = t.inkMute,
                    modifier = Modifier.size(14.dp),
                )
            }

            // 2 段目：承認 chain 进度点列
            if (item.chain.isNotEmpty()) {
                ChainDots(item)
            }

            // 3 段目：上分隔细线 + 出寮日
            Column {
                Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
                Spacer(Modifier.height(4.dp))
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Icon(
                        imageVector = SuzuIcons.Cal,
                        contentDescription = null,
                        tint = t.inkMute,
                        modifier = Modifier.size(11.dp),
                    )
                    Text(
                        item.leaveDate,
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                    )
                }
            }
        }
    }
}

// 承認 chain 进度点列 — 対齐 iOS chainDots
//   底灰横线 + 上层进度线（按 approvedCount/total 占比往右推进；任一 rejected → 进度线变红）
//   节点等距分布：approved = 勾 / rejected = 叉 / pending = 中央小白点
@Composable
private fun ChainDots(item: StayApplication) {
    val t = SuzuT.current
    val total = item.chain.size
    val approvedCount = item.chain.count { it.decision == StayDecision.APPROVED.name }
    val hasRejected = item.chain.any { it.decision == StayDecision.REJECTED.name }
    val progressFrac = if (total > 0) approvedCount.toFloat() / total.toFloat() else 0f
    val dotSize = 12.dp

    // 用 onSizeChanged 量出可用宽度，进度线长 = 宽 × 占比（対齐 iOS GeometryReader）
    var trackWidthPx by remember { mutableStateOf(0) }
    val density = androidx.compose.ui.platform.LocalDensity.current

    Box(
        modifier = Modifier.fillMaxWidth().height(dotSize),
        contentAlignment = Alignment.CenterStart,
    ) {
        // 横线层（左右各留半个点的边距，让线对齐节点圆心）
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = dotSize / 2)
                    .onSizeChanged { trackWidthPx = it.width },
            contentAlignment = Alignment.CenterStart,
        ) {
            // 底灰线
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(2.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(t.hair),
            )
            // 上层进度线（有 rejected 变红，否则绿）
            val progressWidthDp = with(density) { (trackWidthPx * progressFrac).toDp() }
            Box(
                modifier =
                    Modifier
                        .width(progressWidthDp)
                        .height(2.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(if (hasRejected) t.danger else t.ok),
            )
        }

        // 节点层（HStack + Spacer 等距分布）
        Row(modifier = Modifier.fillMaxWidth()) {
            item.chain.forEachIndexed { i, step ->
                ChainDot(step.decision)
                if (i < total - 1) {
                    Spacer(Modifier.weight(1f))
                }
            }
        }
    }
}

// 单个承認节点 — approved = 实心绿+白勾 / rejected = 实心红+白叉 / pending = inkFaint 圆+中央小白点
@Composable
private fun ChainDot(decision: String) {
    val t = SuzuT.current
    val fill =
        when (decision) {
            StayDecision.APPROVED.name -> t.ok
            StayDecision.REJECTED.name -> t.danger
            else -> t.inkFaint // PENDING
        }
    Box(
        modifier =
            Modifier
                .size(12.dp)
                .clip(RoundedCornerShape(percent = 50))
                .background(fill),
        contentAlignment = Alignment.Center,
    ) {
        when (decision) {
            StayDecision.APPROVED.name -> {
                Icon(
                    imageVector = SuzuIcons.Check,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(8.dp),
                )
            }

            StayDecision.REJECTED.name -> {
                Text(
                    "✕",
                    color = Color.White,
                    style = TextStyle(fontSize = 7.sp, fontWeight = FontWeight.Black),
                )
            }

            else -> {
                // PENDING：中央 4dp 小白点
                Box(
                    modifier =
                        Modifier
                            .size(4.dp)
                            .clip(RoundedCornerShape(percent = 50))
                            .background(Color.White),
                )
            }
        }
    }
}

// 状态 → Pill 色调映射（StayStatus）
//   下書き = 灰 / 審査中・一部承認 = 橙 / 承認済 = 绿 / 差戻・要修正 = 红 / 取消済 = 灰
private fun statusTone(status: StayStatus): PillTone =
    when (status) {
        StayStatus.DRAFT -> PillTone.Neutral
        StayStatus.PENDING -> PillTone.Warn
        StayStatus.APPROVED_PARTIAL -> PillTone.Warn
        StayStatus.APPROVED -> PillTone.Ok
        StayStatus.REJECTED -> PillTone.Danger
        StayStatus.RETURNED -> PillTone.Danger
        StayStatus.WITHDRAWN -> PillTone.Neutral
    }

// 種別 → 图标（kind 是 StayKind.label 日语文案，按文案反查图标）
//   「外泊」= 房子 /「帰省」= 房子 /「帰国」= 飞机 /「その他」= 文档
private fun kindIcon(kindLabel: String) =
    when (kindLabel) {
        StayKind.STAY.label -> SuzuIcons.House
        StayKind.HOLIDAY.label -> SuzuIcons.House
        StayKind.RETURN.label -> SuzuIcons.Plane
        else -> SuzuIcons.Doc // その他
    }
