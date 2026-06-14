package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
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
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
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
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 点歌一覧屏「リクエスト曲」— 対齐 iOS MusicView（规格 §3.2 + §3.7）
//   PageHeader「リクエスト曲」level 2 + 右上「+」按钮去投稿
//   曲卡列表（按 id 降序）：左 44 紫渐变方块 + 中曲名/艺术家（点→详情）
// 紫渐变方块用 React tokens 同色（A78BFA→7C3AED），不是主题色，故不走 SuzuT。
private val MusicGradient = Brush.linearGradient(listOf(Color(0xFFA78BFA), Color(0xFF7C3AED)))

@Composable
fun MusicScreen(navController: NavHostController) {
    val t = SuzuT.current

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
                Spacer(Modifier.height(4.dp))

                // ── 曲卡列表 ──
                songs.forEach { song ->
                    SongRow(
                        song = song,
                        onOpenDetail = { navController.navigate(Route.MusicDetail(song.id).path) },
                    )
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 曲卡单行：左 44 紫渐变方块（白 ♪ 图标，点→详情）+ 中曲名/艺术家（点→详情）
@Composable
private fun SongRow(
    song: SongItem,
    onOpenDetail: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(t.paper)
                .clickable(onClick = onOpenDetail)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 左：44 紫渐变方块 + 白 Music 图标
        Box(
            modifier =
                Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(MusicGradient),
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

        // 中：曲名（加粗 1 行省略）+「アーティスト · by号」灰字
        Column(modifier = Modifier.weight(1f)) {
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
    }
}
