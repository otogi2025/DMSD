package jp.tomoshibi.android.ui.screens.applications

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.theme.SuzuT

// 新規申請种类选择 — 对齐 iOS ApplyNewView（独立全屏页，非底部弹层）
// PageHeader「新規申請」level2 + 副标题「申請の種類を選択してください」+ 2 列 12 种卡片
@Composable
fun ApplyNewSelectScreen(navController: NavHostController) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    // 外出禁止（禁足）— 当月扣分 ≥8 分时「外出」这张卡置灰不可点，
    // 提交页 ApplyNewScreen 还有一道同口径的闸（深链绕过卡片时兜底）。
    val outingBanned = state.user.points >= OUTING_BAN_POINTS
    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(t.pearl)
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "新規申請",
                level = 2,
                onLeft = { navController.popBackStack() },
            )
            Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp).padding(bottom = 40.dp)) {
                Text(
                    "申請の種類を選択してください",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp),
                    modifier = Modifier.padding(start = 4.dp, bottom = 14.dp),
                )
                // 禁足中的说明 — 跟置灰的「外出」卡片配套，不然学生只看到卡点不动不知道为什么
                if (outingBanned) {
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(bottom = 12.dp)
                                .clip(RoundedCornerShape(12.dp))
                                .background(t.dangerBg)
                                .padding(12.dp),
                        verticalAlignment = Alignment.Top,
                    ) {
                        Text("⚠", color = t.danger, style = TextStyle(fontSize = 14.sp))
                        Spacer(Modifier.size(8.dp))
                        Text(
                            OUTING_BAN_NOTICE,
                            color = t.danger,
                            style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
                        )
                    }
                }
                APPLY_TYPES.chunked(2).forEach { row ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(bottom = 10.dp),
                        horizontalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        row.forEach { k ->
                            // 只有「外出」这一张卡会被禁足闸置灰，其余类型照常可点
                            val disabled = outingBanned && k.name == OUTING_KIND
                            Column(
                                modifier =
                                    Modifier
                                        .weight(1f)
                                        .clip(RoundedCornerShape(16.dp))
                                        .background(if (disabled) t.pill else t.paper)
                                        .clickable(enabled = !disabled) {
                                            navController.navigate(Route.ApplyNew.withKind(k.name))
                                        }.padding(16.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                            ) {
                                Box(
                                    modifier =
                                        Modifier
                                            .size(52.dp)
                                            .clip(RoundedCornerShape(14.dp))
                                            .background(t.pill),
                                    contentAlignment = Alignment.Center,
                                ) {
                                    Icon(
                                        imageVector = k.icon,
                                        contentDescription = null,
                                        tint = if (disabled) t.inkFaint else primary,
                                        modifier = Modifier.size(22.dp),
                                    )
                                }
                                Spacer(Modifier.height(10.dp))
                                Text(
                                    k.name,
                                    color = if (disabled) t.inkFaint else t.ink,
                                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                                )
                                Spacer(Modifier.height(3.dp))
                                Text(
                                    k.sub,
                                    color = if (disabled) t.inkFaint else t.inkMute,
                                    style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp),
                                    textAlign = TextAlign.Center,
                                )
                            }
                        }
                        if (row.size == 1) Spacer(Modifier.weight(1f))
                    }
                }
            }
        }
    }
}
