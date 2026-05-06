package jp.tomoshibi.android.ui.screens.login

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.AppState
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    var email by remember { mutableStateOf(state.user.email.ifEmpty { "haruki@tomoshibi.jp" }) }
    var password by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(false) }

    val submit: () -> Unit = {
        loading = true
        scope.launch {
            delay(700)
            store.update { it.copy(authed = true) }
            navController.navigate(Route.Home.path) {
                popUpTo(Route.Login.path) { inclusive = true }
            }
        }
    }

    // DEMO: 注册一路点完后回到 Login，1.5 秒自动 ログイン → Home
    // 实质 = iOS 「アカウント作成完了→自動ログイン」体验等价（v1.0 demo 阶段）
    LaunchedEffect(state.user.email) {
        if (state.user.email.isNotBlank() && !state.authed) {
            delay(1500)
            submit()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(tokens.pearl)
            .padding(horizontal = 28.dp)
            .padding(top = 40.dp, bottom = 24.dp)
    ) {
        // ── header: 灯 logo + Tomoshibi 字 ─────────
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(14.dp),
            // header marginTop 30→50dp（按 prompt 调整）
            modifier = Modifier.padding(top = 50.dp, bottom = 60.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(tokens.btnGrad),
                contentAlignment = Alignment.Center
            ) {
                Text("灯", color = Color.White, style = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Light))
            }
            Column {
                Text("Tomoshibi", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
                Text("寮生活アプリ", color = tokens.inkSub, style = TextStyle(fontSize = 12.sp))
            }
        }

        Text("おかえりなさい", color = tokens.ink, style = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.Bold))
        Spacer(Modifier.height(6.dp))
        Text("メールアドレスでログイン", color = tokens.inkSub, style = TextStyle(fontSize = 14.sp))
        Spacer(Modifier.height(24.dp))

        // ── email ──
        Text("メールアドレス", color = tokens.inkSub, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
        Spacer(Modifier.height(6.dp))
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            shape = RoundedCornerShape(12.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = tokens.ink,
                unfocusedBorderColor = tokens.hair,
                focusedContainerColor = tokens.paper,
                unfocusedContainerColor = tokens.paper
            )
        )
        Spacer(Modifier.height(14.dp))

        // ── password ──
        Text("パスワード", color = tokens.inkSub, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
        Spacer(Modifier.height(6.dp))
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            shape = RoundedCornerShape(12.dp),
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            placeholder = { Text("••••••") },
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = tokens.ink,
                unfocusedBorderColor = tokens.hair,
                focusedContainerColor = tokens.paper,
                unfocusedContainerColor = tokens.paper
            )
        )
        Spacer(Modifier.height(8.dp))

        // 忘记密码（暂无功能）
        Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.CenterEnd) {
            TextButton(onClick = { /* TODO: forgot password flow */ }) {
                Text("パスワードを忘れた？", color = tokens.ink, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
            }
        }
        Spacer(Modifier.height(20.dp))

        // ── primary CTA ──
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(tokens.btnGrad),
            contentAlignment = Alignment.Center
        ) {
            Button(
                onClick = submit,
                enabled = !loading && email.isNotBlank(),
                modifier = Modifier.fillMaxSize(),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.Transparent,
                    contentColor = Color.White,
                    disabledContainerColor = Color.Transparent,
                    disabledContentColor = Color.White.copy(alpha = 0.5f)
                ),
                contentPadding = PaddingValues(0.dp)
            ) {
                Text(
                    text = if (loading) "ログイン中…" else "ログイン",
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold)
                )
            }
        }
        Spacer(Modifier.height(12.dp))

        // ── secondary: account creation ──
        OutlinedButton(
            onClick = { navController.navigate(Route.Account.path) },
            modifier = Modifier.fillMaxWidth().height(52.dp),
            shape = RoundedCornerShape(16.dp),
            border = androidx.compose.foundation.BorderStroke(1.5.dp, tokens.hair),
            colors = ButtonDefaults.outlinedButtonColors(contentColor = tokens.ink)
        ) {
            Text("アカウント作成", style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold))
        }

        Spacer(Modifier.weight(1f))
        Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
            Text(
                text = "v1.0.0 · © Tomoshibi",
                color = tokens.inkMute,
                style = TextStyle(fontSize = 12.sp)
            )
        }
    }
}
