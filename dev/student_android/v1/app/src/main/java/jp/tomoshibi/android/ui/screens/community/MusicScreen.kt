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
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
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
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.SongRequestOut
import jp.tomoshibi.android.data.network.endpoints.SongsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 点歌一覧「リクエスト曲」— 对齐 iOS MusicView 生产分支：
//   PageHeader + 右上「+」投稿 + GET /songs 列表（后端已新→旧）
//   曲卡：44 紫渐变（圆角 10）+ 曲名 + 仅艺术家（不显示投稿者）
private val MusicGradient = Brush.linearGradient(listOf(Color(0xFFA78BFA), Color(0xFF7C3AED)))

@Composable
fun MusicScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<List<SongRequestOut>>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = SongsAPI.list()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return
                LoadState.Failed(e.display)
            } catch (_: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.pearl),
        ) {
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

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox(useSpinner = true)
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    EmptyState(
                        icon = SuzuIcons.Music,
                        title = "リクエストされた曲はまだありません",
                    )
                }

                is LoadState.Success -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Spacer(Modifier.height(4.dp))
                        s.value.forEach { song ->
                            SongRow(
                                song = song,
                                onOpenDetail = {
                                    navController.navigate(Route.MusicDetail(song.id).path)
                                },
                            )
                        }
                        Spacer(Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun SongRow(
    song: SongRequestOut,
    onOpenDetail: () -> Unit,
) {
    val t = SuzuT.current
    val artist = song.artist.orEmpty()
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
        // 紫渐变方块圆角 10（对齐 iOS 10pt，非 12）
        Box(
            modifier =
                Modifier
                    .size(44.dp)
                    .clip(RoundedCornerShape(10.dp))
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

        Column(modifier = Modifier.weight(1f)) {
            Text(
                song.songTitle,
                color = t.ink,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.height(2.dp))
            // 生产：仅艺术家，不显示投稿者
            Text(
                artist,
                color = t.inkSub,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style = TextStyle(fontSize = 12.sp),
            )
        }
    }
}
