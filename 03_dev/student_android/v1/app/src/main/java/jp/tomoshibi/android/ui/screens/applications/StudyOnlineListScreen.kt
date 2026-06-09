package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.StudyOnlineRequestOut
import jp.tomoshibi.android.data.network.endpoints.StudyAPI
import jp.tomoshibi.android.ui.components.EmptyState
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.Pill
import jp.tomoshibi.android.ui.components.PillTone
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

// 在线学习申請一覧（L2 子页）— 对齐 iOS StudyOnlineRequestListView，接真后端。
//   PageHeader「オンライン学習申請一覧」level 2 + 竖排卡列表，逐条后端 StudyOnlineRequestOut
//   每条 SuzuCard：左 竖排「期間」标签 + 期间值 periodFrom〜periodTo + reason + 契约书文件名 / 右上 状态 Pill
//   三态：加载中 LoadingBox / 失败 FailedBox（敏感数据失败绝不退化成空列表）/ 空 EmptyState「提出済みの申請はありません」
@Composable
fun StudyOnlineListScreen(navController: NavHostController) {
    val scope = rememberCoroutineScope()
    // 三态：Loading / Failed(消息) / Empty / Success(后端 StudyOnlineRequestOut 列表)
    var ui by remember { mutableStateOf<LoadState<List<StudyOnlineRequestOut>>>(LoadState.Loading) }

    // 加载函数（重试也调它）。失败必须落 Failed，绝不退化成空列表。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                val items = StudyAPI.listMyOnlineRequests()
                if (items.isEmpty()) LoadState.Empty else LoadState.Success(items)
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(
            modifier =
                Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
        ) {
            PageHeader(
                title = "オンライン学習申請一覧",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                // 三态渲染
                when (val s = ui) {
                    LoadState.Loading -> {
                        LoadingBox()
                    }

                    is LoadState.Failed -> {
                        FailedBox(s.message, onRetry = { scope.launch { load() } })
                    }

                    // 空列表占位 —「提出済みの申請はありません」（iOS 同文案）
                    LoadState.Empty -> {
                        EmptyState(
                            title = "提出済みの申請はありません",
                            icon = SuzuIcons.Book,
                        )
                    }

                    is LoadState.Success -> {
                        s.value.forEach { item ->
                            StudyOnlineRequestCard(item)
                        }
                    }
                }
                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// 单条在线学习申請卡 — 左竖排（「期間」标签 + 期間値 + reason + 契約書文件名）+ 右上 状态 Pill
// item 为后端 DTO StudyOnlineRequestOut（不再经 MockData / data.model 本地模型）
@Composable
private fun StudyOnlineRequestCard(item: StudyOnlineRequestOut) {
    val t = SuzuT.current
    SuzuCard(padding = 14) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.Top,
        ) {
            Column(modifier = Modifier.weight(1f)) {
                // 「期間」小标签
                Text(
                    "期間",
                    color = t.inkSub,
                    style = TextStyle(fontSize = 12.sp),
                )
                Spacer(Modifier.height(4.dp))
                // 期間値 periodFrom〜periodTo（等宽字体，对齐 iOS monospaced）
                Text(
                    "${item.periodFrom} 〜 ${item.periodTo}",
                    color = t.ink,
                    style =
                        TextStyle(
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace,
                        ),
                )
                Spacer(Modifier.height(6.dp))
                // 理由 reason
                Text(
                    item.reason,
                    color = t.inkSub,
                    style = TextStyle(fontSize = 13.sp),
                )
                // 契約書文件名 —— 有上传才显示
                if (item.contractFileName != null) {
                    Spacer(Modifier.height(4.dp))
                    Text(
                        item.contractFileName,
                        color = t.inkMute,
                        style = TextStyle(fontSize = 12.sp),
                    )
                }
            }
            Spacer(Modifier.width(10.dp))
            // 状态 Pill —— iOS StudyOnlineRequestListView 専用映射（非 StayStatus 枚举）
            val (label, tone) = studyOnlineStatusPair(item.status)
            Pill(text = label, tone = tone)
        }
    }
}

// 在线学习申請状态 → 徽章文案 + 色调（1:1 抄 iOS studyOnlineStatusPair）
//   approved →「許可」Ok / rejected →「却下」Danger / revoked →「取消」Neutral / 其余 →「審査中」Warn
private fun studyOnlineStatusPair(status: String): Pair<String, PillTone> =
    when (status) {
        "approved" -> "許可" to PillTone.Ok
        "rejected" -> "却下" to PillTone.Danger
        "revoked" -> "取消" to PillTone.Neutral
        else -> "審査中" to PillTone.Warn
    }
