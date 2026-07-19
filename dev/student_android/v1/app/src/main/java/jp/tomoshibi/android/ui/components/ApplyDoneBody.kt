package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// ApplyDoneBody —— 申请完成页共用组件（对齐 iOS ApplyDoneView）
// 96×96 圆角 28 + primary→accent 对角渐变 + 白 checkmark + 阴影；
// 信息卡标签「審査時間の目安」+「1〜2 時間」；底部「一覧へ」。
@Composable
fun ApplyDoneBody(
    kindName: String,
    messageOverride: String? = null,
    backTitle: String = "一覧へ",
    onBack: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 28.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
    ) {
        // 对勾徽章：96×96 / 圆角 28 / primary→accent 渐变 / primary 色阴影 / 白色粗 checkmark
        Box(
            modifier =
                Modifier
                    .size(96.dp)
                    .shadow(
                        elevation = 24.dp,
                        shape = RoundedCornerShape(28.dp),
                        ambientColor = cs.primary.copy(alpha = 0.35f),
                        spotColor = cs.primary.copy(alpha = 0.35f),
                    ).clip(RoundedCornerShape(28.dp))
                    .background(
                        Brush.linearGradient(colors = listOf(cs.primary, cs.secondary)),
                    ),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                SuzuIcons.Check,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(40.dp),
            )
        }
        Spacer(Modifier.height(22.dp))
        Text(
            "申請を提出しました",
            color = t.ink,
            style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold),
        )
        Spacer(Modifier.height(8.dp))
        Text(
            messageOverride ?: "${kindName}申請を受け付けました。\n審査完了時に通知でお知らせします。",
            color = t.inkSub,
            style = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(28.dp))
        // 审查时间卡（标签逐字对齐 iOS「審査時間の目安」）
        SuzuCard {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("審査時間の目安", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
                Spacer(Modifier.weight(1f))
                Text(
                    "1〜2 時間",
                    color = t.ink,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
        Spacer(Modifier.height(28.dp))
        PrimaryButton(title = backTitle, onClick = onBack)
    }
}
