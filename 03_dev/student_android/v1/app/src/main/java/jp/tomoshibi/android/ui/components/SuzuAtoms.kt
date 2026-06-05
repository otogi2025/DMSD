package jp.tomoshibi.android.ui.components

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
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
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
@Composable
fun SuzuCard(
    modifier: Modifier = Modifier,
    padding: Int = 14,
    radius: Int = 16,
    content: @Composable () -> Unit,
) {
    val t = SuzuT.current
    Column(
        modifier =
            modifier
                .fillMaxWidth()
                .shadow(
                    elevation = 4.dp,
                    shape = RoundedCornerShape(radius.dp),
                    ambientColor = t.ink,
                    spotColor = t.ink,
                ).clip(RoundedCornerShape(radius.dp))
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

// 4.14 TToggle — iOS 开关（激活色 primary）
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

// 4.16 PageHeader — 子页统一头部（左键按 level 切 home/返回、标题 17 bold、长按弹面包屑）
// 回调 hoisted：onLeft = level1 回首页 / level2+ 返回；onLongPress = 弹面包屑
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun PageHeader(
    title: String,
    modifier: Modifier = Modifier,
    level: Int = 2,
    onLeft: () -> Unit,
    onLongPress: () -> Unit = {},
    right: (@Composable () -> Unit)? = null,
) {
    val t = SuzuT.current
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
                    .combinedClickable(onClick = onLeft, onLongClick = onLongPress),
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
        Spacer(Modifier.weight(1f))
        if (right != null) right()
    }
}
