package jp.tomoshibi.android.ui.screens.applications

import android.content.Intent
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
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.StudyOnlineRequestOut
import jp.tomoshibi.android.data.network.endpoints.StudyAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ContractFilePicker
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PickedContract
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.io.File

// 「オンライン夜学習申請一覧」— 对齐 iOS StudyOnlineRequestListView，接真后端。

@Composable
fun StudyOnlineListScreen(navController: NavHostController) {
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var ui by remember { mutableStateOf<LoadState<List<StudyOnlineRequestOut>>>(LoadState.Loading) }

    suspend fun load() {
        ui = LoadState.Loading
        val tokenAtStart = store.snapshot().authToken
        ui =
            try {
                val items = StudyAPI.listMyOnlineRequests()
                if (store.snapshot().authToken != tokenAtStart) return
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return
                LoadState.Failed(e.display)
            } catch (_: Exception) {
                LoadState.Failed("オンライン夜学習申請一覧の取得に失敗しました")
            }
    }

    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "オンライン夜学習申請一覧",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                when (val s = ui) {
                    LoadState.Loading -> {
                        LoadingBox()
                    }

                    is LoadState.Failed -> {
                        FailedBox(s.message, onRetry = { scope.launch { load() } })
                    }

                    LoadState.Empty -> {
                        EmptyState(
                            title = "提出済みの申請はありません",
                            icon = SuzuIcons.Book,
                        )
                    }

                    is LoadState.Success -> {
                        s.value.forEach { item ->
                            StudyOnlineRequestCard(
                                item = item,
                                onChanged = { scope.launch { load() } },
                            )
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

@Composable
private fun StudyOnlineRequestCard(
    item: StudyOnlineRequestOut,
    onChanged: () -> Unit,
) {
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    var picked by remember { mutableStateOf<PickedContract?>(null) }
    var uploading by remember { mutableStateOf(false) }
    var downloading by remember { mutableStateOf(false) }

    suspend fun uploadContract(contract: PickedContract) {
        uploading = true
        val tokenAtStart = store.snapshot().authToken
        try {
            StudyAPI.uploadOnlineContract(
                requestId = item.id,
                fileData = contract.data,
                fileName = contract.fileName,
                mimeType = contract.mime,
            )
            if (store.snapshot().authToken != tokenAtStart) return
            store.showToast("契約書を添付しました")
            picked = null
            onChanged()
        } catch (e: ApiError) {
            if (store.handleIfUnauthorized(e, tokenAtStart)) return
            store.showToast(e.display)
            picked = null
        } catch (_: Exception) {
            store.showToast("契約書の添付に失敗しました")
            picked = null
        } finally {
            uploading = false
        }
    }

    fun showContract() {
        scope.launch {
            downloading = true
            val tokenAtStart = store.snapshot().authToken
            try {
                val data = StudyAPI.downloadOnlineContract(requestId = item.id)
                if (store.snapshot().authToken != tokenAtStart) return@launch

                val ext = if (item.contractMime == "application/pdf") "pdf" else "jpg"
                val cacheDir = File(context.cacheDir, "contracts").apply { mkdirs() }
                val file = File(cacheDir, "contract_${item.id}.$ext")
                file.writeBytes(data)

                val authority = "${context.packageName}.fileprovider"
                val uri = FileProvider.getUriForFile(context, authority, file)
                val mime = item.contractMime ?: if (ext == "pdf") "application/pdf" else "image/jpeg"
                val intent =
                    Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, mime)
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }
                context.startActivity(Intent.createChooser(intent, null))
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                store.showToast(e.display)
            } catch (_: Exception) {
                store.showToast("契約書の取得に失敗しました")
            } finally {
                downloading = false
            }
        }
    }

    SuzuCard(padding = 14) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.Top,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text("期間", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "${item.periodFrom} 〜 ${item.periodTo}",
                        color = t.ink,
                        style =
                            TextStyle(
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = FontFamily.Monospace,
                            ),
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(item.reason, color = t.inkSub, style = TextStyle(fontSize = 13.sp))
                }
                Spacer(Modifier.width(10.dp))
                val (label, tone) = studyOnlineStatusPair(item.status)
                Pill(text = label, tone = tone)
            }

            ContractSection(
                item = item,
                picked = picked,
                uploading = uploading,
                downloading = downloading,
                onPicked = { picked = it },
                onAutoSubmit = { contract -> scope.launch { uploadContract(contract) } },
                onShow = { showContract() },
            )
        }
    }
}

@Composable
private fun ContractSection(
    item: StudyOnlineRequestOut,
    picked: PickedContract?,
    uploading: Boolean,
    downloading: Boolean,
    onPicked: (PickedContract?) -> Unit,
    onAutoSubmit: (PickedContract) -> Unit,
    onShow: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    when {
        item.contractFileName != null -> {
            Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    if (item.contractMime == "application/pdf") SuzuIcons.Doc else SuzuIcons.Doc,
                    contentDescription = null,
                    tint = cs.primary,
                    modifier = Modifier.size(15.dp),
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    item.contractFileName,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp),
                    modifier = Modifier.weight(1f),
                    maxLines = 1,
                )
                Text(
                    if (downloading) "読み込み中…" else "表示",
                    color = if (downloading) t.inkMute else cs.primary,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
                    modifier =
                        Modifier.clickable(enabled = !downloading) {
                            onShow()
                        },
                )
            }
        }

        item.status == "pending" -> {
            Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text("契約書が未添付です", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
                if (uploading) {
                    Text("アップロード中…", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
                } else {
                    ContractFilePicker(
                        picked = picked,
                        onPicked = onPicked,
                        onAutoSubmit = onAutoSubmit,
                    )
                }
            }
        }
    }
}

private fun studyOnlineStatusPair(status: String): Pair<String, PillTone> =
    when (status) {
        "approved" -> "許可" to PillTone.Ok
        "rejected" -> "却下" to PillTone.Danger
        "revoked" -> "取消済み" to PillTone.Neutral
        else -> "審査中" to PillTone.Warn
    }
