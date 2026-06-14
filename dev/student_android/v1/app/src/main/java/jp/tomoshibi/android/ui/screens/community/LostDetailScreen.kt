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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 遺失物詳細（L2 子页）— 对齐 iOS LostDetailView（CommunityStubs.swift 行 595–657）
//   PageHeader「遺失物詳細」level 2 → 渐变大色块（aspectRatio 1.3 + 中央 🎒 80sp）
//   → label 名称（22sp heavy）→ 拾得場所 / 拾得日 两枚 Pill → 认领按钮。
//   认领状态走 store.lostFoundClaims（与 LostFoundScreen 同一份状态）：
//     已认领 → 显示「預かり中」灰条；未认领 → PrimaryButton「これは私のもの」点击落库。
//   注：iOS 玻璃组件 GlassSheet 在 Android 无对应，本屏是全屏页（非弹窗），按范本 MyPackagesScreen 用 GlobalScaffold + PageHeader。
//   把 8 位 ARGB hex 字符串转 Color：java.lang.Long.parseLong(hex, 16) → toInt()（8 位无符号 ARGB，照 LostFoundScreen 同法）。
private fun parseArgbHex(hex: String): Color {
    val n = java.lang.Long.parseLong(hex, 16)
    return Color(n.toInt())
}

@Composable
fun LostDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    // 按 id 取数据；取不到 → 走 EmptyState（对齐 iOS 的 EmptyState 分支「見つかりません」）
    val item = MockData.DEFAULT_LOST_FOUND.firstOrNull { it.id == id }

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

            if (item != null) {
                val color = parseArgbHex(item.colorHex)
                // 大色块：左上→右下线性渐变（亮 2/3 → 淡 0.27）+ 中央 🎒 80sp，宽高比 1.3（对齐 iOS）
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .aspectRatio(1.3f)
                            .background(
                                Brush.linearGradient(
                                    colors =
                                        listOf(
                                            color.copy(alpha = 2f / 3f),
                                            color.copy(alpha = 0.27f),
                                        ),
                                ),
                            ),
                    contentAlignment = Alignment.Center,
                ) {
                    Text("🎒", style = TextStyle(fontSize = 80.sp), color = Color.White)
                }

                // 正文区（内边距 20，对齐 iOS .padding(20)）
                Column(modifier = Modifier.fillMaxWidth().padding(20.dp)) {
                    // 名称 = label（22sp heavy，对齐 iOS l.title）
                    Text(
                        item.label,
                        color = t.ink,
                        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Black),
                    )
                    Spacer(Modifier.height(6.dp))
                    // 拾得場所（accent）+ 拾得日（neutral）两枚 Pill，横排间隔 6（对齐 iOS HStack spacing 6）
                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        Pill(text = item.place, tone = PillTone.Accent)
                        Pill(text = item.date, tone = PillTone.Neutral)
                    }
                    Spacer(Modifier.height(20.dp))

                    // 认领区 — 与 LostFoundScreen 共用 lostFoundClaims 状态
                    val claimed = state.lostFoundClaims[item.id] == true
                    if (claimed) {
                        // 已认领 → 灰色「預かり中」状态条（不可点）
                        Box(
                            modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(16.dp))
                                    .background(t.hairSoft)
                                    .padding(vertical = 16.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                "預かり中",
                                color = t.inkSub,
                                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold),
                            )
                        }
                    } else {
                        // 未认领 → 主按钮「これは私のもの」点击写 store.lostFoundClaims[id] = true
                        PrimaryButton(title = "これは私のもの") {
                            scope.launch {
                                store.update { it.copy(lostFoundClaims = it.lostFoundClaims + (item.id to true)) }
                            }
                        }
                    }
                }
            } else {
                // 取不到 → 空状态（对齐 iOS EmptyState「見つかりません」；
                // iOS 用放大镜图标 magnifyingglass，SuzuIcons 无对应 → 用 EmptyState 默认图标）
                EmptyState(title = "見つかりません")
            }
        }
    }
}
