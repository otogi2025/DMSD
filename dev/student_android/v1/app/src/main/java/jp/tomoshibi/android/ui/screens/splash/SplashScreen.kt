package jp.tomoshibi.android.ui.screens.splash

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
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
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

@Composable
fun SplashScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current

    // 1.4 秒后：检查令牌过期 → 有效则恢复会话 + 后台 loadMe；过期则清令牌走登录
    LaunchedEffect(Unit) {
        delaySplash()
        val restored = store.restoreSessionIfNeeded()
        val snap = store.snapshot()
        val target =
            when {
                restored -> Route.Home.path
                snap.onboarded -> Route.Login.path
                else -> Route.Onboarding.path
            }
        if (restored) {
            // 不阻塞导航；对齐 iOS init 里 Task { await loadMe() }
            launch { store.loadMe() }
        }
        navController.navigate(target) {
            popUpTo(Route.Splash.path) { inclusive = true }
        }
    }

    // 灯字 logo 脉冲缩放动画
    val infinite = rememberInfiniteTransition(label = "splashPulse")
    val scale by infinite.animateFloat(
        initialValue = 1f,
        targetValue = 1.05f,
        animationSpec = infiniteRepeatable(tween(1000, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "splashScale",
    )

    Box(
        modifier =
            Modifier
                .fillMaxSize()
                .background(tokens.btnGrad),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            Box(
                modifier =
                    Modifier
                        .size(100.dp)
                        .scale(scale)
                        .clip(RoundedCornerShape(30.dp))
                        .background(Color.White.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "灯",
                    color = Color.White,
                    style = TextStyle(fontSize = 56.sp, fontWeight = FontWeight.Light),
                )
            }
            Text(
                text = "Tomoshibi",
                color = Color.White,
                style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.SemiBold),
            )
            Text(
                text = "寮生活、もっと近くに。",
                color = Color.White.copy(alpha = 0.85f),
                style =
                    TextStyle(
                        fontSize = 13.sp,
                        letterSpacing = 0.6.sp,
                    ),
                textAlign = TextAlign.Center,
            )
        }
    }
}

private suspend fun delaySplash() {
    kotlinx.coroutines.delay(1400)
}
