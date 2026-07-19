package jp.tomoshibi.android.ui.screens.mypage

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
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
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
import jp.tomoshibi.android.data.network.ApiErrorPresenter
import jp.tomoshibi.android.data.network.endpoints.AccountsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.data.translate.TranslateLang
import jp.tomoshibi.android.data.translate.TranslatePrefs
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SectionHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TToggle
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 设定页（L2）— 对齐 iOS MySettingsView（已删暗色模式死开关）
@Composable
fun MySettingsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val ctx = LocalContext.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val primary = MaterialTheme.colorScheme.primary

    // 5 个通知开关 — 纯 UI 本地态，默认全开（还没接后端，跟 iOS demo 屏一致）
    var pointReminder by remember { mutableStateOf(true) }
    var applResult by remember { mutableStateOf(true) }
    var pkgArrival by remember { mutableStateOf(true) }
    var eventReminder by remember { mutableStateOf(true) }
    var pointWarning by remember { mutableStateOf(true) }

    var showDeleteDialog by remember { mutableStateOf(false) }
    var showDeleteFailed by remember { mutableStateOf(false) }
    var deleteFailedMsg by remember { mutableStateOf("") }
    var isDeleting by remember { mutableStateOf(false) }

    // 默认翻译语言（空串 = 「毎回選択する」；与公告详情共用 TranslatePrefs）
    var defaultTranslateLang by remember { mutableStateOf(TranslatePrefs.getDefaultLang(ctx)) }
    val translateOptions =
        remember {
            listOf("" to "毎回選択する") + TranslateLang.entries.map { it.code to it.shortLabel }
        }

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            PageHeader(title = "設定", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                Spacer(Modifier.height(2.dp))

                // ── 「お知らせの翻訳」默认语言（对齐 iOS translateSettingSection）──
                Text(
                    "お知らせの翻訳",
                    color = tokens.inkMute,
                    style =
                        TextStyle(
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 0.6.sp,
                        ),
                )
                SuzuCard(padding = 0) {
                    translateOptions.forEachIndexed { idx, (code, label) ->
                        if (idx > 0) {
                            RowDivider()
                        }
                        Row(
                            modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .clickable {
                                        defaultTranslateLang = code
                                        TranslatePrefs.setDefaultLang(ctx, code)
                                    }.padding(horizontal = 18.dp, vertical = 14.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                label,
                                color = tokens.ink,
                                modifier = Modifier.weight(1f),
                                style = TextStyle(fontSize = 14.sp),
                            )
                            if (defaultTranslateLang == code) {
                                Text(
                                    "✓",
                                    color = primary,
                                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                                )
                            }
                        }
                    }
                }
                Text(
                    "お知らせ詳細の「翻訳」から、本文を選んだ言語に翻訳できます。",
                    color = tokens.inkMute,
                    modifier = Modifier.padding(horizontal = 4.dp),
                    style = TextStyle(fontSize = 11.sp),
                )

                // ── 通知开关卡 ──
                Text(
                    "通知",
                    color = tokens.inkMute,
                    style =
                        TextStyle(
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 0.6.sp,
                        ),
                )
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
                            DemoPushRow("夜学習欠席届 → 承認", ctx)
                            DemoPushRow("夜学習欠席届 → 不承認", ctx)
                            DemoPushRow("夜学習対象に追加された", ctx)
                            DemoPushRow("外泊届（変更届）が再承認された", ctx)
                        }
                    }
                }

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

    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { if (!isDeleting) showDeleteDialog = false },
            confirmButton = {
                TextButton(
                    enabled = !isDeleting,
                    onClick = {
                        scope.launch {
                            isDeleting = true
                            val tokenAtStart = store.snapshot().authToken
                            try {
                                AccountsAPI.deleteMyAccount()
                                if (store.snapshot().authToken != tokenAtStart) return@launch
                                store.clearSession()
                                showDeleteDialog = false
                                navController.navigate(Route.Login.path) {
                                    popUpTo(0) { inclusive = true }
                                }
                            } catch (e: Exception) {
                                deleteFailedMsg =
                                    ApiErrorPresenter.userMessage(e, "削除に失敗しました")
                                showDeleteDialog = false
                                showDeleteFailed = true
                            } finally {
                                isDeleting = false
                            }
                        }
                    },
                ) {
                    Text(if (isDeleting) "削除中…" else "削除する", color = tokens.danger)
                }
            },
            dismissButton = {
                TextButton(
                    enabled = !isDeleting,
                    onClick = { showDeleteDialog = false },
                ) { Text("キャンセル") }
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

    if (showDeleteFailed) {
        AlertDialog(
            onDismissRequest = { showDeleteFailed = false },
            confirmButton = {
                TextButton(onClick = { showDeleteFailed = false }) { Text("OK") }
            },
            title = { Text("削除に失敗しました") },
            text = { Text(deleteFailedMsg) },
            containerColor = tokens.paper,
        )
    }
}

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

@Composable
private fun RowDivider() {
    val t = SuzuT.current
    Divider(
        color = t.hair,
        thickness = 0.5.dp,
        modifier = Modifier.padding(horizontal = 16.dp),
    )
}

@Composable
private fun DemoPushRow(
    label: String,
    ctx: android.content.Context,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
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
                    .clickable { store.showToast("送信しました") }
                    .padding(horizontal = 14.dp, vertical = 6.dp),
        ) {
            Text(
                "送信",
                color = MaterialTheme.colorScheme.primary,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
            )
        }
    }
}
