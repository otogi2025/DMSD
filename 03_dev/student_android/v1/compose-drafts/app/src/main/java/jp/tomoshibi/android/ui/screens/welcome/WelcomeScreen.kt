package jp.tomoshibi.android.ui.screens.welcome

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT

@Composable
fun WelcomeScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val name = state.user.name.ifEmpty { "新入寮生" }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(tokens.btnGrad)
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(120.dp)
                .clip(RoundedCornerShape(32.dp))
                .background(Color.White.copy(alpha = 0.18f)),
            contentAlignment = Alignment.Center
        ) {
            Text("🎉", style = TextStyle(fontSize = 70.sp))
        }
        Spacer(Modifier.height(28.dp))
        Text("ようこそ、${name}さん", color = Color.White,
            style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold),
            textAlign = TextAlign.Center)
        Spacer(Modifier.height(12.dp))
        Text("アカウントが作成されました。\nさっそく使ってみましょう。",
            color = Color.White.copy(alpha = 0.9f),
            style = TextStyle(fontSize = 15.sp, lineHeight = 26.sp),
            textAlign = TextAlign.Center)
        Spacer(Modifier.height(40.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth().height(52.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(Color.White)
                .clickable {
                    navController.navigate(Route.Login.path) {
                        popUpTo(Route.Welcome.path) { inclusive = true }
                    }
                },
            contentAlignment = Alignment.Center
        ) {
            Text("ログインへ", color = tokens.ink,
                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
        }
    }
}
