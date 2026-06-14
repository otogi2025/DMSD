package jp.tomoshibi.android.ui.screens.welcome

import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
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

// 注册完成欢迎屏 — 对应 iOS AuthStubs.swift §2.9 RegisterDoneView（规格 1058-1062 行）
// 全屏居中：绿勾圆（spring 弹入动画）→ ようこそ → アカウント番号大字 44sp → 始める
@Composable
fun WelcomeScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    // 保留原逻辑：从登录态 state 取姓名 / 学号，空则回退到假人占位
    val name = state.user.name.ifEmpty { "リュウイヒ" }
    val studentNo = state.user.studentNo.ifEmpty { MockData.DEFAULT_USER.studentNo }

    // ── 绿勾 spring 弹入动画 ──
    // 对齐 iOS：scaleEffect 0.2→1 + opacity 0→1，spring(response:0.4, damping:0.7)
    // 用一个一次性开关 appeared 触发：进入屏后置 true，animateFloatAsState 从初值弹到目标值
    var appeared by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) { appeared = true }
    val checkScale by animateFloatAsState(
        targetValue = if (appeared) 1f else 0.2f,
        animationSpec = spring(dampingRatio = 0.7f, stiffness = Spring.StiffnessMediumLow),
        label = "checkScale",
    )
    val checkAlpha by animateFloatAsState(
        targetValue = if (appeared) 1f else 0f,
        animationSpec = spring(dampingRatio = 0.7f, stiffness = Spring.StiffnessMediumLow),
        label = "checkAlpha",
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(tokens.pearl)
            .padding(horizontal = 24.dp)
            .padding(top = 60.dp, bottom = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.weight(1f))

        // ── 绿勾圆（100×100 绿色渐变 + 白色对勾，spring 弹入）──
        Box(
            modifier = Modifier
                .size(100.dp)
                .scale(checkScale)
                .alpha(checkAlpha)
                .clip(CircleShape)
                .background(Brush.verticalGradient(listOf(tokens.ok, tokens.okDeep))),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "✓",
                color = Color.White,
                style = TextStyle(fontSize = 56.sp, fontWeight = FontWeight.Bold),
            )
        }

        Spacer(Modifier.height(28.dp))
        Text(
            text = "ようこそ、$name さん",
            color = tokens.ink,
            style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold),
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(8.dp))
        Text(
            text = "アカウントが作成されました",
            color = tokens.inkSub,
            style = TextStyle(fontSize = 13.sp),
            textAlign = TextAlign.Center,
        )

        Spacer(Modifier.height(28.dp))

        // ── アカウント番号 面板（淡青底圆角 20 + 小标题 + 6 桁大字 44sp + 説明）──
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(20.dp))
                .background(cs.primaryContainer)
                .padding(horizontal = 20.dp, vertical = 22.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            // 小标题：11sp bold 字距 2 全大写（規格 §2.9）
            Text(
                text = "あなたのアカウント番号".uppercase(),
                color = cs.primary,
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp),
            )
            Spacer(Modifier.height(8.dp))
            // 6 桁学号大字：44sp heavy 等宽（规格要求，原来是 14sp）
            Text(
                text = studentNo,
                color = cs.primary,
                style = TextStyle(
                    fontSize = 44.sp,
                    fontWeight = FontWeight.Black,
                    fontFamily = FontFamily.Monospace,
                ),
                maxLines = 1,
            )
            Spacer(Modifier.height(10.dp))
            Text(
                text = "次回からはこの 6 桁番号\nまたはメールアドレスと\nパスワードでログインしてください",
                color = tokens.inkSub,
                style = TextStyle(fontSize = 12.sp, lineHeight = 18.sp),
                textAlign = TextAlign.Center,
            )
        }

        Spacer(Modifier.weight(1f))

        // ── 底部 始める 按钮（跳主页，对齐规格导航链 Done →(replace) home）──
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(tokens.btnGrad)
                .clickable {
                    navController.navigate(Route.Home.path) {
                        popUpTo(Route.Welcome.path) { inclusive = true }
                    }
                },
            contentAlignment = Alignment.Center,
        ) {
            Text(
                "始める",
                color = Color.White,
                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
            )
        }
    }
}
