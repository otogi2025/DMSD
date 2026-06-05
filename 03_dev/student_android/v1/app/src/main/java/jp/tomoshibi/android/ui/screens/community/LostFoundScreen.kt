package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.LostItem
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 把 ARGB hex 字符串解析为 Compose Color
// 注意 Long.parseLong 在 0x80000000+ 大值会溢出 → 用 java.lang.Long.parseLong + parseUnsignedInt 不可靠
// 实际处理：用 java.lang.Long.parseLong(hex, 16) — 因为 mock hex 是 8 位无符号 ARGB
private fun parseArgbHex(hex: String): Color {
    val n = java.lang.Long.parseLong(hex, 16)
    return Color(n.toInt())
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LostFoundScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    var query by remember { mutableStateOf("") }

    val filtered =
        remember(query) {
            if (query.isBlank()) {
                MockData.DEFAULT_LOST_FOUND
            } else {
                MockData.DEFAULT_LOST_FOUND.filter { it.label.contains(query, ignoreCase = true) }
            }
        }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 头部
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 18.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(44.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(SuzuIcons.ChevL, contentDescription = "戻る", tint = tokens.ink, modifier = Modifier.size(24.dp))
                }
                Spacer(Modifier.width(4.dp))
                Text(
                    "落し物",
                    color = tokens.ink,
                    modifier = Modifier.weight(1f),
                    style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold),
                )
                Box(
                    modifier =
                        Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(tokens.btnGrad)
                            .clickable { navController.navigate(Route.LostNew.path) },
                    contentAlignment = Alignment.Center,
                ) {
                    Text("+", color = Color.White, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
                }
            }

            // 搜索框
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .border(1.dp, tokens.hair, RoundedCornerShape(12.dp))
                        .background(tokens.paper)
                        .padding(horizontal = 14.dp, vertical = 12.dp),
            ) {
                if (query.isEmpty()) {
                    Text(
                        "検索...",
                        color = tokens.inkFaint,
                        style = TextStyle(fontSize = 14.sp),
                    )
                }
                BasicTextField(
                    value = query,
                    onValueChange = { query = it },
                    singleLine = true,
                    textStyle = TextStyle(color = tokens.ink, fontSize = 14.sp),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            Spacer(Modifier.height(16.dp))

            // 网格 — 96×96dp 色块卡
            LazyVerticalGrid(
                columns = GridCells.Adaptive(minSize = 96.dp),
                modifier = Modifier.weight(1f).fillMaxWidth().padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                contentPadding = PaddingValues(bottom = 20.dp),
            ) {
                items(filtered) { item ->
                    val claimed = state.lostFoundClaims[item.id] == true
                    Column(
                        modifier =
                            Modifier
                                .clickable { navController.navigate(Route.LostDetail(item.id).path) }
                                .alpha(if (claimed) 0.5f else 1f),
                    ) {
                        Box(
                            modifier =
                                Modifier
                                    .size(96.dp)
                                    .clip(RoundedCornerShape(14.dp))
                                    .background(parseArgbHex(item.colorHex)),
                            contentAlignment = Alignment.BottomStart,
                        ) {
                            if (claimed) {
                                Box(
                                    modifier =
                                        Modifier
                                            .padding(6.dp)
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(tokens.ink.copy(alpha = 0.7f))
                                            .padding(horizontal = 6.dp, vertical = 2.dp),
                                ) {
                                    Text(
                                        "預かり中",
                                        color = tokens.pearl,
                                        style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold),
                                    )
                                }
                            }
                        }
                        Spacer(Modifier.height(6.dp))
                        Text(
                            item.label,
                            color = tokens.ink,
                            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium),
                        )
                    }
                }
            }
        }
    }
}
