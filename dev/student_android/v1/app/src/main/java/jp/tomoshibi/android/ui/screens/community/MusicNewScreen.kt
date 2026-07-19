package jp.tomoshibi.android.ui.screens.community

import jp.tomoshibi.android.data.store.LocalAppStore

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
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT

// 点歌投稿表单 — 対齐 iOS MusicNewView（§3.3）：
//   页头「曲を投稿」level 2 + 4 个表单字段（链接 / 曲名* / 艺术家* / 理由）+「投稿する」按钮
//   纯本地：不接后端，提交后弹提示再返回上一页
@Composable
fun MusicNewScreen(navController: NavHostController) {
    val store = LocalAppStore.current
    val tokens = SuzuT.current
    val ctx = LocalContext.current

    // 4 个表单字段的本地输入状态
    var url by remember { mutableStateOf("") } // Apple Music URL（演示版不做自动取得）
    var title by remember { mutableStateOf("") } // 曲名（必填）
    var artist by remember { mutableStateOf("") } // 艺术家（必填）
    var reason by remember { mutableStateOf("") } // 投稿理由（选填）

    // 可点条件：曲名 trim 后非空 且 艺术家 trim 后非空（只输空格不算）
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
                // Apple Music 链接（带提示文「曲情報を自動取得します」）
                Field(label = "Apple Music URL", hint = "曲情報を自動取得します") {
                    TField(
                        value = url,
                        onValueChange = { url = it },
                        placeholder = "https://music.apple.com/...",
                        keyboard = KeyboardType.Uri,
                    )
                }

                // 曲名（必填）
                Field(label = "曲名", required = true) {
                    TField(value = title, onValueChange = { title = it })
                }

                // 艺术家（必填，UI label「アーティスト」）
                Field(label = "アーティスト", required = true) {
                    TField(value = artist, onValueChange = { artist = it })
                }

                // 投稿理由（选填，多行）
                Field(label = "投稿理由") {
                    TArea(
                        value = reason,
                        onValueChange = { reason = it },
                        placeholder = "この曲を寮で流したい理由",
                        rows = 3,
                    )
                }

                Spacer(Modifier.height(4.dp))

                // 投稿按钮：曲名 + 艺术家非空才可点，点了弹 toast 后返回一覧
                PrimaryButton(
                    title = "投稿する",
                    enabled = canSubmit,
                    onClick = {
                        store.showToast("投稿しました")
                        navController.popBackStack()
                    },
                )

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}
