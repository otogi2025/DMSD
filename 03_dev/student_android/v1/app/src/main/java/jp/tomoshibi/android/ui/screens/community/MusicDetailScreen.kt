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
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.SongItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 点歌方块统一紫渐变（对齐 iOS MusicDetailView 的 accentSoft→accent，固定紫值不走主题色）
private val MusicGrad = Brush.linearGradient(listOf(Color(0xFFA78BFA), Color(0xFF7C3AED)))

// 曲詳細 — 对齐 iOS MusicDetailView（规格 §3.4）：
//   PageHeader「曲詳細」level 2 + 160×160 紫渐变大方块 + 曲名 + 「アーティスト · 投稿 by号」
//   + SuzuCard「投稿理由」(写死文) + 大「この曲を通報する」警告按钮 → 通报 ModalBottomSheet（§3.5）
//   按 id 在 MockData.DEFAULT_SONGS 里找曲；找不到显示 EmptyState
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MusicDetailScreen(
    navController: NavHostController,
    id: Int,
) {
    val t = SuzuT.current
    val ctx = LocalContext.current
    // 从假数据里按 id 取曲（无后端）
    val song: SongItem? = MockData.DEFAULT_SONGS.find { it.id == id }
    var reportOpen by remember { mutableStateOf(false) }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "曲詳細", level = 2, onLeft = { navController.popBackStack() })

            if (song == null) {
                // 取不到曲：空态占位
                EmptyState(icon = SuzuIcons.Music, title = "曲が見つかりません")
            } else {
                Column(
                    modifier =
                        Modifier
                            .fillMaxSize()
                            .verticalScroll(rememberScrollState())
                            .padding(horizontal = 20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Spacer(Modifier.height(24.dp))

                    // 160×160 紫渐变大圆角方块 + 白 Music 图标（带阴影），居中
                    Box(
                        modifier =
                            Modifier
                                .size(160.dp)
                                .shadow(
                                    elevation = 12.dp,
                                    shape = RoundedCornerShape(28.dp),
                                    ambientColor = Color(0xFF7C3AED),
                                    spotColor = Color(0xFF7C3AED),
                                ).clip(RoundedCornerShape(28.dp))
                                .background(MusicGrad),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            SuzuIcons.Music,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(64.dp),
                        )
                    }

                    Spacer(Modifier.height(20.dp))

                    // 曲名（22 heavy）
                    Text(
                        song.title,
                        color = t.ink,
                        textAlign = TextAlign.Center,
                        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Black),
                    )
                    Spacer(Modifier.height(6.dp))
                    // 「アーティスト · 投稿 by号」
                    Text(
                        "${song.artist} · 投稿 ${song.by}",
                        color = t.inkSub,
                        textAlign = TextAlign.Center,
                        style = TextStyle(fontSize = 14.sp),
                    )

                    Spacer(Modifier.height(24.dp))

                    // 「投稿理由」卡 + 写死文（演示版无后端，照规格写死）
                    SuzuCard(modifier = Modifier.fillMaxWidth()) {
                        Text(
                            "投稿理由",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                        )
                        Spacer(Modifier.height(8.dp))
                        Text(
                            "朝の支度時間に聴きたい、明るい気持ちになれる曲です。",
                            color = t.ink,
                            style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
                        )
                    }

                    Spacer(Modifier.height(24.dp))

                    // 大「この曲を通報する」按钮（警告色块，高 52）→ 开通报 ModalBottomSheet
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(52.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(t.warnBg)
                                .clickable { reportOpen = true }
                                .padding(horizontal = 16.dp),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            SuzuIcons.Warn,
                            contentDescription = null,
                            tint = t.warnDeep,
                            modifier = Modifier.size(18.dp),
                        )
                        Spacer(Modifier.width(8.dp))
                        Text(
                            "この曲を通報する",
                            color = t.warnDeep,
                            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                        )
                    }

                    Spacer(Modifier.height(14.dp))

                    // 底部说明文
                    Text(
                        "通報内容は寮務の先生に届きます。投稿者には通報した人は知られません。",
                        color = t.inkMute,
                        textAlign = TextAlign.Center,
                        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                    )

                    Spacer(Modifier.height(40.dp))
                }
            }
        }
    }

    // ── 通报 ModalBottomSheet（规格 §3.5 SongReportSheet：4 个自绘 radio）──
    if (reportOpen) {
        val sheetState = rememberModalBottomSheetState()
        // 选中的理由（null = 未选）
        var reason by remember { mutableStateOf<String?>(null) }
        // 选「その他」时填的详情（规格 §3.5-5：展开「詳細 *」TArea）
        var detail by remember { mutableStateOf("") }
        // 4 个固定理由（逐字照抄规格 §3.5-4）
        val reasons =
            listOf(
                "うるさい",
                "曲調が好みでない / 不快",
                "歌詞が不適切",
                "その他",
            )
        ModalBottomSheet(
            onDismissRequest = { reportOpen = false },
            sheetState = sheetState,
            containerColor = t.paper,
        ) {
            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp)
                        .padding(bottom = 24.dp),
            ) {
                Text(
                    "曲を通報する",
                    color = t.ink,
                    style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.height(16.dp))

                // 「通報の理由 *」区块标题（规格 §3.5-4）
                Text(
                    "通報の理由 *",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                )
                Spacer(Modifier.height(8.dp))

                reasons.forEach { r ->
                    ReportReasonRow(label = r, selected = reason == r) { reason = r }
                    Spacer(Modifier.height(8.dp))
                }

                // 选「その他」时展开「詳細 *」多行输入（规格 §3.5-5）
                if (reason == "その他") {
                    Spacer(Modifier.height(8.dp))
                    Field(label = "詳細", required = true) {
                        TArea(
                            value = detail,
                            onValueChange = { detail = it },
                            placeholder = "通報の理由を具体的にお書きください",
                            rows = 3,
                        )
                    }
                }

                Spacer(Modifier.height(8.dp))

                // 底部说明文（规格 §3.5-6：2 行注意文）
                Text(
                    "※ 通報内容は寮務の先生に届きます。投稿者には通報した人は知られません。\n※ 多数の通報を受けた場合、投稿者の投稿が一定期間制限される場合があります。",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                )

                Spacer(Modifier.height(16.dp))

                // 「通報を送る」— 可点条件 = 选了理由 且（若选「その他」则详情非空）（规格 §3.5-7）；提交弹 toast 后关弹窗
                // TODO: 封禁/累计举报阈值升级（≥5/≥10/≥15）逻辑本波略过，待接 AppStore + 后端
                val canSend = reason != null && (reason != "その他" || detail.isNotBlank())
                val sendBg =
                    if (canSend) Modifier.background(t.danger) else Modifier.background(t.inkFaint)
                Row(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .height(52.dp)
                            .clip(RoundedCornerShape(16.dp))
                            .then(sendBg)
                            .clickable(enabled = canSend) {
                                Toast.makeText(ctx, "通報を送信しました。", Toast.LENGTH_SHORT).show()
                                reportOpen = false
                            }.padding(horizontal = 16.dp),
                    horizontalArrangement = Arrangement.Center,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        "通報を送る",
                        color = Color.White,
                        style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                    )
                }
            }
        }
    }
}

// 通报理由单行 — 左自绘圆形 radio（选中粗描边 + 实心点）+ 右理由文字（规格 §3.10 不用 RadioButton）
@Composable
private fun ReportReasonRow(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(if (selected) t.pill else t.hairSoft)
                .clickable(onClick = onClick)
                .padding(horizontal = 14.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 圆形 radio：选中 = primary 粗描边 + 内 10dp 实心点；未选 = inkFaint 描边
        Box(
            modifier =
                Modifier
                    .size(22.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .border(
                        width = 2.dp,
                        color = if (selected) cs.primary else t.inkFaint,
                        shape = RoundedCornerShape(percent = 50),
                    ),
            contentAlignment = Alignment.Center,
        ) {
            if (selected) {
                Box(
                    modifier =
                        Modifier
                            .size(10.dp)
                            .clip(RoundedCornerShape(percent = 50))
                            .background(cs.primary),
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
