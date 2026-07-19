package jp.tomoshibi.android.ui.screens.login

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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
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
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.BuildConfig
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.AuthAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 演示版预填值（对齐 iOS DEMO：番号 060217 / 邮箱 demo@example.com / 密码 12345678）
private const val DEMO_ACCOUNT_NO = "060217"
private const val DEMO_EMAIL = "demo@example.com"
private const val DEMO_PASSWORD = "12345678"

@Composable
fun LoginScreen(navController: NavHostController) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    // 登录方式 tab：true=学号 / false=邮箱
    var accountMode by remember { mutableStateOf(true) }
    var accountNo by remember { mutableStateOf(if (BuildConfig.DEBUG) DEMO_ACCOUNT_NO else "") }
    var email by remember { mutableStateOf(if (BuildConfig.DEBUG) state.user.email.ifEmpty { DEMO_EMAIL } else "") }
    var password by remember { mutableStateOf(if (BuildConfig.DEBUG) DEMO_PASSWORD else "") }
    var loading by remember { mutableStateOf(false) }

    // 可点条件：当前 tab 标识非空 + 密码非空 + 不在加载中（只查非空，不查密码长度——交后端）
    val identifierFilled = if (accountMode) accountNo.isNotBlank() else email.isNotBlank()
    val canSubmit = identifierFilled && password.isNotEmpty() && !loading

    // 真后端登录（对齐 iOS AuthStubs.tryLogin 生产行为）：
    //   成功 → setAuthToken + loadMe → home
    //   401 → 只 toast（不本地计数、不跳锁定页）
    //   423 / 403 → 干净 toast（空则兜底文案）
    //   422 → 直显后端文案
    val submit: () -> Unit = submit@{
        if (loading) return@submit
        val trimmedAcc = accountNo.trim()
        val trimmedEmail = email.trim()
        // 密码不 trim（对齐 iOS）
        if (accountMode) {
            if (trimmedAcc.isEmpty() || password.isEmpty()) {
                store.showToast("アカウント番号とパスワードを入力してください")
                return@submit
            }
        } else {
            if (trimmedEmail.isEmpty() || password.isEmpty()) {
                store.showToast("メールアドレスとパスワードを入力してください")
                return@submit
            }
        }
        loading = true
        scope.launch {
            // debug 包 magic creds：番号 tab 跳过 API 直接进 home
            if (
                accountMode &&
                BuildConfig.DEBUG &&
                trimmedAcc == DEMO_ACCOUNT_NO &&
                password == DEMO_PASSWORD
            ) {
                store.update { it.copy(authed = true) }
                loading = false
                navController.navigate(Route.Home.path) {
                    popUpTo(0) { inclusive = true }
                }
                return@launch
            }
            try {
                val token =
                    if (accountMode) {
                        AuthAPI.loginStudent(trimmedAcc, password)
                    } else {
                        AuthAPI.loginStudentByEmail(trimmedEmail, password)
                    }
                store.setAuthToken(token.accessToken, token.expiresIn)
                store.loadMe()
                loading = false
                navController.navigate(Route.Home.path) {
                    popUpTo(0) { inclusive = true }
                }
            } catch (e: ApiError) {
                loading = false
                when (e) {
                    is ApiError.Unauthorized -> {
                        val msg =
                            if (accountMode) {
                                "アカウント番号またはパスワードが正しくありません"
                            } else {
                                "メールアドレスまたはパスワードが正しくありません"
                            }
                        store.showToast(msg)
                    }

                    is ApiError.Unprocessable -> {
                        store.showToast(e.msg)
                    }

                    is ApiError.Server -> {
                        when (e.code) {
                            423 -> {
                                store.showToast(
                                    e.msg.ifEmpty {
                                        "アカウントロック中です。しばらくしてからお試しください"
                                    },
                                )
                            }

                            403 -> {
                                store.showToast(
                                    e.msg.ifEmpty {
                                        "このアカウントは現在ご利用いただけません。寮監に申し出てください"
                                    },
                                )
                            }

                            else -> {
                                store.showToast(e.display)
                            }
                        }
                    }

                    is ApiError.Network -> {
                        store.showToast("通信エラーが発生しました。電波を確認してください")
                    }

                    else -> {
                        store.showToast(e.display)
                    }
                }
            }
        }
    }

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .background(
                    Brush.verticalGradient(
                        colors = listOf(t.pearl, Color(0xFFE4EBEC)),
                    ),
                ).padding(horizontal = 28.dp)
                .padding(top = 40.dp, bottom = 24.dp),
    ) {
        Spacer(modifier = Modifier.height(40.dp))
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                "Tomoshibi",
                color = MaterialTheme.colorScheme.primary,
                style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.12.sp),
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                "灯火 · ログイン",
                color = t.inkMute,
                style = TextStyle(fontSize = 12.sp, letterSpacing = 1.sp),
            )
        }
        Spacer(modifier = Modifier.height(36.dp))

        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.pill)
                    .padding(3.dp),
            horizontalArrangement = Arrangement.spacedBy(3.dp),
        ) {
            ModeTab(
                title = "番号",
                active = accountMode,
                modifier = Modifier.weight(1f),
                onClick = { accountMode = true },
            )
            ModeTab(
                title = "メール",
                active = !accountMode,
                modifier = Modifier.weight(1f),
                onClick = { accountMode = false },
            )
        }
        Spacer(modifier = Modifier.height(20.dp))

        // 三输入框 placeholder 全空（对齐 iOS）
        if (accountMode) {
            Field(label = "アカウント番号") {
                TField(
                    value = accountNo,
                    onValueChange = { accountNo = it },
                    placeholder = "",
                    keyboard = KeyboardType.Number,
                )
            }
        } else {
            Field(label = "メールアドレス") {
                TField(
                    value = email,
                    onValueChange = { email = it },
                    placeholder = "",
                    keyboard = KeyboardType.Email,
                )
            }
        }
        Spacer(modifier = Modifier.height(18.dp))

        Field(label = "パスワード") {
            TField(
                value = password,
                onValueChange = { password = it },
                placeholder = "",
                secure = true,
                keyboard = KeyboardType.Password,
            )
        }
        Spacer(modifier = Modifier.height(8.dp))

        PrimaryButton(
            title = if (loading) "ログイン中…" else "ログイン",
            enabled = canSubmit,
            onClick = submit,
        )

        Spacer(modifier = Modifier.height(16.dp))
        // footer：左对齐纯文字「新規登録」，无版本号、无密码找回入口
        Text(
            text = "新規登録",
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            modifier = Modifier.clickable { navController.navigate(Route.Account.path) },
        )

        Spacer(modifier = Modifier.weight(1f))
    }
}

@Composable
private fun ModeTab(
    title: String,
    active: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            modifier
                .height(40.dp)
                .then(
                    if (active) {
                        Modifier.shadow(
                            elevation = 2.dp,
                            shape = RoundedCornerShape(10.dp),
                            ambientColor = Color(0x0F1E22).copy(alpha = 0.08f),
                            spotColor = Color(0x0F1E22).copy(alpha = 0.08f),
                        )
                    } else {
                        Modifier
                    },
                ).clip(RoundedCornerShape(10.dp))
                .background(if (active) t.paper else Color.Transparent)
                .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = title,
            color = if (active) MaterialTheme.colorScheme.primary else t.inkSub,
            style = TextStyle(fontSize = 14.sp, fontWeight = if (active) FontWeight.Bold else FontWeight.Medium),
        )
    }
}
