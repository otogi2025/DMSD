package jp.tomoshibi.android.ui.screens.login

import android.widget.Toast
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.BuildConfig
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.ApiErrorPresenter
import jp.tomoshibi.android.data.network.endpoints.AuthAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 演示版预填值（对齐 iOS DEMO 分支：番号 060217 / 邮箱 demo@example.com / 密码 12345678）
private const val DEMO_ACCOUNT_NO = "060217"
private const val DEMO_EMAIL = "demo@example.com"
private const val DEMO_PASSWORD = "12345678"

// 密码本地最小长度（itsuki 2026-06-05 拍板：五端统一 6 位）
private const val PASSWORD_MIN_LEN = 6

@Composable
fun LoginScreen(navController: NavHostController) {
    // 主题色 token（pearl 底色 / ink 主文字 / inkMute 浅灰等）
    val t = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()
    val context = LocalContext.current

    // mode tab：true=番号 tab（默认，对齐 iOS 优先番号）/ false=邮箱 tab
    var accountMode by remember { mutableStateOf(true) }
    // 番号输入框（数字键盘）。演示版（debug 包）预填演示账号方便点；正式版（release）留空，不泄漏演示凭据。
    var accountNo by remember { mutableStateOf(if (BuildConfig.DEBUG) DEMO_ACCOUNT_NO else "") }
    // 邮箱输入框（邮箱键盘）。debug 包预填注册流邮箱 / 演示邮箱；release 留空。
    var email by remember { mutableStateOf(if (BuildConfig.DEBUG) state.user.email.ifEmpty { DEMO_EMAIL } else "") }
    // 密码输入框（secure 遮码）。debug 包预填演示密码；release 留空。
    var password by remember { mutableStateOf(if (BuildConfig.DEBUG) DEMO_PASSWORD else "") }
    // 加载态：点登录后按钮变「ログイン中…」并禁用，避免重复提交
    var loading by remember { mutableStateOf(false) }

    // 当前 tab 的标识输入是否非空（番号 tab 看 accountNo / 邮箱 tab 看 email）
    val identifierFilled = if (accountMode) accountNo.isNotBlank() else email.isNotBlank()
    // 密码本地校验：至少 6 位才算通过
    val passwordValid = password.length >= PASSWORD_MIN_LEN
    // 登录按钮可点条件：标识非空 + 密码达标 + 不在加载中
    val canSubmit = identifierFilled && passwordValid && !loading

    // 真后端登录（对齐 iOS AuthStubs.tryLogin）：
    //   - 成功 → setAuthToken + loadMe + 进 Home
    //   - 401 → DEBUG 走锁定阶梯页；RELEASE 只 toast（锁定真值以后端 423 为准）
    //   - 423 → 写后端剩余秒数进 store → LockoutScreen
    //   - 403 → toast（账号停用）
    val submit: () -> Unit = submit@{
        if (loading) return@submit
        val trimmedAcc = accountNo.trim()
        val trimmedEmail = email.trim()
        if (accountMode) {
            if (trimmedAcc.isEmpty() || password.isEmpty()) {
                Toast.makeText(context, "アカウント番号とパスワードを入力してください", Toast.LENGTH_SHORT).show()
                return@submit
            }
        } else {
            if (trimmedEmail.isEmpty() || password.isEmpty()) {
                Toast.makeText(context, "メールアドレスとパスワードを入力してください", Toast.LENGTH_SHORT).show()
                return@submit
            }
        }
        loading = true
        scope.launch {
            // 演示版 magic creds：仅 debug + 番号 tab 生效，跳过 API 直接进 home
            if (
                accountMode &&
                BuildConfig.DEBUG &&
                trimmedAcc == DEMO_ACCOUNT_NO &&
                password == DEMO_PASSWORD
            ) {
                store.resetLoginFailures()
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
                // IX-036 对齐：一并写过期时刻，再级联拉真实资料
                store.setAuthToken(token.accessToken, token.expiresIn)
                store.resetLoginFailures()
                store.loadMe()
                loading = false
                navController.navigate(Route.Home.path) {
                    popUpTo(0) { inclusive = true }
                }
            } catch (e: ApiError) {
                loading = false
                when (e) {
                    is ApiError.Unauthorized -> {
                        if (BuildConfig.DEBUG) {
                            // 演示：本地累计失败次数 → 锁定页读 store.loginFailCount 渲染阶梯
                            store.recordLoginFailure()
                            navController.navigate(Route.Lockout.path)
                        } else {
                            // 生产：不本地写死倒计时；凭证错只 toast（对齐 iOS 生产）
                            val msg =
                                if (accountMode) {
                                    "アカウント番号またはパスワードが正しくありません"
                                } else {
                                    "メールアドレスまたはパスワードが正しくありません"
                                }
                            Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                        }
                    }

                    is ApiError.Server -> {
                        when (e.code) {
                            // 后端真锁（B6）→ 剩余秒数以后端文案为准
                            423 -> {
                                val msg =
                                    e.msg.ifEmpty {
                                        "アカウントロック中です。しばらくしてからお試しください"
                                    }
                                store.applyBackendLockout(msg)
                                navController.navigate(Route.Lockout.path)
                            }

                            // 账号停用
                            403 -> {
                                val msg =
                                    e.msg.ifEmpty {
                                        "このアカウントは現在ご利用いただけません。寮監に申し出てください"
                                    }
                                Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                            }

                            else -> {
                                Toast.makeText(context, e.display, Toast.LENGTH_SHORT).show()
                            }
                        }
                    }

                    else -> {
                        Toast
                            .makeText(
                                context,
                                ApiErrorPresenter.userMessage(e, "ログインに失敗しました"),
                                Toast.LENGTH_SHORT,
                            ).show()
                    }
                }
            }
        }
    }

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .background(t.pearl)
                .padding(horizontal = 28.dp)
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

        if (accountMode) {
            Field(label = "アカウント番号") {
                TField(
                    value = accountNo,
                    onValueChange = { accountNo = it },
                    placeholder = "000000",
                    keyboard = KeyboardType.Number,
                )
            }
        } else {
            Field(label = "メールアドレス") {
                TField(
                    value = email,
                    onValueChange = { email = it },
                    placeholder = "example@email.com",
                    keyboard = KeyboardType.Email,
                )
            }
        }
        Spacer(modifier = Modifier.height(14.dp))

        Field(
            label = "パスワード",
            error = if (password.isNotEmpty() && !passwordValid) "パスワードは 6 文字以上です" else null,
        ) {
            TField(
                value = password,
                onValueChange = { password = it },
                placeholder = "••••••",
                secure = true,
                keyboard = KeyboardType.Password,
            )
        }
        Spacer(modifier = Modifier.height(20.dp))

        PrimaryButton(
            title = if (loading) "ログイン中…" else "ログイン",
            enabled = canSubmit,
            onClick = submit,
        )
        Spacer(modifier = Modifier.height(12.dp))

        jp.tomoshibi.android.ui.components.GhostButton(
            title = "新規登録",
            onClick = { navController.navigate(Route.Account.path) },
        )

        Spacer(modifier = Modifier.weight(1f))
        Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
            Text(
                text = "v${BuildConfig.VERSION_NAME} · © Tomoshibi",
                color = t.inkMute,
                style = TextStyle(fontSize = 12.sp),
            )
        }
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
                .clip(RoundedCornerShape(9.dp))
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
