package jp.tomoshibi.android.ui.screens.welcome

import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT

// 注册完成欢迎屏 — 对齐 iOS RegisterDoneView：真 loadMe 数据 + 渐变面板 + 矢量对勾
@Composable
fun WelcomeScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    // 失败/断网时显「—」，不泄漏演示假人
    val name = state.user.name.ifEmpty { "—" }
    val studentNo = state.user.studentNo.ifEmpty { "—" }

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
        modifier =
            Modifier
                .fillMaxSize()
                .background(tokens.pearl)
                .padding(horizontal = 24.dp)
                .padding(top = 60.dp, bottom = 32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.weight(1f))

        Box(
            modifier =
                Modifier
                    .size(100.dp)
                    .scale(checkScale)
                    .alpha(checkAlpha)
                    .clip(CircleShape)
                    .background(Brush.verticalGradient(listOf(tokens.ok, tokens.okDeep))),
            contentAlignment = Alignment.Center,
        ) {
            // 自绘矢量对勾（对齐 iOS CheckIcon）
            Canvas(modifier = Modifier.size(48.dp)) {
                val path =
                    Path().apply {
                        moveTo(size.width * 0.18f, size.height * 0.52f)
                        lineTo(size.width * 0.40f, size.height * 0.72f)
                        lineTo(size.width * 0.82f, size.height * 0.28f)
                    }
                drawPath(
                    path = path,
                    color = Color.White,
                    style =
                        Stroke(
                            width = size.width * 0.12f,
                            cap = StrokeCap.Round,
                            join = StrokeJoin.Round,
                        ),
                )
            }
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

        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(20.dp))
                    .background(
                        Brush.linearGradient(
                            colors = listOf(Color(0xFFE8F4F6), Color(0xFFA8DCE2)),
                        ),
                    ).padding(horizontal = 20.dp, vertical = 22.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = "あなたのアカウント番号".uppercase(),
                color = Color(0xFF0E3840),
                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 2.sp),
            )
            Spacer(Modifier.height(8.dp))
            Text(
                text = studentNo,
                color = Color(0xFF0E3840),
                style =
                    TextStyle(
                        fontSize = 44.sp,
                        fontWeight = FontWeight.Black,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = (-0.9).sp,
                    ),
                maxLines = 1,
                softWrap = false,
                overflow = TextOverflow.Ellipsis,
            )
            Spacer(Modifier.height(10.dp))
            Text(
                text = "次回からは、この6桁の番号\nまたはメールアドレスと\nパスワードでログインしてください",
                color = Color(0xFF0E3840).copy(alpha = 0.8f),
                style = TextStyle(fontSize = 12.sp, lineHeight = 18.sp),
                textAlign = TextAlign.Center,
            )
        }

        Spacer(Modifier.weight(1f))

        Box(
            modifier =
                Modifier
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
