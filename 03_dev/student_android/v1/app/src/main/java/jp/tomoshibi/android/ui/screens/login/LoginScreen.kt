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
import androidx.compose.runtime.mutableIntStateOf
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
import jp.tomoshibi.android.data.network.ApiClient
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

// 演示版预填值（对齐 iOS DEMO 分支：番号 060217 / 邮箱 demo@example.com / 密码 12345678）
private const val DEMO_ACCOUNT_NO = "060217"
private const val DEMO_EMAIL = "demo@example.com"
private const val DEMO_PASSWORD = "12345678"

// 密码本地最小长度（itsuki 2026-06-05 拍板：五端统一 6 位）
private const val PASSWORD_MIN_LEN = 6

// 登录失败累计到这个次数 → 跳锁定页（401 锁定）
private const val LOGIN_FAIL_THRESHOLD = 3

@Composable
fun LoginScreen(navController: NavHostController) {
    // 主题色 token（pearl 底色 / ink 主文字 / inkMute 浅灰等）
    val t = SuzuT.current
    // 登录态 store：演示版校验通过后写 authed=true
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
    // 登录失败累计计数（本地 state，到阈值跳锁定页）
    var failCount by remember { mutableIntStateOf(0) }

    // 当前 tab 的标识输入是否非空（番号 tab 看 accountNo / 邮箱 tab 看 email）
    val identifierFilled = if (accountMode) accountNo.isNotBlank() else email.isNotBlank()
    // 密码本地校验：至少 6 位才算通过
    val passwordValid = password.length >= PASSWORD_MIN_LEN
    // 登录按钮可点条件：标识非空 + 密码达标 + 不在加载中
    val canSubmit = identifierFilled && passwordValid && !loading

    // 真后端登录（对齐 iOS AuthStubs.tryLogin）：
    //   - 邮箱 tab → 后端未实装邮箱登录，提示切番号
    //   - 番号 tab → 调 AuthAPI.loginStudent → set ApiClient.token + 持久化 DataStore → 进 home
    //   - 演示版（debug 包）magic creds（060217 / 12345678）→ 跳过 API 直接进 home（无后端演示 / 离线场景）
    //   - 401 → 失败累计到阈值跳锁定页；422 / 网络 → 原样弹后端 / 兜底文案
    val submit: () -> Unit = submit@{
        if (loading) return@submit
        // 邮箱 tab：后端只支持学号登录，提示切番号（对齐 iOS）
        if (!accountMode) {
            Toast.makeText(context, "アカウント番号でログインしてください", Toast.LENGTH_SHORT).show()
            return@submit
        }
        // 账号去首尾空白（学号是 6 桁数字、复制粘贴常带空格 / 换行）；密码不 trim（空格也算密码内容）
        val trimmedAcc = accountNo.trim()
        if (trimmedAcc.isEmpty() || password.isEmpty()) {
            Toast.makeText(context, "アカウント番号とパスワードを入力してください", Toast.LENGTH_SHORT).show()
            return@submit
        }
        loading = true
        scope.launch {
            // 演示版 magic creds：仅 debug 包生效，跳过 API 直接进 home（用于无后端演示 / 离线）
            if (BuildConfig.DEBUG && trimmedAcc == DEMO_ACCOUNT_NO && password == DEMO_PASSWORD) {
                failCount = 0
                store.update { it.copy(authed = true) }
                loading = false
                navController.navigate(Route.Home.path) {
                    popUpTo(0) { inclusive = true }
                }
                return@launch
            }
            // 真实 API 登录
            try {
                val token = AuthAPI.loginStudent(trimmedAcc, password)
                // set ApiClient.token：之后所有请求自动带 Authorization: Bearer
                ApiClient.token = token.accessToken
                failCount = 0
                // 持久化令牌进 DataStore（authed + authToken），下次启动 MainActivity 自动恢复 = 自动登录
                store.update { it.copy(authed = true, authToken = token.accessToken) }
                loading = false
                navController.navigate(Route.Home.path) {
                    popUpTo(0) { inclusive = true }
                }
            } catch (e: ApiError) {
                loading = false
                when (e) {
                    // 学号 / 密码错（401）→ 失败累计，到阈值跳锁定页
                    is ApiError.Unauthorized -> {
                        failCount += 1
                        if (failCount >= LOGIN_FAIL_THRESHOLD) {
                            navController.navigate(Route.Lockout.path)
                        } else {
                            Toast.makeText(context, "アカウント番号またはパスワードが違います", Toast.LENGTH_SHORT).show()
                        }
                    }

                    // 422（格式错，后端日语消息）/ 网络 / 解码 等 → 原样弹提示，不累计失败
                    else -> {
                        Toast.makeText(context, e.display, Toast.LENGTH_SHORT).show()
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
        // ── 顶部居中标题块（Tomoshibi + 灯火 · ログイン）─────────
        Spacer(Modifier.height(40.dp))
        Column(
            modifier = Modifier.fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                "Tomoshibi",
                color = MaterialTheme.colorScheme.primary,
                style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.12.sp),
            )
            Spacer(Modifier.height(6.dp))
            Text(
                "灯火 · ログイン",
                color = t.inkMute,
                style = TextStyle(fontSize = 12.sp, letterSpacing = 1.sp),
            )
        }
        Spacer(Modifier.height(36.dp))

        // ── mode tab（2 段切换：番号 / メール）───────────────
        // 容器底 pill 圆角 12 padding 3，激活 tab = paper 底 + primary 字 / 非激活 = 透明 + inkSub。
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
        Spacer(Modifier.height(20.dp))

        // ── 字段区：随 tab 切标识输入框 + 恒显密码 ───────────
        if (accountMode) {
            // 番号 mode：アカウント番号（数字键盘）
            Field(label = "アカウント番号") {
                TField(
                    value = accountNo,
                    onValueChange = { accountNo = it },
                    placeholder = "000000",
                    keyboard = KeyboardType.Number,
                )
            }
        } else {
            // メール mode：メールアドレス（邮箱键盘）
            Field(label = "メールアドレス") {
                TField(
                    value = email,
                    onValueChange = { email = it },
                    placeholder = "example@email.com",
                    keyboard = KeyboardType.Email,
                )
            }
        }
        Spacer(Modifier.height(14.dp))

        // 密码（secure 遮码）；本地校验最少 6 位，不足时 Field 显示红字错误
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
        // 规格 §2.10：右侧「パスワードを忘れた」入口在 v1.0 上架版已隐藏（避免 Apple 死按钮被拒），
        // Android 也不做这个链接 —— PwReset 屏作为路由保留备用，但登录页不给入口。
        Spacer(Modifier.height(20.dp))

        // ── 登录主按钮（演示版本地校验 → 进主页）───────────
        PrimaryButton(
            title = if (loading) "ログイン中…" else "ログイン",
            enabled = canSubmit,
            onClick = submit,
        )
        Spacer(Modifier.height(12.dp))

        // ── 次按钮：新規登録（跳注册第 1 步）───────────────
        jp.tomoshibi.android.ui.components.GhostButton(
            title = "新規登録",
            onClick = { navController.navigate(Route.Account.path) },
        )

        Spacer(Modifier.weight(1f))
        // 版本号脚注
        Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
            Text(
                text = "v0.12.0 · © Tomoshibi",
                color = t.inkMute,
                style = TextStyle(fontSize = 12.sp),
            )
        }
    }
}

// mode tab 单段：激活 = paper 底 + primary 字 + 加粗 / 非激活 = 透明 + inkSub。高 40。
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
