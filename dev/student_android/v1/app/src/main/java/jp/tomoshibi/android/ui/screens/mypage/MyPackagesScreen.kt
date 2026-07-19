package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.FrontDeskAPI
import jp.tomoshibi.android.data.network.endpoints.FrontDeskItemOut
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.screens.community.formatPkgDate
import jp.tomoshibi.android.ui.screens.community.isWaiting
import jp.tomoshibi.android.ui.screens.community.packageTitle
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 荷物受取履歴 — 对齐 iOS MyPackagesView 生产分支：
//   与宅配一覧同源 GET /front-desk/mine；点卡进 PackageDetail
@Composable
fun MyPackagesScreen(navController: NavHostController) {
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<List<FrontDeskItemOut>>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = FrontDeskAPI.listMine()
                if (store.snapshot().authToken != tokenAtStart) return
                store.replacePackages(items)
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return
                LoadState.Failed(e.display)
            } catch (_: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "荷物受取履歴",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    EmptyState(title = "なし", icon = SuzuIcons.Pkg)
                }

                is LoadState.Success -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        s.value.forEach { pkg ->
                            PackageHistoryCard(
                                pkg = pkg,
                                onClick = {
                                    navController.navigate(Route.PackageDetail(pkg.id).path)
                                },
                            )
                        }
                        Spacer(modifier = Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun PackageHistoryCard(
    pkg: FrontDeskItemOut,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val waiting = pkg.isWaiting
    SuzuCard(
        padding = 14,
        modifier = Modifier.clickable(onClick = onClick),
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("📦", style = TextStyle(fontSize = 28.sp))
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    packageTitle(pkg),
                    color = t.ink,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    formatPkgDate(pkg.createdAt),
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Pill(
                text = if (waiting) "受取待ち" else "受取済",
                tone = if (waiting) PillTone.Warn else PillTone.Neutral,
            )
        }
    }
}
