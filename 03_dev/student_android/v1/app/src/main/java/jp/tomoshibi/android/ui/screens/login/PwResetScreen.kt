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
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import androidx.compose.material3.Text
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// 找回密码说明页 — 对齐 iOS PwResetView（规格 §2.12）
//   认证页，不套 GlobalScaffold（跟 LoginScreen 一样是独立外壳）。
//   v1.0 登录页入口已隐藏（用户走不到这屏），但屏体保留备用。
//   内容：顶部返回箭头 + 标题「パスワードをリセット」→ 说明正文 → 淡青信息框 → 底部「戻る」按钮。
@Composable
fun PwResetScreen(navController: NavHostController) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme

    // 返回登录页（清掉本屏，回不来）
    val backToLogin: () -> Unit = {
        navController.navigate(Route.Login.path) {
            popUpTo(Route.PwReset.path) { inclusive = true }
        }
    }

    Column(
        modifier =
            Modifier
                .fillMaxSize()
                .background(t.pearl),
    ) {
        // ── 顶部头：左侧返回箭头（36×36）+ 居中标题 + 右侧 36 占位让标题真居中 ──
        // 对齐 iOS RegisterHeader（高 48，箭头按钮 36，标题 17 bold）
        Row(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .padding(horizontal = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier =
                    Modifier
                        .size(36.dp)
                        .clickable(onClick = backToLogin),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = SuzuIcons.ChevL,
                    contentDescription = null,
                    tint = t.ink,
                    modifier = Modifier.size(22.dp),
                )
            }
            Spacer(Modifier.weight(1f))
            Text(
                "パスワードをリセット",
                color = t.ink,
                style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.weight(1f))
            // 右侧 36 占位（与左箭头对称，使标题居中）
            Spacer(Modifier.size(36.dp))
        }

        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp),
            verticalArrangement = Arrangement.spacedBy(20.dp),
        ) {
            Spacer(Modifier.height(8.dp))

            // ── 说明正文（15sp，行距宽）── 逐字照抄规格 §2.12
            Text(
                "パスワードのリセットは App 内では行えません。寮監に直接お声がけください。寮監がシステム後台で手動でリセットします。",
                color = t.inkSub,
                style = TextStyle(fontSize = 15.sp, lineHeight = 24.sp),
            )

            // ── 信息框（极淡青底圆角，左 ℹ 图标 + 文）──
            Row(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(cs.primaryContainer)
                        .padding(14.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    imageVector = SuzuIcons.Info,
                    contentDescription = null,
                    tint = cs.primary,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(Modifier.width(10.dp))
                Text(
                    "リセット後、新しいパスワードが寮監から伝えられます",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
                )
            }
        }

        // ── 底部按钮：ログインに戻る（撑到底）──
        Spacer(Modifier.weight(1f))
        Column(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
                    .padding(bottom = 24.dp),
        ) {
            PrimaryButton(title = "戻る", onClick = backToLogin)
        }
    }
}
