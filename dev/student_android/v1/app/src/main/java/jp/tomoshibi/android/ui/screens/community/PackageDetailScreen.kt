package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.HorizontalDivider
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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.FrontDeskAPI
import jp.tomoshibi.android.data.network.endpoints.FrontDeskItemOut
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

// 宅配詳細 — 对齐 iOS PackageDetailView 生产分支：
//   meta：内容 / 件数 / 到着 / 状態（+ 保管場所非空才显）
//   无「受取確認」按钮（生产无学生自助确认端点）
@Composable
fun PackageDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<FrontDeskItemOut>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = FrontDeskAPI.listMine()
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
            PageHeader(title = "宅配詳細", level = 2, onLeft = { navController.popBackStack() })

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox(useSpinner = true)
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    EmptyState(title = "荷物が見つかりません", icon = SuzuIcons.Pkg)
                }

                is LoadState.Success -> {
                    val pkg = s.value
                    val arrivedIso = pkg.notifiedAt ?: pkg.createdAt
                    val rows =
                        buildList {
                            add("内容" to packageTitle(pkg))
                            add("件数" to "${pkg.itemCount}件")
                            add("到着" to formatPkgArrived(arrivedIso))
                            add("状態" to packageStatusLabel(pkg.status))
                            val loc = pkg.location?.takeIf { it.isNotBlank() }
                            if (loc != null) add("保管場所" to loc)
                        }

                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                    ) {
                        SuzuCard(padding = 20) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.Center,
                            ) {
                                Text("📦", style = TextStyle(fontSize = 56.sp))
                            }
                            Spacer(Modifier.height(14.dp))
                            rows.forEach { (label, value) ->
                                MetaRow(label, value)
                            }
                        }
                        // 生产版故意不放「受取確認」——取走由老师标记 / NFC（v1.1+）
                        Spacer(Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun MetaRow(
    label: String,
    value: String,
) {
    val t = SuzuT.current
    HorizontalDivider(color = t.hair, thickness = 0.5.dp)
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = t.inkSub, style = TextStyle(fontSize = 13.sp))
        Spacer(modifier = Modifier.weight(1f))
        Text(
            value,
            color = t.ink,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}
