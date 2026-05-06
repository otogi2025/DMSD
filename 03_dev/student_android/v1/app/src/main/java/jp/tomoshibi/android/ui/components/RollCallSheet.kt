package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalTime
import java.time.format.DateTimeFormatter

// 点呼扫卡 sheet — 完全对齐 iOS RollcallSheet (HomeStubs.swift §1136)
//
// 视觉结构（顶 → 底）:
//   ① drag handle (36×4dp)
//   ② 标题「スキャンの準備ができました」18sp Bold
//   ③ 操作说明 2 行：① 入口の NFC マークにスマホをかざす / ② 画面が光ったら完了
//   ④ amber 警告 pill「点呼時間外です。点呼開始まで少々お待ちください。」
//   ⑤ 大圆 NFC 视觉（180dp accentSoft 圆 + 内 100dp PhoneNfc icon primary）
//   ⑥ NFC をかざす CTA (52dp btnGrad)
//   ⑦ キャンセル text button（不再是 border button — iOS 风格）
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RollCallSheet(onDismiss: () -> Unit) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = tokens.paper,
        scrimColor = Color.Black.copy(alpha = 0.32f),
        dragHandle = {
            Box(
                modifier = Modifier
                    .padding(top = 10.dp, bottom = 16.dp)
                    .size(width = 40.dp, height = 5.dp)
                    .clip(CircleShape)
                    .background(tokens.inkFaint)
            )
        }
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(bottom = 28.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // ② 标题
            Text(
                text = "スキャンの準備ができました",
                color = tokens.ink,
                style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold),
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(14.dp))

            // ③ 操作说明 2 行（左对齐 in 容器中央）
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.Start
            ) {
                Text(
                    text = "① 入口の NFC マークにスマホをかざす",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 13.sp, lineHeight = 20.sp)
                )
                Text(
                    text = "② 画面が光ったら完了",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 13.sp, lineHeight = 20.sp)
                )
            }

            Spacer(Modifier.height(16.dp))

            // ④ amber 警告 pill「点呼時間外です」
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(tokens.warnBg)
                    .border(1.dp, tokens.warn.copy(alpha = 0.25f), RoundedCornerShape(12.dp))
                    .padding(horizontal = 14.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    "⚠", color = tokens.warnDeep,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold)
                )
                Text(
                    text = "点呼時間外です。点呼開始まで少々お待ちください。",
                    color = tokens.warnDeep,
                    style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp)
                )
            }

            Spacer(Modifier.height(28.dp))

            // ⑤ 大圆 NFC 视觉（180dp accentSoft 圆 + 内 100dp PhoneNfc primary + 周围 ring）
            Box(
                modifier = Modifier.size(200.dp),
                contentAlignment = Alignment.Center
            ) {
                // 外圈淡 ring
                Box(
                    modifier = Modifier
                        .size(200.dp)
                        .clip(CircleShape)
                        .border(1.dp, tokens.pill, CircleShape)
                )
                // 内 180dp 实心圆 (pill 色)
                Box(
                    modifier = Modifier
                        .size(180.dp)
                        .clip(CircleShape)
                        .background(tokens.pill),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = SuzuIcons.PhoneNfc,
                        contentDescription = "NFC scan",
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(100.dp)
                    )
                }
            }

            Spacer(Modifier.height(28.dp))

            // ⑥ NFC をかざす CTA（demo 实际触发模拟扫描完成）
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(54.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(tokens.btnGrad)
                    .clickable {
                        scope.launch {
                            store.update { current ->
                                current.copy(
                                    rollState = RollState.DONE,
                                    checkinAt = LocalTime.now()
                                        .format(DateTimeFormatter.ofPattern("HH:mm"))
                                )
                            }
                        }
                        onDismiss()
                    },
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "NFC をかざす",
                    color = Color.White,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold)
                )
            }

            Spacer(Modifier.height(8.dp))

            // ⑦ キャンセル ghost text button (无 border)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .clickable { onDismiss() },
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "キャンセル",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium)
                )
            }
        }
    }
}
