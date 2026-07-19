package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.SheetState
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import jp.tomoshibi.android.ui.theme.SuzuT

// GlassBottomSheet — 对齐 iOS GlassSheet + GlassBackdrop 的 Compose 近似
// iOS 用 .glassEffect（系统磨砂）；Android 无等价 API →
//   容器：paper@85% 半透明 + 顶圆角 28dp
//   遮罩：ink@35%（对齐 T.glassBackdrop）
//   拖拽条：36×5dp、inkMute@30%
// 后续 8 种全局弹窗统一走本组件，勿再直接裸用 ModalBottomSheet。

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GlassBottomSheet(
    onDismissRequest: () -> Unit,
    modifier: Modifier = Modifier,
    sheetState: SheetState = rememberModalBottomSheetState(),
    content: @Composable ColumnScope.() -> Unit,
) {
    val t = SuzuT.current
    ModalBottomSheet(
        onDismissRequest = onDismissRequest,
        modifier = modifier,
        sheetState = sheetState,
        // 对齐 iOS T.glassSheet = 白@85%（无原生 blur 时的半透明近似）
        containerColor = t.paper.copy(alpha = 0.85f),
        // 对齐 iOS T.glassBackdrop = ink@35%
        scrimColor = t.ink.copy(alpha = 0.35f),
        shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp),
        dragHandle = {
            Box(
                modifier =
                    Modifier
                        .padding(top = 10.dp, bottom = 8.dp)
                        .size(width = 36.dp, height = 5.dp)
                        .clip(RoundedCornerShape(percent = 50))
                        .background(t.inkMute.copy(alpha = 0.3f)),
            )
        },
        content = content,
    )
}
