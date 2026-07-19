package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.PhotoCamera
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.LostFoundAPI
import jp.tomoshibi.android.data.network.endpoints.LostFoundBody
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 遗失物投稿 — 对齐 iOS LostNewView 生产分支：
//   画像占位 / 種別（「拾得物」|「落とし物」）/「品名」* /「場所」* /「特徴」* /「投稿する」→ POST /lost-found
//   （学生端一览已拔「+」入口；本屏保留供路由复用，与 iOS 一致）
@Composable
fun LostNewScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()

    // found =「拾得物」/ lost =「落とし物」
    var postType by remember { mutableStateOf("found") }
    var itemName by remember { mutableStateOf("") }
    var place by remember { mutableStateOf("") }
    var feature by remember { mutableStateOf("") }
    var isSubmitting by remember { mutableStateOf(false) }

    val canSubmit = itemName.trim().isNotEmpty()

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize()) {
            PageHeader(
                title = "遺失物を投稿",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp)
                        .padding(top = 4.dp, bottom = 24.dp),
            ) {
                Field(label = "画像", required = true) {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(14.dp))
                                .border(BorderStroke(1.5.dp, t.inkFaint), RoundedCornerShape(14.dp))
                                .padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        Icon(
                            imageVector = Icons.Outlined.PhotoCamera,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(28.dp),
                        )
                        Text(
                            "写真を追加",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 13.sp),
                        )
                    }
                }
                Spacer(Modifier.height(18.dp))

                Field(label = "種別", required = true) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        TypeChip(
                            title = "拾得物",
                            selected = postType == "found",
                            onClick = { postType = "found" },
                        )
                        TypeChip(
                            title = "落とし物",
                            selected = postType == "lost",
                            onClick = { postType = "lost" },
                        )
                    }
                }
                Spacer(Modifier.height(18.dp))

                Field(label = "品名", required = true) {
                    TField(
                        value = itemName,
                        onValueChange = { itemName = it },
                        placeholder = "傘 / 鍵 / 財布 …",
                    )
                }
                Spacer(Modifier.height(18.dp))

                Field(label = "場所", required = true) {
                    TField(
                        value = place,
                        onValueChange = { place = it },
                        placeholder = "玄関 / 廊下 / …",
                    )
                }
                Spacer(Modifier.height(18.dp))

                Field(label = "特徴", required = true) {
                    TArea(
                        value = feature,
                        onValueChange = { feature = it },
                        placeholder = "色・大きさ・目印",
                        rows = 3,
                    )
                }
                Spacer(Modifier.height(18.dp))

                // iOS 已删写死「拾得日時」栏 — 本屏不画

                PrimaryButton(
                    title = "投稿する",
                    enabled = canSubmit && !isSubmitting,
                ) {
                    if (isSubmitting) return@PrimaryButton
                    isSubmitting = true
                    val loc = place.trim()
                    val desc = feature.trim()
                    val body =
                        LostFoundBody(
                            postType = postType,
                            itemName = itemName.trim(),
                            description = desc.ifEmpty { null },
                            location = loc.ifEmpty { null },
                        )
                    scope.launch {
                        val tokenAtStart = store.snapshot().authToken
                        try {
                            LostFoundAPI.create(body)
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
                }
            }
        }
    }
}

@Composable
private fun TypeChip(
    title: String,
    selected: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Text(
        title,
        color = if (selected) primary else t.ink,
        style =
            TextStyle(
                fontSize = 14.sp,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
            ),
        modifier =
            Modifier
                .clip(RoundedCornerShape(12.dp))
                .background(if (selected) primary.copy(alpha = 0.06f) else t.pearl)
                .border(
                    width = if (selected) 1.5.dp else 1.dp,
                    color = if (selected) primary else t.hair,
                    shape = RoundedCornerShape(12.dp),
                ).clickable(onClick = onClick)
                .padding(horizontal = 16.dp, vertical = 10.dp),
    )
}
