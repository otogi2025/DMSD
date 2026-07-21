package jp.tomoshibi.android.ui.screens.splash

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.BuildConfig
import jp.tomoshibi.android.R
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.delay
import kotlinx.coroutines.withTimeoutOrNull

// 启动闪屏 — 对齐 iOS SplashView：白→#F4F7F8 渐变 + 白卡片火焰图 + 一次性 fadeIn
@Composable
fun SplashScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    var appear by remember { mutableStateOf(false) }
    val alpha by animateFloatAsState(
        targetValue = if (appear) 1f else 0f,
        animationSpec = tween(600),
        label = "splashFade",
    )

    LaunchedEffect(Unit) {
        appear = true
        delay(2200)
        val restored = store.restoreSessionIfNeeded()
        val snap = store.snapshot()
        val target =
            when {
                restored -> Route.Home.path
                snap.onboarded -> Route.Login.path
                else -> Route.Onboarding.path
            }
        // android#71：恢复会话须 await loadMe 再跳转，避免首页先闪种子 DEFAULT_USER
        if (restored) {
            withTimeoutOrNull(8_000L) {
                runCatching { store.loadMe() }
            }
            // 超时/失败仍进首页，不卡死在闪屏
        }
        navController.navigate(target) {
            popUpTo(Route.Splash.path) { inclusive = true }
        }
    }

    Box(
        modifier =
            Modifier
                .fillMaxSize()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(Color.White, Color(0xFFF4F7F8)),
                    ),
                ),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.alpha(alpha),
        ) {
            Spacer(Modifier.weight(1f))
            Box(
                modifier =
                    Modifier
                        .size(168.dp)
                        .shadow(
                            elevation = 20.dp,
                            shape = RoundedCornerShape(32.dp),
                            ambientColor = Color.Black.copy(alpha = 0.08f),
                            spotColor = Color.Black.copy(alpha = 0.08f),
                        ).clip(RoundedCornerShape(32.dp))
                        .background(Color.White),
                contentAlignment = Alignment.Center,
            ) {
                Image(
                    painter = painterResource(R.drawable.tomoshibi_flame),
                    contentDescription = null,
                    modifier = Modifier.size(120.dp),
                    contentScale = ContentScale.Fit,
                )
            }
            Spacer(Modifier.height(36.dp))
            Text(
                text = "Tomoshibi · 灯火",
                color = tokens.ink,
                style =
                    TextStyle(
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 2.2.sp,
                    ),
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = "v${BuildConfig.VERSION_NAME}",
                color = tokens.inkMute,
                style =
                    TextStyle(
                        fontSize = 11.sp,
                        fontFamily = FontFamily.Monospace,
                    ),
            )
            Spacer(Modifier.weight(1.4f))
        }
    }
}
