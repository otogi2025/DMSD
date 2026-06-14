package jp.tomoshibi.android.ui.screens.mypage

import android.widget.Toast
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
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.seed.MockData
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

// ───────────────────────────────────────────────────────────────
// 個人情報屏（MyInfoScreen，L2）+ 連絡先・部屋編集屏（MyInfoEditScreen，L3）
// 对齐 iOS MyInfoView / MyInfoEditView（规格 §3，2164-2199 行）
// 演示版假数据全从 MockData.DEFAULT_USER 读，不接后端
// ───────────────────────────────────────────────────────────────

// §3 個人情報（L2）— 10 行键值信息表卡 + 編集按钮 + info box
@Composable
fun MyInfoScreen(navController: NavHostController) {
    val t = SuzuT.current
    val u = MockData.DEFAULT_USER

    // 生年月日「2006-10-14 (19 歳)」与 寮・部屋「男寮 A5」由多字段拼出
    val age = ageFrom(u.birthDate)
    val birthLine = if (age != null) "${u.birthDate} ($age 歳)" else u.birthDate
    val dormRoom = "${u.dorm} ${u.room}"

    // 信息表 10 行（标签固定中文注释，UI 标签为日语原文，逐字照抄规格）
    val rows =
        listOf(
            "氏名" to u.name,
            "フリガナ" to u.kana,
            "生年月日" to birthLine,
            "性別" to u.gender,
            "アカウント番号" to u.studentNo,
            "学年・組・番号" to u.gradeClass,
            "寮・部屋" to dormRoom,
            "区分" to u.category,
            "メール" to u.email,
            "電話" to u.phone,
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
                // A. 信息表卡（padding 0，10 行键值，行间细分隔线）
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
                            // 左列标签固定宽 120
                            Text(
                                label,
                                color = t.inkSub,
                                modifier = Modifier.width(120.dp),
                                style = TextStyle(fontSize = 13.sp),
                            )
                            // 右列值
                            Text(
                                value,
                                color = t.ink,
                                modifier = Modifier.weight(1f),
                                style = TextStyle(fontSize = 13.5.sp, fontWeight = FontWeight.Medium),
                            )
                        }
                    }
                }

                // B. 編集按钮（青绿 8% 底圆角 12，高 44，居中 → 連絡先・部屋編集屏）
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
                        Spacer(Modifier.width(6.dp))
                        Text(
                            "学年・組・番号・部屋を編集",
                            color = MaterialTheme.colorScheme.primary,
                            style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
                        )
                    }
                }

                // D. info box（青绿 4% 底 + 描边圆角 12）
                InfoBox("氏名・生年月日・性別・メール・電話などの変更は、寮監にご連絡ください。")

                Spacer(Modifier.height(20.dp))
            }
        }
    }
}

// §3 連絡先・部屋編集（L3）— read-only 头 + 部屋番号 / メール / 電話 + help box + 保存
@Composable
fun MyInfoEditScreen(navController: NavHostController) {
    val t = SuzuT.current
    val ctx = LocalContext.current
    val u = MockData.DEFAULT_USER

    // 寮前缀方块（M=男寮 / W=女寮 / 其它取原房号首个非数字字符；A5→A）
    val dormPrefix = dormPrefixOf(u.dorm, u.room)
    // 房号去掉前缀只留数字部分（A5→5）
    val initialRoomNo = u.room.filter { it.isDigit() }

    var roomNo by remember { mutableStateOf(initialRoomNo) }
    var email by remember { mutableStateOf(u.email) }
    var phone by remember { mutableStateOf(u.phone) }

    // 仅三字段都非空才可点保存
    val canSave = roomNo.isNotBlank() && email.isNotBlank() && phone.isNotBlank()

    GlobalScaffold(activeTab = "me", navController = navController) {
        Column(modifier = Modifier.fillMaxSize().background(t.pearl)) {
            PageHeader(title = "連絡先・部屋編集", level = 3, onLeft = { navController.popBackStack() })

            // 滚动区
            Column(
                modifier =
                    Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .verticalScroll(rememberScrollState())
                        .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                // read-only 头：小标题 + 卡（学号 / 氏名 + 锁图标，学生不可改）
                SectionHeader(title = "変更不可（先生に依頼）")
                SuzuCard(padding = 0) {
                    LockedRow(label = "学号", value = u.studentNo)
                    Box(modifier = Modifier.fillMaxWidth().height(1.dp).background(t.hairSoft))
                    LockedRow(label = "氏名", value = u.name)
                }

                // 部屋番号字段：左侧固定寮前缀方块 + 数字 TField（只留数字、最多 3 位）
                Field(label = "部屋番号") {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        // 寮前缀方块（青绿 8% 底）
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
                        Spacer(Modifier.width(10.dp))
                        TField(
                            value = roomNo,
                            onValueChange = { input ->
                                // 只保留数字，最多 3 位
                                roomNo = input.filter { it.isDigit() }.take(3)
                            },
                            modifier = Modifier.weight(1f),
                            keyboard = KeyboardType.Number,
                        )
                    }
                }

                // メール字段（邮箱键盘）
                Field(label = "メール") {
                    TField(
                        value = email,
                        onValueChange = { email = it },
                        keyboard = KeyboardType.Email,
                    )
                }

                // 電話字段（电话键盘）
                Field(label = "電話") {
                    TField(
                        value = phone,
                        onValueChange = { phone = it },
                        keyboard = KeyboardType.Phone,
                    )
                }

                // help box
                InfoBox(
                    "学号・姓名・生年月日・性別の変更は寮監にご連絡ください。" +
                        "\n変更履歴は次の画面で確認できます。",
                )

                Spacer(Modifier.height(20.dp))
            }

            // 底部固定 PrimaryButton「保存する」（三字段都非空才可点）
            Box(modifier = Modifier.fillMaxWidth().padding(20.dp)) {
                PrimaryButton(
                    title = "保存する",
                    enabled = canSave,
                    onClick = {
                        // 拼回前缀 + 数字 = 新房号（演示版仅弹 toast 不真持久化）
                        Toast.makeText(ctx, "保存しました", Toast.LENGTH_SHORT).show()
                        navController.popBackStack()
                    },
                )
            }
        }
    }
}

// info / help box — 青绿 4% 底 + 13% 描边圆角 12，ℹ + 文案
@Composable
private fun InfoBox(text: String) {
    val t = SuzuT.current
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
        // 规格 §0 的 T.primaryDk（#0E3840 深青绿）Android 没有对应 token，
        // 用 MaterialTheme primary（teal #1F6B74）近似，遵守"不写 hex"铁律
        Text(
            text,
            color = MaterialTheme.colorScheme.primary,
            style = TextStyle(fontSize = 12.5.sp, lineHeight = 18.sp),
        )
    }
}

// read-only 行 — 标签 + 值 + 右侧锁图标
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

// 由生年月日「yyyy-MM-dd」粗算年龄（仅按年差，演示版够用）；解析失败返回 null
private fun ageFrom(birthDate: String): Int? {
    val parts = birthDate.split("-")
    if (parts.size != 3) return null
    val year = parts[0].toIntOrNull() ?: return null
    // 演示版固定基准 2025 年（跟 iOS 假数据「19 歳」对齐）
    val baseYear = 2025
    val age = baseYear - year
    return if (age in 0..150) age else null
}

// 寮前缀字母：男寮→M / 女寮→W / 其它取原房号首个非数字字符（A5→A），都没有则取寮名首字
private fun dormPrefixOf(
    dorm: String,
    room: String,
): String =
    when {
        dorm.startsWith("男") -> {
            "M"
        }

        dorm.startsWith("女") -> {
            "W"
        }

        else -> {
            val letter = room.firstOrNull { !it.isDigit() }
            letter?.uppercaseChar()?.toString() ?: dorm.take(1)
        }
    }
