package jp.tomoshibi.android.ui.screens.mypage

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
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.ChangeLogEntry
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.endpoints.StudentSelfUpdateBody
import jp.tomoshibi.android.data.network.endpoints.StudentsAPI
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.Field
import jp.tomoshibi.android.ui.components.GlobalScaffold
import jp.tomoshibi.android.ui.components.PageHeader
import jp.tomoshibi.android.ui.components.PrimaryButton
import jp.tomoshibi.android.ui.components.SectionHeader
import jp.tomoshibi.android.ui.components.SuzuCard
import jp.tomoshibi.android.ui.components.TField
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter

// 个人信息 + 联系方式/房间编辑 — 对齐 iOS MyInfoView / MyInfoEditView 生产分支

@Composable
fun MyInfoScreen(navController: NavHostController) {
    val store = LocalAppStore.current
    val t = SuzuT.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val changeLog by store.changeLog.collectAsState()
    val u = state.user

    val birthLine =
        when {
            u.birthDate.isBlank() -> {
                "—"
            }

            else -> {
                val age = ageFrom(u.birthDate)
                if (age != null) "${u.birthDate} ($age 歳)" else u.birthDate
            }
        }
    val dormRoom = "${u.dorm} ${u.room}"

    val rows =
        listOf(
            "氏名" to u.name.ifBlank { "—" },
            "フリガナ" to u.kana.ifBlank { "—" },
            "生年月日" to birthLine,
            "性別" to u.gender.ifBlank { "—" },
            "アカウント番号" to u.studentNo.ifBlank { "—" },
            "学年・組・番号" to u.gradeClass.ifBlank { "—" },
            "寮・部屋" to dormRoom.trim().ifBlank { "—" },
            "区分" to u.category.ifBlank { "—" },
            "メール" to u.email.ifBlank { "—" },
            "電話" to u.phone.ifBlank { "—" },
        )

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "個人情報", level = 2, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                SuzuCard(padding = 0) {
                    rows.forEachIndexed { i, (label, value) ->
                        if (i > 0) {
                            Box(
                                modifier =
                                    Modifier
                                        .fillMaxWidth()
                                        .height(1.dp)
                                        .background(t.hairSoft),
                            )
                        }
                        Row(
                            modifier =
                                Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 14.dp, vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                label,
                                color = t.inkSub,
                                modifier = Modifier.width(120.dp),
                                style = TextStyle(fontSize = 13.sp),
                            )
                            Text(
                                value,
                                color = t.ink,
                                modifier = Modifier.weight(1f),
                                style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Medium),
                            )
                        }
                    }
                }

                Box(
                    modifier =
                        Modifier
                            .fillMaxWidth()
                            .height(44.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(t.pill)
                            .clickable { navController.navigate(Route.MyInfoEdit.path) },
                    contentAlignment = Alignment.Center,
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            SuzuIcons.Edit,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                            modifier = Modifier.size(16.dp),
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            "連絡先・部屋を編集",
                            color = MaterialTheme.colorScheme.primary,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                        )
                    }
                }

                if (changeLog.isNotEmpty()) {
                    Text(
                        "変更履歴",
                        color = t.inkSub,
                        style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                    )
                    SuzuCard(padding = 0) {
                        changeLog.forEachIndexed { idx, entry ->
                            if (idx > 0) {
                                Box(
                                    modifier =
                                        Modifier
                                            .fillMaxWidth()
                                            .height(1.dp)
                                            .background(t.hairSoft),
                                )
                            }
                            ChangeLogRow(entry)
                        }
                    }
                }

                InfoBox("学年・組・番号・氏名・生年月日・性別の変更は、寮監にご連絡ください。")

                Spacer(modifier = Modifier.height(20.dp))
            }
        }
    }
}

@Composable
private fun ChangeLogRow(entry: ChangeLogEntry) {
    val t = SuzuT.current
    val primary = MaterialTheme.colorScheme.primary
    val timeText =
        DateTimeFormatter
            .ofPattern("yyyy/MM/dd HH:mm")
            .withZone(ZoneId.of("Asia/Tokyo"))
            .format(Instant.ofEpochMilli(entry.atEpochMs))
    Column(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                entry.label,
                color = primary,
                style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
            )
            Spacer(modifier = Modifier.weight(1f))
            Text(
                timeText,
                color = t.inkSub,
                style = TextStyle(fontSize = 11.sp),
            )
        }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                entry.before,
                color = t.inkSub,
                style = TextStyle(fontSize = 13.sp, textDecoration = TextDecoration.LineThrough),
            )
            Spacer(modifier = Modifier.width(6.dp))
            Text("→", color = t.inkSub, style = TextStyle(fontSize = 13.sp))
            Spacer(modifier = Modifier.width(6.dp))
            Text(
                entry.after,
                color = t.ink,
                style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold),
            )
        }
    }
}

@Composable
fun MyInfoEditScreen(navController: NavHostController) {
    val store = LocalAppStore.current
    val t = SuzuT.current
    val scope = rememberCoroutineScope()
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    val u = state.user

    val dormPrefix = dormPrefixOf(u.dorm, u.room)
    val initialRoomNo = u.room.filter { it.isDigit() }

    var roomNo by remember(u.room) { mutableStateOf(initialRoomNo) }
    var email by remember(u.email) { mutableStateOf(u.email) }
    var phone by remember(u.phone) { mutableStateOf(u.phone) }
    var isSubmitting by remember { mutableStateOf(false) }

    val canSave = roomNo.isNotBlank() && email.isNotBlank() && phone.isNotBlank() && !isSubmitting

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "連絡先・部屋編集", level = 3, onLeft = { navController.popBackStack() })

            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                SectionHeader(title = "変更不可（先生に依頼）")
                SuzuCard(padding = 0) {
                    LockedRow(label = "アカウント番号", value = u.studentNo)
                    Box(modifier = Modifier.fillMaxWidth().height(1.dp).background(t.hairSoft))
                    LockedRow(label = "氏名", value = u.name)
                }

                Field(label = "部屋番号") {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier =
                                Modifier
                                    .size(48.dp)
                                    .clip(RoundedCornerShape(12.dp))
                                    .background(t.pill),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                dormPrefix,
                                color = MaterialTheme.colorScheme.primary,
                                style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold),
                            )
                        }
                        Spacer(modifier = Modifier.width(10.dp))
                        TField(
                            value = roomNo,
                            onValueChange = { input ->
                                roomNo = input.filter { it.isDigit() }.take(3)
                            },
                            modifier = Modifier.weight(1f),
                            keyboard = KeyboardType.Number,
                        )
                    }
                }

                Field(label = "メール") {
                    TField(
                        value = email,
                        onValueChange = { email = it },
                        keyboard = KeyboardType.Email,
                    )
                }

                Field(label = "電話") {
                    TField(
                        value = phone,
                        onValueChange = { phone = it },
                        keyboard = KeyboardType.Phone,
                    )
                }

                InfoBox(
                    "アカウント番号・学年・組・番号・氏名・生年月日・性別の変更は、寮監にご連絡ください。" +
                        "\n変更履歴は次の画面で確認できます。",
                )

                Spacer(modifier = Modifier.height(20.dp))
            }

            Box(modifier = Modifier.fillMaxWidth().padding(20.dp)) {
                PrimaryButton(
                    title = if (isSubmitting) "保存中…" else "保存する",
                    enabled = canSave,
                    onClick = {
                        if (isSubmitting) return@PrimaryButton
                        isSubmitting = true
                        val newRoom = dormPrefix + roomNo
                        val before = u
                        val body =
                            StudentSelfUpdateBody(
                                email = email.takeIf { it != before.email },
                                phone = phone.takeIf { it != before.phone },
                                roomNo = newRoom.takeIf { it != before.room },
                            )
                        val tokenAtStart = state.authToken
                        scope.launch {
                            try {
                                StudentsAPI.updateMe(body)
                                if (store.snapshot().authToken != tokenAtStart) return@launch
                                store.appendChange("room", "部屋番号", before.room, newRoom)
                                store.appendChange("email", "メール", before.email, email)
                                store.appendChange("phone", "電話", before.phone, phone)
                                store.applyLocalUserContact(newRoom, email, phone)
                                store.showToast("保存しました")
                                navController.popBackStack()
                            } catch (e: ApiError.Unprocessable) {
                                store.showToast(e.msg)
                            } catch (_: Exception) {
                                store.showToast("保存に失敗しました")
                            } finally {
                                isSubmitting = false
                            }
                        }
                    },
                )
            }
        }
    }
}

@Composable
private fun InfoBox(text: String) {
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.04f))
                .border(
                    width = 1.dp,
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.13f),
                    shape = RoundedCornerShape(12.dp),
                ).padding(12.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Icon(
            SuzuIcons.Info,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(16.dp).padding(top = 1.dp),
        )
        Spacer(Modifier.width(8.dp))
        Text(
            text,
            color = MaterialTheme.colorScheme.primary,
            style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
        )
    }
}

@Composable
private fun LockedRow(
    label: String,
    value: String,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            label,
            color = t.inkSub,
            modifier = Modifier.width(120.dp),
            style = TextStyle(fontSize = 13.sp),
        )
        Text(
            value,
            color = t.ink,
            modifier = Modifier.weight(1f),
            style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Medium),
        )
        Icon(
            SuzuIcons.Shield,
            contentDescription = null,
            tint = t.inkMute,
            modifier = Modifier.size(16.dp),
        )
    }
}

private fun ageFrom(birthDate: String): Int? {
    val parts = birthDate.split("-")
    if (parts.size != 3) return null
    val year = parts[0].toIntOrNull() ?: return null
    val baseYear = 2025
    val age = baseYear - year
    return if (age in 0..150) age else null
}

// 寮前缀：先看房号字母前缀（A5→A），再按寮名性别兜底 M/W。
private fun dormPrefixOf(
    dorm: String,
    room: String,
): String {
    val fromRoom = room.firstOrNull { !it.isDigit() }
    if (fromRoom != null) return fromRoom.uppercaseChar().toString()
    return when {
        dorm.startsWith("男") -> "M"
        dorm.startsWith("女") -> "W"
        else -> dorm.take(1)
    }
}
