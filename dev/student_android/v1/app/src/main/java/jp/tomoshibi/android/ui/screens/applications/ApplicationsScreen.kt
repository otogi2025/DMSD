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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.Application
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.ApplicationsAPI
import jp.tomoshibi.android.data.network.endpoints.OutingsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

// 对齐 iOS ApplyListView：
//   头部 = 「申し込み」+ home 图标；筛选 chip =「すべて」/「審査中」/「承認済」/「下書き」
//   列表 = ApplicationsAPI.listMine + OutingsAPI.listMine 合并（外出 id 加 "outing:"）
//   FAB → 独立全屏「新規申請」种类页（非底部弹层）
@Composable
fun ApplicationsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val scope = rememberCoroutineScope()
    val store = LocalAppStore.current
    var filter by remember { mutableStateOf("all") }

    var ui by remember { mutableStateOf<LoadState<List<Application>>>(LoadState.Loading) }

    // 并行拉出寮届 + 外出，合并按提交时间倒序；401 → 清令牌跳登录。
    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                coroutineScope {
                    val appsDeferred = async { ApplicationsAPI.listMine().map { it.toUiApplication() } }
                    val outingsDeferred = async { OutingsAPI.listMine().map { it.toUiApplication() } }
                    val items =
                        (appsDeferred.await() + outingsDeferred.await())
                            .sortedByDescending { it.createdAt }
                    if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
                }
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) {
                    return
                }
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Box(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            Column(modifier = Modifier.fillMaxSize()) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 16.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        modifier =
                            Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .clickable {
                                    navController.navigate(Route.Home.path) {
                                        popUpTo(Route.Home.path) { inclusive = true }
                                    }
                                },
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(
                            imageVector = SuzuIcons.Home,
                            contentDescription = "ホームへ",
                            tint = tokens.ink,
                            modifier = Modifier.size(22.dp),
                        )
                    }
                    Spacer(Modifier.width(8.dp))
                    Text(
                        "申し込み",
                        color = tokens.ink,
                        style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold),
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(bottom = 16.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    listOf(
                        "all" to "すべて",
                        "pending" to "審査中",
                        "approved" to "承認済",
                        "draft" to "下書き",
                    ).forEach { (k, l) ->
                        val active = filter == k
                        Box(
                            modifier =
                                Modifier
                                    .clip(RoundedCornerShape(99.dp))
                                    .background(if (active) primary else tokens.pill)
                                    .clickable { filter = k }
                                    .padding(horizontal = 14.dp, vertical = 7.dp),
                        ) {
                            Text(
                                l,
                                color = if (active) Color.White else primary,
                                style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold),
                            )
                        }
                    }
                }

                when (val s = ui) {
                    LoadState.Loading -> {
                        Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
                            LoadingBox()
                        }
                    }

                    is LoadState.Failed -> {
                        Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
                            FailedBox(s.message, onRetry = { scope.launch { load() } })
                        }
                    }

                    LoadState.Empty -> {
                        Box(modifier = Modifier.weight(1f).fillMaxWidth(), contentAlignment = Alignment.Center) {
                            ApplicationsEmptyCard()
                        }
                    }

                    is LoadState.Success -> {
                        val filtered =
                            s.value.filter { app ->
                                when (filter) {
                                    "all" -> true

                                    "pending" -> app.status == ApplicationStatus.PENDING

                                    // 「承認済」tab 同时收承認済与一部承認（映射后都是 APPROVED）
                                    "approved" -> app.status == ApplicationStatus.APPROVED

                                    "draft" -> false

                                    else -> true
                                }
                            }

                        Column(
                            modifier =
                                Modifier
                                    .weight(1f)
                                    .fillMaxWidth()
                                    .verticalScroll(rememberScrollState())
                                    .padding(horizontal = 16.dp),
                            verticalArrangement = Arrangement.spacedBy(10.dp),
                        ) {
                            if (filtered.isEmpty()) {
                                ApplicationsEmptyCard()
                            }
                            filtered.forEach { app ->
                                ApplicationRow(
                                    kind = app.kind,
                                    summary = app.dest,
                                    date = app.createdAt,
                                    status = app.status,
                                    onClick = { navController.navigate("applications/${app.id}") },
                                )
                            }
                            Spacer(Modifier.height(120.dp))
                        }
                    }
                }
            }

            // FAB → 独立全屏「新規申請」种类页（对齐 iOS ApplyNewView）
            Box(
                modifier =
                    Modifier
                        .align(Alignment.BottomEnd)
                        .padding(end = 18.dp, bottom = 96.dp)
                        .size(56.dp)
                        .shadow(
                            elevation = 12.dp,
                            shape = RoundedCornerShape(18.dp),
                            spotColor = primary.copy(alpha = 0.35f),
                            ambientColor = primary.copy(alpha = 0.35f),
                        ).clip(RoundedCornerShape(18.dp))
                        .background(primary)
                        .clickable { navController.navigate(Route.ApplyNewSelect.path) },
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = SuzuIcons.Plus,
                    contentDescription = "新規申請",
                    tint = Color.White,
                    modifier = Modifier.size(24.dp),
                )
            }
        }
    }
}

@Composable
private fun ApplicationRow(
    kind: String,
    summary: String,
    date: String,
    status: ApplicationStatus,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier =
                    Modifier
                        .size(40.dp)
                        .clip(RoundedCornerShape(10.dp))
                        .background(t.pill),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = iconForKind(kind),
                    contentDescription = null,
                    tint = primary,
                    modifier = Modifier.size(20.dp),
                )
            }
            Spacer(Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        kind,
                        color = t.ink,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                    )
                    Spacer(Modifier.width(8.dp))
                    ApplicationStatusPill(status, kind = kind)
                }
                Spacer(Modifier.height(3.dp))
                Text(
                    summary,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp),
                )
            }
        }
        Spacer(Modifier.height(8.dp))
        Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
        Spacer(Modifier.height(8.dp))
        Text(
            date,
            color = t.inkMute,
            style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
        )
    }
}

@Composable
private fun ApplicationsEmptyCard() {
    val tokens = SuzuT.current
    Column(
        modifier = Modifier.fillMaxWidth().padding(vertical = 60.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Text("📋", style = TextStyle(fontSize = 40.sp))
        Text(
            "申請はありません",
            color = tokens.inkSub,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
        )
        Text(
            "下の＋ボタンから新規作成できます",
            color = tokens.inkMute,
            style = TextStyle(fontSize = 12.sp),
        )
    }
}

@Composable
internal fun ApplicationStatusPill(
    status: ApplicationStatus,
    kind: String = "",
) {
    val tokens = SuzuT.current
    val label = rowStatusLabel(kind, status)
    val (bg, fg) =
        when (status) {
            ApplicationStatus.PENDING -> tokens.warnBg to tokens.warnDeep
            ApplicationStatus.APPROVED -> tokens.okBg to tokens.okDeep
            ApplicationStatus.RETURNED -> tokens.dangerBg to tokens.danger
            ApplicationStatus.REJECTED -> tokens.dangerBg to tokens.danger
            ApplicationStatus.WITHDRAWN -> tokens.pill to tokens.inkMute
        }
    Box(
        modifier =
            Modifier
                .clip(RoundedCornerShape(99.dp))
                .background(bg)
                .padding(horizontal = 10.dp, vertical = 4.dp),
    ) {
        Text(
            label,
            color = fg,
            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}
