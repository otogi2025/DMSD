package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.RollCallReportOut
import jp.tomoshibi.android.data.network.endpoints.RollCallReportsAPI
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

// 体調報告履歴 — 对齐 iOS MyHealthView 生产分支：
//   GET /rollcall/reports/mine → filter kind==health；三态 + 401 清会话

@Composable
fun MyHealthScreen(navController: NavHostController) {
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<List<RollCallReportOut>>>(LoadState.Loading) }
    var sessionExpired by remember { mutableStateOf(false) }

    suspend fun load() {
        ui = LoadState.Loading
        sessionExpired = false
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items =
                    RollCallReportsAPI
                        .listMine()
                        .filter { it.kind == "health" }
                if (store.snapshot().authToken != tokenAtStart) return
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError.Unauthorized) {
                store.handleIfUnauthorized(e, tokenAtStart)
                sessionExpired = true
                LoadState.Failed("セッションの有効期限が切れました。再度ログインしてください。")
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) {
                    sessionExpired = true
                    return
                }
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
            PageHeader(title = "体調報告履歴", level = 2, onLeft = { navController.popBackStack() })

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    if (sessionExpired) {
                        EmptyState(
                            title = "セッションの有効期限が切れました。再度ログインしてください。",
                            icon = SuzuIcons.Warn,
                        )
                    } else {
                        FailedBox(s.message, onRetry = { scope.launch { load() } })
                    }
                }

                LoadState.Empty -> {
                    EmptyState(title = "体調報告はありません", icon = SuzuIcons.Face)
                }

                is LoadState.Success -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        s.value.forEach { rec ->
                            HealthCard(rec)
                        }
                        Spacer(modifier = Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun HealthCard(rec: RollCallReportOut) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Text(
            isoToYmd(rec.createdAt),
            color = t.inkMute,
            style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
        )
        Spacer(modifier = Modifier.height(6.dp))
        Text(
            rec.body,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
        )
    }
}
