package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.SongItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 点歌方块统一紫渐变（对齐 iOS MusicDetailView 的 accentSoft→accent，固定紫值不走主题色）
private val MusicGrad = Brush.linearGradient(listOf(Color(0xFFA78BFA), Color(0xFF7C3AED)))

// 曲詳細 — 对齐 iOS MusicDetailView（规格 §3.4）：
//   PageHeader「曲詳細」level 2 + 160×160 紫渐变大方块 + 曲名 + 「アーティスト · 投稿 by号」
//   + SuzuCard「投稿理由」(写死文)
//   按 id 在 MockData.DEFAULT_SONGS 里找曲；找不到显示 EmptyState
@Composable
fun MusicDetailScreen(
    navController: NavHostController,
    id: Int,
) {
    val t = SuzuT.current
    // 从假数据里按 id 取曲（无后端）
    val song: SongItem? = MockData.DEFAULT_SONGS.find { it.id == id }

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

                    Spacer(Modifier.height(40.dp))
                }
            }
        }
    }
}
