package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.SongRequestBody
import jp.tomoshibi.android.data.network.endpoints.SongsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 点歌投稿 — 对齐 iOS MusicNewView 生产分支：
//   Apple Music URL（选填，不传后端）/「曲名」* /「アーティスト」* /「投稿理由」
//   → POST /songs（song_title / artist / note）
@Composable
fun MusicNewScreen(navController: NavHostController) {
    val store = LocalAppStore.current
    val tokens = SuzuT.current
    val scope = rememberCoroutineScope()

    var url by remember { mutableStateOf("") }
    var title by remember { mutableStateOf("") }
    var artist by remember { mutableStateOf("") }
    var reason by remember { mutableStateOf("") }
    var isSubmitting by remember { mutableStateOf(false) }

    val canSubmit = title.trim().isNotEmpty() && artist.trim().isNotEmpty()

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            PageHeader(title = "曲を投稿", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(18.dp),
            ) {
                Field(label = "Apple Music URL", hint = "曲情報を自動取得します") {
                    TField(
                        value = url,
                        onValueChange = { url = it },
                        placeholder = "https://music.apple.com/...",
                        keyboard = KeyboardType.Uri,
                    )
                }

                Field(label = "曲名", required = true) {
                    TField(value = title, onValueChange = { title = it })
                }

                Field(label = "アーティスト", required = true) {
                    TField(value = artist, onValueChange = { artist = it })
                }

                Field(label = "投稿理由") {
                    TArea(
                        value = reason,
                        onValueChange = { reason = it },
                        placeholder = "この曲を寮で流したい理由",
                        rows = 3,
                    )
                }

                Spacer(Modifier.height(4.dp))

                PrimaryButton(
                    title = "投稿する",
                    enabled = canSubmit && !isSubmitting,
                    onClick = {
                        if (isSubmitting) return@PrimaryButton
                        isSubmitting = true
                        val note = reason.trim()
                        val body =
                            SongRequestBody(
                                songTitle = title.trim(),
                                artist = artist.trim(),
                                note = note.ifEmpty { null },
                            )
                        scope.launch {
                            val tokenAtStart = store.snapshot().authToken
                            try {
                                SongsAPI.create(body)
                                if (store.snapshot().authToken != tokenAtStart) return@launch
                                store.showToast("投稿しました")
                                navController.popBackStack()
                            } catch (e: ApiError) {
                                if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                                store.showToast("投稿に失敗しました")
                            } catch (_: Exception) {
                                store.showToast("投稿に失敗しました")
                            } finally {
                                isSubmitting = false
                            }
                        }
                    },
                )

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}
