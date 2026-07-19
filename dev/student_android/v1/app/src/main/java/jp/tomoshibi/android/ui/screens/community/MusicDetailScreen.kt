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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
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
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.SongRequestOut
import jp.tomoshibi.android.data.network.endpoints.SongsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

private val MusicGrad = Brush.linearGradient(listOf(Color(0xFFA78BFA), Color(0xFF7C3AED)))

// 曲詳細 — 对齐 iOS MusicDetailView 生产分支：
//   副标题仅 artist；投稿理由 = 真实 note 或「（理由は未記入です）」；空态「見つかりません」
@Composable
fun MusicDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<SongRequestOut>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = SongsAPI.list()
                val found = items.firstOrNull { it.id.equals(id, ignoreCase = true) }
                if (found == null) LoadState.Empty else LoadState.Success(found)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return
                LoadState.Failed(e.display)
            } catch (_: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(id) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "曲詳細", level = 2, onLeft = { navController.popBackStack() })

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox(useSpinner = true)
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    EmptyState(icon = SuzuIcons.Music, title = "見つかりません")
                }

                is LoadState.Success -> {
                    val song = s.value
                    val artist = song.artist.orEmpty()
                    val reason = song.note?.takeIf { it.isNotBlank() } ?: "（理由は未記入です）"

                    Column(
                        modifier =
                            Modifier
                                .fillMaxSize()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        Spacer(Modifier.height(24.dp))

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

                        Text(
                            song.songTitle,
                            color = t.ink,
                            textAlign = TextAlign.Center,
                            style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Black),
                        )
                        Spacer(Modifier.height(6.dp))
                        // 生产：只显示艺术家，不显示「投稿 by号」
                        Text(
                            artist,
                            color = t.inkSub,
                            textAlign = TextAlign.Center,
                            style = TextStyle(fontSize = 14.sp),
                        )

                        Spacer(Modifier.height(24.dp))

                        SuzuCard(modifier = Modifier.fillMaxWidth()) {
                            Text(
                                "投稿理由",
                                color = t.inkSub,
                                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                            )
                            Spacer(Modifier.height(8.dp))
                            Text(
                                reason,
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
}
