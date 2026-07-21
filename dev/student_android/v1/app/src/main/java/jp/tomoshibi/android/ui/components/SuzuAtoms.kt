package jp.tomoshibi.android.ui.components

import androidx.compose.animation.core.animateFloat
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.rememberDatePickerState
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// ───────────────────────────────────────────────────────────────
// Suzu 中央共享组件库 — 对齐 iOS Foundation/Components/UIAtoms.swift + Field.swift + PrimaryButton.swift
// 各屏不再内联重写原子，统一从这里取，保证外观跟 iOS 一致。
// 颜色取值：主色 = MaterialTheme.colorScheme.primary（teal）/ accent = .secondary / accentSoft = .primaryContainer
//          其余语义色（paper/ink/hair/pill/warn/danger/ok…）= SuzuT.current
// ───────────────────────────────────────────────────────────────

// 4.1 Card — 白卡片容器（padding 默认 14、圆角 16、双层柔阴影）
// 双层对齐 iOS UIAtoms Card：radius14/y4@5% + radius2/y1@4%
@Composable
fun SuzuCard(
    modifier: Modifier = Modifier,
    padding: Int = 14,
    radius: Int = 16,
    content: @Composable () -> Unit,
) {
    val t = SuzuT.current
    val shape = RoundedCornerShape(radius.dp)
    Column(
        modifier =
            modifier
                .fillMaxWidth()
                // 大范围软阴影
                .shadow(
                    elevation = 14.dp,
                    shape = shape,
                    ambientColor = t.ink.copy(alpha = 0.05f),
                    spotColor = t.ink.copy(alpha = 0.05f),
                )
                // 小范围贴边阴影
                .shadow(
                    elevation = 2.dp,
                    shape = shape,
                    ambientColor = t.ink.copy(alpha = 0.04f),
                    spotColor = t.ink.copy(alpha = 0.04f),
                ).clip(shape)
                .background(t.paper)
                .padding(padding.dp),
    ) {
        content()
    }
}

// 4.2 Pill — 胶囊小标签（11sp semibold、内边距 横10 竖4、Capsule、5 色调）
enum class PillTone { Neutral, Ok, Warn, Danger, Accent }

@Composable
fun Pill(
    text: String,
    tone: PillTone = PillTone.Neutral,
) {
    val t = SuzuT.current
    val (fg, bg) =
        when (tone) {
            PillTone.Neutral -> t.inkSub to t.hair
            PillTone.Ok -> t.okDeep to t.okBg
            PillTone.Warn -> t.warnDeep to t.warnBg
            PillTone.Danger -> t.danger to t.dangerBg
            PillTone.Accent -> MaterialTheme.colorScheme.primary to t.pill
        }
    Box(
        modifier =
            Modifier
                .clip(RoundedCornerShape(percent = 50))
                .background(bg)
                .padding(horizontal = 10.dp, vertical = 4.dp),
    ) {
        Text(text, color = fg, style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.SemiBold))
    }
}

// 4.3 Avatar — 圆形头文字（默认 44dp、圆底 pill、中央 1 字母）
@Composable
fun Avatar(
    letter: String,
    size: Int = 44,
) {
    val t = SuzuT.current
    Box(
        modifier =
            Modifier
                .size(size.dp)
                .clip(RoundedCornerShape(percent = 50))
                .background(t.pill),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = letter.take(1),
            color = MaterialTheme.colorScheme.primary,
            style = TextStyle(fontSize = (size * 0.44f).sp, fontWeight = FontWeight.Bold),
        )
    }
}

// 4.4 SectionHeader — 区块小标题（13sp bold inkSub、全大写、字间距 1）
@Composable
fun SectionHeader(
    title: String,
    right: (@Composable () -> Unit)? = null,
) {
    val t = SuzuT.current
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = title.uppercase(),
            color = t.inkSub,
            style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp),
        )
        Spacer(Modifier.weight(1f))
        if (right != null) right()
    }
}

// 4.5 PrimaryButton — 主按钮（高 52、圆角 16、字 16 bold、撑满；三态：正常径向渐变 / 禁用灰 / 危险红）
@Composable
fun PrimaryButton(
    title: String,
    modifier: Modifier = Modifier,
    icon: ImageVector? = null,
    enabled: Boolean = true,
    destructive: Boolean = false,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val bgBrush: Brush =
        when {
            !enabled -> {
                SolidColor(t.inkFaint)
            }

            destructive -> {
                SolidColor(t.danger)
            }

            // 正常态：径向渐变 accentSoft（中心亮）→ accent → primary（外缘深），对齐 iOS
            else -> {
                Brush.radialGradient(
                    colors = listOf(cs.primaryContainer, cs.secondary, cs.primary),
                )
            }
        }
    Row(
        modifier =
            modifier
                .fillMaxWidth()
                .height(52.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(bgBrush)
                .clickable(enabled = enabled, onClick = onClick)
                .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icon != null) {
            Icon(icon, contentDescription = null, tint = Color.White, modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(8.dp))
        }
        Text(
            text = title,
            color = Color.White,
            style = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Bold, letterSpacing = 0.32.sp),
        )
    }
}

// 4.6 GhostButton — 次按钮（高 52、圆角 16、字 15 medium primary、描边 primary@30%）
@Composable
fun GhostButton(
    title: String,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    val cs = MaterialTheme.colorScheme
    Row(
        modifier =
            modifier
                .fillMaxWidth()
                .height(52.dp)
                .clip(RoundedCornerShape(16.dp))
                .border(BorderStroke(1.dp, cs.primary.copy(alpha = 0.3f)), RoundedCornerShape(16.dp))
                .clickable(onClick = onClick)
                .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(title, color = cs.primary, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Medium))
    }
}

// 4.7 Field — 表单字段包裹（label 13 semibold + required 红*、内容 slot、error 11 红 / hint 11 inkMute）
@Composable
fun Field(
    label: String,
    modifier: Modifier = Modifier,
    required: Boolean = false,
    error: String? = null,
    hint: String? = null,
    content: @Composable () -> Unit,
) {
    val t = SuzuT.current
    Column(modifier = modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(7.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(label, color = t.inkSub, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
            if (required) {
                Text(" *", color = t.danger, style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
            }
        }
        content()
        when {
            error != null -> Text(error, color = t.danger, style = TextStyle(fontSize = 11.sp))
            hint != null -> Text(hint, color = t.inkMute, style = TextStyle(fontSize = 11.sp, lineHeight = 14.sp))
        }
    }
}

// 4.8 TField — 单行输入（高 48、圆角 12、底 pearl、字 15、未聚焦 hair 1 / 聚焦 primary 1.5）
@Composable
fun TField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    secure: Boolean = false,
    keyboard: KeyboardType = KeyboardType.Text,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    val interaction = remember { MutableInteractionSource() }
    val focused by interaction.collectIsFocusedAsState()
    val borderColor = if (focused) cs.primary else t.hair
    val borderWidth = if (focused) 1.5.dp else 1.dp
    BasicTextField(
        value = value,
        onValueChange = onValueChange,
        modifier =
            modifier
                .fillMaxWidth()
                .height(48.dp)
                .clip(RoundedCornerShape(12.dp))
                .background(t.pearl)
                .border(BorderStroke(borderWidth, borderColor), RoundedCornerShape(12.dp)),
        textStyle = TextStyle(fontSize = 15.sp, color = t.ink),
        singleLine = true,
        interactionSource = interaction,
        cursorBrush = SolidColor(cs.primary),
        visualTransformation = if (secure) PasswordVisualTransformation() else VisualTransformation.None,
        keyboardOptions = KeyboardOptions(keyboardType = keyboard),
        decorationBox = { inner ->
            Box(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 14.dp),
                contentAlignment = Alignment.CenterStart,
            ) {
                if (value.isEmpty() && placeholder.isNotEmpty()) {
                    Text(placeholder, color = t.inkMute, style = TextStyle(fontSize = 15.sp))
                }
                inner()
            }
        },
    )
}

// 4.9 TArea — 多行输入（高 = rows×22+20、内边距 8、底 hairSoft、圆角 12、边框 hair 1、placeholder overlay）
@Composable
fun TArea(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    placeholder: String = "",
    rows: Int = 4,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    BasicTextField(
        value = value,
        onValueChange = onValueChange,
        modifier =
            modifier
                .fillMaxWidth()
                .heightIn(min = (rows * 22 + 20).dp)
                .clip(RoundedCornerShape(12.dp))
                .background(t.hairSoft)
                .border(BorderStroke(1.dp, t.hair), RoundedCornerShape(12.dp)),
        textStyle = TextStyle(fontSize = 15.sp, color = t.ink),
        cursorBrush = SolidColor(cs.primary),
        decorationBox = { inner ->
            Box(modifier = Modifier.fillMaxWidth().padding(14.dp)) {
                if (value.isEmpty() && placeholder.isNotEmpty()) {
                    Text(placeholder, color = t.inkMute, style = TextStyle(fontSize = 14.sp))
                }
                inner()
            }
        },
    )
}

// 4.10 RadioCard — 单选大卡（左圆 radio 22 + 右标题/副文字；选中底 pill / 未选底 hairSoft）
@Composable
fun RadioCard(
    title: String,
    selected: Boolean,
    modifier: Modifier = Modifier,
    detail: String? = null,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    Row(
        modifier =
            modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp))
                .background(if (selected) t.pill else t.hairSoft)
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        // 圆形 radio：选中 = primary 描边 + 内 10dp 实心点；未选 = inkFaint 描边
        Box(
            modifier =
                Modifier
                    .size(22.dp)
                    .clip(RoundedCornerShape(percent = 50))
                    .border(BorderStroke(2.dp, if (selected) cs.primary else t.inkFaint), RoundedCornerShape(percent = 50)),
            contentAlignment = Alignment.Center,
        ) {
            if (selected) {
                Box(
                    modifier =
                        Modifier
                            .size(10.dp)
                            .clip(RoundedCornerShape(percent = 50))
                            .background(cs.primary),
                )
            }
        }
        Spacer(Modifier.width(12.dp))
        Column {
            Text(title, color = t.ink, style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold))
            if (detail != null) {
                Text(detail, color = t.inkSub, style = TextStyle(fontSize = 12.sp))
            }
        }
    }
}

// 4.11 ChipGroup — 横向自动换行胶囊选择组（FlowRow，选中 白字+primary 底 / 未选 ink+paper 底）
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun ChipGroup(
    options: List<String>,
    selected: String?,
    modifier: Modifier = Modifier,
    onSelect: (String) -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    FlowRow(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(6.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        options.forEach { opt ->
            val isSel = opt == selected
            Box(
                modifier =
                    Modifier
                        .clip(RoundedCornerShape(percent = 50))
                        .background(if (isSel) cs.primary else t.paper)
                        .border(
                            BorderStroke(1.dp, if (isSel) cs.primary else t.hair),
                            RoundedCornerShape(percent = 50),
                        ).clickable { onSelect(opt) }
                        .padding(horizontal = 12.dp, vertical = 7.dp),
            ) {
                Text(
                    opt,
                    color = if (isSel) Color.White else t.ink,
                    style = TextStyle(fontSize = 12.sp, fontWeight = FontWeight.SemiBold),
                )
            }
        }
    }
}

// 4.12 EmptyState — 空状态占位（图标 40 inkMute + title 14 semibold + 可选 message 12 居中、padding 40）
@Composable
fun EmptyState(
    title: String,
    modifier: Modifier = Modifier,
    icon: ImageVector = SuzuIcons.Box,
    message: String? = null,
) {
    val t = SuzuT.current
    Column(
        modifier = modifier.fillMaxWidth().padding(40.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Icon(icon, contentDescription = null, tint = t.inkMute, modifier = Modifier.size(40.dp))
        Text(title, color = t.inkSub, style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold))
        if (message != null) {
            Text(
                message,
                color = t.inkMute,
                style = TextStyle(fontSize = 12.sp),
                textAlign = TextAlign.Center,
            )
        }
    }
}

// 4.13 TToggle — iOS 开关（激活色 primary）
@Composable
fun TToggle(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit,
) {
    val cs = MaterialTheme.colorScheme
    Switch(
        checked = checked,
        onCheckedChange = onCheckedChange,
        colors = SwitchDefaults.colors(checkedTrackColor = cs.primary),
    )
}

// 4.14 PageHeader — 子页统一头部（左键按 level 切 home/返回、标题 17 bold、长按弹面包屑）
// onLongPress 默认：轻触觉 + 打开全局 BreadcrumbOverlay（对齐 iOS PageHeader 0.4s 长按）
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun PageHeader(
    title: String,
    modifier: Modifier = Modifier,
    level: Int = 2,
    onLeft: () -> Unit,
    onLongPress: (() -> Unit)? = null,
    right: (@Composable () -> Unit)? = null,
) {
    val t = SuzuT.current
    val store = jp.tomoshibi.android.data.store.LocalAppStore.current
    val haptics =
        jp.tomoshibi.android.ui.haptics
            .rememberHaptics()
    val longPressHandler =
        onLongPress ?: {
            haptics(jp.tomoshibi.android.ui.haptics.HapticKind.Light)
            store.openBreadcrumb()
        }
    Row(
        modifier =
            modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        Box(
            modifier =
                Modifier
                    .size(36.dp)
                    .combinedClickable(onClick = onLeft, onLongClick = longPressHandler),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = if (level <= 1) SuzuIcons.Home else SuzuIcons.ChevL,
                contentDescription = null,
                tint = t.ink,
                modifier = Modifier.size(22.dp),
            )
        }
        Text(title, color = t.ink, style = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.Bold))
        // android#22: Spacer 必须用独立 Modifier，勿复用入参 modifier（已套在外层 Row 上）
        Spacer(Modifier.weight(1f))
        if (right != null) right()
    }
}

// 4.15 Skeleton — 对齐 iOS UIAtoms Skeleton（圆角 6 + 1.4s 扫光）
@Composable
fun SuzuSkeleton(
    modifier: Modifier = Modifier,
    height: Int = 14,
) {
    val t = SuzuT.current
    val transition =
        androidx.compose.animation.core
            .rememberInfiniteTransition(label = "skeleton")
    val shift by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec =
            androidx.compose.animation.core.infiniteRepeatable(
                animation =
                    androidx.compose.animation.core.tween(
                        durationMillis = 1400,
                        easing = androidx.compose.animation.core.LinearEasing,
                    ),
            ),
        label = "skeleton-shift",
    )
    val brush =
        Brush.linearGradient(
            colors = listOf(t.hair, t.hairSoft, t.hair),
            start =
                androidx.compose.ui.geometry.Offset(
                    x = -200f + 400f * shift,
                    y = 0f,
                ),
            end =
                androidx.compose.ui.geometry.Offset(
                    x = 200f + 400f * shift,
                    y = 0f,
                ),
        )
    Box(
        modifier =
            modifier
                .fillMaxWidth()
                .height(height.dp)
                .clip(RoundedCornerShape(6.dp))
                .background(brush),
    )
}

// 4.16 DateField — 日期选择字段（Field 包裹 + 点击弹 Material DatePicker，回传 ISO "yyyy-MM-dd"）
// minDate / maxDate：可选下限 / 上限（yyyy-MM-dd），对齐 iOS ApplyDateField 的 minDate 硬限制。
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DateField(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    required: Boolean = false,
    placeholder: String = "日付を選択",
    minDate: String? = null,
    maxDate: String? = null,
    onPick: (String) -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    var open by remember { mutableStateOf(false) }
    Field(label = label, required = required, modifier = modifier) {
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.pearl)
                    .border(BorderStroke(1.dp, t.hair), RoundedCornerShape(12.dp))
                    .clickable { open = true }
                    .padding(horizontal = 14.dp),
            contentAlignment = Alignment.CenterStart,
        ) {
            Text(
                value.ifEmpty { placeholder },
                color = if (value.isEmpty()) t.inkMute else t.ink,
                style = TextStyle(fontSize = 15.sp),
            )
        }
    }
    if (open) {
        // min/max 转 UTC 当天 0 点毫秒（跟 DatePicker 选中值同口径）
        val minMillis =
            minDate?.let {
                runCatching {
                    java.time.LocalDate
                        .parse(it)
                        .atStartOfDay(java.time.ZoneOffset.UTC)
                        .toInstant()
                        .toEpochMilli()
                }.getOrNull()
            }
        val maxMillis =
            maxDate?.let {
                runCatching {
                    java.time.LocalDate
                        .parse(it)
                        .atStartOfDay(java.time.ZoneOffset.UTC)
                        .toInstant()
                        .toEpochMilli()
                }.getOrNull()
            }
        val selectable =
            object : androidx.compose.material3.SelectableDates {
                override fun isSelectableDate(utcTimeMillis: Long): Boolean {
                    if (minMillis != null && utcTimeMillis < minMillis) return false
                    if (maxMillis != null && utcTimeMillis > maxMillis) return false
                    return true
                }
            }
        // android#23: value 非空时解析为 UTC 当天 0 点毫秒，让日历高亮已选日
        val initialSelectedMillis =
            if (value.isNotBlank()) {
                runCatching {
                    java.time.LocalDate
                        .parse(value)
                        .atStartOfDay(java.time.ZoneOffset.UTC)
                        .toInstant()
                        .toEpochMilli()
                }.getOrNull()
            } else {
                null
            }
        // key 住 min/max/value，避免范围或已选日变了还沿用旧 state
        androidx.compose.runtime.key(minDate, maxDate, value) {
            val state =
                rememberDatePickerState(
                    initialSelectedDateMillis = initialSelectedMillis,
                    selectableDates = selectable,
                )
            DatePickerDialog(
                onDismissRequest = { open = false },
                confirmButton = {
                    TextButton(onClick = {
                        state.selectedDateMillis?.let { ms ->
                            // DatePicker 选中毫秒是 UTC 当天 0 点，按 UTC 取日历日避免偏移
                            val d =
                                java.time.Instant
                                    .ofEpochMilli(ms)
                                    .atZone(java.time.ZoneOffset.UTC)
                                    .toLocalDate()
                            onPick(d.toString())
                        }
                        open = false
                    }) { Text("OK", color = cs.primary) }
                },
                dismissButton = {
                    TextButton(onClick = { open = false }) { Text("キャンセル", color = t.inkSub) }
                },
            ) {
                DatePicker(state = state)
            }
        }
    }
}

// 4.17 TimeField — 时刻选择字段（Field 包裹 + 点击弹 Material TimePicker，回传 "HH:mm"）
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TimeField(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    required: Boolean = false,
    placeholder: String = "時刻を選択",
    onPick: (String) -> Unit,
) {
    val t = SuzuT.current
    val cs = MaterialTheme.colorScheme
    var open by remember { mutableStateOf(false) }
    Field(label = label, required = required, modifier = modifier) {
        Box(
            modifier =
                Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(t.pearl)
                    .border(BorderStroke(1.dp, t.hair), RoundedCornerShape(12.dp))
                    .clickable { open = true }
                    .padding(horizontal = 14.dp),
            contentAlignment = Alignment.CenterStart,
        ) {
            Text(
                value.ifEmpty { placeholder },
                color = if (value.isEmpty()) t.inkMute else t.ink,
                style = TextStyle(fontSize = 15.sp),
            )
        }
    }
    if (open) {
        // android#2: 从已有 "HH:mm" 解析初始时分，避免默认 00:00 覆盖已填时刻
        val (initialHour, initialMinute) =
            runCatching {
                val parts = value.split(":")
                require(parts.size == 2)
                val h = parts[0].toInt()
                val m = parts[1].toInt()
                require(h in 0..23 && m in 0..59)
                h to m
            }.getOrElse { 0 to 0 }
        val state =
            rememberTimePickerState(
                initialHour = initialHour,
                initialMinute = initialMinute,
                is24Hour = true,
            )
        AlertDialog(
            onDismissRequest = { open = false },
            confirmButton = {
                TextButton(onClick = {
                    onPick("%02d:%02d".format(state.hour, state.minute))
                    open = false
                }) { Text("OK", color = cs.primary) }
            },
            dismissButton = {
                TextButton(onClick = { open = false }) { Text("キャンセル", color = t.inkSub) }
            },
            text = { TimePicker(state = state) },
            containerColor = t.paper,
        )
    }
}
