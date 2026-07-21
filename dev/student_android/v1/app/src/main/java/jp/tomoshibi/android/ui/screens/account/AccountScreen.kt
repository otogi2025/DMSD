package jp.tomoshibi.android.ui.screens.account

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
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
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.BuildConfig
import jp.tomoshibi.android.data.account.RoomCoding
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.StudentAccountCreateBody
import jp.tomoshibi.android.data.network.endpoints.AccountsAPI
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.ZoneOffset

// 5 步注册 — 对齐 iOS AuthStubs.swift RegisterStep1-5
//
// Step1 基本信息 / Step2 点呼区分 / Step3 联络方式 / Step4 密码 / Step5「登録コード」
// 提交走 AccountsAPI.createAccount 真后端（对齐 iOS 2318-2342）

private data class FormData(
    val name: String = "",
    val gender: String = "", // canNext 已要求 male/female，空串强制用户选（女生防误带 male）
    val isOverseas: Boolean = false,
    val birth: LocalDate = LocalDate.of(2008, 1, 1), // 中性占位
    val grade: String = "高3", // 选择器默认（非 PII，保留）
    val classSuffix: String = "B",
    val seatNo: String = "",
    val room: String = "",
    val cat: String = "regular",
    val email: String = "",
    val phone: String = "",
    val pw: String = "",
    val pw2: String = "",
    val code: String = "",
)

// 演示预填（对齐 LoginScreen 的 BuildConfig.DEBUG 门控）— 仅 DEBUG 包注入，release 空表单
private fun demoFormData() =
    FormData(
        name = "リュウイヒ",
        gender = "male",
        birth = LocalDate.of(2006, 10, 14),
        seatNo = "18",
        room = "M101",
        email = "demo@example.com",
        phone = "090-0000-0000",
        pw = "demo1234",
        pw2 = "demo1234",
    )

private val GRADES = listOf("中1", "中2", "中3", "高1", "高2", "高3")

private fun gradeCode(g: String): String =
    when (g) {
        "中1" -> "01"
        "中2" -> "02"
        "中3" -> "03"
        "高1" -> "04"
        "高2" -> "05"
        "高3" -> "06"
        else -> "00"
    }

private fun classCode(c: String): String = if (c == "A") "01" else "02"

private fun computedAccount(d: FormData): String {
    val n = (d.seatNo.toIntOrNull() ?: 0).coerceIn(0, 99)
    return gradeCode(d.grade) + classCode(d.classSuffix) + "%02d".format(n)
}

private fun assembledRoom(d: FormData): String = RoomCoding.assembleRoomNo(d.room, d.gender)

private fun catName(d: FormData): String = if (d.cat == "soccer") "サッカー部" else "一般寮生"

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AccountScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var step by remember { mutableStateOf(1) }
    var data by remember { mutableStateOf(if (BuildConfig.DEBUG) demoFormData() else FormData()) }
    var submitting by remember { mutableStateOf(false) }
    var errorMsg by remember { mutableStateOf<String?>(null) }

    val roomMismatch = RoomCoding.roomGenderMismatch(data.room, data.gender)
    // android#5: Step1 即跑逐寮正则（与后端 validate_room_dorm_match 同源），非法房号禁用「次へ」
    val roomFormatOk =
        data.room.isNotBlank() &&
            RoomCoding.validateRoomDormMatch(
                assembledRoom(data),
                RoomCoding.dormUnit(data.room, data.gender),
                data.gender,
            )
    val seatOk = (data.seatNo.toIntOrNull() ?: 0) in 1..99

    val canNext: Boolean =
        when (step) {
            1 -> {
                data.name.isNotBlank() &&
                    (data.gender == "male" || data.gender == "female") &&
                    data.grade.isNotEmpty() &&
                    data.classSuffix.isNotEmpty() &&
                    seatOk &&
                    data.room.isNotBlank() &&
                    !roomMismatch &&
                    roomFormatOk
            }

            2 -> {
                true
            }

            3 -> {
                android.util.Patterns.EMAIL_ADDRESS
                    .matcher(data.email)
                    .matches() && data.phone.length >= 8
            }

            4 -> {
                data.pw.length >= 6 && data.pw == data.pw2
            }

            5 -> {
                data.code.length == 6 && data.code.all(Char::isDigit) && !submitting
            }

            else -> {
                false
            }
        }

    // 提交建号 — 真调 AccountsAPI.createAccount（对齐 iOS RegisterStep5.submit）
    val doSubmit: () -> Unit = {
        if (!submitting) {
            scope.launch {
                submitting = true
                errorMsg = null
                val roomNo = assembledRoom(data)
                val dorm = RoomCoding.dormUnit(data.room, data.gender)
                val seatPadded = "%02d".format((data.seatNo.toIntOrNull() ?: 0).coerceIn(0, 99))
                val body =
                    StudentAccountCreateBody(
                        name = data.name.trim(),
                        nameKana = null,
                        birthday = data.birth.toString(),
                        gender = data.gender,
                        gradeCode = gradeCode(data.grade),
                        classCode = classCode(data.classSuffix),
                        seatNo = seatPadded,
                        category = catName(data),
                        roomNo = roomNo,
                        dormUnit = dorm,
                        isOverseas = data.isOverseas,
                        email = data.email.takeIf { it.isNotBlank() },
                        phone = data.phone.takeIf { it.isNotBlank() },
                        password = data.pw,
                        registrationCode = data.code,
                    )
                val validationError = body.validate()
                if (validationError != null) {
                    errorMsg = validationError
                    submitting = false
                    return@launch
                }
                try {
                    val res = AccountsAPI.createAccount(body)
                    store.setAuthToken(res.accessToken, res.expiresIn)
                    store.loadMe()
                    submitting = false
                    navController.navigate(Route.Welcome.path) {
                        popUpTo(Route.Account.path) { inclusive = true }
                    }
                } catch (e: ApiError.Unprocessable) {
                    errorMsg = e.msg
                    submitting = false
                } catch (e: Exception) {
                    // android#24: 协程取消必须重抛，勿吞成假「通信エラー」；重抛前复位 submitting，
                    // 防取消时界面仍在导致主按钮永停在「提交中」（审查补强）
                    if (e is kotlinx.coroutines.CancellationException) {
                        submitting = false
                        throw e
                    }
                    errorMsg = "通信エラーが発生しました。もう一度お試しください。"
                    submitting = false
                }
            }
        }
    }

    val onNext: () -> Unit = {
        if (step < 5) {
            step++
            errorMsg = null
        } else {
            doSubmit()
        }
    }

    val onBack: () -> Unit = {
        if (step > 1) step-- else navController.popBackStack()
    }

    val title =
        when (step) {
            1 -> "基本情報"
            2 -> "点呼区分"
            3 -> "連絡先"
            4 -> "パスワード設定"
            else -> "登録コード"
        }

    Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier.size(44.dp).clip(CircleShape).clickable { onBack() },
                contentAlignment = Alignment.Center,
            ) {
                Text("‹", color = tokens.ink, style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Light))
            }
            Spacer(Modifier.weight(1f))
            Text(
                title,
                color = tokens.ink,
                style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.weight(1f))
            Spacer(Modifier.size(44.dp))
        }

        Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp).padding(bottom = 20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "アカウント作成",
                    color = tokens.inkSub,
                    style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
                )
                Spacer(Modifier.weight(1f))
                Text(
                    "$step / 5",
                    color = tokens.inkMute,
                    style = TextStyle(fontSize = 12.sp, fontFamily = FontFamily.Monospace),
                )
            }
            Spacer(Modifier.height(8.dp))
            Box(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .height(4.dp)
                        .clip(RoundedCornerShape(2.dp))
                        .background(tokens.hair),
            ) {
                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth(step / 5f)
                            .height(4.dp)
                            .clip(RoundedCornerShape(2.dp))
                            .background(tokens.btnGrad),
                )
            }
        }

        Column(
            modifier =
                Modifier
                    .weight(1f)
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(horizontal = 24.dp)
                    .padding(top = 8.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(18.dp),
        ) {
            when (step) {
                1 -> {
                    Step1Basic(data, roomMismatch, roomFormatOk) { data = it }
                }

                2 -> {
                    Step2Cat(data) { data = it }
                }

                3 -> {
                    Step3Contact(data) { data = it }
                }

                4 -> {
                    Step4Password(data) { data = it }
                }

                5 -> {
                    Step5Code(data, errorMsg) {
                        data = it
                        errorMsg = null
                    }
                }
            }
        }

        FooterBar(
            step = step,
            canNext = canNext,
            submitting = submitting,
            onBack = onBack,
            onNext = onNext,
        )
    }
}

@Composable
private fun Step1Basic(
    d: FormData,
    roomMismatch: Boolean,
    roomFormatOk: Boolean,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary

    FieldLabel("アバター")
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        Box(
            modifier =
                Modifier
                    .size(64.dp)
                    .clip(CircleShape)
                    .background(t.pill),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                d.name.firstOrNull()?.toString() ?: "リ",
                color = t.ink,
                style = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.Bold),
            )
        }
        Column(modifier = Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            SoftBtn("デフォルトを使う") { /* 默认头像即字母占位，无需动作 */ }
        }
    }

    LabeledTextField("氏名", required = true, value = d.name, placeholder = "") {
        onChange(d.copy(name = it))
    }
    Text(
        "日本人の方は漢字、留学生の方はカタカナでご入力ください",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )

    FieldLabel("性別", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ChoiceChip(d.gender == "male", "男性", Modifier.weight(1f)) { onChange(d.copy(gender = "male")) }
        ChoiceChip(d.gender == "female", "女性", Modifier.weight(1f)) { onChange(d.copy(gender = "female")) }
    }
    Text(
        "性別に応じて自動的に男子寮・女子寮に振り分けられます",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )

    FieldLabel("学生区分", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ChoiceChip(!d.isOverseas, "一般生", Modifier.weight(1f)) { onChange(d.copy(isOverseas = false)) }
        ChoiceChip(d.isOverseas, "留学生", Modifier.weight(1f)) { onChange(d.copy(isOverseas = true)) }
    }

    BirthField(d.birth) { onChange(d.copy(birth = it)) }

    FieldLabel("学年", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        GRADES.forEach { g ->
            ChoiceChip(d.grade == g, g, Modifier.weight(1f), height = 36.dp) { onChange(d.copy(grade = g)) }
        }
    }

    FieldLabel("組", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ChoiceChip(d.classSuffix == "A", "A組", Modifier.weight(1f)) { onChange(d.copy(classSuffix = "A")) }
        ChoiceChip(d.classSuffix == "B", "B組", Modifier.weight(1f)) { onChange(d.copy(classSuffix = "B")) }
    }

    LabeledTextField("出席番号", required = true, value = d.seatNo, placeholder = "", keyboard = KeyboardType.Number) {
        onChange(d.copy(seatNo = it.filter(Char::isDigit).take(2)))
    }

    LabeledTextField(
        "部屋番号",
        required = true,
        value = d.room,
        placeholder = "",
        errorText =
            when {
                // 性别/前缀矛盾优先提示
                roomMismatch -> {
                    "選択した性別と部屋番号が一致しません（女子寮はW・男子寮はM／Aで始まります）"
                }

                // android#5: 格式非法提示与后端 body.validate() / iOS 一致
                d.room.isNotBlank() && !roomFormatOk -> {
                    "部屋番号を正しく入力してください"
                }

                else -> {
                    null
                }
            },
    ) {
        onChange(d.copy(room = it.filter { c -> c.isLetterOrDigit() }.uppercase().take(4)))
    }

    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(primary.copy(alpha = 0.06f))
                .border(1.dp, primary.copy(alpha = 0.15f), RoundedCornerShape(12.dp))
                .padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            "アカウント番号",
            color = t.inkSub,
            style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
            modifier = Modifier.weight(1f),
        )
        Text(
            computedAccount(d),
            color = primary,
            style =
                TextStyle(
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    fontFamily = FontFamily.Monospace,
                    letterSpacing = 2.sp,
                ),
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun BirthField(
    birth: LocalDate,
    onChange: (LocalDate) -> Unit,
) {
    val t = SuzuT.current
    var open by remember { mutableStateOf(false) }
    FieldLabel("生年月日", required = true)
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(48.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(t.pill)
                .clickable { open = true }
                .padding(horizontal = 14.dp),
        contentAlignment = Alignment.CenterStart,
    ) {
        Text(
            "${birth.year} 年 ${birth.monthValue} 月 ${birth.dayOfMonth} 日",
            color = t.ink,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
        )
    }
    if (open) {
        val state =
            rememberDatePickerState(
                initialSelectedDateMillis = birth.atStartOfDay(ZoneOffset.UTC).toInstant().toEpochMilli(),
            )
        DatePickerDialog(
            onDismissRequest = { open = false },
            confirmButton = {
                TextButton(onClick = {
                    state.selectedDateMillis?.let {
                        val d =
                            java.time.Instant
                                .ofEpochMilli(it)
                                .atZone(ZoneOffset.UTC)
                                .toLocalDate()
                        onChange(d)
                    }
                    open = false
                }) { Text("OK") }
            },
            dismissButton = { TextButton(onClick = { open = false }) { Text("キャンセル") } },
        ) {
            DatePicker(state = state)
        }
    }
}

@Composable
private fun Step2Cat(
    d: FormData,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current
    Text(
        "あなたの点呼区分",
        color = t.ink,
        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
    )
    // 半角 · 前后各 2 空格（对齐 iOS）
    CatCard(
        selected = d.cat == "regular",
        title = "一般寮生",
        sub = "平日: 朝 7:40 / 晩 22:00  ·  土日: 朝 8:50 / 晩 20:00",
        onClick = { onChange(d.copy(cat = "regular")) },
    )
    CatCard(
        selected = d.cat == "soccer",
        title = "サッカー部",
        sub = "平日: 朝 7:10 / 晩 22:00  ·  土日: 朝 7:10 / 晩 20:00",
        onClick = { onChange(d.copy(cat = "soccer")) },
    )
}

@Composable
private fun CatCard(
    selected: Boolean,
    title: String,
    sub: String,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(if (selected) primary.copy(alpha = 0.03f) else t.paper)
                .border(
                    width = if (selected) 1.5.dp else 1.dp,
                    color = if (selected) primary else t.hair,
                    shape = RoundedCornerShape(16.dp),
                ).clickable { onClick() }
                .padding(18.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                title,
                color = t.ink,
                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                modifier = Modifier.weight(1f),
            )
            Box(
                modifier =
                    Modifier
                        .size(22.dp)
                        .clip(CircleShape)
                        .border(
                            width = if (selected) 6.dp else 1.5.dp,
                            color = if (selected) primary else t.inkFaint,
                            shape = CircleShape,
                        ).background(if (selected) Color.White else Color.Transparent),
            )
        }
        Text(
            sub,
            color = t.inkSub,
            style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
        )
    }
}

@Composable
private fun Step3Contact(
    d: FormData,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current
    LabeledTextField(
        "メールアドレス",
        required = true,
        value = d.email,
        placeholder = "",
        keyboard = KeyboardType.Email,
    ) {
        onChange(d.copy(email = it))
    }
    Text(
        "学校のメールアドレスでも、ご自身のメールアドレスでも登録できます。このメールアドレスはログインにも使えます。確認メールは送信されません",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
    )

    LabeledTextField(
        "電話番号",
        required = true,
        value = d.phone,
        placeholder = "",
        keyboard = KeyboardType.Phone,
    ) {
        onChange(d.copy(phone = it))
    }
    Text(
        "寮監から連絡する際に使用します",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )
}

@Composable
private fun Step4Password(
    d: FormData,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current
    val mismatch = d.pw.isNotBlank() && d.pw2.isNotBlank() && d.pw != d.pw2
    val tooShort = d.pw.isNotEmpty() && d.pw.length < 6

    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(t.warnBg)
                .border(1.dp, t.warn.copy(alpha = 0.25f), RoundedCornerShape(14.dp))
                .padding(horizontal = 16.dp, vertical = 14.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Box(
            modifier = Modifier.size(24.dp).clip(CircleShape).background(t.warn),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                "!",
                color = Color.White,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
            )
        }
        Column {
            Text(
                "ご注意ください",
                color = t.warnDeep,
                style = TextStyle(fontSize = 12.5.sp, fontWeight = FontWeight.Bold),
            )
            Spacer(Modifier.height(3.dp))
            Text(
                "パスワードはご自身では変更できません。変更には寮監への連絡が必要です。入力の際は慎重にお願いいたします。",
                color = t.warnDeep,
                style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
            )
        }
    }

    LabeledTextField(
        "パスワード",
        required = true,
        value = d.pw,
        placeholder = "",
        isPassword = true,
        errorText = if (tooShort) "パスワードは6文字以上で入力してください" else null,
    ) {
        onChange(d.copy(pw = it))
    }
    Text("6文字以上", color = t.inkMute, style = TextStyle(fontSize = 11.sp))

    LabeledTextField(
        "パスワード（確認）",
        required = true,
        value = d.pw2,
        placeholder = "",
        isPassword = true,
        errorText = if (mismatch) "パスワードが一致しません" else null,
    ) {
        onChange(d.copy(pw2 = it))
    }
}

@Composable
private fun Step5Code(
    d: FormData,
    errorMsg: String?,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current

    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(14.dp))
                .background(t.warnBg)
                .border(1.dp, t.warn.copy(alpha = 0.25f), RoundedCornerShape(14.dp))
                .padding(horizontal = 16.dp, vertical = 14.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Box(
            modifier = Modifier.size(24.dp).clip(CircleShape).background(t.warn),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                "!",
                color = Color.White,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Bold),
            )
        }
        Text(
            "教員から発行された6桁の登録コードを入力してください。コードは発行から5分以内のみ有効です。",
            color = t.warnDeep,
            style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
        )
    }

    FieldLabel("登録コード（6桁）")

    OutlinedTextField(
        value = d.code,
        onValueChange = { onChange(d.copy(code = it.filter(Char::isDigit).take(6))) },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        shape = RoundedCornerShape(12.dp),
        textStyle =
            TextStyle(
                fontSize = 28.sp,
                fontWeight = FontWeight.Black,
                fontFamily = FontFamily.Monospace,
                letterSpacing = 8.sp,
                textAlign = TextAlign.Center,
            ),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        placeholder = {
            Text(
                "000000",
                color = t.inkFaint,
                style =
                    TextStyle(
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Black,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 8.sp,
                        textAlign = TextAlign.Center,
                    ),
                modifier = Modifier.fillMaxWidth(),
            )
        },
        isError = errorMsg != null,
        colors =
            OutlinedTextFieldDefaults.colors(
                focusedBorderColor = MaterialTheme.colorScheme.primary,
                unfocusedBorderColor = t.hair,
                focusedContainerColor = t.pill,
                unfocusedContainerColor = t.pill,
                errorBorderColor = t.danger,
            ),
    )

    if (errorMsg != null) {
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.dangerBg)
                    .border(1.dp, t.danger.copy(alpha = 0.25f), RoundedCornerShape(12.dp))
                    .padding(horizontal = 14.dp, vertical = 10.dp),
        ) {
            Text(
                errorMsg,
                color = t.danger,
                style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
            )
        }
    }
    // 无重发按钮 — 对齐 iOS（注册码由老师发，App 内不能重发）
}

@Composable
private fun FooterBar(
    step: Int,
    canNext: Boolean,
    submitting: Boolean,
    onBack: () -> Unit,
    onNext: () -> Unit,
) {
    val t = SuzuT.current
    val nextLabel =
        when {
            step < 5 -> "次へ"
            submitting -> "送信中…"
            else -> "アカウントを作成"
        }
    Column {
        Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp).padding(top = 16.dp, bottom = 32.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            if (step > 1) {
                Box(
                    modifier =
                        Modifier
                            .weight(1f)
                            .height(52.dp)
                            .clip(RoundedCornerShape(16.dp))
                            .background(t.paper)
                            .border(1.dp, t.hair, RoundedCornerShape(16.dp))
                            .clickable { onBack() },
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        "戻る",
                        color = t.ink,
                        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold),
                    )
                }
            }
            Box(
                modifier =
                    Modifier
                        .weight(1f)
                        .height(52.dp)
                        .clip(RoundedCornerShape(16.dp))
                        .then(
                            if (canNext) {
                                Modifier.background(t.btnGrad).clickable { onNext() }
                            } else {
                                Modifier.background(t.inkFaint)
                            },
                        ),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    nextLabel,
                    color = Color.White,
                    style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold),
                )
            }
        }
    }
}

@Composable
private fun FieldLabel(
    label: String,
    required: Boolean = false,
) {
    val t = SuzuT.current
    Row {
        Text(
            label,
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
        )
        if (required) {
            Text(
                " *",
                color = t.danger,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold),
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun LabeledTextField(
    label: String,
    value: String,
    placeholder: String,
    required: Boolean = false,
    keyboard: KeyboardType = KeyboardType.Text,
    isPassword: Boolean = false,
    errorText: String? = null,
    onChange: (String) -> Unit,
) {
    val t = SuzuT.current
    Column(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        FieldLabel(label, required)
        OutlinedTextField(
            value = value,
            onValueChange = onChange,
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            shape = RoundedCornerShape(12.dp),
            visualTransformation = if (isPassword) PasswordVisualTransformation() else VisualTransformation.None,
            keyboardOptions = KeyboardOptions(keyboardType = if (isPassword) KeyboardType.Password else keyboard),
            placeholder = { if (placeholder.isNotEmpty()) Text(placeholder, color = t.inkFaint) },
            isError = errorText != null,
            colors =
                OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = MaterialTheme.colorScheme.primary,
                    unfocusedBorderColor = t.hair,
                    focusedContainerColor = t.pill,
                    unfocusedContainerColor = t.pill,
                    errorBorderColor = t.danger,
                ),
        )
        if (errorText != null) {
            Text(
                errorText,
                color = t.danger,
                style = TextStyle(fontSize = 12.sp),
            )
        }
    }
}

@Composable
private fun ChoiceChip(
    selected: Boolean,
    label: String,
    modifier: Modifier = Modifier,
    height: androidx.compose.ui.unit.Dp = 42.dp,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    Box(
        modifier =
            modifier
                .height(height)
                .clip(RoundedCornerShape(12.dp))
                .background(if (selected) primary.copy(alpha = 0.08f) else t.paper)
                .border(
                    width = if (selected) 1.5.dp else 1.dp,
                    color = if (selected) primary else t.hair,
                    shape = RoundedCornerShape(12.dp),
                ).clickable { onClick() },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            color = if (selected) primary else t.inkSub,
            style =
                TextStyle(
                    fontSize = 14.sp,
                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                ),
        )
    }
}

@Composable
private fun SoftBtn(
    label: String,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(38.dp)
                .clip(RoundedCornerShape(10.dp))
                .background(t.pill)
                .clickable { onClick() },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            color = t.ink,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}
