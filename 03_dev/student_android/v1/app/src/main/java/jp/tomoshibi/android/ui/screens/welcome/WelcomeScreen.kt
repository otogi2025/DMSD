package jp.tomoshibi.android.ui.screens.welcome

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT

// 注册完成欢迎屏 — 对应 iOS AuthStubs.swift §0.7 RegisterDoneView
// 视觉对齐 21.54.56 截图：绿勾圆 + ようこそ + 学号 + 始める
@Composable
fun WelcomeScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val name = state.user.name.ifEmpty { "リュウイヒ" }
    val studentNo = state.user.studentNo.ifEmpty { MockData.DEFAULT_USER.studentNo }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(tokens.pearl)
            .padding(horizontal = 24.dp)
            .padding(top = 60.dp, bottom = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(Modifier.weight(1f))

        // ── 绿勾圆 ──
        Box(
            modifier = Modifier
                .size(96.dp)
                .clip(CircleShape)
                .background(tokens.ok),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "✓",
                color = Color.White,
                style = TextStyle(fontSize = 56.sp, fontWeight = FontWeight.Bold)
            )
        }
        Spacer(Modifier.height(28.dp))
        Text(
            text = "ようこそ、${name}さん",
            color = tokens.ink,
            style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold),
            textAlign = TextAlign.Center
        )
        Spacer(Modifier.height(8.dp))
        Text(
            text = "アカウントが作成されました",
            color = tokens.inkSub,
            style = TextStyle(fontSize = 14.sp),
            textAlign = TextAlign.Center
        )

        Spacer(Modifier.height(28.dp))

        // ── アカウント番号 box（14sp Bold mono 行 + 6 桁号 + 説明）──
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(20.dp))
                .background(tokens.paper)
                .padding(horizontal = 20.dp, vertical = 22.dp)
        ) {
            Text(
                text = "あなたのアカウント番号",
                color = tokens.inkSub,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium)
            )
            Spacer(Modifier.height(6.dp))
            // prompt 指定 14sp Bold mono — 学号行
            Text(
                text = "アカウント番号 $studentNo",
                color = tokens.ink,
                style = TextStyle(
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace
                )
            )
            Spacer(Modifier.height(10.dp))
            Text(
                text = "次回からはこの 6 桁番号\nまたはメールアドレスと\nパスワードでログインしてください",
                color = tokens.inkMute,
                style = TextStyle(fontSize = 12.sp, lineHeight = 18.sp)
            )
        }

        Spacer(Modifier.weight(1f))

        // ── 底部 CTA capsule ──
        Box(
            modifier = Modifier
                .fillMaxWidth().height(52.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(tokens.btnGrad)
                .clickable {
                    navController.navigate(Route.Login.path) {
                        popUpTo(Route.Welcome.path) { inclusive = true }
                    }
                },
            contentAlignment = Alignment.Center
        ) {
            Text("始める", color = Color.White,
                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
        }
    }
}
