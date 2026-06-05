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
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.delay
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
    // 番号输入框（数字键盘）
    var accountNo by remember { mutableStateOf(DEMO_ACCOUNT_NO) }
    // 邮箱输入框（邮箱键盘）— 若注册流预填了 user.email 用它，否则用演示邮箱
    var email by remember { mutableStateOf(state.user.email.ifEmpty { DEMO_EMAIL }) }
    // 密码输入框（secure 遮码）
    var password by remember { mutableStateOf(DEMO_PASSWORD) }
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

    // 演示版登录：本地校验通过 → authed=true → 进主页（清栈不让返回登录）；
    // 校验不过当失败处理，累计到阈值跳锁定页。
    val submit: () -> Unit = submit@{
        if (loading) return@submit
        loading = true
        scope.launch {
            delay(600)
            // 演示版校验：标识非空 + 密码达 6 位即视为登录成功
            val ok = identifierFilled && passwordValid
            if (ok) {
                failCount = 0
                store.update { it.copy(authed = true) }
                navController.navigate(Route.Home.path) {
                    popUpTo(0) { inclusive = true }
                }
            } else {
                // 失败累计；到阈值跳 401 锁定页，否则原地 toast 提示
                failCount += 1
                loading = false
                if (failCount >= LOGIN_FAIL_THRESHOLD) {
                    navController.navigate(Route.Lockout.path)
                } else {
                    Toast.makeText(context, "ログインに失敗しました", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    // DEMO：注册一路点完后回到 Login，1.5 秒自动 ログイン → Home
    // 实质 = iOS「アカウント作成完了→自動ログイン」体验等价（v1.0 demo 阶段）。
    // 仅在注册流真正预填了 user.email 且尚未登录时触发，不影响手动登录。
    androidx.compose.runtime.LaunchedEffect(state.user.email) {
        if (state.user.email.isNotBlank() && !state.authed) {
            // 注册流回来时让邮箱 tab 直接显示注册用的邮箱
            email = state.user.email
            delay(1500)
            store.update { it.copy(authed = true) }
            navController.navigate(Route.Home.path) {
                popUpTo(0) { inclusive = true }
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
