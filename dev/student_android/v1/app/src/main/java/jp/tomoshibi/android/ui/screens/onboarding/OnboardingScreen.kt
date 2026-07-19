package jp.tomoshibi.android.ui.screens.onboarding

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
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

// 4 页介绍 — 对齐 iOS OnboardingView（无跳过；看完 → login）
// 页 4 裁决：Android 无 Apple Intelligence，只留「お知らせをワンタップ翻訳」一条

private data class OnboardingPage(
    val icon: ImageVector,
    val title: String,
    val sub: String? = null,
    val features: List<String>? = null,
    val gradStart: Color,
    val gradEnd: Color,
    val fg: Color,
)

@Composable
fun OnboardingScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var page by remember { mutableStateOf(0) }

    val pages =
        remember(primary) {
            listOf(
                OnboardingPage(
                    icon = SuzuIcons.Nfc,
                    title = "タッチで点呼",
                    sub = "かざすだけで\n毎日の点呼が数秒で完了",
                    gradStart = Color(0xFFE8F4F6),
                    gradEnd = Color(0xFFA8DCE2),
                    fg = primary,
                ),
                OnboardingPage(
                    icon = SuzuIcons.Edit,
                    title = "外泊も帰省もアプリから",
                    sub = "外泊・帰省・タクシー…\n申請はすべてここで",
                    gradStart = Color(0xFFFDF4E1),
                    gradEnd = Color(0xFFFFE9B5),
                    fg = Color(0xFFB8761A),
                ),
                OnboardingPage(
                    icon = SuzuIcons.Person,
                    title = "自分の記録をいつでも",
                    sub = "点呼履歴も減点も\nマイページで確認",
                    gradStart = Color(0xFFE3F1EA),
                    gradEnd = Color(0xFF8BC6A3),
                    fg = Color(0xFF2E7D4F),
                ),
                OnboardingPage(
                    icon = SuzuIcons.Sparkle,
                    title = "AIでもっと便利に",
                    features = listOf("お知らせをワンタップ翻訳"),
                    gradStart = Color(0xFFF0EBFB),
                    gradEnd = Color(0xFFC9B8F0),
                    fg = Color(0xFF7A5CC4),
                ),
            )
        }
    val current = pages[page]

    val finishOnboarding: () -> Unit = {
        scope.launch {
            store.update { it.copy(onboarded = true) }
            navController.navigate(Route.Login.path) {
                popUpTo(Route.Onboarding.path) { inclusive = true }
            }
        }
    }

    val next: () -> Unit = {
        if (page < pages.lastIndex) page++ else finishOnboarding()
    }

    Column(
        modifier = Modifier.fillMaxSize().background(tokens.paper),
    ) {
        // 无跳过按钮 — itsuki 拍板必须看完 4 页

        Column(
            modifier = Modifier.weight(1f).fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Box(
                modifier =
                    Modifier
                        .size(200.dp)
                        .shadow(elevation = 30.dp, shape = RoundedCornerShape(36.dp))
                        .clip(RoundedCornerShape(36.dp))
                        .background(
                            Brush.linearGradient(
                                colors = listOf(current.gradStart, current.gradEnd),
                            ),
                        ),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = current.icon,
                    contentDescription = null,
                    tint = current.fg,
                    modifier = Modifier.size(100.dp),
                )
            }
            Spacer(Modifier.height(36.dp))
            Text(
                text = current.title,
                color = tokens.ink,
                style =
                    TextStyle(
                        fontSize = 26.sp,
                        fontWeight = FontWeight.Bold,
                        lineHeight = 34.sp,
                    ),
                textAlign = TextAlign.Center,
                modifier = Modifier.padding(horizontal = 24.dp),
            )
            Spacer(Modifier.height(12.dp))
            current.sub?.let { sub ->
                Text(
                    text = sub,
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 15.sp, lineHeight = 24.sp),
                    textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 24.dp),
                )
            }
            current.features?.let { features ->
                Column(
                    modifier = Modifier.padding(horizontal = 40.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    features.forEach { label ->
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                        ) {
                            Box(
                                modifier =
                                    Modifier
                                        .size(28.dp)
                                        .clip(CircleShape)
                                        .background(current.fg.copy(alpha = 0.12f)),
                                contentAlignment = Alignment.Center,
                            ) {
                                Icon(
                                    imageVector = SuzuIcons.Globe,
                                    contentDescription = null,
                                    tint = current.fg,
                                    modifier = Modifier.size(14.dp),
                                )
                            }
                            Text(
                                text = label,
                                color = tokens.ink,
                                style = TextStyle(fontSize = 14.5.sp, fontWeight = FontWeight.Medium),
                            )
                        }
                    }
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(top = 20.dp),
            horizontalArrangement = Arrangement.Center,
        ) {
            pages.indices.forEach { i ->
                val w by animateDpAsState(if (i == page) 24.dp else 8.dp, label = "dotWidth")
                Box(
                    modifier =
                        Modifier
                            .padding(horizontal = 4.dp)
                            .size(width = w, height = 8.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .background(if (i == page) primary else tokens.inkFaint),
                )
            }
        }

        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
                    .padding(top = 20.dp, bottom = 32.dp),
        ) {
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(52.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .background(tokens.btnGrad)
                        .clickable { next() },
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = if (page < pages.lastIndex) "次へ" else "始める",
                    color = Color.White,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
    }
}
