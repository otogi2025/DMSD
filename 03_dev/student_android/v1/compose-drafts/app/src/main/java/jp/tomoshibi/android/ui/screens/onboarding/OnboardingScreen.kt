package jp.tomoshibi.android.ui.screens.onboarding

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
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

private data class OnboardingPage(val emoji: String, val title: String, val body: String, val accent: String)

private val PAGES = listOf(
    OnboardingPage("🔔", "点呼を、もっとシンプルに。", "NFCタッチで一瞬。寮監も生徒もラクに。", "点呼"),
    OnboardingPage("📝", "申請がスマホで完結。", "外泊・外出の申請、承認状況も一覧で。", "申請"),
    OnboardingPage("🏠", "寮生活の中心へ。", "お知らせ、行事、忘れ物、ぜんぶここに。", "寮生活")
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
        if (page < 2) page++
        else finishOnboarding()
    }

    Column(
        modifier = Modifier.fillMaxSize().background(tokens.pearl)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
            horizontalArrangement = Arrangement.End
        ) {
            Box(modifier = Modifier.clickable { finishOnboarding() }.padding(8.dp)) {
                Text("スキップ", color = tokens.inkSub,
                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium))
            }
        }

        Column(
            modifier = Modifier.weight(1f).fillMaxWidth().padding(horizontal = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Box(
                modifier = Modifier
                    .size(140.dp)
                    .shadow(elevation = 12.dp, shape = RoundedCornerShape(36.dp))
                    .clip(RoundedCornerShape(36.dp))
                    .background(tokens.btnGrad),
                contentAlignment = Alignment.Center
            ) {
                Text(current.emoji, style = TextStyle(fontSize = 70.sp))
            }
            Spacer(Modifier.height(20.dp))
            Text(current.accent.uppercase(), color = tokens.ink,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp))
            Spacer(Modifier.height(16.dp))
            Text(current.title, color = tokens.ink,
                style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold, lineHeight = 36.sp),
                textAlign = TextAlign.Center)
            Spacer(Modifier.height(20.dp))
            Text(current.body, color = tokens.inkSub,
                style = TextStyle(fontSize = 15.sp, lineHeight = 26.sp),
                textAlign = TextAlign.Center,
                modifier = Modifier.widthIn(max = 280.dp))
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(vertical = 20.dp),
            horizontalArrangement = Arrangement.Center
        ) {
            (0..2).forEach { i ->
                val w by animateDpAsState(if (i == page) 24.dp else 8.dp, label = "dotWidth")
                Box(
                    modifier = Modifier
                        .padding(horizontal = 4.dp)
                        .size(width = w, height = 8.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(if (i == page) tokens.ink else tokens.hair)
                )
            }
        }

        Box(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp).padding(bottom = 32.dp, top = 8.dp)) {
            Box(
                modifier = Modifier
                    .fillMaxWidth().height(52.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .background(tokens.btnGrad)
                    .clickable { next() },
                contentAlignment = Alignment.Center
            ) {
                Text(if (page < 2) "次へ" else "はじめる",
                    color = Color.White,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
            }
        }
    }
}
