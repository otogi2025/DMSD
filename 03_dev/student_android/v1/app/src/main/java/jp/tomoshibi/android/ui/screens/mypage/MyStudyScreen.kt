package jp.tomoshibi.android.ui.screens.mypage

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.theme.SuzuT

// 学習履歴（晩学習＝夜间学习的出席履歴）— 対齐 iOS MyStudyView（L2 子页）
//   入口 = 着陆页学習卡。按 MockData.DEFAULT_USER.isStudyTarget 切两种界面：
//   - false（当前假数据值）→ 居中「学習対象外です」空状态（本屏唯一走通分支）
//   - true → 月度统计 / 缺席届 / 出席打卡履历 / 说明盒 四块竖排（本波先不做，留 TODO）
@Composable
fun MyStudyScreen(navController: NavHostController) {
    val t = SuzuT.current
    val isStudyTarget = MockData.DEFAULT_USER.isStudyTarget

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "学習履歴", level = 2, onLeft = { navController.popBackStack() })

            if (isStudyTarget) {
                // TODO: 是晚自习对象的分支 — 四块竖排（月度统计卡 / 当月缺席届卡 /
                //   出席打卡履历卡 / 说明盒），见对齐规格 §10b 2263-2267 行。
                //   本波因假数据 isStudyTarget=false 不触发，留待下一波实装。
            } else {
                // 非晚自习对象：居中大 emoji + 标题 + 两行说明
                Column(
                    modifier = Modifier.fillMaxSize().padding(horizontal = 32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                ) {
                    Text("📚", style = TextStyle(fontSize = 44.sp))
                    Spacer(Modifier.height(12.dp))
                    Text(
                        "学習対象外です",
                        color = t.ink,
                        style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold),
                        textAlign = TextAlign.Center,
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        "あなたは現在、晩学習（夜間学習）の対象ではありません。\n学習担当の先生が対象に指定すると、ここに出席状況が表示されます。",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 13.sp, lineHeight = 19.sp),
                        textAlign = TextAlign.Center,
                    )
                }
            }
        }
    }
}
