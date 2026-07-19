package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.GaihakuCreateBody
import jp.tomoshibi.android.data.network.KikokuCreateBody
import jp.tomoshibi.android.data.network.KisheiCreateBody
import jp.tomoshibi.android.data.network.MealSkipBody
import jp.tomoshibi.android.data.network.StayLocationBody
import jp.tomoshibi.android.data.network.endpoints.ApplicationsAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.ui.components.ApplyDoneBody
import jp.tomoshibi.android.ui.components.ChipGroup
import jp.tomoshibi.android.ui.components.DateField
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TArea
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.components.TToggle
import jp.tomoshibi.android.ui.components.TimeField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

// ─────────────────────────────────────────────────────────────────────
// StayForm —— 出寮届（外泊 / 帰省 / 帰国 三合一）
// 对齐 iOS ApplyStubs.swift StayForm；提交走 ApplicationsAPI.create（Kishei/Gaihaku/Kikoku）。
// kind 取「外泊」/「帰省」/「帰国」，按 kind 累积显隐区块。
// v1.0：单按钮「提出する」直接提交（已删「下書き保存」与确认页），成功进完成页。
// ─────────────────────────────────────────────────────────────────────

// 宿泊先一行（§5）—— 用稳定 id 当列表 key，删中间行不串内容
private data class StayPlace(
    val id: Long,
    var address: String,
)

private const val TAXI_METHOD = "タクシー"
private val MEAL_ORDER = listOf("朝食", "昼食", "夕食")
private val HMS_SUFFIX = ":00" // 后端 time 要 HH:mm:ss；TimeField 只给 HH:mm

// 把「HH:mm」补成「HH:mm:ss」；已是 8 字符则原样返回
private fun toHms(hm: String): String =
    when {
        hm.length == 5 -> hm + HMS_SUFFIX
        else -> hm
    }

private fun nilIfBlank(s: String): String? = s.trim().takeIf { it.isNotEmpty() }

// 日期 + 时刻 → 「yyyy-MM-ddTHH:mm:ss+09:00」（对齐 iOS formatISOWithTokyo）
private fun formatIsoWithTokyo(
    dateYmd: String,
    timeHm: String,
): String = "${dateYmd}T${toHms(timeHm)}+09:00"

// 食事不要期間展开成 meals_skip 条目列表（对齐 iOS expandMealsSkip）
private fun expandMealsSkip(
    startDate: String,
    startMeal: String,
    endDate: String,
    endMeal: String,
): List<MealSkipBody> {
    if (startDate.isBlank() || endDate.isBlank()) return emptyList()
    val start =
        try {
            LocalDate.parse(startDate)
        } catch (_: Exception) {
            return emptyList()
        }
    val end =
        try {
            LocalDate.parse(endDate)
        } catch (_: Exception) {
            return emptyList()
        }
    if (end.isBefore(start)) return emptyList()
    val result = mutableListOf<MealSkipBody>()
    var current = start
    while (!current.isAfter(end)) {
        val isFirst = current == start
        val isLast = current == end
        val lo = if (isFirst) MEAL_ORDER.indexOf(startMeal).coerceAtLeast(0) else 0
        val hi = if (isLast) MEAL_ORDER.indexOf(endMeal).let { if (it < 0) 2 else it } else 2
        if (lo <= hi) {
            val dateStr = current.format(DateTimeFormatter.ISO_LOCAL_DATE)
            for (i in lo..hi) {
                result.add(MealSkipBody(date = dateStr, meal = MEAL_ORDER[i]))
            }
        }
        current = current.plus(1, ChronoUnit.DAYS)
    }
    return result
}

// 出寮方法选项（帰省 / 外泊・帰国 略有差异 —— 这里出寮段用同一套，规格 §3 列了 10 项）
private val LEAVE_METHODS =
    listOf(
        "西口1便",
        "西口2便",
        "金川1便",
        "金川2便",
        "寮生特別運行",
        "JR",
        "自家用車",
        "タクシー",
        "教員",
        "その他",
    )

// 帰寮方法选项（§4，8 项，登校便措辞跟出寮段不同）
private val RETURN_METHODS =
    listOf(
        "西口登校便",
        "金川登校便",
        "寮生特別運行",
        "JR",
        "自家用車",
        "タクシー",
        "教員",
        "その他",
    )

// 餐次（§6 食事不要期間用）
private val MEALS = listOf("朝食", "昼食", "夕食")

@Composable
fun StayForm(
    navController: NavHostController,
    kind: String,
) {
    val t = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val user = state.user

    // kind 派生显隐标记（§2.2）
    val isHoliday = kind == "帰省" // 帰省
    val isReturnCountry = kind == "帰国" // 帰国
    val isStay = kind == "外泊" // 外泊
    val needPlaces = isStay || isReturnCountry // §5 同行者/行先/宿泊先（外泊・帰国）
    val needDestCity = isStay // §5「行先（都市名）」仅外泊（帰国隐藏）
    val needMeal = isStay || isReturnCountry // §6 食事申告（外泊・帰国）
    val needFlight = isReturnCountry // §7 飛行機（仅帰国）
    val isOverseas = user.category == "留学生" // 留学生 → 食事不要期間申告；日本人 → 提示走食事入力表

    // 类型名（PageHeader 标题 + Header 卡 + 完成页都用）
    val kindName = kind // 「外泊」/「帰省」/「帰国」本身就是日语显示名

    // edit（填写）→ done（完成）；无确认页（对齐 iOS v1.0）
    var stage by remember { mutableStateOf("edit") }
    var submitting by remember { mutableStateOf(false) }
    val tomorrow = remember { JstDate.today().plusDays(1).toString() }

    // ── §2 連絡先・届の区分 ──
    var contactPhone by remember { mutableStateOf("") }
    var isLongVacation by remember { mutableStateOf<Boolean?>(null) } // 仅帰省：通常時用 / 長期休暇用

    // ── §3 出寮 ──
    var leaveDate by remember { mutableStateOf("") }
    var leaveTime by remember { mutableStateOf("") }
    var leaveMethod by remember { mutableStateOf<String?>(null) }
    var taxiTime by remember { mutableStateOf("") } // 出寮方法选「タクシー」时露出的希望時刻

    // ── §4 帰寮 ──
    var returnDate by remember { mutableStateOf("") }
    var returnTime by remember { mutableStateOf("") }
    var returnMethod by remember { mutableStateOf<String?>(null) }

    // ── §5 同行者・行先・宿泊先 ──
    var companion by remember { mutableStateOf("") }
    var destCity by remember { mutableStateOf("") }
    val stayPlaces = remember { mutableStateListOf(StayPlace(System.nanoTime(), "")) }

    // ── §6 食事不要期間（留学生）──
    var mealSkipOn by remember { mutableStateOf(false) }
    var mealStartDate by remember { mutableStateOf("") }
    var mealStartMeal by remember { mutableStateOf<String?>(null) }
    var mealEndDate by remember { mutableStateOf("") }
    var mealEndMeal by remember { mutableStateOf<String?>(null) }
    var mealNote by remember { mutableStateOf("") }

    // ── §7 飛行機（帰国）──
    var flightDepAir by remember { mutableStateOf("") }
    var flightDepTime by remember { mutableStateOf("") }
    var flightArrAir by remember { mutableStateOf("") }
    var flightArrTime by remember { mutableStateOf("") }

    // ── §8 理由 ──
    var reason by remember { mutableStateOf("") }

    // 区块编号（§8 动态：帰国=8 / 外泊=7 / 帰省=5）—— 跟 iOS 一致
    val reasonSectionNo =
        when {
            isReturnCountry -> 8
            isStay -> 7
            else -> 5
        }

    // 提交可否（规格 §2.3）：理由非空 + 出入寮方法已选 + 帰寮晚于出寮 + 外泊/帰国宿泊先≥1 非空 + 帰国机场都非空
    val canSubmit by remember {
        derivedStateOf {
            // 理由
            if (reason.trim().isEmpty()) return@derivedStateOf false
            // 出寮 / 帰寮 日时 + 方法必填
            if (leaveDate.isEmpty() || leaveTime.isEmpty()) return@derivedStateOf false
            if (returnDate.isEmpty() || returnTime.isEmpty()) return@derivedStateOf false
            if (leaveMethod == null || returnMethod == null) return@derivedStateOf false
            // 帰寮（日+時刻）必须晚于出寮（防同日时刻倒挂）
            val leaveAt = "$leaveDate $leaveTime"
            val returnAt = "$returnDate $returnTime"
            if (returnAt <= leaveAt) return@derivedStateOf false
            // 外泊 / 帰国：宿泊先至少 1 行 trim 后非空
            if (needPlaces && stayPlaces.none { it.address.trim().isNotEmpty() }) return@derivedStateOf false
            // 帰国：出発空港 + 到着空港都非空
            if (needFlight && (flightDepAir.trim().isEmpty() || flightArrAir.trim().isEmpty())) {
                return@derivedStateOf false
            }
            true
        }
    }

    // 真提交：按 kind dispatch 到 Kishei/Gaihaku/Kikoku → ApplicationsAPI.create
    fun submitStay() {
        if (submitting) return
        scope.launch {
            submitting = true
            val tokenAtStart = store.snapshot().authToken
            try {
                val leaveTimeStr = toHms(leaveTime)
                val returnTimeStr = toHms(returnTime)
                val contactPhoneValue = nilIfBlank(contactPhone)
                val mealNoteValue = if (isOverseas) nilIfBlank(mealNote) else null
                val companionValue = nilIfBlank(companion)
                val destCitiesValue = nilIfBlank(destCity)
                val taxiTimeValue =
                    if (leaveMethod == TAXI_METHOD) toHms(taxiTime).takeIf { taxiTime.isNotBlank() } else null
                val stayLocations =
                    stayPlaces
                        .map { it.address.trim() }
                        .filter { it.isNotEmpty() }
                        .map { StayLocationBody(kind = "その他", name = it, address = it, phone = null) }
                val mealsSkip =
                    if (needMeal && isOverseas && mealSkipOn) {
                        val expanded =
                            expandMealsSkip(
                                mealStartDate,
                                mealStartMeal ?: MEAL_ORDER.first(),
                                mealEndDate,
                                mealEndMeal ?: MEAL_ORDER.last(),
                            )
                        if (expanded.isEmpty()) {
                            store.showToast("食事不要期間が指定されていません。開始と終了の食事の順序をご確認ください")
                            return@launch
                        }
                        expanded
                    } else {
                        emptyList()
                    }

                when (kind) {
                    "帰省" -> {
                        ApplicationsAPI.create(
                            KisheiCreateBody(
                                reason = reason,
                                contactPhone = contactPhoneValue,
                                mealNote = mealNoteValue,
                                isLongVacation = isLongVacation ?: false,
                                leaveDate = leaveDate,
                                leaveMethod = leaveMethod!!,
                                leaveTime = leaveTimeStr,
                                returnDate = returnDate,
                                returnMethod = returnMethod!!,
                                returnTime = returnTimeStr,
                                taxiReservationTime = taxiTimeValue,
                            ),
                        )
                    }

                    "外泊" -> {
                        ApplicationsAPI.create(
                            GaihakuCreateBody(
                                reason = reason,
                                contactPhone = contactPhoneValue,
                                mealNote = mealNoteValue,
                                companion = companionValue,
                                destCities = destCitiesValue,
                                leaveDate = leaveDate,
                                leaveMethod = leaveMethod!!,
                                leaveTime = leaveTimeStr,
                                returnDate = returnDate,
                                returnMethod = returnMethod!!,
                                returnTime = returnTimeStr,
                                stayLocations = stayLocations,
                                mealsSkip = mealsSkip,
                                taxiReservationTime = taxiTimeValue,
                            ),
                        )
                    }

                    "帰国" -> {
                        ApplicationsAPI.create(
                            KikokuCreateBody(
                                reason = reason,
                                contactPhone = contactPhoneValue,
                                mealNote = mealNoteValue,
                                companion = companionValue,
                                destCities = destCitiesValue,
                                leaveDate = leaveDate,
                                leaveMethod = leaveMethod!!,
                                leaveTime = leaveTimeStr,
                                returnDate = returnDate,
                                returnMethod = returnMethod!!,
                                returnTime = returnTimeStr,
                                stayLocations = stayLocations,
                                mealsSkip = mealsSkip,
                                flightDepAir = flightDepAir.trim(),
                                flightDepAt = formatIsoWithTokyo(leaveDate, flightDepTime.ifBlank { leaveTime }),
                                flightArrAir = flightArrAir.trim(),
                                flightArrAt = formatIsoWithTokyo(returnDate, flightArrTime.ifBlank { returnTime }),
                                taxiReservationTime = taxiTimeValue,
                            ),
                        )
                    }

                    else -> {
                        store.showToast("この種類の届には対応していません")
                        return@launch
                    }
                }
                if (store.snapshot().authToken != tokenAtStart) return@launch
                store.showToast("${kindName}申請を提出しました")
                stage = "done"
            } catch (e: ApiError) {
                if (store.handleIfUnauthorized(e, tokenAtStart)) return@launch
                store.showToast(e.display)
            } catch (e: Exception) {
                store.showToast("申請の提出に失敗しました")
            } finally {
                submitting = false
            }
        }
    }

    GlobalScaffold(activeTab = "apply", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(
                title = "${kindName}届",
                level = 2,
                onLeft = { navController.popBackStack() },
            )

            when (stage) {
                "done" -> {
                    ApplyDoneBody(kindName = kindName) { navController.popBackStack() }
                }

                else -> {
                    Column(
                        modifier =
                            Modifier
                                .fillMaxWidth()
                                .verticalScroll(rememberScrollState())
                                .padding(horizontal = 16.dp),
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                    ) {
                        Spacer(Modifier.height(2.dp))
                        EditBody(
                            t = t,
                            kind = kind,
                            kindName = kindName,
                            isHoliday = isHoliday,
                            needPlaces = needPlaces,
                            needDestCity = needDestCity,
                            needMeal = needMeal,
                            needFlight = needFlight,
                            isOverseas = isOverseas,
                            reasonSectionNo = reasonSectionNo,
                            tomorrow = tomorrow,
                            userStudentNo = user.studentNo,
                            userName = user.name,
                            userGradeClass = user.gradeClass,
                            userDorm = user.dorm,
                            userRoom = user.room,
                            userCategory = user.category,
                            userPhone = user.phone,
                            contactPhone = contactPhone,
                            onContactPhone = { contactPhone = it },
                            isLongVacation = isLongVacation,
                            onLongVacation = { isLongVacation = it },
                            leaveDate = leaveDate,
                            onLeaveDate = { leaveDate = it },
                            leaveTime = leaveTime,
                            onLeaveTime = { leaveTime = it },
                            leaveMethod = leaveMethod,
                            onLeaveMethod = { leaveMethod = it },
                            taxiTime = taxiTime,
                            onTaxiTime = { taxiTime = it },
                            returnDate = returnDate,
                            onReturnDate = { returnDate = it },
                            returnTime = returnTime,
                            onReturnTime = { returnTime = it },
                            returnMethod = returnMethod,
                            onReturnMethod = { returnMethod = it },
                            companion = companion,
                            onCompanion = { companion = it },
                            destCity = destCity,
                            onDestCity = { destCity = it },
                            stayPlaces = stayPlaces,
                            mealSkipOn = mealSkipOn,
                            onMealSkipOn = { mealSkipOn = it },
                            mealStartDate = mealStartDate,
                            onMealStartDate = { mealStartDate = it },
                            mealStartMeal = mealStartMeal,
                            onMealStartMeal = { mealStartMeal = it },
                            mealEndDate = mealEndDate,
                            onMealEndDate = { mealEndDate = it },
                            mealEndMeal = mealEndMeal,
                            onMealEndMeal = { mealEndMeal = it },
                            mealNote = mealNote,
                            onMealNote = { mealNote = it },
                            flightDepAir = flightDepAir,
                            onFlightDepAir = { flightDepAir = it },
                            flightDepTime = flightDepTime,
                            onFlightDepTime = { flightDepTime = it },
                            flightArrAir = flightArrAir,
                            onFlightArrAir = { flightArrAir = it },
                            flightArrTime = flightArrTime,
                            onFlightArrTime = { flightArrTime = it },
                            reason = reason,
                            onReason = { reason = it },
                            onBus = {
                                navController.navigate(jp.tomoshibi.android.nav.Route.BusList.path)
                            },
                            canSubmit = canSubmit && !submitting,
                            submitting = submitting,
                            onSubmit = { submitStay() },
                        )
                        Spacer(Modifier.height(40.dp))
                    }
                }
            }
        }
    }
}

// ════════════════════════════════════════════════════════════════════
// 编辑态正文（§1～§8 + 底部双按钮 + 注记）
// ════════════════════════════════════════════════════════════════════
@Composable
private fun EditBody(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    kind: String,
    kindName: String,
    isHoliday: Boolean,
    needPlaces: Boolean,
    needDestCity: Boolean,
    needMeal: Boolean,
    needFlight: Boolean,
    isOverseas: Boolean,
    reasonSectionNo: Int,
    tomorrow: String,
    userStudentNo: String,
    userName: String,
    userGradeClass: String,
    userDorm: String,
    userRoom: String,
    userCategory: String,
    userPhone: String,
    contactPhone: String,
    onContactPhone: (String) -> Unit,
    isLongVacation: Boolean?,
    onLongVacation: (Boolean) -> Unit,
    leaveDate: String,
    onLeaveDate: (String) -> Unit,
    leaveTime: String,
    onLeaveTime: (String) -> Unit,
    leaveMethod: String?,
    onLeaveMethod: (String) -> Unit,
    taxiTime: String,
    onTaxiTime: (String) -> Unit,
    returnDate: String,
    onReturnDate: (String) -> Unit,
    returnTime: String,
    onReturnTime: (String) -> Unit,
    returnMethod: String?,
    onReturnMethod: (String) -> Unit,
    companion: String,
    onCompanion: (String) -> Unit,
    destCity: String,
    onDestCity: (String) -> Unit,
    stayPlaces: androidx.compose.runtime.snapshots.SnapshotStateList<StayPlace>,
    mealSkipOn: Boolean,
    onMealSkipOn: (Boolean) -> Unit,
    mealStartDate: String,
    onMealStartDate: (String) -> Unit,
    mealStartMeal: String?,
    onMealStartMeal: (String) -> Unit,
    mealEndDate: String,
    onMealEndDate: (String) -> Unit,
    mealEndMeal: String?,
    onMealEndMeal: (String) -> Unit,
    mealNote: String,
    onMealNote: (String) -> Unit,
    flightDepAir: String,
    onFlightDepAir: (String) -> Unit,
    flightDepTime: String,
    onFlightDepTime: (String) -> Unit,
    flightArrAir: String,
    onFlightArrAir: (String) -> Unit,
    flightArrTime: String,
    onFlightArrTime: (String) -> Unit,
    reason: String,
    onReason: (String) -> Unit,
    onBus: () -> Unit,
    canSubmit: Boolean,
    submitting: Boolean,
    onSubmit: () -> Unit,
) {
    // ── 1. kind 提示横幅（黄色背景，圆角 12）—— 按 kind 三选一（§2.1-1）──
    val banner =
        when {
            isHoliday -> "⏰ 帰省申請の締切は毎週水曜日18:00です"
            needFlight -> "✈️ 帰国申請は航空券確定後に提出してください"
            else -> "📝 外泊申請は出発の3日前までに提出してください"
        }
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.warnBg)
                .padding(14.dp),
    ) {
        Text(banner, color = t.warnDeep, style = TextStyle(fontSize = 12.sp, lineHeight = 17.sp))
    }

    // ── 2. Header 卡（淡蓝底+蓝边）：图标方块 +「<类型名>許可願」+ 副标题（§2.1-2）──
    val kindIcon =
        when {
            isHoliday -> SuzuIcons.House

            // 帰省 = house.lodge → House
            needFlight -> SuzuIcons.Plane

            // 帰国 = airplane → Plane
            else -> SuzuIcons.House // 外泊 = house → House
        }
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(t.pill)
                .border(1.dp, MaterialPrimary(), RoundedCornerShape(16.dp))
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier =
                Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(MaterialPrimary()),
            contentAlignment = Alignment.Center,
        ) {
            androidx.compose.material3.Icon(
                kindIcon,
                contentDescription = null,
                tint = Color.White,
                modifier = Modifier.size(22.dp),
            )
        }
        Spacer(Modifier.width(12.dp))
        Column {
            Text("${kindName}許可願", color = t.ink, style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
            Spacer(Modifier.height(2.dp))
            Text("朝日塾中等教育学校 国際交流部寮", color = t.inkSub, style = TextStyle(fontSize = 12.sp))
        }
    }

    // ── §1 申請者本人（只读 InfoRow 列表，6 行）（§2.1-3）──
    SectionLabel(t, "1", "申請者本人")
    SuzuCard(padding = 0) {
        InfoRow(t, "アカウント番号", userStudentNo, mono = true, first = true)
        InfoRow(t, "氏名", userName)
        InfoRow(t, "学年・組", userGradeClass)
        InfoRow(t, "寮・部屋", "$userDorm $userRoom")
        InfoRow(t, "区分", userCategory)
        InfoRow(t, "携帯電話", userPhone, mono = true)
    }
    Text(
        "※ ログイン中のアカウントで提出されます。他の生徒の代理提出はできません。",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
    )

    // ── §2 連絡先・届の区分（§2.1-4）──
    SectionLabel(t, "2", "連絡先・届の区分")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Field(label = "本人連絡先（携帯電話）") {
                TField(
                    value = contactPhone,
                    onValueChange = onContactPhone,
                    placeholder = "090-0000-0000",
                    keyboard = KeyboardType.Phone,
                )
            }
            // 仅帰省：帰省届の区分（通常時用 / 長期休暇用 → 绑布尔 isLongVacation）
            if (isHoliday) {
                Field(label = "帰省届の区分") {
                    ChipGroup(
                        options = listOf("通常時用", "長期休暇用"),
                        selected =
                            when (isLongVacation) {
                                true -> "長期休暇用"
                                false -> "通常時用"
                                null -> null
                            },
                        onSelect = { onLongVacation(it == "長期休暇用") },
                    )
                }
            }
        }
    }

    // ── §3 出寮（§2.1-5）──
    SectionLabel(t, "3", "出寮")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                DateField(
                    label = "出寮日",
                    value = leaveDate,
                    modifier = Modifier.weight(1f),
                    minDate = tomorrow,
                    onPick = onLeaveDate,
                )
                TimeField(label = "出寮時刻", value = leaveTime, modifier = Modifier.weight(1f), onPick = onLeaveTime)
            }
            Text(
                "※ 出寮日は明日以降のみ選択できます",
                color = t.inkMute,
                style = TextStyle(fontSize = 11.sp),
            )
            // 帰省时标签「帰省方法」/ 其余「出寮方法」
            Field(label = if (isHoliday) "帰省方法" else "出寮方法") {
                ChipGroup(options = LEAVE_METHODS, selected = leaveMethod, onSelect = onLeaveMethod)
            }
            BusTimetableLink(t, onBus)
            // 连动：出寮方法选「タクシー」→ 当场露出「タクシー希望時刻」
            if (leaveMethod == "タクシー") {
                TimeField(label = "タクシー希望時刻", value = taxiTime, onPick = onTaxiTime)
            }
        }
    }

    // ── §4 帰寮（§2.1-6）──
    SectionLabel(t, "4", "帰寮")
    SuzuCard {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                DateField(
                    label = "帰寮日",
                    value = returnDate,
                    modifier = Modifier.weight(1f),
                    minDate = leaveDate.ifEmpty { tomorrow },
                    onPick = onReturnDate,
                )
                TimeField(label = "帰寮時刻", value = returnTime, modifier = Modifier.weight(1f), onPick = onReturnTime)
            }
            Field(label = "帰寮方法") {
                ChipGroup(options = RETURN_METHODS, selected = returnMethod, onSelect = onReturnMethod)
            }
            BusTimetableLink(t, onBus)
        }
    }

    // ── §5 同行者・行先・外泊地点（仅 外泊 / 帰国）（§2.1-7）──
    if (needPlaces) {
        SectionLabel(t, "5", "同行者・行先・宿泊先")
        SuzuCard {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Field(label = "同行者") {
                    TField(value = companion, onValueChange = onCompanion, placeholder = "同行者がいる場合は入力")
                }
                // 仅 外泊（帰国隐藏）：行先（都市名）
                if (needDestCity) {
                    Field(label = "行先（都市名）") {
                        TField(value = destCity, onValueChange = onDestCity, placeholder = "例：東京・大阪・ソウル")
                    }
                }
                // 宿泊先：可增删的住所输入行列表（用稳定 id 当 key，删中间行不串内容）
                Field(label = "宿泊先") {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        stayPlaces.forEachIndexed { index, place ->
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                TField(
                                    value = place.address,
                                    onValueChange = { stayPlaces[index] = place.copy(address = it) },
                                    modifier = Modifier.weight(1f),
                                    placeholder = "宿泊先住所",
                                )
                                // 行数 > 1 时右侧红色减号删除按钮
                                if (stayPlaces.size > 1) {
                                    Spacer(Modifier.width(8.dp))
                                    Box(
                                        modifier =
                                            Modifier
                                                .size(36.dp)
                                                .clip(RoundedCornerShape(10.dp))
                                                .background(t.dangerBg)
                                                .clickable { stayPlaces.removeAt(index) },
                                        contentAlignment = Alignment.Center,
                                    ) {
                                        Text("−", color = t.danger, style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold))
                                    }
                                }
                            }
                        }
                    }
                }
                // 底部「滞在先を追加」蓝色加号按钮
                Row(
                    modifier =
                        Modifier
                            .clip(RoundedCornerShape(10.dp))
                            .clickable { stayPlaces.add(StayPlace(System.nanoTime(), "")) }
                            .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    androidx.compose.material3.Icon(
                        SuzuIcons.Plus,
                        contentDescription = null,
                        tint = MaterialPrimary(),
                        modifier = Modifier.size(18.dp),
                    )
                    Spacer(Modifier.width(6.dp))
                    Text("滞在先を追加", color = MaterialPrimary(), style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
                }
                Text(
                    "※ 複数の場所に滞在する場合はすべて入力してください",
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                )
            }
        }
    }

    // ── §6 「寮食堂 食事の申し込み」（仅 外泊 / 帰国）（§2.1-8）——分留学生 / 日本人 ──
    if (needMeal) {
        SectionLabel(t, "6", "寮食堂 食事の申し込み")
        SuzuCard {
            if (isOverseas) {
                // 留学生：开关「食事不要期間を登録する」+ 展开后的开始/结束 + 食事备考
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            "食事不要期間を登録する",
                            color = t.ink,
                            modifier = Modifier.weight(1f),
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium),
                        )
                        TToggle(checked = mealSkipOn, onCheckedChange = onMealSkipOn)
                    }
                    if (mealSkipOn) {
                        Field(label = "不要 開始") {
                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                DateField(label = "日付", value = mealStartDate, onPick = onMealStartDate)
                                ChipGroup(options = MEALS, selected = mealStartMeal, onSelect = onMealStartMeal)
                            }
                        }
                        Field(label = "不要 終了") {
                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                DateField(label = "日付", value = mealEndDate, onPick = onMealEndDate)
                                ChipGroup(options = MEALS, selected = mealEndMeal, onSelect = onMealEndMeal)
                            }
                        }
                        Text(
                            "※ 上記の期間（開始の食事から終了の食事まで）は寮食堂の食事を停止します",
                            color = t.inkMute,
                            style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                        )
                        Field(label = "食事備考") {
                            TArea(
                                value = mealNote,
                                onValueChange = onMealNote,
                                placeholder = "例：8月10日の朝食まで必要、8月20日の夕食から必要",
                                rows = 3,
                            )
                        }
                    }
                }
            } else {
                // 日本人：不显示开关，只显示提示
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("食事の変更は食事入力表にご記入ください", color = t.ink, style = TextStyle(fontSize = 14.sp))
                    Text(
                        "※ 日本人生徒の食事の変更は、学校指定の食事入力表で行ってください。",
                        color = t.inkMute,
                        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
                    )
                }
            }
        }
    }

    // ── §7 飛行機（仅 帰国）（§2.1-9）──
    if (needFlight) {
        SectionLabel(t, "7", "飛行機")
        SuzuCard {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Field(label = "出発空港", required = true) {
                    TField(value = flightDepAir, onValueChange = onFlightDepAir, placeholder = "出発空港名")
                }
                TimeField(label = "出発時刻", value = flightDepTime, onPick = onFlightDepTime)
                Field(label = "到着空港", required = true) {
                    TField(value = flightArrAir, onValueChange = onFlightArrAir, placeholder = "到着空港名")
                }
                TimeField(label = "到着時刻", value = flightArrTime, onPick = onFlightArrTime)
            }
        }
    }

    // ── §8 理由（全 kind 共通，区块编号动态：帰国=8 / 外泊=7 / 帰省=5）（§2.1-10）──
    val reasonLabel =
        when {
            isHoliday -> "帰省の理由"
            needFlight -> "帰国の理由"
            else -> "外泊の理由"
        }
    SectionLabel(t, reasonSectionNo.toString(), "理由")
    SuzuCard {
        Field(label = reasonLabel, required = true) {
            TArea(value = reason, onValueChange = onReason, placeholder = "理由を入力してください", rows = 3)
        }
    }

    // ── 11. 底部单按钮「提出する」（v1.0 已删「下書き保存」与确认页）──
    PrimaryButton(
        title = if (submitting) "提出中…" else "提出する",
        enabled = canSubmit,
        onClick = onSubmit,
    )

    // ── 12. 底部居中灰字（§2.1-12）──
    Text(
        "提出後は担当の先生へメールで承認依頼が送信されます。",
        color = t.inkMute,
        modifier = Modifier.fillMaxWidth(),
        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
        textAlign = androidx.compose.ui.text.style.TextAlign.Center,
    )
}

// ════════════════════════════════════════════════════════════════════
// 私有小组件（对齐 iOS StayForm 私有 SectionLabel / InfoRow）
// ════════════════════════════════════════════════════════════════════

// 区块编号标签（22×22 圆角 6 方块蓝底白字 + 区块名）
@Composable
private fun SectionLabel(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    num: String,
    label: String,
) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(22.dp)
                    .clip(RoundedCornerShape(6.dp))
                    .background(MaterialPrimary()),
            contentAlignment = Alignment.Center,
        ) {
            Text(num, color = Color.White, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold))
        }
        Text(label, color = t.ink, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold))
    }
}

// 只读信息行（左标签固定宽 88 + 右值；非首行顶部 0.5 细线分隔）
@Composable
private fun InfoRow(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    label: String,
    value: String,
    mono: Boolean = false,
    first: Boolean = false,
) {
    if (!first) {
        Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
    }
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(label, color = t.inkSub, modifier = Modifier.width(88.dp), style = TextStyle(fontSize = 12.sp))
        Text(
            value,
            color = t.ink,
            style =
                TextStyle(
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    fontFamily = if (mono) FontFamily.Monospace else null,
                ),
        )
    }
}

// 「寮生特別運行の時刻表を見る」链接按钮（§3 / §4 出寮・帰寮方法下方）
@Composable
private fun BusTimetableLink(
    t: jp.tomoshibi.android.ui.theme.SuzuTokens,
    onClick: () -> Unit,
) {
    Row(
        modifier =
            Modifier
                .clip(RoundedCornerShape(8.dp))
                .clickable(onClick = onClick)
                .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        androidx.compose.material3.Icon(
            SuzuIcons.CalClock,
            contentDescription = null,
            tint = MaterialPrimary(),
            modifier = Modifier.size(14.dp),
        )
        Spacer(Modifier.width(6.dp))
        Text(
            "寮生特別運行の時刻表を見る",
            color = MaterialPrimary(),
            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.Medium),
        )
    }
}

// 主色短手（Header 卡 / 区块编号方块 / 链接 / 加号 用，避免每处都写 MaterialTheme.colorScheme.primary）
@Composable
private fun MaterialPrimary(): Color = androidx.compose.material3.MaterialTheme.colorScheme.primary
