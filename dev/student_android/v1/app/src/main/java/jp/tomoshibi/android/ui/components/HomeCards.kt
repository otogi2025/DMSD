package jp.tomoshibi.android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import jp.tomoshibi.android.ui.icons.SuzuIcons
import jp.tomoshibi.android.ui.theme.SuzuT

// API 契约:
//   icon: 左侧 icon
//   iconBg: icon 容器背景色（一般 SuzuT.current.pill / accent / btnGrad 用 paper）
//   title: 主标题（14sp semibold）
//   subtitle: 副标题（11sp inkMute），可空
//   badge: 数字 badge（红圆，右侧），可空
//   onClick: 整 row 点击
//
// Stage 0 已实装可用 — Session B Home omnibus 各 section 调用本组件
@Composable
fun SectionCard(
    icon: ImageVector,
    iconBg: Color,
    title: String,
    subtitle: String? = null,
    badge: Int? = null,
    iconTint: Color = Color.White,
    onClick: () -> Unit,
) {
    val t = SuzuT.current
    Row(
        modifier =
            Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(18.dp))
                .background(t.paper)
                .clickable(onClick = onClick)
                .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier =
                Modifier
                    .size(40.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(iconBg),
            contentAlignment = Alignment.Center,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = iconTint,
                modifier = Modifier.size(20.dp),
            )
        }
        Spacer(modifier = Modifier.width(12.dp))
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                color = t.ink,
                style = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold),
            )
            if (subtitle != null) {
                Text(
                    text = subtitle,
                    color = t.inkMute,
                    style = TextStyle(fontSize = 11.sp),
                )
            }
        }
        if (badge != null) {
            Box(
                modifier =
                    Modifier
                        .size(20.dp)
                        .clip(CircleShape)
                        .background(t.danger),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "$badge",
                    color = Color.White,
                    style = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.Bold),
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
        }
        Icon(
            imageVector = SuzuIcons.ChevR,
            contentDescription = null,
            tint = t.inkMute,
            modifier = Modifier.size(16.dp),
        )
    }
}
