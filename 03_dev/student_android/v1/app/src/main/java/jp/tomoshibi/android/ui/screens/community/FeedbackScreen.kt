package jp.tomoshibi.android.ui.screens.community

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

// 匿名フィードバック — 寮運営への建議
// 以 JSON 字符串拼接形式存进 AppState.feedback（List<String>），P6 接 backend 时切换
@Composable
fun FeedbackScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val ctx = LocalContext.current
    val scope = rememberCoroutineScope()

    var category by remember { mutableStateOf<String?>(null) }
    var mood by remember { mutableStateOf<String?>(null) }
    var text by remember { mutableStateOf("") }

    val maxLen = 500
    val canSubmit = category != null && mood != null && text.isNotBlank()

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .background(tokens.pearl)
                    .verticalScroll(rememberScrollState()),
        ) {
            // 头部
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp).padding(top = 18.dp, bottom = 4.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(44.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(SuzuIcons.ChevL, contentDescription = "戻る", tint = tokens.ink, modifier = Modifier.size(24.dp))
                }
                Spacer(Modifier.width(4.dp))
                Column {
                    Text(
                        "匿名フィードバック",
                        color = tokens.ink,
                        style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold),
                    )
                    Text(
                        "寮運営への匿名建議",
                        color = tokens.inkSub,
                        style = TextStyle(fontSize = 13.sp),
                    )
                }
            }
            Spacer(Modifier.height(16.dp))

            // カテゴリー
            Text(
                "カテゴリー",
                color = tokens.inkSub,
                modifier = Modifier.padding(horizontal = 16.dp),
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium),
            )
            Spacer(Modifier.height(8.dp))
            Row(
                modifier = Modifier.padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                listOf("設備", "運営", "食事", "その他").forEach { c ->
                    val active = category == c
                    Box(
                        modifier =
                            Modifier
                                .clip(RoundedCornerShape(99.dp))
                                .background(if (active) tokens.ink else tokens.paper)
                                .then(if (active) Modifier else Modifier.border(1.dp, tokens.hair, RoundedCornerShape(99.dp)))
                                .clickable { category = c }
                                .padding(horizontal = 14.dp, vertical = 8.dp),
                    ) {
                        Text(
                            c,
                            color = if (active) tokens.pearl else tokens.inkSub,
                            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                        )
                    }
                }
            }
            Spacer(Modifier.height(20.dp))

            // 気持ち（emoji 5 chip）
            Text(
                "気持ち",
                color = tokens.inkSub,
                modifier = Modifier.padding(horizontal = 16.dp),
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium),
            )
            Spacer(Modifier.height(8.dp))
            val moods =
                listOf(
                    "happy" to "😊嬉しい",
                    "neutral" to "😐普通",
                    "trouble" to "😟困った",
                    "angry" to "😠不満",
                    "idea" to "💡提案",
                )
            // 用 FlowRow 太重，改为两行 Row 排
            Column(modifier = Modifier.padding(horizontal = 16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    moods.take(3).forEach { (k, l) -> MoodChip(k, l, mood == k) { mood = k } }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    moods.drop(3).forEach { (k, l) -> MoodChip(k, l, mood == k) { mood = k } }
                }
            }
            Spacer(Modifier.height(20.dp))

            // 自由記述
            Text(
                "自由記述",
                color = tokens.inkSub,
                modifier = Modifier.padding(horizontal = 16.dp),
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium),
            )
            Spacer(Modifier.height(8.dp))
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .heightIn(min = 140.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(tokens.paper)
                        .border(1.dp, tokens.hair, RoundedCornerShape(12.dp))
                        .padding(14.dp),
            ) {
                if (text.isEmpty()) {
                    Text(
                        "ご自由にお書きください...",
                        color = tokens.inkFaint,
                        style = TextStyle(fontSize = 14.sp),
                    )
                }
                BasicTextField(
                    value = text,
                    onValueChange = { if (it.length <= maxLen) text = it },
                    textStyle = TextStyle(color = tokens.ink, fontSize = 14.sp, lineHeight = 20.sp),
                    modifier = Modifier.fillMaxWidth().heightIn(min = 120.dp),
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp).padding(top = 4.dp),
                horizontalArrangement = Arrangement.End,
            ) {
                Text(
                    "${text.length} / $maxLen",
                    color = tokens.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )
            }
            Spacer(Modifier.height(20.dp))

            // 送信 — Brush 与 Color 不能混在三元里（Kotlin 重载推不出公共类型），分支构造 Modifier
            val submitBg =
                if (canSubmit) {
                    Modifier.background(tokens.btnGrad)
                } else {
                    Modifier.background(tokens.hairSoft)
                }
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp)
                        .clip(RoundedCornerShape(99.dp))
                        .then(submitBg)
                        .clickable(enabled = canSubmit) {
                            // 先快照当前值再启协程 — 协程异步执行，下面会立即清空 category/mood/text。
                            // 用早返回而非 ?: ""：极快连点时第二次会读到已清空的 null，避免提交空 payload（Codex 5.5 审查）
                            val snapCategory = category ?: return@clickable
                            val snapMood = mood ?: return@clickable
                            val snapText = text.takeIf { it.isNotBlank() } ?: return@clickable
                            scope.launch {
                                val payload =
                                    buildJsonObject {
                                        put("category", snapCategory)
                                        put("mood", snapMood)
                                        put("text", snapText)
                                    }.toString()
                                store.update { s -> s.copy(feedback = s.feedback + payload) }
                            }
                            Toast.makeText(ctx, "送信しました", Toast.LENGTH_SHORT).show()
                            category = null
                            mood = null
                            text = ""
                        }.padding(vertical = 14.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    "送信",
                    color = if (canSubmit) Color.White else tokens.inkFaint,
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                )
            }
            Spacer(Modifier.height(20.dp))
        }
    }
}

@Composable
private fun MoodChip(
    @Suppress("UNUSED_PARAMETER") key: String,
    label: String,
    active: Boolean,
    onClick: () -> Unit,
) {
    val tokens = SuzuT.current
    Box(
        modifier =
            Modifier
                .clip(RoundedCornerShape(99.dp))
                .background(if (active) tokens.pill else tokens.paper)
                .border(1.dp, if (active) tokens.ink else tokens.hair, RoundedCornerShape(99.dp))
                .clickable(onClick = onClick)
                .padding(horizontal = 14.dp, vertical = 8.dp),
    ) {
        Text(
            label,
            color = tokens.ink,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
        )
    }
}
