package jp.tomoshibi.android.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.theme.SuzuT

// 全局 Toast — 对齐 iOS Foundation/Components/Toast.swift
// 规格：ink@88% 胶囊 / 白字 13sp medium / 水平 18 垂直 12 / 距底 100dp / 滑入淡出

@Composable
fun SuzuToastView(text: String) {
    val t = SuzuT.current
    Text(
        text = text,
        color = Color.White,
        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Medium),
        modifier =
            Modifier
                .clip(RoundedCornerShape(percent = 50))
                .background(t.ink.copy(alpha = 0.88f))
                .padding(horizontal = 18.dp, vertical = 12.dp),
    )
}

/** 挂在根层：读 AppStore.toast，有文案时显示。 */
@Composable
fun SuzuToastHost(modifier: Modifier = Modifier) {
    val store = LocalAppStore.current
    val toast by store.toast.collectAsState()
    // 缓存最后一次非空文案：toast 置 null 触发 exit 时 content 仍能带文字滑出
    var lastToastText by remember { mutableStateOf<String?>(null) }
    if (toast != null) {
        lastToastText = toast
    }

    Box(modifier = modifier.fillMaxSize()) {
        AnimatedVisibility(
            visible = toast != null,
            enter = slideInVertically { it / 2 } + fadeIn(),
            exit = slideOutVertically { it / 2 } + fadeOut(),
            modifier =
                Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 100.dp),
        ) {
            val text = lastToastText
            if (text != null) {
                SuzuToastView(text = text)
            }
        }
    }
}
