package jp.tomoshibi.android.ui.screens.account

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.User
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch

private data class FormData(
    val name: String = "", val kana: String = "", val email: String = "",
    val dorm: String = "A棟", val kind: String = "中等部", val room: String = "",
    val tel: String = "", val emTel: String = "",
    val pw: String = "", val pw2: String = ""
)

private val LABELS = listOf("基本情報", "区分", "連絡先", "パスワード")

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AccountScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val scope = rememberCoroutineScope()
    var step by remember { mutableStateOf(0) }
    var data by remember { mutableStateOf(FormData()) }

    val valid: Boolean = when (step) {
        0 -> data.name.isNotBlank() && data.kana.isNotBlank()
        1 -> data.dorm.isNotBlank() && data.kind.isNotBlank() && data.room.isNotBlank()
        2 -> data.email.matches(Regex("\\S+@\\S+")) && data.tel.length >= 8
        3 -> data.pw.length >= 6 && data.pw == data.pw2
        else -> false
    }

    val onNext: () -> Unit = {
        if (step < 3) step++
        else scope.launch {
            store.update {
                it.copy(user = User(
                    name = data.name, kana = data.kana, email = data.email,
                    dorm = data.dorm, room = data.room,
                    avatar = data.name.firstOrNull()?.toString() ?: "春"
                ))
            }
            navController.navigate(Route.Welcome.path) {
                popUpTo(Route.Account.path) { inclusive = true }
            }
        }
    }

    Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier.size(44.dp).clickable {
                    if (step > 0) step-- else navController.popBackStack()
                },
                contentAlignment = Alignment.Center
            ) {
                Text("←", color = tokens.ink, style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.SemiBold))
            }
            Column(modifier = Modifier.weight(1f)) {
                Text("アカウント作成", color = tokens.ink,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold))
                Text("ステップ ${step + 1} / 4", color = tokens.inkSub,
                    style = TextStyle(fontSize = 12.sp))
            }
            Spacer(Modifier.width(44.dp))
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(bottom = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            (0..3).forEach { i ->
                val color by animateColorAsState(
                    if (i <= step) tokens.ink else tokens.hair, label = "progress"
                )
                Box(modifier = Modifier
                    .weight(1f).height(4.dp)
                    .clip(RoundedCornerShape(2.dp))
                    .background(color))
            }
        }

        Column(
            modifier = Modifier
                .weight(1f).fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp).padding(bottom = 20.dp)
        ) {
            Text(LABELS[step], color = tokens.ink,
                style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold),
                modifier = Modifier.padding(bottom = 20.dp))

            when (step) {
                0 -> {
                    FormField("氏名", data.name, "山田 春樹") { data = data.copy(name = it) }
                    FormField("フリガナ", data.kana, "ヤマダ ハルキ") { data = data.copy(kana = it) }
                }
                1 -> {
                    OptionField("寮", data.dorm, listOf("A棟", "B棟", "C棟")) { data = data.copy(dorm = it) }
                    OptionField("区分", data.kind, listOf("中等部", "高等部", "大学部")) { data = data.copy(kind = it) }
                    FormField("部屋番号", data.room, "203") { data = data.copy(room = it) }
                }
                2 -> {
                    FormField("メールアドレス", data.email, "haruki@example.com", KeyboardType.Email) { data = data.copy(email = it) }
                    FormField("電話番号", data.tel, "090-1234-5678", KeyboardType.Phone) { data = data.copy(tel = it) }
                    FormField("緊急連絡先", data.emTel, "保護者の電話番号", KeyboardType.Phone) { data = data.copy(emTel = it) }
                }
                3 -> {
                    FormField("パスワード（6文字以上）", data.pw, "", isPassword = true) { data = data.copy(pw = it) }
                    FormField("パスワード（確認）", data.pw2, "", isPassword = true) { data = data.copy(pw2 = it) }
                    if (data.pw.isNotBlank() && data.pw2.isNotBlank() && data.pw != data.pw2) {
                        Text("パスワードが一致しません", color = tokens.danger,
                            style = TextStyle(fontSize = 13.sp))
                    }
                }
            }
        }

        Box(modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 12.dp, bottom = 20.dp)) {
            Box(
                modifier = Modifier
                    .fillMaxWidth().height(52.dp)
                    .clip(RoundedCornerShape(16.dp))
                    .then(
                        if (valid) Modifier.background(tokens.btnGrad).clickable { onNext() }
                        else Modifier.background(tokens.inkFaint)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(if (step < 3) "次へ" else "アカウントを作成",
                    color = Color.White,
                    style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold))
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FormField(
    label: String,
    value: String,
    placeholder: String,
    keyboard: KeyboardType = KeyboardType.Text,
    isPassword: Boolean = false,
    onChange: (String) -> Unit
) {
    val tokens = SuzuT.current
    Column(modifier = Modifier.padding(bottom = 16.dp)) {
        Text(label, color = tokens.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
        Spacer(Modifier.height(6.dp))
        OutlinedTextField(
            value = value,
            onValueChange = onChange,
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            shape = RoundedCornerShape(12.dp),
            visualTransformation = if (isPassword) PasswordVisualTransformation() else VisualTransformation.None,
            keyboardOptions = KeyboardOptions(keyboardType = if (isPassword) KeyboardType.Password else keyboard),
            placeholder = { if (placeholder.isNotEmpty()) Text(placeholder, color = tokens.inkMute) },
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = tokens.ink,
                unfocusedBorderColor = tokens.hair,
                focusedContainerColor = tokens.paper,
                unfocusedContainerColor = tokens.paper
            )
        )
    }
}

@Composable
private fun OptionField(label: String, value: String, options: List<String>, onChange: (String) -> Unit) {
    val tokens = SuzuT.current
    Column(modifier = Modifier.padding(bottom = 16.dp)) {
        Text(label, color = tokens.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
        Spacer(Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            options.forEach { opt ->
                val isSelected = value == opt
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (isSelected) tokens.pill else tokens.paper)
                        .clickable { onChange(opt) }
                        .padding(horizontal = 16.dp, vertical = 10.dp)
                ) {
                    Text(opt,
                        color = if (isSelected) tokens.ink else tokens.inkSub,
                        style = TextStyle(
                            fontSize = 14.sp,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium
                        ))
                }
            }
        }
    }
}
