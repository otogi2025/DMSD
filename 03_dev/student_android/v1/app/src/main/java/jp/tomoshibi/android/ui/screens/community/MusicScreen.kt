package jp.tomoshibi.android.ui.screens.community

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.SongItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 点歌一覧屏「リクエスト曲」— 対齐 iOS MusicView（规格 §3.2 + §3.5 + §3.7）
//   PageHeader「リクエスト曲」level 2 + 右上「+」按钮去投稿
//   hint banner（浅主色底 + 主色描边）说明「通報」动线
//   曲卡列表（按 id 降序）：左 44 紫渐变方块 + 中曲名/艺术家 + 右「⚠ 通報」胶囊
//   点「通報」打开本文件内 ModalBottomSheet（曲を通報する）
// 注意：賛成/反対投票 2026-05-01 已废止，只剩「通報」动线。
// 紫渐变方块用 React tokens 同色（A78BFA→7C3AED），不是主题色，故不走 SuzuT。
private val MusicGradient = Brush.linearGradient(listOf(Color(0xFFA78BFA), Color(0xFF7C3AED)))

// 通报理由 4 选项（对齐 iOS SongReportReason，日语 label 逐字照抄规格）
private val ReportReasons =
    listOf(
        "うるさい",
        "曲調が好みでない / 不快",
        "歌詞が不適切",
        "その他",
    )

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MusicScreen(navController: NavHostController) {
    val t = SuzuT.current
    val ctx = LocalContext.current

    // 当前正在通报哪首曲（null = 弹窗关闭）；存整条 SongItem 方便弹窗里显示曲信息
    var reportFor by remember { mutableStateOf<SongItem?>(null) }

    // 一覧按 id 降序（新→旧）；MockData 已降序排好，这里再排一次保险
    val songs = remember { MockData.DEFAULT_SONGS.sortedByDescending { it.id } }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.pearl),
        ) {
            // ── 页头：标题 + 右上「+」去投稿 ──
            PageHeader(
                title = "リクエスト曲",
                level = 2,
                onLeft = { navController.popBackStack() },
                right = {
                    Box(
                        modifier =
                            Modifier
                                .size(36.dp)
                                .clip(RoundedCornerShape(percent = 50))
                                .background(t.btnGrad)
                                .clickable { navController.navigate(Route.MusicNew.path) },
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            SuzuIcons.Plus,
                            contentDescription = "曲を投稿",
                            tint = Color.White,
                            modifier = Modifier.size(20.dp),
                        )
                    }
                },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                // ── hint banner：浅主色底 + 主色描边圆角卡 ──
                Row(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(MaterialTheme.colorScheme.primaryContainer)
                            .border(
                                1.dp,
                                MaterialTheme.colorScheme.primary,
                                RoundedCornerShape(14.dp),
                            ).padding(horizontal = 14.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        SuzuIcons.Info,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(18.dp),
                    )
                    Spacer(Modifier.width(10.dp))
                    Text(
                        "気になる曲があれば、各曲の「⚠ 通報」ボタンから先生にお伝えできます。",
                        color = MaterialTheme.colorScheme.primary,
                        style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
                    )
                }

                Spacer(Modifier.height(2.dp))

                // ── 曲卡列表 ──
                songs.forEach { song ->
                    SongRow(
                        song = song,
                        onOpenDetail = { navController.navigate(Route.MusicDetail(song.id).path) },
                        onReport = { reportFor = song },
                    )
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }

    // ── 通报弹窗（曲を通報する）──
    if (reportFor != null) {
        val song = reportFor!!
        val sheetState = rememberModalBottomSheetState()
        ModalBottomSheet(
            onDismissRequest = { reportFor = null },
            sheetState = sheetState,
            containerColor = t.paper,
        ) {
            SongReportSheet(
                song = song,
                onSubmit = {
                    // TODO: 接后端 reportSong(...) + 累计举报数自动封禁逻辑（阈值 5/10/15），本波略过
                    Toast.makeText(ctx, "通報を送信しました。", Toast.LENGTH_SHORT).show()
                    reportFor = null
                },
            )
        }
    }
}

// 曲卡单行：左 44 紫渐变方块（白 ♪ 图标，点→详情）+ 中曲名/艺术家（点→详情）+ 右「⚠ 通報」胶囊
@Composable
private fun SongRow(
    song: SongItem,
    onOpenDetail: () -> Unit,
    onReport: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(t.paper)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 左：44 紫渐变方块 + 白 Music 图标（点→详情）
        Box(
            modifier =
                Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(MusicGradient)
                    .clickable(onClick = onOpenDetail),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                SuzuIcons.Music,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(22.dp),
            )
        }
        Spacer(Modifier.width(12.dp))

        // 中：曲名（加粗 1 行省略）+「アーティスト · by号」灰字（点→详情）
        Column(
            modifier =
                Modifier
                    .weight(1f)
                    .clickable(onClick = onOpenDetail),
        ) {
            Text(
                song.title,
                color = t.ink,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.height(2.dp))
            Text(
                "${song.artist} · ${song.by}",
                color = t.inkSub,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style = TextStyle(fontSize = 12.sp),
            )
        }
        Spacer(Modifier.width(8.dp))

        // 右：「⚠ 通報」胶囊（warnBg 底 + warnDeep 字 + 警告图标）→ 开通报弹窗
        Row(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(percent = 50))
                    .background(t.warnBg)
                    .clickable(onClick = onReport)
                    .padding(horizontal = 12.dp, vertical = 7.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                SuzuIcons.Warn,
                contentDescription = null,
                tint = t.warnDeep,
                modifier = Modifier.size(14.dp),
            )
            Spacer(Modifier.width(4.dp))
            Text(
                "通報",
                color = t.warnDeep,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
            )
        }
    }
}

// 通报弹窗内容（ModalBottomSheet 里）：标题 + 曲信息小卡 + 4 个自绘 radio + 其他详情 + 注意文 + 提交按钮
@Composable
private fun SongReportSheet(
    song: SongItem,
    onSubmit: () -> Unit,
) {
    val t = SuzuT.current
    var reason by remember { mutableStateOf<String?>(null) } // 选中的理由 label（null = 未选）
    var detail by remember { mutableStateOf("") } // 「その他」展开后的详情

    val isOther = reason == "その他"
    // 可点条件：选了理由 且（若选「その他」则详情非空，trim 后判断）
    val canSubmit = reason != null && (!isOther || detail.trim().isNotEmpty())

    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp)
                .padding(bottom = 28.dp),
    ) {
        // 标题
        Text(
            "曲を通報する",
            color = t.ink,
            style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold),
        )
        Spacer(Modifier.height(14.dp))

        // 曲信息小卡：38 紫渐变方块 + 曲名/艺术家
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.hairSoft)
                    .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier =
                    Modifier
                        .size(38.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(MusicGradient),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    SuzuIcons.Music,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(18.dp),
                )
            }
            Spacer(Modifier.width(10.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    song.title,
                    color = t.ink,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                )
                Text(
                    song.artist,
                    color = t.inkSub,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    style = TextStyle(fontSize = 12.sp),
                )
            }
        }
        Spacer(Modifier.height(16.dp))

        // 「通報の理由 *」label
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                "通報の理由",
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            )
            Text(
                " *",
                color = t.danger,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            )
        }
        Spacer(Modifier.height(10.dp))

        // 4 个自绘 radio 行（选中主色粗描边 + 内实心点）
        ReportReasons.forEach { r ->
            ReasonRadioRow(
                label = r,
                selected = reason == r,
                onClick = { reason = r },
            )
            Spacer(Modifier.height(8.dp))
        }

        // 选「その他」展开「詳細 *」TArea
        if (isOther) {
            Spacer(Modifier.height(4.dp))
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "詳細",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                )
                Text(
                    " *",
                    color = t.danger,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                )
            }
            Spacer(Modifier.height(7.dp))
            TArea(
                value = detail,
                onValueChange = { detail = it },
                placeholder = "通報の理由を具体的にお書きください",
                rows = 3,
            )
        }

        Spacer(Modifier.height(14.dp))

        // 注意文（2 行，逐字照抄规格）
        Text(
            "※ 通報内容は寮務の先生に届きます。投稿者には通報した人は知られません。\n" +
                "※ 多数の通報を受けた場合、投稿者の投稿が一定期間制限される場合があります。",
            color = t.inkMute,
            style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
        )
        Spacer(Modifier.height(16.dp))

        // 提交按钮
        PrimaryButton(
            title = "通報を送る",
            enabled = canSubmit,
            onClick = onSubmit,
        )
    }
}

// 自绘 radio 行（不用 Material RadioButton，对齐 iOS 粗描边设计）：
//   左圆圈（选中 = 主色 2dp 描边 + 内 10dp 实心点；未选 = inkFaint 描边）+ 右 label
@Composable
private fun ReasonRadioRow(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(if (selected) t.pill else t.hairSoft)
                .clickable(onClick = onClick)
                .padding(horizontal = 14.dp, vertical = 13.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier =
                Modifier
                    .size(22.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .border(
                        2.dp,
                        if (selected) primary else t.inkFaint,
                        RoundedCornerShape(percent = 50),
                    ),
            contentAlignment = Alignment.Center,
        ) {
            if (selected) {
                Box(
                    modifier =
                        Modifier
                            .size(10.dp)
                            .clip(RoundedCornerShape(percent = 50))
                            .background(primary),
                )
            }
        }
        Spacer(Modifier.width(12.dp))
        Text(
            label,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
        )
    }
}
