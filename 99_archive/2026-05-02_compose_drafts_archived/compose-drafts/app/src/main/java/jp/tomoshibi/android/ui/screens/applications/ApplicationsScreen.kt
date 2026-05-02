package jp.tomoshibi.android.ui.screens.applications

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import jp.tomoshibi.android.data.model.ApplicationStatus
import jp.tomoshibi.android.data.seed.MockData
import jp.tomoshibi.android.data.store.LocalAppStore
import jp.tomoshibi.android.nav.Route
import jp.tomoshibi.android.ui.components.BottomTabs
import jp.tomoshibi.android.ui.theme.SuzuT

@Composable
fun ApplicationsScreen(navController: NavHostController) {
    val tokens = SuzuT.current
    val store = LocalAppStore.current
    val state by store.state.collectAsState(initial = MockData.INITIAL_STATE)
    var filter by remember { mutableStateOf("all") }

    val filtered = state.applications.filter { app ->
        when (filter) {
            "all" -> true
            "pending" -> app.status == ApplicationStatus.PENDING
            "approved" -> app.status == ApplicationStatus.APPROVED
            "rejected" -> app.status == ApplicationStatus.REJECTED || app.status == ApplicationStatus.RETURNED
            else -> true
        }
    }

    Column(modifier = Modifier.fillMaxSize().background(tokens.pearl)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(top = 24.dp, bottom = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("申請", color = tokens.ink, modifier = Modifier.weight(1f),
                style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold))
            Box(
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(tokens.btnGrad)
                    .clickable { navController.navigate(Route.ApplyNew.path) },
                contentAlignment = Alignment.Center
            ) {
                Text("+", color = Color.White,
                    style = TextStyle(fontSize = 22.sp, fontWeight = FontWeight.Bold))
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).padding(bottom = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("all" to "すべて", "pending" to "審査中", "approved" to "承認済", "rejected" to "却下/差戻").forEach { (k, l) ->
                val active = filter == k
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(99.dp))
                        .background(if (active) tokens.ink else tokens.paper)
                        .then(if (active) Modifier else Modifier.border(1.dp, tokens.hair, RoundedCornerShape(99.dp)))
                        .clickable { filter = k }
                        .padding(horizontal = 14.dp, vertical = 8.dp)
                ) {
                    Text(l,
                        color = if (active) tokens.pearl else tokens.inkSub,
                        style = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.SemiBold))
                }
            }
        }

        Column(
            modifier = Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()).padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            if (filtered.isEmpty()) {
                Box(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 60.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("該当する申請はありません", color = tokens.inkMute,
                        style = TextStyle(fontSize = 14.sp))
                }
            }
            filtered.forEach { app ->
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(tokens.paper)
                        .clickable { navController.navigate("applications/${app.id}") }
                        .padding(16.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(tokens.pill)
                                .padding(horizontal = 8.dp, vertical = 2.dp)
                        ) {
                            Text(app.kind, color = tokens.ink,
                                style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
                        }
                        Spacer(Modifier.width(8.dp))
                        StatusPill(app.status)
                        Spacer(Modifier.weight(1f))
                        Text("#${app.id}", color = tokens.inkMute, style = TextStyle(fontSize = 11.sp))
                    }
                    Spacer(Modifier.height(8.dp))
                    Text(app.dest, color = tokens.ink,
                        style = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Bold))
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = if (app.from == app.to) app.from else "${app.from} 〜 ${app.to}",
                        color = tokens.inkSub,
                        style = TextStyle(fontSize = 13.sp)
                    )
                }
            }
            Spacer(Modifier.height(20.dp))
        }

        BottomTabs(navController = navController, active = "apply")
    }
}

@Composable
private fun StatusPill(status: ApplicationStatus) {
    val tokens = SuzuT.current
    val (label, bg, fg) = when (status) {
        ApplicationStatus.PENDING -> Triple("審査中", tokens.warnBg, tokens.warnDeep)
        ApplicationStatus.APPROVED -> Triple("承認済", tokens.okBg, tokens.okDeep)
        ApplicationStatus.RETURNED -> Triple("要修正", tokens.dangerBg, tokens.danger)
        ApplicationStatus.REJECTED -> Triple("却下", tokens.dangerBg, tokens.danger)
    }
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(6.dp))
            .background(bg)
            .padding(horizontal = 8.dp, vertical = 2.dp)
    ) {
        Text(label, color = fg,
            style = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold))
    }
}
