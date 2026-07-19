package jp.tomoshibi.android.ui.screens.account

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.account.RoomCoding
import jp.tomoshibi.android.data.model.User
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.ZoneOffset

// 5 step 注册 — 对齐 iOS AuthStubs.swift §0.3-§0.7 RegisterStep1-5（规格 §2.4~§2.8）
//
// Step 1 基本情報    : アバター + 氏名 + 性別 toggle + 学生区分 toggle + 生年月日 + 学年 chip + 組 toggle + 出席番号 + 部屋番号 + アカウント番号 060218 自動算
// Step 2 点呼区分    : 一般寮生 / サッカー部 single-select card
// Step 3 連絡先      : メール + 電話
// Step 4「パスワード設定」: 琥珀色警告条 + 密码 + 密码确认（本地校验最少 6 位，itsuki 2026-06-05 拍板统一 6）
// Step 5「認証コード」  : 琥珀色警告条 + 6 桁大字输入 + 倒计时重发按钮 + 422 错误位 → 完成跳「ようこそ」欢迎页
//
// FormData 全部 demo seed 预填 — itsuki 一路点「次へ」即可完成（iOS 00 号 demo 等价）
private data class FormData(
    val name: String = "リュウイヒ",
    val gender: String = "male", // male / female → dorm 自动算
    val isOverseas: Boolean = false, // 一般生 / 留学生
    val birth: LocalDate = LocalDate.of(2006, 10, 14),
    val grade: String = "高3", // 中1/中2/中3/高1/高2/高3
    val classSuffix: String = "B", // A / B
    val seatNo: String = "18",
    val roomDigit: String = "101", // 不含 M/W 前缀（前缀靠 gender 自动算）
    val cat: String = "regular", // regular / soccer
    val email: String = "demo@example.com",
    val phone: String = "090-0000-0000",
    val pw: String = "demo1234",
    val pw2: String = "demo1234",
    val code: String = "000000", // 「認証コード」认证码 — 演示版预填 6 桁（对齐 iOS DEMO 预填 000000）
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

// 房号 / 寮名判定已抽到 data/account/RoomCoding（纯逻辑、可单测、跟 iOS/后端对齐）；这里只做 FormData 适配。
private fun fullRoom(d: FormData): String = RoomCoding.fullRoom(d.gender, d.roomDigit)

private fun dormName(d: FormData): String = RoomCoding.dormLabel(d.gender)

private fun catName(d: FormData): String = if (d.cat == "soccer") "サッカー部" else "一般寮生"

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AccountScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var step by remember { mutableStateOf(1) } // 1..5 (跟 iOS RegisterStep1-5 一致)
    var data by remember { mutableStateOf(FormData()) }
    val context = androidx.compose.ui.platform.LocalContext.current

    val canNext: Boolean =
        when (step) {
            1 -> {
                data.name.isNotBlank() && (data.seatNo.toIntOrNull() ?: 0) > 0 && data.roomDigit.isNotBlank()
            }

            2 -> {
                true
            }

            // 任一选中即可（默认 regular）
            3 -> {
                android.util.Patterns.EMAIL_ADDRESS
                    .matcher(data.email)
                    .matches() && data.phone.length >= 8
            }

            4 -> {
                // 密码本地校验：最少 6 位 + 两次一致（itsuki 2026-06-05 拍板统一 6）
                data.pw.length >= 6 && data.pw == data.pw2
            }

            5 -> {
                // 认证码：恰好 6 位数字（对齐 iOS canSubmit）
                data.code.length == 6 && data.code.all(Char::isDigit)
            }

            else -> {
                false
            }
        }

    // 提交建号 — 演示版本地写假人 + 跳欢迎页（不接后端）
    val submit: () -> Unit = {
        scope.launch {
            store.update {
                it.copy(
                    // 注册即登录 — 写假人的同时把登录态置 true（对齐 LoginScreen 登录后置 authed=true）。
                    // 缺这句的话：注册→Welcome→Home 后 authed 仍为 false，下次启动 Splash 会按 authed 判定把人踢回登录页。
                    authed = true,
                    user =
                        User(
                            name = data.name,
                            kana = data.name, // demo 简化
                            email = data.email,
                            dorm = dormName(data),
                            room = fullRoom(data),
                            avatar = data.name.firstOrNull()?.toString() ?: "リ",
                            studentNo = computedAccount(data),
                            gradeClass = "${data.grade}${data.classSuffix}組 ${data.seatNo}番",
                            category = catName(data),
                            phone = data.phone,
                        ),
                )
            }
            navController.navigate(Route.Welcome.path) {
                popUpTo(Route.Account.path) { inclusive = true }
            }
        }
    }

    val onNext: () -> Unit = {
        // Step4 完成后进 Step5 认证码（原本 Step4 直接跳 Welcome，现改成 Step4 → Step5 → Welcome）
        if (step < 5) {
            step++
        } else {
            submit()
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
            else -> "認証コード"
        }

    Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        // ── header: ← + 中央 title ──
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

        // ── progress: 「アカウント作成 X / 4」+ 4dp capsule fill ──
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

        // ── 内容滚动区 ──
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
                1 -> Step1Basic(data) { data = it }
                2 -> Step2Cat(data) { data = it }
                3 -> Step3Contact(data) { data = it }
                4 -> Step4Password(data) { data = it }
                5 -> Step5Code(data, context) { data = it }
            }
        }

        // ── footer ──
        FooterBar(step = step, canNext = canNext, onBack = onBack, onNext = onNext)
    }
}

// ════════════════════════════════════════════════════════════════
// Step 1 基本情報 — mega field
// ════════════════════════════════════════════════════════════════
@Composable
private fun Step1Basic(
    d: FormData,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current

    // アバター
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
            GhostBtn("写真を選択") { /* demo no-op */ }
            SoftBtn("デフォルトを使う") { /* demo no-op */ }
        }
    }

    // 氏名
    LabeledTextField("氏名", required = true, value = d.name, placeholder = "リュウ イヒ") {
        onChange(d.copy(name = it))
    }

    // 性別
    FieldLabel("性別", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ChoiceChip(d.gender == "male", "男", Modifier.weight(1f)) { onChange(d.copy(gender = "male")) }
        ChoiceChip(d.gender == "female", "女", Modifier.weight(1f)) { onChange(d.copy(gender = "female")) }
    }
    Text(
        "性別により自動的に男寮 / 女寮に配属されます",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )

    // 学生区分
    FieldLabel("学生区分", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ChoiceChip(!d.isOverseas, "一般生", Modifier.weight(1f)) { onChange(d.copy(isOverseas = false)) }
        ChoiceChip(d.isOverseas, "留学生", Modifier.weight(1f)) { onChange(d.copy(isOverseas = true)) }
    }
    Text(
        "留学生は出寮届の承認に国際交流の先生方も加わります",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )

    // 生年月日 (Material3 DatePicker dialog — Android 没有 inline wheel)
    BirthField(d.birth) { onChange(d.copy(birth = it)) }

    // 学年 6 chip
    FieldLabel("学年", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        GRADES.forEach { g ->
            ChoiceChip(d.grade == g, g, Modifier.weight(1f)) { onChange(d.copy(grade = g)) }
        }
    }

    // 組 A / B
    FieldLabel("組", required = true)
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        ChoiceChip(d.classSuffix == "A", "A組", Modifier.weight(1f)) { onChange(d.copy(classSuffix = "A")) }
        ChoiceChip(d.classSuffix == "B", "B組", Modifier.weight(1f)) { onChange(d.copy(classSuffix = "B")) }
    }

    // 出席番号
    LabeledTextField("出席番号", required = true, value = d.seatNo, placeholder = "18", keyboard = KeyboardType.Number) {
        onChange(d.copy(seatNo = it.filter(Char::isDigit).take(3)))
    }
    Text(
        "学年 + 組 + 番号でアカウント番号が自動生成されます（例：高3 B組 18番 → 060218）",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )

    // 部屋番号
    LabeledTextField("部屋番号", required = true, value = d.roomDigit, placeholder = "101") {
        onChange(d.copy(roomDigit = it.filter { c -> c.isLetterOrDigit() }.uppercase().take(4)))
    }
    Text(
        "例：101 / 12B · 男寮 M / 女寮 W は性別から自動付与",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )

    // アカウント番号 preview
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(t.pill)
                .border(1.dp, t.pill, RoundedCornerShape(12.dp))
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
            color = t.ink,
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

// ════════════════════════════════════════════════════════════════
// Step 2 点呼区分 — 2 card single-select
// ════════════════════════════════════════════════════════════════
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

    CatCard(
        selected = d.cat == "regular",
        title = "一般寮生",
        sub = "平日: 朝 7:40 / 晩 22:00 ・ 土日: 朝 8:50 / 晩 20:00",
        onClick = { onChange(d.copy(cat = "regular")) },
    )
    CatCard(
        selected = d.cat == "soccer",
        title = "サッカー部",
        sub = "平日: 朝 7:10 / 晩 22:00 ・ 土日: 朝 7:10 / 晩 20:00",
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
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(if (selected) t.pill else t.paper)
                .border(
                    width = if (selected) 1.5.dp else 1.dp,
                    color = if (selected) t.ink else t.hair,
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
            // radio marker 22dp
            Box(
                modifier =
                    Modifier
                        .size(22.dp)
                        .clip(CircleShape)
                        .border(
                            width = if (selected) 6.dp else 1.5.dp,
                            color = if (selected) t.ink else t.inkFaint,
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

// ════════════════════════════════════════════════════════════════
// Step 3 連絡先
// ════════════════════════════════════════════════════════════════
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
        placeholder = "example@email.com",
        keyboard = KeyboardType.Email,
    ) {
        onChange(d.copy(email = it))
    }
    Text(
        // 「確認用のメール」→「確認メール」（jp-reviewer 2026-07-19，与 iOS 同步）：原文括号里的
        // 「将来のパスワードリセット時の確認用です」被删后，「確認用の」指代悬空、读者不知在确认什么。
        "学校のメールアドレスでも、ご自身のメールアドレスでも登録できます。このメールアドレスはログインにも使えます。確認メールは送信されません",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp, lineHeight = 16.sp),
    )

    LabeledTextField(
        "電話番号",
        required = true,
        value = d.phone,
        placeholder = "090-1234-5678",
        keyboard = KeyboardType.Phone,
    ) {
        onChange(d.copy(phone = it))
    }
    Text(
        "寮監があなたに連絡する場合に使います",
        color = t.inkMute,
        style = TextStyle(fontSize = 11.sp),
    )
}

// ════════════════════════════════════════════════════════════════
// Step 4 パスワード設定
// ════════════════════════════════════════════════════════════════
@Composable
private fun Step4Password(
    d: FormData,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current
    val mismatch = d.pw.isNotBlank() && d.pw2.isNotBlank() && d.pw != d.pw2

    // amber 警告 banner
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
                "パスワードは自分では変更できません。変更には寮監への連絡が必要です。入力時は慎重にお願いします。",
                color = t.warnDeep,
                style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
            )
        }
    }

    LabeledTextField("パスワード", required = true, value = d.pw, placeholder = "", isPassword = true) {
        onChange(d.copy(pw = it))
    }
    // 提示文案对齐本地校验最少 6 位（itsuki 2026-06-05 拍板统一 6）
    Text("6 文字以上", color = t.inkMute, style = TextStyle(fontSize = 11.sp))

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

// ════════════════════════════════════════════════════════════════
// Step 5 認証コード（规格 §2.8）— 琥珀警告条 + 6 桁大字输入 + 倒计时重发 + 422 错误位
// ════════════════════════════════════════════════════════════════
@Composable
private fun Step5Code(
    d: FormData,
    context: android.content.Context,
    onChange: (FormData) -> Unit,
) {
    val t = SuzuT.current

    // 倒计时秒数 — 进屏即从 60 倒数，到 0 才允许「再送信」（本地 state，不接后端）
    var remain by remember { mutableStateOf(60) }
    // 422 错误位 — 演示版恒为空（真实环境放后端返回的日语错误串）
    val errorMsg: String? = null

    // 每秒减 1，到 0 停（LaunchedEffect 跟 remain 绑定，每次变动重新挂一帧 delay）
    LaunchedEffect(remain) {
        if (remain > 0) {
            kotlinx.coroutines.delay(1000)
            remain -= 1
        }
    }

    // 琥珀色警告条（同 Step4 样式，正文换成认证码说明）
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
            "教員から発行された 6 桁の認証コードを入力してください。コードは発行から 5 分以内のみ有効です。",
            color = t.warnDeep,
            style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
        )
    }

    // 标签
    FieldLabel("認証コード（6 桁）")

    // 居中超大输入框：28sp heavy 等宽 + 字距 8，数字键盘，实时过滤只留数字、最多 6 位
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
                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
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
                        textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                    ),
                modifier = Modifier.fillMaxWidth(),
            )
        },
        isError = errorMsg != null,
        colors =
            OutlinedTextFieldDefaults.colors(
                focusedBorderColor = t.ink,
                unfocusedBorderColor = t.hair,
                focusedContainerColor = t.pill,
                unfocusedContainerColor = t.pill,
                errorBorderColor = t.danger,
            ),
    )

    // 422 错误条：红字红底圆角框（演示版 errorMsg 恒空 → 不显示）
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

    // 倒计时重发按钮：remain > 0 时灰禁用显「再送信（NN 秒）」，到 0 可点显「再送信」
    val canResend = remain == 0
    Box(
        modifier =
            Modifier
                .fillMaxWidth()
                .height(44.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(if (canResend) t.pill else t.hairSoft)
                .then(
                    if (canResend) {
                        Modifier.clickable {
                            // 演示版：本地重置倒计时 + toast（不真发码）
                            remain = 60
                            android.widget.Toast
                                .makeText(context, "認証コードを再送信しました", android.widget.Toast.LENGTH_SHORT)
                                .show()
                        }
                    } else {
                        Modifier
                    },
                ),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            if (canResend) "再送信" else "再送信（$remain 秒）",
            color = if (canResend) t.ink else t.inkMute,
            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
        )
    }
}

// ════════════════════════════════════════════════════════════════
// Footer (戻る + 次へ / アカウント作成完了)
// ════════════════════════════════════════════════════════════════
@Composable
private fun FooterBar(
    step: Int,
    canNext: Boolean,
    onBack: () -> Unit,
    onNext: () -> Unit,
) {
    val t = SuzuT.current
    // 末步（Step5 认证码）按钮文案改成「アカウント作成完了」，其余步是「次へ」
    val nextLabel = if (step < 5) "次へ" else "アカウント作成完了"
    Column {
        Box(modifier = Modifier.fillMaxWidth().height(0.5.dp).background(t.hair))
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp).padding(top = 16.dp, bottom = 32.dp),
            horizontalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            if (step > 1) {
                // 戻る ghost
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
            // 次へ primary
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

// ════════════════════════════════════════════════════════════════
// Helpers
// ════════════════════════════════════════════════════════════════

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
                    focusedBorderColor = t.ink,
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
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Box(
        modifier =
            modifier
                .height(42.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(if (selected) t.pill else t.paper)
                .border(
                    width = if (selected) 1.5.dp else 1.dp,
                    color = if (selected) t.ink else t.hair,
                    shape = RoundedCornerShape(12.dp),
                ).clickable { onClick() },
        contentAlignment = Alignment.Center,
    ) {
        Text(
            label,
            color = if (selected) t.ink else t.inkSub,
            style =
                TextStyle(
                    fontSize = 14.sp,
                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                ),
        )
    }
}

@Composable
private fun GhostBtn(
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
                .background(t.paper)
                .border(1.dp, t.hair, RoundedCornerShape(10.dp))
                .clickable { onClick() },
        contentAlignment = Alignment.Center,
    ) {
        Text(label, color = t.ink, style = TextStyle(fontSize = 13.sp))
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
