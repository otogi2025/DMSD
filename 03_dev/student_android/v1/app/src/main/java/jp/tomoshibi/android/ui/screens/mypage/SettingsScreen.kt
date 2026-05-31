package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Divider
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.ThemeMode
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

@Composable
fun SettingsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    var pushEnabled by remember { mutableStateOf(true) }
    var emailEnabled by remember { mutableStateOf(false) }
    var showResetDialog by remember { mutableStateOf(false) }

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 顶部 ← + 設定
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Text("←", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
                }
                Spacer(Modifier.width(8.dp))
                Text("設定", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }

            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp),
            ) {
                // 表示
                SectionHeader("表示")
                Column(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper)) {
                    SwitchRow(
                        label = "ダークモード",
                        sub = "暗い背景に切り替え",
                        checked = state.themeMode == ThemeMode.DARK,
                        onChange = { v ->
                            scope.launch {
                                store.update { it.copy(themeMode = if (v) ThemeMode.DARK else ThemeMode.LIGHT) }
                            }
                        },
                    )
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    Column(modifier = Modifier.padding(horizontal = 18.dp, vertical = 14.dp)) {
                        Text(
                            "文字サイズ",
                            color = tokens.ink,
                            style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium),
                        )
                        Text(
                            "読みやすさを調整",
                            color = tokens.inkMute,
                            style = TextStyle(fontSize = 11.sp),
                        )
                        Spacer(Modifier.height(10.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            listOf(0.9f to "小", 1.0f to "中", 1.15f to "大").forEach { (scale, label) ->
                                val active = kotlin.math.abs(state.fontScale - scale) < 0.05f
                                Box(
                                    modifier =
                                        Modifier
                                            .weight(1f)
                                            .clip(RoundedCornerShape(10.dp))
                                            .background(if (active) tokens.ink else tokens.pill)
                                            .clickable { scope.launch { store.update { it.copy(fontScale = scale) } } }
                                            .padding(vertical = 10.dp),
                                    contentAlignment = Alignment.Center,
                                ) {
                                    Text(
                                        label,
                                        color = if (active) tokens.pearl else tokens.ink,
                                        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
                                    )
                                }
                            }
                        }
                    }
                }

                // アカウント
                SectionHeader("アカウント")
                Column(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper)) {
                    SwitchRow("プッシュ通知", "新しい通知を受け取る", pushEnabled) { pushEnabled = it }
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    SwitchRow("メール通知", "重要な通知をメールでも受信", emailEnabled) { emailEnabled = it }
                }

                // その他
                SectionHeader("その他")
                Column(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper)) {
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                "バージョン",
                                color = tokens.ink,
                                style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium),
                            )
                        }
                        Text(
                            jp.tomoshibi.android.BuildConfig.VERSION_NAME,
                            color = tokens.inkMute,
                            style =
                                TextStyle(
                                    fontSize = 13.sp,
                                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                                ),
                        )
                    }
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    NavRow("プライバシーポリシー") { /* TODO web link */ }
                    Divider(color = tokens.hair, thickness = 0.5.dp)
                    NavRow("利用規約") { /* TODO */ }
                }

                // データ初期化（red）
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .height(52.dp)
                            .clip(RoundedCornerShape(14.dp))
                            .border(1.5.dp, tokens.danger.copy(alpha = 0.4f), RoundedCornerShape(14.dp))
                            .clickable { showResetDialog = true },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        "データを初期化",
                        color = tokens.danger,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                    )
                }

                Spacer(Modifier.height(20.dp))
            }
        }
    }

    if (showResetDialog) {
        AlertDialog(
            onDismissRequest = { showResetDialog = false },
            confirmButton = {
                TextButton(onClick = {
                    scope.launch {
                        store.reset()
                        showResetDialog = false
                        navController.navigate(Route.Splash.path) { popUpTo(0) { inclusive = true } }
                    }
                }) { Text("初期化", color = tokens.danger) }
            },
            dismissButton = {
                TextButton(onClick = { showResetDialog = false }) { Text("キャンセル") }
            },
            title = { Text("データを初期化しますか？") },
            text = { Text("すべての保存データが削除されます。この操作は取り消せません。") },
            containerColor = tokens.paper,
        )
    }
}

@Composable
private fun SectionHeader(text: String) {
    val t = SuzuT.current
    Text(
        text,
        color = t.inkSub,
        modifier = Modifier.padding(horizontal = 4.dp),
        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp),
    )
}

@Composable
private fun SwitchRow(
    label: String,
    sub: String,
    checked: Boolean,
    onChange: (Boolean) -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 18.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(label, color = t.ink, style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium))
            Text(sub, color = t.inkMute, style = TextStyle(fontSize = 11.sp))
        }
        Switch(
            checked = checked,
            onCheckedChange = onChange,
            colors =
                SwitchDefaults.colors(
                    checkedThumbColor = Color.White,
                    checkedTrackColor = t.ok,
                    uncheckedThumbColor = Color.White,
                    uncheckedTrackColor = t.hair,
                ),
        )
    }
}

@Composable
private fun NavRow(
    label: String,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick).padding(horizontal = 18.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            label,
            color = t.ink,
            modifier = Modifier.weight(1f),
            style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium),
        )
        Text("›", color = t.inkMute, style = TextStyle(fontSize = 18.sp))
    }
}
