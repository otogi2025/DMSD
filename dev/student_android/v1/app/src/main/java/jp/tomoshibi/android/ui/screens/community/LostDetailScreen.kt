package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.LostFoundAPI
import jp.tomoshibi.android.data.network.endpoints.LostFoundOut
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 遗失物详情 — 对齐 iOS LostDetailView 生产分支：
//   渐变大图 🎒 + 标题 + Pill(场所/日期/[「解決済み」]) + description
//   仅投稿者本人且未解决 →「解決済みにする」→ PATCH /lost-found/{id}/resolve
//   （不是任意学生「认领」）
@Composable
fun LostDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<LostFoundOut>>(LoadState.Loading) }
    var resolving by remember { mutableStateOf(false) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = LostFoundAPI.list()
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
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "遺失物詳細",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox(useSpinner = true)
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    EmptyState(icon = SuzuIcons.Search, title = "見つかりません")
                }

                is LoadState.Success -> {
                    val item = s.value
                    val accent = Color(0xFF7C3AED)
                    val place = item.location?.takeIf { it.isNotBlank() } ?: "—"
                    val date = formatLostDate(item.createdAt)
                    val isResolved = item.status == "resolved"
                    val detailText =
                        item.description?.takeIf { it.isNotBlank() } ?: "（説明はありません）"
                    // 本人投稿且未解决才可标解决（大小写不敏感比对 UUID）
                    val canResolve =
                        !isResolved &&
                            state.myStudentId != null &&
                            item.studentId.equals(state.myStudentId, ignoreCase = true)

                    Box(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .aspectRatio(1.3f)
                                .background(
                                    Brush.linearGradient(
                                        listOf(
                                            accent.copy(alpha = 2f / 3f),
                                            accent.copy(alpha = 0.27f),
                                        ),
                                    ),
                                ),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text("🎒", style = TextStyle(fontSize = 80.sp), color = Color.White)
                    }

                    Column(modifier = Modifier.fillMaxWidth().padding(20.dp)) {
                        Text(
                            item.itemName,
                            color = t.ink,
                            style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Black),
                        )
                        Spacer(Modifier.height(6.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            Pill(text = place, tone = PillTone.Accent)
                            Pill(text = date, tone = PillTone.Neutral)
                            if (isResolved) {
                                Pill(text = "解決済み", tone = PillTone.Ok)
                            }
                        }
                        Spacer(Modifier.height(14.dp))
                        Text(
                            detailText,
                            color = t.inkSub,
                            style = TextStyle(fontSize = 14.sp, lineHeight = 22.sp),
                        )
                        Spacer(Modifier.height(20.dp))

                        if (canResolve) {
                            PrimaryButton(
                                title = "解決済みにする",
                                enabled = !resolving,
                            ) {
                                if (resolving) return@PrimaryButton
                                resolving = true
                                scope.launch {
                                    val tokenAtStart = store.snapshot().authToken
                                    try {
                                        val updated = LostFoundAPI.resolve(item.id)
                                        if (store.snapshot().authToken != tokenAtStart) return@launch
                                        ui = LoadState.Success(updated)
                                        store.showToast("解決済みにしました")
                                    } catch (e: ApiError) {
                                        if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                        store.showToast("操作に失敗しました")
                                    } catch (_: Exception) {
                                        store.showToast("操作に失敗しました")
                                    } finally {
                                        resolving = false
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
