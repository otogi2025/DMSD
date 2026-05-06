package jp.tomoshibi.android.ui.screens.splash

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
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
import jp.tomoshibi.android.data.model.AppState
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.delay

@Composable
fun SplashScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)

    // 1.4 秒后跳转 — 看 onboarded / authed flag 决定去哪
    LaunchedEffect(state) {
        delay(1400)
        val target = when {
            state.authed -> Route.Home.path
            state.onboarded -> Route.Login.path
            else -> Route.Onboarding.path
        }
        navController.navigate(target) {
            popUpTo(Route.Splash.path) { inclusive = true }
        }
    }

    // 灯字 logo 脉冲缩放动画
    val infinite = rememberInfiniteTransition(label = "splashPulse")
    val scale by infinite.animateFloat(
        initialValue = 1f, targetValue = 1.05f,
        animationSpec = infiniteRepeatable(tween(1000, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "splashScale"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(tokens.btnGrad),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(20.dp)
        ) {
            // 灯字 logo — 100dp 圆角 30dp（iOS Splash 视觉对齐）
            Box(
                modifier = Modifier
                    .size(100.dp)
                    .scale(scale)
                    .clip(RoundedCornerShape(30.dp))
                    .background(Color.White.copy(alpha = 0.15f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = "灯",
                    color = Color.White,
                    style = TextStyle(fontSize = 56.sp, fontWeight = FontWeight.Light)
                )
            }
            Text(
                text = "Tomoshibi",
                color = Color.White,
                style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.SemiBold)
            )
            Text(
                text = "寮生活、もっと近くに。",
                color = Color.White.copy(alpha = 0.85f),
                style = TextStyle(
                    fontSize = 13.sp,
                    letterSpacing = 0.6.sp
                ),
                textAlign = TextAlign.Center
            )
        }
    }
}
