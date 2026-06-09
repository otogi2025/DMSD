package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// LoadState.kt
// 列表 / 详情屏「从后端读数据」的统一状态机 —— 对应 Android 接后端施工图 §3③ 的「加载中 / 失败 / 空」三态。
//
// 为什么要有这层：各屏原来直接 `val list = MockData.DEFAULT_XXX`（同步、永不失败）。接真后端后
// 网络请求是异步的、可能失败、可能返回空，UI 必须区分这三种情况，不能把「失败」混成「空」。
//
// 用法（在屏的 LaunchedEffect 里）：
//   var ui by remember { mutableStateOf<LoadState<List<XxxOut>>>(LoadState.Loading) }
//   suspend fun load() {
//       ui = LoadState.Loading
//       ui = try {
//           val list = XxxAPI.list()                                  // data/network/endpoints 里现成函数
//           if (list.isEmpty()) LoadState.Empty else LoadState.Success(list)
//       } catch (e: ApiError) { LoadState.Failed(e.display) }          // 失败带后端日语提示
//         catch (e: Exception) { LoadState.Failed("读取失败兜底文案") }
//   }
//   LaunchedEffect(Unit) { load() }
// 渲染：when (val s = ui) {
//   LoadState.Loading -> LoadingBox()
//   is LoadState.Failed -> FailedBox(s.message, onRetry = { scope.launch { load() } })
//   LoadState.Empty -> EmptyState(title = "...", icon = ...)          // 复用 SuzuAtoms.EmptyState
//   is LoadState.Success -> { /* 渲染 s.value */ }
// }
//
// ⚠️ 减点 / 点呼履历这类敏感页（施工图 §3③ 重点）：网络失败必须走 FailedBox（显「読み込みに失敗しました」），
//    绝不能 catch 后退化成空列表、把失败显示成「没有 / 零扣分」—— 会让学生误以为自己没被扣分。
sealed interface LoadState<out T> {
    // 加载中（请求未回来）
    data object Loading : LoadState<Nothing>

    // 加载失败 —— message 给用户看的日语提示（来自 ApiError.display 或兜底文案）
    data class Failed(
        val message: String,
    ) : LoadState<Nothing>

    // 请求成功但数据为空（真没数据，区别于失败）
    data object Empty : LoadState<Nothing>

    // 加载成功，value 是拿到的数据
    data class Success<T>(
        val value: T,
    ) : LoadState<T>
}

// 加载中占位 —— 居中转圈（primary 青绿色）。padding 40 让它在列表区垂直居中显眼。
@Composable
fun LoadingBox(modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxWidth().padding(40.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        CircularProgressIndicator(
            color = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(32.dp),
        )
    }
}

// 加载失败占位 —— 警告图标 + 失败文案 +（可选）「再試行」按钮。
// onRetry 非空时显示重试按钮，点了重新触发加载。风格跟 SuzuAtoms.EmptyState 对齐。
@Composable
fun FailedBox(
    message: String,
    modifier: Modifier = Modifier,
    onRetry: (() -> Unit)? = null,
) {
    val t = SuzuT.current
    Column(
        modifier = modifier.fillMaxWidth().padding(40.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Icon(SuzuIcons.Warn, contentDescription = null, tint = t.inkMute, modifier = Modifier.size(40.dp))
        Text(
            message,
            color = t.inkSub,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
            textAlign = TextAlign.Center,
        )
        if (onRetry != null) {
            Text(
                "再試行",
                color = MaterialTheme.colorScheme.primary,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .clickable { onRetry() }
                        .padding(horizontal = 16.dp, vertical = 8.dp),
            )
        }
    }
}
