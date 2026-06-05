package jp.tomoshibi.android.ui.screens.mypage

import android.widget.Toast
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
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Divider
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.BuildConfig
import jp.tomoshibi.android.data.model.ThemeMode
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SectionHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TToggle
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 通知设定页（L2）— 对齐 iOS MySettingsView（规格 §11 / 第 11 节）：
//   PageHeader「通知設定」level 2 + 5 行通知开关卡 + 暗色模式卡
//   + 演示版限定的「Push 通知 デモ」段（BuildConfig.DEBUG 包住，上线包不可见）
//   + 账号删除段（App Store 强制要求，Android 也保留）
@Composable
fun MySettingsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val ctx = LocalContext.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    // 5 个通知开关 — 纯 UI 本地态，默认全开（还没接后端，跟 iOS demo 屏一致）
    var pointReminder by remember { mutableStateOf(true) } // 「点呼リマインダー」开关
    var applResult by remember { mutableStateOf(true) } // 「申請結果」开关
    var pkgArrival by remember { mutableStateOf(true) } // 「荷物到着」开关
    var eventReminder by remember { mutableStateOf(true) } // 「活動リマインダー」开关
    var pointWarning by remember { mutableStateOf(true) } // 「減点警告」开关

    var showDeleteDialog by remember { mutableStateOf(false) } // 账号删除确认框开关

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            PageHeader(title = "通知設定", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                Spacer(Modifier.height(2.dp))

                // ── 通知开关卡：5 行 TToggle，行间分隔线 ──
                SuzuCard(padding = 0) {
                    ToggleRow("点呼リマインダー", pointReminder) { pointReminder = it }
                    RowDivider()
                    ToggleRow("申請結果", applResult) { applResult = it }
                    RowDivider()
                    ToggleRow("荷物到着", pkgArrival) { pkgArrival = it }
                    RowDivider()
                    ToggleRow("活動リマインダー", eventReminder) { eventReminder = it }
                    RowDivider()
                    ToggleRow("減点警告", pointWarning) { pointWarning = it }
                }

                // ── 暗色模式卡（「ダークモード」）：单行 + TToggle 绑 themeMode ──
                SuzuCard(padding = 0) {
                    ToggleRow(
                        label = "ダークモード",
                        checked = state.themeMode == ThemeMode.DARK,
                        onChange = { v ->
                            scope.launch {
                                store.update { it.copy(themeMode = if (v) ThemeMode.DARK else ThemeMode.LIGHT) }
                            }
                        },
                    )
                }

                // ── 演示版限定的「Push 通知 デモ」段（BuildConfig.DEBUG 包住，上线包不编译进去）──
                if (BuildConfig.DEBUG) {
                    SuzuCard {
                        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                            Text(
                                "⚠️ Push 通知 デモ",
                                color = tokens.warnDeep,
                                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                            )
                            Text(
                                "この section は demo 版限定です（production では非表示）。",
                                color = tokens.inkSub,
                                style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp),
                            )
                            DemoPushRow("学習欠席届 → 承認", ctx)
                            DemoPushRow("学習欠席届 → 不承認", ctx)
                            DemoPushRow("学習対象に追加された", ctx)
                            DemoPushRow("外泊届（修改届）が再承認された", ctx)
                        }
                    }
                }

                // ── 账号删除段 ──
                SectionHeader("アカウント")
                SuzuCard(padding = 0) {
                    Row(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .clickable { showDeleteDialog = true }
                                .padding(horizontal = 16.dp, vertical = 14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            "アカウントを削除",
                            color = tokens.danger,
                            modifier = Modifier.weight(1f),
                            style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.SemiBold),
                        )
                        Text("›", color = tokens.inkFaint, style = TextStyle(fontSize = 18.sp))
                    }
                }
                Text(
                    "削除すると元に戻せません。",
                    color = tokens.inkMute,
                    modifier = Modifier.padding(horizontal = 4.dp),
                    style = TextStyle(fontSize = 11.sp),
                )

                Spacer(Modifier.height(20.dp))
            }
        }
    }

    // 账号删除确认框
    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            confirmButton = {
                TextButton(onClick = {
                    scope.launch {
                        // demo 阶段无后端：清本地登录态 → 跳登录页（清空返回栈）
                        store.reset()
                        showDeleteDialog = false
                        navController.navigate(Route.Login.path) { popUpTo(0) { inclusive = true } }
                    }
                }) { Text("削除する", color = tokens.danger) }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = false }) { Text("キャンセル") }
            },
            title = { Text("アカウントを削除しますか？") },
            text = {
                Text(
                    "削除すると元に戻せません。点呼履歴・申請履歴・プロフィール情報がすべて閲覧できなくなります。",
                )
            },
            containerColor = tokens.paper,
        )
    }
}

// 通知开关单行 — 左标题 + 右 TToggle
@Composable
private fun ToggleRow(
    label: String,
    checked: Boolean,
    onChange: (Boolean) -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            label,
            color = t.ink,
            modifier = Modifier.weight(1f),
            style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium),
        )
        TToggle(checked = checked, onCheckedChange = onChange)
    }
}

// 行间分隔线（卡内左右留 16dp 内缩）
@Composable
private fun RowDivider() {
    val t = SuzuT.current
    Divider(
        color = t.hair,
        thickness = 0.5.dp,
        modifier = Modifier.padding(horizontal = 16.dp),
    )
}

// 演示段单行 — 🔔 铃铛 + 文案 + 「送信」按钮（点了弹 toast 即可）
@Composable
private fun DemoPushRow(
    label: String,
    ctx: android.content.Context,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(10.dp))
                .background(t.hairSoft)
                .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("🔔", style = TextStyle(fontSize = 16.sp))
        Spacer(Modifier.width(10.dp))
        Text(
            label,
            color = t.ink,
            modifier = Modifier.weight(1f),
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
        )
        Spacer(Modifier.width(8.dp))
        Box(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(99.dp))
                    .background(t.pill)
                    .clickable { Toast.makeText(ctx, "送信しました", Toast.LENGTH_SHORT).show() }
                    .padding(horizontal = 14.dp, vertical = 6.dp),
        ) {
            Text(
                "送信",
                color = androidx.compose.material3.MaterialTheme.colorScheme.primary,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
            )
        }
    }
}
