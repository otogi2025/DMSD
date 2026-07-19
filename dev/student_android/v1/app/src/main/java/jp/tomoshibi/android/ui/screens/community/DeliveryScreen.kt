package jp.tomoshibi.android.ui.screens.community

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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
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
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
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
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 宅配一覧 — 对齐 iOS PackagesView 生产分支：
//   PageHeader「宅配」+「受取待ち/受取済」tab + GET /front-desk/mine
//   「受取」pill 仅视觉展示（整卡进详情）；学生无自助确认收货
@Composable
fun DeliveryScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var tab by remember { mutableStateOf("wait") } // wait / done
    var ui by remember { mutableStateOf<LoadState<List<FrontDeskItemOut>>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = FrontDeskAPI.listMine()
                if (store.snapshot().authToken != tokenAtStart) return
                // 写回 AppStore 缓存，供通知中心 / 首页角标共用
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

    val all = (ui as? LoadState.Success)?.value.orEmpty()
    val waitList = all.filter { it.isWaiting }
    val doneList = all.filter { !it.isWaiting }
    val shown = if (tab == "wait") waitList else doneList

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            PageHeader(title = "宅配", level = 2, onLeft = { navController.popBackStack() })

            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(tokens.hairSoft)
                        .padding(4.dp),
                horizontalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                SegTab(
                    "受取待ち · ${waitList.size}",
                    tab == "wait",
                    Modifier.weight(1f),
                ) { tab = "wait" }
                SegTab(
                    "受取済 · ${doneList.size}",
                    tab == "done",
                    Modifier.weight(1f),
                ) { tab = "done" }
            }

            Spacer(Modifier.height(16.dp))

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty, is LoadState.Success -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        if (shown.isEmpty()) {
                            val emptyTitle =
                                if (tab == "wait") {
                                    "受取待ちの荷物はありません"
                                } else {
                                    "受取済の荷物はありません"
                                }
                            EmptyState(title = emptyTitle, icon = SuzuIcons.Pkg)
                        }
                        shown.forEach { pkg ->
                            PackageRow(
                                pkg = pkg,
                                showReceivePill = pkg.isWaiting,
                                onClick = {
                                    navController.navigate(Route.PackageDetail(pkg.id).path)
                                },
                            )
                        }
                        Spacer(Modifier.height(20.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun SegTab(
    label: String,
    active: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            modifier
                .clip(RoundedCornerShape(9.dp))
                .background(if (active) t.paper else Color.Transparent)
                .clickable(onClick = onClick)
                .padding(vertical = 9.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            color = if (active) t.ink else t.inkMute,
            style =
                TextStyle(
                    fontSize = 13.sp,
                    fontWeight = if (active) FontWeight.Bold else FontWeight.Medium,
                ),
        )
    }
}

@Composable
private fun PackageRow(
    pkg: FrontDeskItemOut,
    showReceivePill: Boolean,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("📦", style = TextStyle(fontSize = 28.sp))
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            // 生产标题 = description（空则「荷物N件」）；不拼「荷物」后缀
            Text(
                packageTitle(pkg),
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
            )
            Spacer(Modifier.height(2.dp))
            Text(
                formatPkgDate(pkg.createdAt),
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
            )
        }
        // 「受取」仅视觉 pill，不可单独点确认（整卡进详情）
        if (showReceivePill) {
            Spacer(Modifier.width(8.dp))
            Box(
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(10.dp))
                        .background(t.btnGrad)
                        .padding(horizontal = 16.dp, vertical = 8.dp),
            ) {
                Text(
                    "受取",
                    color = Color.White,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                )
            }
        }
    }
}

/** pending / notified = 待取 */
internal val FrontDeskItemOut.isWaiting: Boolean
    get() = status == "pending" || status == "notified"

internal fun packageTitle(pkg: FrontDeskItemOut): String = if (pkg.description.isBlank()) "荷物${pkg.itemCount}件" else pkg.description

internal fun packageStatusLabel(status: String): String =
    when (status) {
        "pending", "notified" -> "受取待ち"
        "picked_up" -> "受取済"
        "expired" -> "期限切れ"
        "discarded" -> "処分済"
        else -> status
    }

internal fun formatPkgDate(iso: String): String = formatIsoJst(iso, "yyyy-MM-dd")

internal fun formatPkgArrived(iso: String): String = formatIsoJst(iso, "yyyy-MM-dd HH:mm")

private fun formatIsoJst(
    iso: String,
    pattern: String,
): String {
    val instant =
        jp.tomoshibi.android.data.format.JstDate
            .parseInstant(iso)
            ?: return iso.take(16).replace('T', ' ')
    return java.time.format.DateTimeFormatter
        .ofPattern(pattern)
        .withZone(jp.tomoshibi.android.data.format.JstDate.TOKYO)
        .format(instant)
}
