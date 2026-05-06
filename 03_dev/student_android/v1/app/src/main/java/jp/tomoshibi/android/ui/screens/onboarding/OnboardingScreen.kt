package jp.tomoshibi.android.ui.screens.onboarding

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 3 page onboarding — 对应 iOS AuthStubs.swift OnboardingView
// 240dp 圆角 36dp 渐变 illustration + 大 icon + title 28sp + sub 15sp
private data class OnboardingPage(
    val icon: ImageVector,
    val title: String,
    val sub: String,
    val gradStart: Color,
    val gradEnd: Color,
    val fg: Color
)

private val PAGES = listOf(
    OnboardingPage(
        icon = SuzuIcons.Nfc,
        title = "タッチで点呼",
        sub = "NFC にかざすだけ",
        gradStart = Color(0xFFE8F4F6), gradEnd = Color(0xFFA8DCE2),
        fg = Color(0xFF2A7E84)
    ),
    OnboardingPage(
        icon = SuzuIcons.Edit,
        title = "申請はアプリで",
        sub = "外泊・帰省・タクシー",
        gradStart = Color(0xFFFDF4E1), gradEnd = Color(0xFFFFE9B5),
        fg = Color(0xFFB8761A)
    ),
    OnboardingPage(
        icon = SuzuIcons.Sparkle,
        title = "寮生活をひとつに",
        sub = "バス・活動・荷物",
        gradStart = Color(0xFFE3F1EA), gradEnd = Color(0xFF8BC6A3),
        fg = Color(0xFF2E7D4F)
    )
)

@Composable
fun OnboardingScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var page by remember { mutableStateOf(0) }
    val current = PAGES[page]

    val finishOnboarding: () -> Unit = {
        scope.launch {
            store.update { it.copy(onboarded = true) }
            navController.navigate(Route.Account.path) {
                popUpTo(Route.Onboarding.path) { inclusive = true }
            }
        }
    }

    val next: () -> Unit = {
        if (page < PAGES.lastIndex) page++
        else finishOnboarding()
    }

    Column(
        modifier = Modifier.fillMaxSize().background(tokens.paper)
    ) {
        // ── top-right スキップ ──
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.End
        ) {
            Box(modifier = Modifier.clickable { finishOnboarding() }.padding(8.dp)) {
                Text(
                    text = "スキップ",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium)
                )
            }
        }

        // ── illustration + title + sub ──
        Column(
            modifier = Modifier.weight(1f).fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(240.dp)
                    .shadow(elevation = 30.dp, shape = RoundedCornerShape(36.dp))
                    .clip(RoundedCornerShape(36.dp))
                    .background(
                        Brush.linearGradient(
                            colors = listOf(current.gradStart, current.gradEnd)
                        )
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = current.icon,
                    contentDescription = null,
                    tint = current.fg,
                    modifier = Modifier.size(120.dp)
                )
            }
            Spacer(Modifier.height(44.dp))
            Text(
                text = current.title,
                color = tokens.ink,
                style = TextStyle(
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    lineHeight = 38.sp
                ),
                textAlign = TextAlign.Center
            )
            Spacer(Modifier.height(10.dp))
            Text(
                text = current.sub,
                color = tokens.inkSub,
                style = TextStyle(fontSize = 15.sp, lineHeight = 24.sp),
                textAlign = TextAlign.Center
            )
        }

        // ── dot indicator ──
        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 20.dp),
            horizontalArrangement = Arrangement.Center
        ) {
            PAGES.indices.forEach { i ->
                val w by animateDpAsState(if (i == page) 24.dp else 8.dp, label = "dotWidth")
                Box(
                    modifier = Modifier
                        .padding(horizontal = 4.dp)
                        .size(width = w, height = 8.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(if (i == page) tokens.ink else tokens.inkFaint)
                )
            }
        }

        // ── CTA capsule ──
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 24.dp)
                .padding(top = 20.dp, bottom = 32.dp)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth().height(52.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(tokens.btnGrad)
                    .clickable { next() },
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (page < PAGES.lastIndex) "次へ" else "始める",
                    color = Color.White,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold)
                )
            }
        }
    }
}
