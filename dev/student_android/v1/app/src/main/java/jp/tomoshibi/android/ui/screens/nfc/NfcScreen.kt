package jp.tomoshibi.android.ui.screens.nfc

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.RollCall
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private enum class NfcStage { READY, SCANNING, SUCCESS }

@Composable
fun NfcScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var stage by remember { mutableStateOf(NfcStage.READY) }
    var successTimestamp by remember { mutableStateOf("") }

    val goScan: () -> Unit = {
        stage = NfcStage.SCANNING
        scope.launch {
            delay(1600)
            stage = NfcStage.SUCCESS
            successTimestamp = SimpleDateFormat("HH:mm", Locale.JAPAN).format(Date())
            store.update { s ->
                s.copy(rollCalls = s.rollCalls + RollCall(
                    id = "R-${System.currentTimeMillis()}",
                    ts = System.currentTimeMillis(),
                    status = "ok",
                    method = "nfc"
                ))
            }
            delay(1400)
            navController.popBackStack()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(tokens.btnGrad)
    ) {
        // ── top bar with close button ──
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 4.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clickable { navController.popBackStack() },
                contentAlignment = Alignment.Center
            ) {
                Text("✕", color = Color.White, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
            }
            Text(
                text = "NFC点呼",
                color = Color.White,
                modifier = Modifier.weight(1f),
                textAlign = TextAlign.Center,
                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
            )
            Spacer(Modifier.width(44.dp))
        }

        // ── 主体 ──
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            val primary = MaterialTheme.colorScheme.primary
            when (stage) {
                NfcStage.READY -> ReadyState(primary, goScan)
                NfcStage.SCANNING -> ScanningState()
                NfcStage.SUCCESS -> SuccessState(primary, successTimestamp)
            }
        }
    }
}

@Composable
private fun ReadyState(primary: Color, onScan: () -> Unit) {
    val infinite = rememberInfiniteTransition(label = "nfcPulse")
    val scale by infinite.animateFloat(
        1f, 1.05f,
        infiniteRepeatable(tween(1000, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "nfcReadyScale"
    )
    Box(
        modifier = Modifier
            .size(200.dp)
            .scale(scale)
            .clip(CircleShape)
            .background(Color.White.copy(alpha = 0.15f)),
        contentAlignment = Alignment.Center
    ) {
        // 📡 emoji 替换为 Material Icon — 视觉上更接近 NFC 信号语义
        Icon(
            imageVector = SuzuIcons.PhoneNfc,
            contentDescription = null,
            tint = Color.White,
            modifier = Modifier.size(60.dp)
        )
    }
    Spacer(Modifier.height(28.dp))
    Text("カードをかざしてください", color = Color.White,
        style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold), textAlign = TextAlign.Center)
    Spacer(Modifier.height(8.dp))
    Text(
        text = "背面のNFCマークを\nリーダーに近づけてください",
        color = Color.White.copy(alpha = 0.85f),
        style = TextStyle(fontSize = 14.sp, lineHeight = 22.sp),
        textAlign = TextAlign.Center
    )
    Spacer(Modifier.height(28.dp))
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(99.dp))
            .background(Color.White)
            .clickable { onScan() }
            .padding(horizontal = 32.dp, vertical = 14.dp)
    ) {
        Text("シミュレート", color = primary,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
    }
}

@Composable
private fun ScanningState() {
    val infinite = rememberInfiniteTransition(label = "nfcRipple")
    Box(
        modifier = Modifier.size(200.dp),
        contentAlignment = Alignment.Center
    ) {
        // 3 道波纹（不同 phase）
        listOf(0, 1, 2).forEach { i ->
            val ripple by infinite.animateFloat(
                initialValue = 0.5f, targetValue = 1.4f,
                animationSpec = infiniteRepeatable(
                    tween(1600, delayMillis = i * 500, easing = LinearEasing),
                    RepeatMode.Restart
                ),
                label = "ripple$i"
            )
            val alpha by infinite.animateFloat(
                initialValue = 1f, targetValue = 0f,
                animationSpec = infiniteRepeatable(
                    tween(1600, delayMillis = i * 500, easing = LinearEasing),
                    RepeatMode.Restart
                ),
                label = "rippleAlpha$i"
            )
            Box(
                modifier = Modifier
                    .matchParentSize()
                    .scale(ripple)
                    .border(2.dp, Color.White.copy(alpha = alpha * 0.5f), CircleShape)
            )
        }
        Box(
            modifier = Modifier
                .size(100.dp)
                .clip(CircleShape)
                .background(Color.White.copy(alpha = 0.25f)),
            contentAlignment = Alignment.Center
        ) {
            Icon(
                imageVector = SuzuIcons.PhoneNfc,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(44.dp)
            )
        }
    }
    Spacer(Modifier.height(28.dp))
    Text("読み取り中...", color = Color.White,
        style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
    Spacer(Modifier.height(8.dp))
    Text("そのままお待ちください",
        color = Color.White.copy(alpha = 0.85f), style = TextStyle(fontSize = 14.sp))
}

@Composable
private fun SuccessState(primary: Color, timestamp: String) {
    // pop in 缩放
    val scale = remember { Animatable(0.3f) }
    LaunchedEffect(Unit) {
        scale.animateTo(1f, animationSpec = spring(dampingRatio = 0.5f, stiffness = 300f))
    }
    // 80dp ✓ glyph 用 Material Check icon — 比 Text "✓" 锐利
    Box(
        modifier = Modifier
            .size(160.dp)
            .scale(scale.value)
            .clip(CircleShape)
            .background(Color.White),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            imageVector = SuzuIcons.Check,
            contentDescription = null,
            tint = primary,
            modifier = Modifier.size(80.dp)
        )
    }
    Spacer(Modifier.height(28.dp))
    Text("点呼完了", color = Color.White,
        style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
    Spacer(Modifier.height(8.dp))
    Text(
        text = "$timestamp に記録しました",
        color = Color.White.copy(alpha = 0.9f),
        style = TextStyle(fontSize = 15.sp)
    )
}
