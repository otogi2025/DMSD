package jp.tomoshibi.android.nav

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import jp.tomoshibi.android.ui.screens.account.AccountScreen
import jp.tomoshibi.android.ui.screens.announcements.*
import jp.tomoshibi.android.ui.screens.applications.*
import jp.tomoshibi.android.ui.screens.bus.BusListScreen
import jp.tomoshibi.android.ui.screens.community.*
import jp.tomoshibi.android.ui.screens.deduction.DeductionScreen
import jp.tomoshibi.android.ui.screens.home.HomeScreen
import jp.tomoshibi.android.ui.screens.login.*
import jp.tomoshibi.android.ui.screens.mypage.*
import jp.tomoshibi.android.ui.screens.nfc.NfcScreen
import jp.tomoshibi.android.ui.screens.notifications.NotifDetailScreen
import jp.tomoshibi.android.ui.screens.notifications.NotificationsScreen
import jp.tomoshibi.android.ui.screens.onboarding.OnboardingScreen
import jp.tomoshibi.android.ui.screens.rollcall.RollCallScreen
import jp.tomoshibi.android.ui.screens.splash.SplashScreen
import jp.tomoshibi.android.ui.screens.welcome.WelcomeScreen

// NavHost — 22 个 destination
// 转场动画对应 React app-shell.jsx slide / fade / modal
@Composable
fun TomoshibiNavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Route.Splash.path,
        // BottomTab 切换 + 屏间 push/pop 全部用 fade — iOS 风格的 cross-fade
        // (原 horizontal slide 在 tab 切换时太重，被 itsuki 反馈"不好看")
        enterTransition = { fadeIn(tween(220)) },
        exitTransition = { fadeOut(tween(180)) },
        popEnterTransition = { fadeIn(tween(220)) },
        popExitTransition = { fadeOut(tween(180)) },
    ) {
        // ── auth flow ─────────────
        composable(Route.Splash.path) { SplashScreen(navController) }
        composable(Route.Onboarding.path) { OnboardingScreen(navController) }
        composable(Route.Account.path) { AccountScreen(navController) }
        composable(Route.Welcome.path) { WelcomeScreen(navController) }
        composable(Route.Login.path) { LoginScreen(navController) }

        // ── core 5 tab ────────────
        composable(Route.Home.path) { HomeScreen(navController) }
        composable(Route.Applications.path) { ApplicationsScreen(navController) }
        composable(
            route = Route.Nfc.path,
            enterTransition = { slideInVertically(tween(320)) { it } + fadeIn(tween(280)) },
            exitTransition = { fadeOut(tween(200)) },
            popExitTransition = { slideOutVertically(tween(320)) { it } + fadeOut(tween(280)) },
        ) { NfcScreen(navController) }
        composable(Route.Notifications.path) { NotificationsScreen(navController) }
        composable(Route.MyPage.path) { MyPageScreen(navController) }

        // ── second-level ──────────
        composable(Route.ApplyNewSelect.path) { ApplyNewSelectScreen(navController) }
        composable(
            route = Route.ApplyNew.PATH,
            arguments =
                listOf(
                    navArgument(Route.ApplyNew.ARG_KIND) {
                        type = NavType.StringType
                        defaultValue = "外泊"
                    },
                ),
        ) { entry ->
            val kind = entry.arguments?.getString(Route.ApplyNew.ARG_KIND) ?: "外泊"
            ApplyNewScreen(navController, kind = kind)
        }
        composable(
            route = Route.ApplicationDetail.PATH,
            arguments = listOf(navArgument(Route.ApplicationDetail.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = entry.arguments?.getString(Route.ApplicationDetail.ARG_ID) ?: ""
            ApplicationDetailScreen(navController, id)
        }
        composable(
            route = Route.NotifDetail.PATH,
            arguments = listOf(navArgument(Route.NotifDetail.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = entry.arguments?.getString(Route.NotifDetail.ARG_ID) ?: ""
            NotifDetailScreen(navController, id)
        }
        composable(Route.Deduction.path) { DeductionScreen(navController) }
        composable(Route.RollCall.path) { RollCallScreen(navController) }

        // ── 个人页（「マイページ」）13 子页 ────
        composable(Route.MyInfo.path) { MyInfoScreen(navController) }
        composable(Route.MyInfoEdit.path) { MyInfoEditScreen(navController) }
        composable(Route.MyRollcall.path) { MyRollcallScreen(navController) }
        composable(
            route = Route.MyRollcallDetail.PATH,
            arguments = listOf(navArgument(Route.MyRollcallDetail.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = Route.MyRollcallDetail.parseId(entry.arguments?.getString(Route.MyRollcallDetail.ARG_ID))
            MyRollcallDetailScreen(navController, id)
        }
        composable(Route.MyPoints.path) { MyPointsScreen(navController) }
        composable(Route.MyPointsChart.path) { MyPointsChartScreen(navController) }
        composable(Route.MyDiscipline.path) { MyDisciplineScreen(navController) }
        composable(Route.MyHealth.path) { MyHealthScreen(navController) }
        composable(Route.MyPackages.path) { MyPackagesScreen(navController) }
        composable(Route.MyStudy.path) { MyStudyScreen(navController) }
        composable(Route.MySettings.path) { MySettingsScreen(navController) }
        composable(Route.MyAbout.path) { MyAboutScreen(navController) }

        // ── 杂项 / 公告 / 认证补全 ────
        composable(Route.BusList.path) { BusListScreen(navController) }
        composable(
            route = Route.PackageDetail.PATH,
            arguments = listOf(navArgument(Route.PackageDetail.ARG_ID) { type = NavType.IntType }),
        ) { entry ->
            val id = entry.arguments?.getInt(Route.PackageDetail.ARG_ID) ?: 0
            PackageDetailScreen(navController, id)
        }
        composable(Route.Announcements.path) { AnnouncementsScreen(navController) }
        composable(
            route = Route.Announcement.PATH,
            arguments = listOf(navArgument(Route.Announcement.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = entry.arguments?.getString(Route.Announcement.ARG_ID) ?: ""
            AnnouncementDetailScreen(navController, id)
        }
        composable(Route.PwReset.path) { PwResetScreen(navController) }
        composable(Route.MusicNew.path) { MusicNewScreen(navController) }
        composable(
            route = Route.MusicDetail.PATH,
            arguments = listOf(navArgument(Route.MusicDetail.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = entry.arguments?.getString(Route.MusicDetail.ARG_ID) ?: ""
            MusicDetailScreen(navController, id)
        }
        composable(
            route = Route.EventDetail.PATH,
            arguments = listOf(navArgument(Route.EventDetail.ARG_ID) { type = NavType.IntType }),
        ) { entry ->
            val id = entry.arguments?.getInt(Route.EventDetail.ARG_ID) ?: 0
            EventDetailScreen(navController, id)
        }

        // ── community 5 屏 ────────
        composable(Route.Music.path) { MusicScreen(navController) }
        composable(Route.LostFound.path) { LostFoundScreen(navController) }
        composable(Route.Schedule.path) { ScheduleScreen(navController) }
        composable(Route.Bus.path) { BusScreen(navController) }
        composable(Route.Delivery.path) { DeliveryScreen(navController) }

        // ── 申請履歴 family（老師38条#5）────
        composable(Route.StayList.path) { StayListScreen(navController) }
        composable(
            route = Route.StayDetail.PATH,
            arguments = listOf(navArgument(Route.StayDetail.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = entry.arguments?.getString(Route.StayDetail.ARG_ID) ?: ""
            StayDetailScreen(navController, id)
        }
        composable(
            route = Route.StayEdit.PATH,
            arguments = listOf(navArgument(Route.StayEdit.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = entry.arguments?.getString(Route.StayEdit.ARG_ID) ?: ""
            StayEditScreen(navController, id)
        }

        // ── 4 类型申請一覧 ────
        composable(Route.DormEventList.path) { DormEventListScreen(navController) }
        composable(Route.StudyOnlineList.path) { StudyOnlineListScreen(navController) }
        composable(Route.FridgeList.path) { FridgeListScreen(navController) }
        composable(Route.ItemList.path) { ItemListScreen(navController) }

        // ── 遺失物投稿/詳細 + 本周活动列表 ────
        composable(Route.LostNew.path) { LostNewScreen(navController) }
        composable(
            route = Route.LostDetail.PATH,
            arguments = listOf(navArgument(Route.LostDetail.ARG_ID) { type = NavType.StringType }),
        ) { entry ->
            val id = entry.arguments?.getString(Route.LostDetail.ARG_ID) ?: ""
            LostDetailScreen(navController, id)
        }
        composable(Route.Events.path) { EventsScreen(navController) }
    }
}
