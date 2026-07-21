package jp.tomoshibi.android.ui.screens.announcements

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
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckBox
import androidx.compose.material.icons.filled.CheckBoxOutlineBlank
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.AnnouncementDetail
import jp.tomoshibi.android.data.network.AnnouncementReplyOut
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.AnnouncementsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.data.translate.AnnouncementTranslator
import jp.tomoshibi.android.data.translate.TranslateLang
import jp.tomoshibi.android.data.translate.TranslatePrefs
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 公告详情（标题「お知らせ詳細」）— 接真后端 AnnouncementsAPI.detail(id)（规格 §5.4）。
//   三态加载详情；底部回复；「翻訳」用 ML Kit 设备端翻译（不做「AI要約」）。
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnnouncementDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val t = SuzuT.current
    val ctx = LocalContext.current
    val scope = rememberCoroutineScope()
    val store = LocalAppStore.current

    var ui by remember { mutableStateOf<LoadState<AnnouncementDetail>>(LoadState.Loading) }
    var replyText by remember { mutableStateOf("") }
    var sending by remember { mutableStateOf(false) }

    // 翻译态（对齐 iOS AnnouncementDetailView）
    var isTranslating by remember { mutableStateOf(false) }
    var translateFailed by remember { mutableStateOf(false) }
    var translatedText by remember { mutableStateOf<String?>(null) }
    var translatedLabel by remember { mutableStateOf<String?>(null) }
    var lastTargetLang by remember { mutableStateOf<TranslateLang?>(null) }
    var showLangPicker by remember { mutableStateOf(false) }
    var rememberAsDefault by remember { mutableStateOf(false) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                LoadState.Success(AnnouncementsAPI.detail(id))
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

    fun resetToOriginal() {
        translatedText = null
        translatedLabel = null
        translateFailed = false
        isTranslating = false
        lastTargetLang = null
    }

    fun startTranslate(
        lang: TranslateLang,
        body: String,
    ) {
        translatedText = null
        translateFailed = false
        isTranslating = true
        translatedLabel = lang.shortLabel
        lastTargetLang = lang
        scope.launch {
            try {
                translatedText = AnnouncementTranslator.translate(body, lang)
                translateFailed = false
            } catch (_: Exception) {
                translatedText = null
                translateFailed = true
            } finally {
                isTranslating = false
            }
        }
    }

    fun onTapTranslate(body: String) {
        val defaultCode = TranslatePrefs.getDefaultLang(ctx)
        val lang = TranslateLang.fromCode(defaultCode)
        if (lang != null) {
            startTranslate(lang, body)
        } else {
            rememberAsDefault = false
            showLangPicker = true
        }
    }

    GlobalScaffold(activeTab = "", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "お知らせ詳細", level = 2, onLeft = { navController.popBackStack() })

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                LoadState.Empty -> {
                    FailedBox("読み込みに失敗しました", onRetry = { scope.launch { load() } })
                }

                is LoadState.Success -> {
                    val detail = s.value
                    val displayBody = translatedText ?: detail.body
                    Column(
                        modifier =
                            Modifier
                                .weight(1f)
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                    ) {
                        Spacer(Modifier.height(4.dp))
                        Text(
                            detail.title,
                            color = t.ink,
                            style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold, lineHeight = 28.sp),
                        )
                        Spacer(Modifier.height(6.dp))
                        Text(
                            "${detail.authorTeacherName} · ${fmtTime(detail.createdAt)}",
                            color = t.inkMute,
                            style = TextStyle(fontSize = 12.sp),
                        )
                        Spacer(Modifier.height(14.dp))
                        Text(
                            displayBody,
                            color = t.ink,
                            style = TextStyle(fontSize = 15.sp, lineHeight = 24.sp),
                        )
                        Spacer(Modifier.height(12.dp))
                        TranslateActionChip(onClick = { onTapTranslate(detail.body) })
                        Spacer(Modifier.height(8.dp))
                        TranslateStatusBar(
                            isTranslating = isTranslating,
                            failed = translateFailed,
                            label = translatedLabel,
                            hasTranslation = translatedText != null,
                            onRetry = { lastTargetLang?.let { startTranslate(it, detail.body) } },
                            onReset = { resetToOriginal() },
                        )
                        Spacer(Modifier.height(18.dp))
                        HorizontalDivider(color = t.hair)
                        Spacer(Modifier.height(14.dp))
                        Text(
                            "返信 (${detail.replies.size})",
                            color = t.inkSub,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                        )
                        Spacer(Modifier.height(10.dp))
                        if (detail.replies.isEmpty()) {
                            Text("まだ返信はありません", color = t.inkMute, style = TextStyle(fontSize = 13.sp))
                        } else {
                            detail.replies.forEach { reply ->
                                AnnouncementReplyRow(reply = reply)
                                Spacer(Modifier.height(12.dp))
                            }
                        }
                        Spacer(Modifier.height(16.dp))
                    }

                    ReplyComposer(
                        value = replyText,
                        sending = sending,
                        onValueChange = { replyText = it },
                        onSend = {
                            if (!sending && replyText.isNotBlank()) {
                                sending = true
                                scope.launch {
                                    val tokenAtStart = store.snapshot().authToken
                                    try {
                                        val sentBody = replyText
                                        val newReply = AnnouncementsAPI.postReply(id, sentBody)
                                        replyText = ""
                                        // 静默追加回复，不调 load() 避免整页闪 Loading
                                        val cur = ui
                                        if (cur is LoadState.Success) {
                                            ui =
                                                LoadState.Success(
                                                    cur.value.copy(
                                                        replies = cur.value.replies + newReply,
                                                    ),
                                                )
                                        }
                                    } catch (e: ApiError) {
                                        if (store.handleIfUnauthorized(e, tokenAtStart)) {
                                            return@launch
                                        }
                                        store.showToast(e.display)
                                    } catch (e: Exception) {
                                        store.showToast("送信に失敗しました")
                                    } finally {
                                        sending = false
                                    }
                                }
                            }
                        },
                    )

                    if (showLangPicker) {
                        TranslateLangPickerSheet(
                            rememberAsDefault = rememberAsDefault,
                            onRememberChange = { rememberAsDefault = it },
                            onDismiss = { showLangPicker = false },
                            onPick = { lang ->
                                if (rememberAsDefault) {
                                    TranslatePrefs.setDefaultLang(ctx, lang.code)
                                }
                                showLangPicker = false
                                startTranslate(lang, detail.body)
                            },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun TranslateActionChip(onClick: () -> Unit) {
    val primary = MaterialTheme.colorScheme.primary
    Row(
        modifier =
            Modifier
                .clip(RoundedCornerShape(percent = 50))
                .background(primary.copy(alpha = 0.08f))
                .clickable(onClick = onClick)
                .padding(horizontal = 12.dp, vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(5.dp),
    ) {
        Icon(
            imageVector = Icons.Filled.Language,
            contentDescription = null,
            tint = primary,
            modifier = Modifier.size(14.dp),
        )
        Text(
            "翻訳",
            color = primary,
            style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}

@Composable
private fun TranslateStatusBar(
    isTranslating: Boolean,
    failed: Boolean,
    label: String?,
    hasTranslation: Boolean,
    onRetry: () -> Unit,
    onReset: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    when {
        isTranslating -> {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(14.dp),
                    strokeWidth = 2.dp,
                    color = primary,
                )
                Text("翻訳中…", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
            }
        }

        failed -> {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Icon(
                    Icons.Filled.Warning,
                    contentDescription = null,
                    tint = t.danger,
                    modifier = Modifier.size(14.dp),
                )
                Text("翻訳に失敗しました", color = t.danger, style = TextStyle(fontSize = 12.sp))
                Spacer(Modifier.weight(1f))
                Text(
                    "再試行",
                    color = t.danger,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                    modifier = Modifier.clickable(onClick = onRetry),
                )
            }
        }

        hasTranslation && label != null -> {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Icon(
                    Icons.Filled.Language,
                    contentDescription = null,
                    tint = primary,
                    modifier = Modifier.size(14.dp),
                )
                Text(
                    "$label に翻訳しました",
                    color = primary,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium),
                )
                Spacer(Modifier.weight(1f))
                Text(
                    "原文に戻す",
                    color = primary,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                    modifier = Modifier.clickable(onClick = onReset),
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun TranslateLangPickerSheet(
    rememberAsDefault: Boolean,
    onRememberChange: (Boolean) -> Unit,
    onDismiss: () -> Unit,
    onPick: (TranslateLang) -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = t.paper,
    ) {
        Column(modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 20.dp)
                        .padding(top = 4.dp, bottom = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    Icons.Filled.Language,
                    contentDescription = null,
                    tint = primary,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    "翻訳する言語",
                    color = primary,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                )
                Spacer(Modifier.weight(1f))
                IconButton(onClick = onDismiss) {
                    Icon(Icons.Filled.Close, contentDescription = "閉じる", tint = t.inkMute)
                }
            }
            TranslateLang.entries.forEachIndexed { idx, lang ->
                if (idx > 0) {
                    HorizontalDivider(color = t.hair)
                }
                Row(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .clickable { onPick(lang) }
                            .padding(horizontal = 20.dp, vertical = 14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        lang.pickerLabel,
                        color = t.ink,
                        style = TextStyle(fontSize = 15.sp),
                        modifier = Modifier.weight(1f),
                    )
                    Text("›", color = t.inkMute, style = TextStyle(fontSize = 16.sp))
                }
            }
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .clickable { onRememberChange(!rememberAsDefault) }
                        .padding(horizontal = 20.dp, vertical = 14.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Icon(
                    imageVector =
                        if (rememberAsDefault) {
                            Icons.Filled.CheckBox
                        } else {
                            Icons.Filled.CheckBoxOutlineBlank
                        },
                    contentDescription = null,
                    tint = if (rememberAsDefault) primary else t.inkMute,
                    modifier = Modifier.size(22.dp),
                )
                Text(
                    "次回からこの言語に翻訳する",
                    color = t.ink,
                    style = TextStyle(fontSize = 13.sp),
                )
            }
            Text(
                "デフォルトの言語は設定画面でいつでも変更できます。",
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp),
                modifier = Modifier.padding(horizontal = 20.dp).padding(bottom = 20.dp),
            )
        }
    }
}

@Composable
private fun AnnouncementReplyRow(reply: AnnouncementReplyOut) {
    val t = SuzuT.current
    Column(modifier = Modifier.fillMaxWidth()) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                reply.authorName,
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
            )
            if (reply.authorKind == "teacher") {
                Spacer(Modifier.width(6.dp))
                Pill(text = "教員", tone = PillTone.Accent)
            }
            Spacer(Modifier.width(8.dp))
            Text(
                fmtTime(reply.createdAt),
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp),
            )
        }
        Spacer(Modifier.height(4.dp))
        Text(
            reply.body,
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, lineHeight = 21.sp),
        )
    }
}

@Composable
private fun ReplyComposer(
    value: String,
    sending: Boolean,
    onValueChange: (String) -> Unit,
    onSend: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val canSend = value.isNotBlank() && !sending

    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .background(t.paper)
                .padding(horizontal = 12.dp, vertical = 10.dp),
        verticalAlignment = Alignment.Bottom,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.weight(1f).heightIn(min = 48.dp),
            placeholder = {
                Text("返信を入力...", color = t.inkMute, style = TextStyle(fontSize = 15.sp))
            },
            textStyle = TextStyle(fontSize = 15.sp, color = t.ink),
            shape = RoundedCornerShape(12.dp),
            minLines = 1,
            maxLines = 4,
        )
        Box(
            modifier =
                Modifier
                    .size(48.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .background(if (canSend) cs.primary else t.inkFaint),
            contentAlignment = Alignment.Center,
        ) {
            IconButton(onClick = onSend, enabled = canSend) {
                Icon(
                    imageVector = Icons.Filled.Send,
                    contentDescription = "送信",
                    tint = Color.White,
                    modifier = Modifier.size(20.dp),
                )
            }
        }
    }
}

private fun fmtTime(iso: String): String {
    val formatted =
        jp.tomoshibi.android.data.format.JstDate
            .formatChangeLog(iso)
    // formatChangeLog 解析失败时原样返回；旧兜底把日期改成 yyyy/MM/dd
    return if (formatted == iso) {
        runCatching {
            "${iso.substring(0, 10).replace('-', '/')} ${iso.substring(11, 16)}"
        }.getOrDefault(iso)
    } else {
        formatted
    }
}
