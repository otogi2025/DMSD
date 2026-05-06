package jp.tomoshibi.android.ui.screens.community

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.MusicRequest
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.MonoNumeralStyle
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 紫色 ♪ 圆 — 用 React tokens.jsx 紫调（M3 默认 colorScheme primary 覆盖会带来歧义，
// 这里固定一个紫值与 iOS Music 一致；不是主题色，所以不走 SuzuT）
private val MusicPurple = Color(0xFF8B5CF6)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MusicScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    var sort by remember { mutableStateOf("popular") }
    var addOpen by remember { mutableStateOf(false) }
    var reportFor by remember { mutableStateOf<String?>(null) }

    val sorted = remember(state.musicRequests, sort) {
        when (sort) {
            "popular" -> state.musicRequests.sortedByDescending { it.votes }
            else -> state.musicRequests.reversed() // 新着 = 后加的在前（mock 简化）
        }
    }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // ── header ──
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 18.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier.size(44.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center
                ) {
                    Icon(SuzuIcons.ChevL, contentDescription = "戻る", tint = tokens.ink, modifier = Modifier.size(24.dp))
                }
                Spacer(Modifier.width(4.dp))
                Text("リクエスト曲", color = tokens.ink, modifier = Modifier.weight(1f),
                    style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
                Box(
                    modifier = Modifier.size(40.dp).clip(CircleShape).background(tokens.btnGrad)
                        .clickable { addOpen = true },
                    contentAlignment = Alignment.Center
                ) {
                    Text("+", color = Color.White, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
                }
            }

            // ── hint banner ──
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp)
                    .clip(RoundedCornerShape(14.dp))
                    .background(tokens.warnBg)
                    .border(1.dp, tokens.warn, RoundedCornerShape(14.dp))
                    .padding(horizontal = 14.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(SuzuIcons.Info, contentDescription = null, tint = tokens.warnDeep, modifier = Modifier.size(18.dp))
                Spacer(Modifier.width(8.dp))
                Text(
                    text = "投稿は寮内放送のみ。著作権配慮で YouTube リンク共有",
                    color = tokens.warnDeep,
                    style = TextStyle(fontSize = 12.sp, lineHeight = 16.sp)
                )
            }
            Spacer(Modifier.height(12.dp))

            // ── sort tabs ──
            Row(
                modifier = Modifier.padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf("popular" to "人気順", "new" to "新着順").forEach { (k, l) ->
                    val active = sort == k
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(99.dp))
                            .background(if (active) tokens.ink else tokens.paper)
                            .then(if (active) Modifier else Modifier.border(1.dp, tokens.hair, RoundedCornerShape(99.dp)))
                            .clickable { sort = k }
                            .padding(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text(l,
                            color = if (active) tokens.pearl else tokens.inkSub,
                            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
                    }
                }
            }
            Spacer(Modifier.height(12.dp))

            // ── list ──
            Column(
                modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState())
                    .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                sorted.forEach { req ->
                    val voted = state.musicVotes[req.id] == "up"
                    Row(
                        modifier = Modifier.fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(tokens.paper)
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier.size(32.dp).clip(CircleShape).background(MusicPurple),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("♪", color = Color.White,
                                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
                        }
                        Spacer(Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(req.title, color = tokens.ink,
                                style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold))
                            Spacer(Modifier.height(2.dp))
                            Text(req.artist, color = tokens.inkSub,
                                style = TextStyle(fontSize = 12.sp))
                            Spacer(Modifier.height(4.dp))
                            Text(
                                text = "通報",
                                color = tokens.danger,
                                modifier = Modifier.clickable { reportFor = req.id },
                                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium)
                            )
                        }
                        Spacer(Modifier.width(8.dp))
                        Text(
                            text = "${req.votes}",
                            color = tokens.ink,
                            style = MonoNumeralStyle.copy(fontSize = 16.sp, lineHeight = 20.sp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Box(
                            modifier = Modifier.size(36.dp).clip(CircleShape)
                                .background(if (voted) tokens.pill else tokens.hairSoft)
                                .clickable {
                                    if (!voted) {
                                        scope.launch {
                                            store.update { s ->
                                                s.copy(
                                                    musicVotes = s.musicVotes + (req.id to "up"),
                                                    musicRequests = s.musicRequests.map {
                                                        if (it.id == req.id) it.copy(votes = it.votes + 1) else it
                                                    }
                                                )
                                            }
                                        }
                                    }
                                },
                            contentAlignment = Alignment.Center
                        ) {
                            Text("↑", color = if (voted) tokens.ink else tokens.inkSub,
                                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }

    // ── add dialog ──
    if (addOpen) {
        AddRequestDialog(
            onDismiss = { addOpen = false },
            onSubmit = { title, artist, _ ->
                scope.launch {
                    store.update { s ->
                        s.copy(
                            musicRequests = s.musicRequests + MusicRequest(
                                id = "M-${System.currentTimeMillis()}",
                                title = title,
                                artist = artist,
                                votes = 0
                            )
                        )
                    }
                }
                addOpen = false
            }
        )
    }

    // ── report bottom sheet ──
    if (reportFor != null) {
        val sheetState = rememberModalBottomSheetState()
        ModalBottomSheet(
            onDismissRequest = { reportFor = null },
            sheetState = sheetState,
            containerColor = tokens.paper
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(bottom = 24.dp)
            ) {
                Text("通報の理由", color = tokens.ink,
                    style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold))
                Spacer(Modifier.height(12.dp))
                listOf("著作権", "不適切", "その他").forEach { reason ->
                    Box(
                        modifier = Modifier.fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .border(1.dp, tokens.hair, RoundedCornerShape(12.dp))
                            .clickable { reportFor = null }
                            .padding(horizontal = 14.dp, vertical = 14.dp)
                    ) {
                        Text(reason, color = tokens.ink,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium))
                    }
                    Spacer(Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun AddRequestDialog(
    onDismiss: () -> Unit,
    onSubmit: (title: String, artist: String, url: String) -> Unit
) {
    val tokens = SuzuT.current
    var title by remember { mutableStateOf("") }
    var artist by remember { mutableStateOf("") }
    var url by remember { mutableStateOf("") }

    Dialog(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier.fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(tokens.paper)
                .padding(20.dp)
        ) {
            Text("リクエスト投稿", color = tokens.ink,
                style = TextStyle(fontSize = 18.sp, fontWeight = FontWeight.Bold))
            Spacer(Modifier.height(14.dp))
            DialogField("曲名", title, KeyboardType.Text) { title = it }
            Spacer(Modifier.height(10.dp))
            DialogField("アーティスト", artist, KeyboardType.Text) { artist = it }
            Spacer(Modifier.height(10.dp))
            DialogField("YouTube URL", url, KeyboardType.Uri) { url = it }
            Spacer(Modifier.height(16.dp))
            Row(horizontalArrangement = Arrangement.End, modifier = Modifier.fillMaxWidth()) {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(99.dp))
                        .clickable { onDismiss() }
                        .padding(horizontal = 16.dp, vertical = 10.dp)
                ) {
                    Text("キャンセル", color = tokens.inkSub,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
                }
                Spacer(Modifier.width(8.dp))
                val canSubmit = title.isNotBlank() && artist.isNotBlank()
                // Brush 与 Color 不能混在三元里 — 分支构造 Modifier 再 then
                val submitBg = if (canSubmit)
                    Modifier.background(tokens.btnGrad)
                else
                    Modifier.background(tokens.hairSoft)
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(99.dp))
                        .then(submitBg)
                        .clickable(enabled = canSubmit) { onSubmit(title.trim(), artist.trim(), url.trim()) }
                        .padding(horizontal = 18.dp, vertical = 10.dp)
                ) {
                    Text("送信",
                        color = if (canSubmit) Color.White else tokens.inkFaint,
                        style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
                }
            }
        }
    }
}

@Composable
private fun DialogField(label: String, value: String, kind: KeyboardType, onChange: (String) -> Unit) {
    val tokens = SuzuT.current
    Column {
        Text(label, color = tokens.inkSub,
            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium))
        Spacer(Modifier.height(4.dp))
        Box(
            modifier = Modifier.fillMaxWidth()
                .clip(RoundedCornerShape(10.dp))
                .border(1.dp, tokens.hair, RoundedCornerShape(10.dp))
                .padding(horizontal = 12.dp, vertical = 10.dp)
        ) {
            BasicTextField(
                value = value,
                onValueChange = onChange,
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = kind),
                textStyle = TextStyle(color = tokens.ink, fontSize = 14.sp),
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}
