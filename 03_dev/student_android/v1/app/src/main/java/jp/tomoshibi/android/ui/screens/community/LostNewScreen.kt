package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT

// 遺失物投稿（拾到东西后发帖登记，L2 子页）— 对齐 iOS LostNewView（CommunityStubs.swift §5）
//   PageHeader「遺失物を投稿」level 2（左键返回上一页）
//   竖排表单：「画像」必填占位框（相机图标 +「写真を追加」）/「拾得場所」必填 TField /「特徴」必填 TArea
//            /「拾得日時」固定文字框（"2026-04-22 15:00"，纯展示）/「投稿する」主按钮
@Composable
fun LostNewScreen(navController: NavHostController) {
    val t = SuzuT.current
    // 输入态：拾得場所 / 特徴（对齐 iOS @State place / feature）
    var place by remember { mutableStateOf("") }
    var feature by remember { mutableStateOf("") }

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
                // 「画像」必填 — 虚线框占位：相机图标 +「写真を追加」（v1.0 不接真实选图）
                Field(label = "画像", required = true) {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(14.dp))
                                // 对齐 iOS 虚线描边占位框（Android 无现成 dash 描边 → 用 inkFaint 实线 1.5 近似）
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

                // 「拾得場所」必填 — 单行输入，placeholder「玄関 / 廊下 / ...」
                Field(label = "拾得場所", required = true) {
                    TField(
                        value = place,
                        onValueChange = { place = it },
                        placeholder = "玄関 / 廊下 / ...",
                    )
                }
                Spacer(Modifier.height(18.dp))

                // 「特徴」必填 — 多行输入，placeholder「色・大きさ・目印」
                Field(label = "特徴", required = true) {
                    TArea(
                        value = feature,
                        onValueChange = { feature = it },
                        placeholder = "色・大きさ・目印",
                        rows = 3,
                    )
                }
                Spacer(Modifier.height(18.dp))

                // 「拾得日時」— 固定展示文字（iOS 原样写死，纯只读）
                Field(label = "拾得日時") {
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(48.dp)
                                .clip(RoundedCornerShape(12.dp))
                                .background(t.pearl)
                                .border(BorderStroke(1.dp, t.hair), RoundedCornerShape(12.dp))
                                .padding(horizontal = 14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            "2026-04-22 15:00",
                            color = t.ink,
                            style = TextStyle(fontSize = 15.sp),
                        )
                        Spacer(Modifier.weight(1f))
                    }
                }
                Spacer(Modifier.height(18.dp))

                // 「投稿する」主按钮 — 当前仅返回上一页
                PrimaryButton(title = "投稿する") {
                    // TODO: 真实 POST 投稿到后端待接（iOS 现也是占位：showToast「投稿しました」后回 homeLost）
                    navController.popBackStack()
                }
            }
        }
    }
}
