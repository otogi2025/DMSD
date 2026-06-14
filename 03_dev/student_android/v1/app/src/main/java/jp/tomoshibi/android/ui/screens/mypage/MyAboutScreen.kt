package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.BuildConfig
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.theme.SuzuT

// Tomoshibi について（关于页，L2）— 对齐 iOS MyAboutView：
//   PageHeader「Tomoshibi について」level 2
//   居中字标块（Tomoshibi 40 heavy 深青绿 + 灯 火 14 大字距 + 版本号 11 等宽）
//   作者署名卡（SuzuCard 圆角 18）：系统说明 + 灯火由来引文 + 分隔线 + 作者署名
@Composable
fun MyAboutScreen(navController: NavHostController) {
    val t = SuzuT.current
    // 主色 teal #1F6B74：字标块大字 / 灯火二字
    val primary = MaterialTheme.colorScheme.primary

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "Tomoshibi について",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Spacer(Modifier.height(24.dp))

                // 字标块 ── 居中三行：英文标 / 灯火 / 版本号
                Text(
                    "Tomoshibi",
                    color = primary,
                    style = TextStyle(fontSize = 40.sp, fontWeight = FontWeight.Black),
                    textAlign = TextAlign.Center,
                )
                Spacer(Modifier.height(6.dp))
                Text(
                    "灯 火",
                    color = primary,
                    style =
                        TextStyle(
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                            // 大字距：两字拉开间隔，对齐 iOS 字标块
                            letterSpacing = 8.sp,
                        ),
                    textAlign = TextAlign.Center,
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    // 版本号：演示/生产统一取构建配置的 versionName
                    BuildConfig.VERSION_NAME,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                    textAlign = TextAlign.Center,
                )

                Spacer(Modifier.height(28.dp))

                // AC 署名卡（圆角 18）
                SuzuCard(padding = 18, radius = 18) {
                    Text(
                        "Tomoshibi は、日本の寮での点呼と生活管理を一体化したシステムです。",
                        color = t.ink,
                        style = TextStyle(fontSize = 14.sp, lineHeight = 22.sp),
                    )
                    Spacer(Modifier.height(14.dp))
                    Text(
                        "「日本で留学する私にとって、寮は異国の第二の家。このシステムが守るのは『灯火』—— 毎晩学生が無事に帰宅し、部屋に灯りが灯ること。だから日本語名を Tomoshibi（灯火）にしました。」",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 13.sp, lineHeight = 22.sp),
                    )
                    Spacer(Modifier.height(16.dp))
                    // 分隔线（hair 8% 淡描边）
                    Box(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .height(1.dp)
                                .background(t.hair),
                    )
                    Spacer(Modifier.height(16.dp))
                    Text(
                        "個人開発プロジェクト",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "— リュウ イヒ",
                        color = t.inkMute,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }

                Spacer(Modifier.height(24.dp))
            }
        }
    }
}
