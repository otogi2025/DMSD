package jp.tomoshibi.android.ui.components

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.provider.MediaStore
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream

// 选好的契約書文件（已转成后端 / 老师网页都能处理的格式）。对齐 iOS PickedContract。
data class PickedContract(
    val data: ByteArray,
    val fileName: String,
    val mime: String, // "image/jpeg" | "application/pdf"
) {
    val sizeText: String
        get() {
            val kb = data.size / 1024.0
            return if (kb >= 1024) String.format("%.1f MB", kb / 1024.0) else String.format("%.0f KB", kb)
        }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is PickedContract) return false
        return fileName == other.fileName && mime == other.mime && data.contentEquals(other.data)
    }

    override fun hashCode(): Int = 31 * fileName.hashCode() + mime.hashCode() + data.contentHashCode()
}

private const val MAX_BYTES = 10 * 1024 * 1024
private const val MAX_EDGE = 2400

// ContractFilePicker —— 契約書文件选择（对齐 iOS ContractFilePicker.swift）
// 底部弹三选项：「写真を撮る」(相机不可用时隐藏) / 「写真から選ぶ」 / 「ファイルを選ぶ」
// 图片统一转 JPEG（长边≤2400 + 质量 0.8）；PDF 原样；客户端拦 10MB。
@Composable
fun ContractFilePicker(
    picked: PickedContract?,
    onPicked: (PickedContract?) -> Unit,
    // 选中后自动回调（一覧补传场景：选完立刻上传）
    onAutoSubmit: ((PickedContract) -> Unit)? = null,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var showDialog by remember { mutableStateOf(false) }
    var errorText by remember { mutableStateOf<String?>(null) }
    var processing by remember { mutableStateOf(false) }

    val cameraAvailable =
        remember {
            MediaStore.Images.Media.EXTERNAL_CONTENT_URI // 仅占位读；真正判断靠 PackageManager
            context.packageManager.hasSystemFeature(android.content.pm.PackageManager.FEATURE_CAMERA_ANY)
        }

    fun accept(contract: PickedContract) {
        if (contract.data.size > MAX_BYTES) {
            errorText = "ファイルサイズが大きすぎます（10MB以下にしてください）"
            return
        }
        errorText = null
        onPicked(contract)
        onAutoSubmit?.invoke(contract)
    }

    fun fail(msg: String) {
        errorText = msg
    }

    val takePicture =
        rememberLauncherForActivityResult(ActivityResultContracts.TakePicturePreview()) { bitmap ->
            if (bitmap == null) return@rememberLauncherForActivityResult
            scope.launch {
                processing = true
                val jpeg =
                    withContext(Dispatchers.Default) {
                        compressBitmapToJpeg(bitmap)
                    }
                processing = false
                if (jpeg == null) {
                    fail("画像の読み込みに失敗しました")
                } else {
                    accept(PickedContract(jpeg, "contract.jpg", "image/jpeg"))
                }
            }
        }

    val pickVisual =
        rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
            if (uri == null) return@rememberLauncherForActivityResult
            scope.launch {
                processing = true
                val result =
                    withContext(Dispatchers.IO) {
                        runCatching {
                            context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
                        }.getOrNull()
                    }
                val jpeg =
                    if (result != null) {
                        withContext(Dispatchers.Default) { decodeAndCompress(result) }
                    } else {
                        null
                    }
                processing = false
                if (jpeg == null) {
                    fail("画像の読み込みに失敗しました")
                } else {
                    accept(PickedContract(jpeg, "contract.jpg", "image/jpeg"))
                }
            }
        }

    val openDocument =
        rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
            if (uri == null) return@rememberLauncherForActivityResult
            scope.launch {
                processing = true
                val outcome =
                    withContext(Dispatchers.IO) {
                        runCatching {
                            val name =
                                context.contentResolver.query(uri, null, null, null, null)?.use { c ->
                                    val idx = c.getColumnIndex(android.provider.OpenableColumns.DISPLAY_NAME)
                                    if (c.moveToFirst() && idx >= 0) c.getString(idx) else null
                                } ?: "contract"
                            val mime = context.contentResolver.getType(uri) ?: ""
                            val bytes =
                                context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
                                    ?: return@runCatching null
                            Triple(name, mime, bytes)
                        }.getOrNull()
                    }
                processing = false
                if (outcome == null) {
                    fail("ファイルの読み込みに失敗しました")
                    return@launch
                }
                val (name, mime, bytes) = outcome
                when {
                    mime == "application/pdf" || name.lowercase().endsWith(".pdf") -> {
                        if (bytes.size > MAX_BYTES) {
                            fail("ファイルサイズが大きすぎます（10MB以下にしてください）")
                        } else {
                            accept(PickedContract(bytes, name, "application/pdf"))
                        }
                    }

                    mime.startsWith("image/") ||
                        listOf("jpg", "jpeg", "png", "heic", "webp", "gif")
                            .any { name.lowercase().endsWith(".$it") }
                    -> {
                        val jpeg = withContext(Dispatchers.Default) { decodeAndCompress(bytes) }
                        if (jpeg == null) {
                            fail("画像の読み込みに失敗しました")
                        } else {
                            accept(PickedContract(jpeg, "contract.jpg", "image/jpeg"))
                        }
                    }

                    else -> {
                        fail("対応していないファイル形式です")
                    }
                }
            }
        }

    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        if (picked != null) {
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(t.pill)
                        .padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    if (picked.mime == "application/pdf") SuzuIcons.Doc else SuzuIcons.Doc,
                    contentDescription = null,
                    tint = cs.primary,
                    modifier = Modifier.size(18.dp),
                )
                Spacer(Modifier.width(10.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        picked.fileName,
                        color = t.ink,
                        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                        maxLines = 1,
                    )
                    Text(picked.sizeText, color = t.inkSub, style = TextStyle(fontSize = 11.sp))
                }
                Text(
                    "×",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 20.sp),
                    modifier =
                        Modifier
                            .clickable {
                                onPicked(null)
                                errorText = null
                            }.padding(4.dp),
                )
            }
        } else {
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(44.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .border(
                            width = 1.dp,
                            color = cs.primary.copy(alpha = 0.4f),
                            shape = RoundedCornerShape(12.dp),
                        ).clickable(enabled = !processing) {
                            errorText = null
                            showDialog = true
                        },
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
            ) {
                Icon(SuzuIcons.Doc, contentDescription = null, tint = cs.primary, modifier = Modifier.size(14.dp))
                Spacer(Modifier.width(8.dp))
                Text(
                    if (processing) "処理中…" else "契約書を添付",
                    color = cs.primary,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
        errorText?.let {
            Text(it, color = t.danger, style = TextStyle(fontSize = 12.sp))
        }
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            title = { Text("契約書を追加", color = t.ink, style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold)) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    if (cameraAvailable) {
                        TextButton(onClick = {
                            showDialog = false
                            takePicture.launch(null)
                        }) {
                            Text("写真を撮る", color = cs.primary)
                        }
                    }
                    TextButton(onClick = {
                        showDialog = false
                        pickVisual.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
                    }) {
                        Text("写真から選ぶ", color = cs.primary)
                    }
                    TextButton(onClick = {
                        showDialog = false
                        openDocument.launch(arrayOf("application/pdf", "image/*"))
                    }) {
                        Text("ファイルを選ぶ", color = cs.primary)
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("キャンセル", color = t.inkSub)
                }
            },
            containerColor = t.paper,
        )
    }
}

// 原始字节 → 解码 + 缩放 + JPEG 编码（对齐 iOS ContractImage.decodeAndCompress）
private fun decodeAndCompress(raw: ByteArray): ByteArray? {
    val bitmap = BitmapFactory.decodeByteArray(raw, 0, raw.size) ?: return null
    return compressBitmapToJpeg(bitmap)
}

private fun compressBitmapToJpeg(bitmap: Bitmap): ByteArray? {
    val scaled = downscale(bitmap, MAX_EDGE)
    val out = ByteArrayOutputStream()
    val ok = scaled.compress(Bitmap.CompressFormat.JPEG, 80, out)
    if (scaled !== bitmap) scaled.recycle()
    if (!ok) return null
    return out.toByteArray()
}

private fun downscale(
    bitmap: Bitmap,
    maxEdge: Int,
): Bitmap {
    val w = bitmap.width
    val h = bitmap.height
    val longest = maxOf(w, h)
    if (longest <= maxEdge || longest <= 0) return bitmap
    val scale = maxEdge.toFloat() / longest
    val matrix = Matrix().apply { setScale(scale, scale) }
    return Bitmap.createBitmap(bitmap, 0, 0, w, h, matrix, true)
}
