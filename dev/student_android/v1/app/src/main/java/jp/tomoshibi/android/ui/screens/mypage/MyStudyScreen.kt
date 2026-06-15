package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.StudyHistoryEntry
import jp.tomoshibi.android.data.model.StudyTap
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.theme.SuzuT

// 晩自習履歴（晩学習＝夜间学习的出席履歴）— 対齐 iOS MyStudyView（L2 子页）
//   入口 = 着陆页学習卡。按 MockData.DEFAULT_USER.isStudyTarget 切两种界面：
//   - false（当前假数据值）→ 居中「晩自習対象外です」空状态
//   - true → 月度统计卡 / 当月欠席届卡 / 出席打卡履历卡 / 说明盒 四块竖排
@Composable
fun MyStudyScreen(navController: NavHostController) {
    val t = SuzuT.current
    val isStudyTarget = MockData.DEFAULT_USER.isStudyTarget

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "晩自習履歴", level = 2, onLeft = { navController.popBackStack() })

            if (isStudyTarget) {
                StudyTargetBody()
            } else {
                NotStudyTargetNotice()
            }
        }
    }
}

// 非晚自习对象：居中大 emoji + 标题 + 两行说明
@Composable
private fun NotStudyTargetNotice() {
    val t = SuzuT.current
    Column(
        modifier = Modifier.fillMaxSize().padding(horizontal = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        Text("📚", style = TextStyle(fontSize = 44.sp))
        Spacer(Modifier.height(12.dp))
        Text(
            "晩自習対象外です",
            color = t.ink,
            style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold),
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            "あなたは現在、晩自習の対象ではありません。\n晩自習担当の先生が対象に指定すると、ここに出席状況が表示されます。",
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
            textAlign = TextAlign.Center,
        )
    }
}

// 一天的打卡分组
private data class DayGroup(
    val date: String,
    val items: List<StudyHistoryEntry>,
)

// 晚自习对象：四块竖排（月度统计 / 欠席届 / 履历 / 说明盒）
@Composable
private fun StudyTargetBody() {
    val history = MockData.DEFAULT_STUDY_HISTORY
    // 按日期分组（保序）
    val grouped =
        buildList {
            val map = LinkedHashMap<String, MutableList<StudyHistoryEntry>>()
            history.forEach { map.getOrPut(it.date) { mutableListOf() }.add(it) }
            map.forEach { (d, items) -> add(DayGroup(d, items)) }
        }
    // 月度统计：齐全且无遅刻=出席 / 齐全有遅刻=遅刻 / 缺一种=異常
    var present = 0
    var late = 0
    var abnormal = 0
    grouped.forEach { g ->
        val kinds = g.items.map { it.tapKind }.toSet()
        if (kinds.size == StudyTap.values().size) {
            if (g.items.any { it.note?.contains("遅刻") == true }) late++ else present++
        } else if (kinds.isNotEmpty()) {
            abnormal++
        }
    }
    val leaveCount = MockData.STUDY_LEAVE_COUNT

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 4.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        SummaryCard(present, late, abnormal)
        LeaveStatsCard(leaveCount)
        HistoryCard(grouped)
        HelpInfoBox()
        Spacer(Modifier.height(20.dp))
    }
}

// 月度 summary 卡：header +「対象」pill + 3 个 statBox
@Composable
private fun SummaryCard(
    present: Int,
    late: Int,
    abnormal: Int,
) {
    val t = SuzuT.current
    SuzuCard(padding = 18) {
        Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "今月の晩自習出席",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.2.sp),
                    modifier = Modifier.weight(1f),
                )
                Box(
                    modifier =
                        Modifier
                            .clip(RoundedCornerShape(999.dp))
                            .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.10f))
                            .padding(horizontal = 8.dp, vertical = 2.dp),
                ) {
                    Text(
                        "対象",
                        color = MaterialTheme.colorScheme.primary,
                        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
                    )
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatBox("出席", present, t.ok, Modifier.weight(1f))
                StatBox("遅刻", late, t.warn, Modifier.weight(1f))
                StatBox("異常", abnormal, t.danger, Modifier.weight(1f))
            }
        }
    }
}

@Composable
private fun StatBox(
    label: String,
    count: Int,
    color: Color,
    modifier: Modifier = Modifier,
) {
    val t = SuzuT.current
    Column(
        modifier =
            modifier
                .clip(RoundedCornerShape(12.dp))
                .background(t.pill)
                .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(label, color = t.inkSub, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold))
        Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(3.dp)) {
            Text(
                "$count",
                color = color,
                style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Monospace),
            )
            Text("回", color = t.inkMute, style = TextStyle(fontSize = 11.sp))
        }
    }
}

// 当月欠席届 卡：📝 + count（>3 红 + 超過 pill）
@Composable
private fun LeaveStatsCard(leaveCount: Int) {
    val t = SuzuT.current
    val over = leaveCount > 3
    SuzuCard(padding = 14) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Box(
                modifier = Modifier.size(40.dp).clip(CircleShape).background(t.warnBg),
                contentAlignment = Alignment.Center,
            ) {
                Text("📝", style = TextStyle(fontSize = 22.sp))
            }
            Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text("今月の晩自習欠席届", color = t.inkSub, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
                Row(verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(
                        "$leaveCount",
                        color = if (over) t.danger else t.ink,
                        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Black, fontFamily = FontFamily.Monospace),
                    )
                    Text("回", color = t.inkMute, style = TextStyle(fontSize = 12.sp))
                }
            }
            if (over) {
                Box(
                    modifier =
                        Modifier
                            .clip(RoundedCornerShape(999.dp))
                            .background(t.dangerBg)
                            .padding(horizontal = 8.dp, vertical = 3.dp),
                ) {
                    Text("超過", color = t.danger, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
                }
            }
        }
    }
}

// 「出席タップ履歴」卡：header + 按日分组 dayBlock
@Composable
private fun HistoryCard(grouped: List<DayGroup>) {
    val t = SuzuT.current
    SuzuCard(padding = 0) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp).padding(top = 14.dp, bottom = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    "出席タップ履歴",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.2.sp),
                    modifier = Modifier.weight(1f),
                )
                Text(
                    "${grouped.sumOf { it.items.size }} 件",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold, fontFamily = FontFamily.Monospace),
                )
            }
            if (grouped.isEmpty()) {
                Column(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 30.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(10.dp),
                ) {
                    Text("✨", style = TextStyle(fontSize = 40.sp))
                    Text("履歴はまだありません", color = t.inkMute, style = TextStyle(fontSize = 13.sp))
                }
            } else {
                grouped.forEachIndexed { idx, grp ->
                    if (idx > 0) Box(Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
                    DayBlock(grp)
                }
            }
        }
    }
}

@Composable
private fun DayBlock(grp: DayGroup) {
    val t = SuzuT.current
    val kinds = grp.items.map { it.tapKind }.toSet()
    val complete = kinds.size == StudyTap.values().size
    val hasLate = grp.items.any { it.note?.contains("遅刻") == true }
    Column(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 10.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(
                grp.date,
                color = t.inkSub,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold, fontFamily = FontFamily.Monospace),
            )
            when {
                complete && hasLate -> StatusPill("遅刻", t.warnDeep, t.warnBg)
                complete -> StatusPill("時間内", t.okDeep, t.okBg)
                else -> StatusPill("未完", t.danger, t.dangerBg)
            }
            Spacer(Modifier.weight(1f))
            Text(
                "${grp.items.size} / ${StudyTap.values().size}",
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
            )
        }
        Column(modifier = Modifier.padding(start = 4.dp)) {
            grp.items.forEachIndexed { i, e ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Text(
                        e.timeHM,
                        color = t.ink,
                        modifier = Modifier.width(50.dp),
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold, fontFamily = FontFamily.Monospace),
                    )
                    Text(
                        StudyTap.valueOf(e.tapKind).label,
                        color = t.ink,
                        style = TextStyle(fontSize = 13.sp),
                    )
                    Spacer(Modifier.weight(1f))
                    e.note?.let { StatusPill(it, t.warnDeep, t.warnBg) }
                }
                if (i < grp.items.size - 1) Box(Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
            }
        }
    }
}

@Composable
private fun StatusPill(
    text: String,
    fg: Color,
    bg: Color,
) {
    Box(
        modifier = Modifier.clip(RoundedCornerShape(999.dp)).background(bg).padding(horizontal = 7.dp, vertical = 2.dp),
    ) {
        Text(text, color = fg, style = TextStyle(fontSize = 10.5.sp, fontWeight = FontWeight.Bold))
    }
}

// 说明盒：ℹ NFC「1 日 2 回タップ」提示
@Composable
private fun HelpInfoBox() {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(primary.copy(alpha = 0.04f))
                .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(
            "ℹ 晩自習出席は NFC を 1 日 2 回タップ",
            color = primary,
            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
        )
        Text(
            "晩自習開始 (19:40) ／ 晩自習終了 (21:45)。2 回揃わない場合は異常扱いとなり、晩自習担当の先生が手動で判定します。",
            color = primary.copy(alpha = 0.85f),
            style = TextStyle(fontSize = 11.5.sp, lineHeight = 17.sp),
        )
    }
}
