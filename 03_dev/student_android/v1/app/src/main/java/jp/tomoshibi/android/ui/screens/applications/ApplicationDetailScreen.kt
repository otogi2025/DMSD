package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Divider
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.Application
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.ApplicationsAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.FailedBox
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.LoadState
import jp.tomoshibi.android.ui.components.LoadingBox
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate

// 承認チェーン 1 步 — 役職 / 状态 / 时间戳
private data class ChainStep(
    val role: String,
    val state: String /* approved/pending/idle */,
    val ts: String?,
)

@Composable
fun ApplicationDetailScreen(
    navController: NavHostController,
    id: String,
) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    // 登录学生信息（学号 / 氏名 / 区分 等）仍走本地 store —— 那是「申請者本人」卡 + 承認链推断要用的，不是本屏要接的申請数据。
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val scope = rememberCoroutineScope()

    // 三态：Loading / Failed(消息) / Success(单条 Application)。详情屏是单条，不需要 Empty 态。
    var ui by remember { mutableStateOf<LoadState<Application>>(LoadState.Loading) }

    // 加载函数（重试也调它）。调 ApplicationsAPI.detail(id) 拿 ApplicationOut，再 .toUiApplication() 转成界面用的本地 Application。
    // 后端 404（找不到此申請）等异常一律走 Failed，绝不退化成空/假数据。
    suspend fun load() {
        ui = LoadState.Loading
        ui =
            try {
                LoadState.Success(ApplicationsAPI.detail(id).toUiApplication())
            } catch (e: ApiError) {
                LoadState.Failed(e.display)
            } catch (e: Exception) {
                LoadState.Failed("読み込みに失敗しました")
            }
    }
    LaunchedEffect(Unit) { load() }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
            // 顶部 ← + 标题
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier.size(36.dp).clip(CircleShape).clickable { navController.popBackStack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Text("←", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
                }
                Spacer(Modifier.width(8.dp))
                Text("申請詳細", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }

            when (val s = ui) {
                LoadState.Loading -> {
                    LoadingBox()
                }

                is LoadState.Failed -> {
                    FailedBox(s.message, onRetry = { scope.launch { load() } })
                }

                // 详情屏单条无 Empty 态，Empty 分支理论上不会发生，兜底也按失败处理避免崩溃。
                LoadState.Empty -> {
                    FailedBox("読み込みに失敗しました", onRetry = { scope.launch { load() } })
                }

                is LoadState.Success -> {
                    val app = s.value
                    Column(
                        modifier =
                            Modifier
                                .weight(1f)
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 20.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                    ) {
                        // ── 顶部状态卡 ──
                        Row(
                            modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(14.dp))
                                    .background(tokens.paper)
                                    .padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Box(
                                modifier =
                                    Modifier
                                        .clip(RoundedCornerShape(6.dp))
                                        .background(tokens.pill)
                                        .padding(horizontal = 8.dp, vertical = 2.dp),
                            ) {
                                Text(
                                    app.kind,
                                    color = tokens.ink,
                                    style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold),
                                )
                            }
                            Spacer(Modifier.width(8.dp))
                            ApplicationStatusPill(app.status)
                            Spacer(Modifier.weight(1f))
                            Text(
                                "#${app.id}",
                                color = tokens.inkMute,
                                style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                            )
                        }

                        // ── 申請者本人 ──
                        Section("申請者本人")
                        Column(
                            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
                        ) {
                            KvRow("学号", state.user.studentNo, mono = true)
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("氏名", state.user.name)
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("学年・組", state.user.gradeClass)
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("寮・部屋", "${state.user.dorm} ${state.user.room}")
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("区分", state.user.category)
                        }

                        // ── 申請内容 ──
                        Section("申請内容")
                        Column(
                            modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(tokens.paper),
                        ) {
                            KvRow("種類", app.kind)
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("行先", app.dest)
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("期間", if (app.from == app.to) app.from else "${app.from} 〜 ${app.to}")
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("理由", app.reason)
                            Divider(color = tokens.hair, thickness = 0.5.dp)
                            KvRow("提出日", app.createdAt)
                        }

                        // ── 承認チェーン ──
                        Section("承認の流れ")
                        val chain = buildChain(state.user.category, app)
                        Column(
                            modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(14.dp))
                                    .background(tokens.paper)
                                    .padding(vertical = 8.dp),
                        ) {
                            chain.forEachIndexed { idx, step ->
                                ChainRow(step, isLast = idx == chain.lastIndex)
                            }
                        }

                        // ── 撤回ボタン ──（仅 PENDING 且出寮日 24 時間前可撤回）
                        val withdrawable = app.status == ApplicationStatus.PENDING && canWithdraw(app.from)
                        if (withdrawable) {
                            Box(
                                modifier =
                                    Modifier
                                        .fillMaxWidth()
                                        .height(48.dp)
                                        .clip(RoundedCornerShape(12.dp))
                                        .border(1.5.dp, tokens.danger.copy(alpha = 0.4f), RoundedCornerShape(12.dp))
                                        .clickable {
                                            // TODO 接后端：撤回 endpoint（后端目前无撤回接口，先仅返回上一屏）
                                            navController.popBackStack()
                                        },
                                contentAlignment = Alignment.Center,
                            ) {
                                Text(
                                    "申請を撤回する",
                                    color = tokens.danger,
                                    style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
                                )
                            }
                            Text(
                                "※ 出寮日 24 時間前まで撤回可能です",
                                color = tokens.inkMute,
                                style = TextStyle(fontSize = 11.sp),
                            )
                        }
                        Spacer(Modifier.height(40.dp))
                    } // 申請内容主体 Column 结束
                } // is LoadState.Success 分支结束
            } // when (ui) 三态结束
        }
    }
}

// 一般寮生 = 3 段：担任 → 寮務課長 → 管理係
// 留学生 = 5 段：担任 → 寮務課長 → 国際交流部長 → 寮務部長 → 管理係
private fun buildChain(
    category: String,
    app: Application,
): List<ChainStep> {
    val approved = app.status == ApplicationStatus.APPROVED
    val pending = app.status == ApplicationStatus.PENDING
    val rejected = app.status == ApplicationStatus.REJECTED || app.status == ApplicationStatus.RETURNED

    val isOverseas = category.contains("留学生")
    val roles =
        if (isOverseas) {
            listOf("担任", "寮務課長", "国際交流部長", "寮務部長", "管理係")
        } else {
            listOf("担任", "寮務課長", "管理係")
        }

    // 简化：approved 全部绿 / rejected 第 1 个红 + 后续灰 / pending 第 1 个绿 + 第 2 个黄 + 后续灰
    return roles.mapIndexed { i, role ->
        when {
            approved -> ChainStep(role, "approved", "${app.createdAt} 16:30")
            rejected && i == 0 -> ChainStep(role, "rejected", "${app.createdAt} 09:15")
            rejected -> ChainStep(role, "idle", null)
            pending && i == 0 -> ChainStep(role, "approved", "${app.createdAt} 10:20")
            pending && i == 1 -> ChainStep(role, "pending", null)
            else -> ChainStep(role, "idle", null)
        }
    }
}

@Composable
private fun ChainRow(
    step: ChainStep,
    isLast: Boolean,
) {
    val t = SuzuT.current
    val (dotColor, label) =
        when (step.state) {
            "approved" -> t.ok to "承認"
            "pending" -> t.warn to "審査中"
            "rejected" -> t.danger to "差戻"
            else -> t.inkFaint to "—"
        }
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 圆点 + 连接线
        Column(
            modifier = Modifier.width(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Box(
                modifier = Modifier.size(14.dp).clip(CircleShape).background(dotColor),
                contentAlignment = Alignment.Center,
            ) {
                if (step.state == "approved") {
                    Text("✓", color = Color.White, style = TextStyle(fontSize = 9.sp, fontWeight = FontWeight.Bold))
                } else if (step.state == "rejected") {
                    Text("×", color = Color.White, style = TextStyle(fontSize = 9.sp, fontWeight = FontWeight.Bold))
                }
            }
            if (!isLast) {
                Box(modifier = Modifier.height(20.dp).width(1.5.dp).background(t.hair))
            }
        }
        Spacer(Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(step.role, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
            if (step.ts != null) {
                Text(
                    step.ts,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, fontFamily = FontFamily.Monospace),
                )
            }
        }
        Box(
            modifier =
                Modifier
                    .clip(RoundedCornerShape(6.dp))
                    .background(dotColor.copy(alpha = 0.12f))
                    .padding(horizontal = 8.dp, vertical = 2.dp),
        ) {
            Text(label, color = dotColor, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
        }
    }
}

private fun canWithdraw(fromDate: String): Boolean =
    try {
        val d = LocalDate.parse(fromDate)
        d.isAfter(LocalDate.now().plusDays(1))
    } catch (e: Exception) {
        true
    }

@Composable
private fun Section(label: String) {
    val t = SuzuT.current
    Text(
        label,
        color = t.inkSub,
        style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.5.sp),
    )
}

@Composable
private fun KvRow(
    label: String,
    value: String,
    mono: Boolean = false,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Text(label, color = t.inkSub, modifier = Modifier.width(80.dp), style = TextStyle(fontSize = 12.sp))
        Text(
            value,
            color = t.ink,
            style =
                TextStyle(
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = if (mono) FontFamily.Monospace else null,
                    lineHeight = 20.sp,
                ),
        )
    }
}
