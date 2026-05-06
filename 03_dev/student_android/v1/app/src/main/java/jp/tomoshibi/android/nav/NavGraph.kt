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
import jp.tomoshibi.android.ui.screens.applications.ApplicationDetailScreen
import jp.tomoshibi.android.ui.screens.applications.ApplicationsScreen
import jp.tomoshibi.android.ui.screens.applications.ApplyNewScreen
import jp.tomoshibi.android.ui.screens.community.*
import jp.tomoshibi.android.ui.screens.deduction.DeductionScreen
import jp.tomoshibi.android.ui.screens.home.HomeScreen
import jp.tomoshibi.android.ui.screens.login.LoginScreen
import jp.tomoshibi.android.ui.screens.mypage.MyPageScreen
import jp.tomoshibi.android.ui.screens.mypage.SettingsScreen
import jp.tomoshibi.android.ui.screens.nfc.NfcScreen
import jp.tomoshibi.android.ui.screens.notifications.NotifDetailScreen
import jp.tomoshibi.android.ui.screens.notifications.NotificationsScreen
import jp.tomoshibi.android.ui.screens.onboarding.OnboardingScreen
import jp.tomoshibi.android.ui.screens.rollcall.RollCallScreen
import jp.tomoshibi.android.ui.screens.splash.SplashScreen
import jp.tomoshibi.android.ui.screens.welcome.WelcomeScreen

// NavHost — 23 个 destination
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
        popExitTransition = { fadeOut(tween(180)) }
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
            popExitTransition = { slideOutVertically(tween(320)) { it } + fadeOut(tween(280)) }
        ) { NfcScreen(navController) }
        composable(Route.Notifications.path) { NotificationsScreen(navController) }
        composable(Route.MyPage.path) { MyPageScreen(navController) }

        // ── second-level ──────────
        composable(
            route = Route.ApplyNew.PATH,
            arguments = listOf(navArgument(Route.ApplyNew.ARG_KIND) {
                type = NavType.StringType
                defaultValue = "外泊"
            })
        ) { entry ->
            val kind = entry.arguments?.getString(Route.ApplyNew.ARG_KIND) ?: "外泊"
            ApplyNewScreen(navController, kind = kind)
        }
        composable(
            route = Route.ApplicationDetail.PATH,
            arguments = listOf(navArgument(Route.ApplicationDetail.ARG_ID) { type = NavType.StringType })
        ) { entry ->
            val id = entry.arguments?.getString(Route.ApplicationDetail.ARG_ID) ?: ""
            ApplicationDetailScreen(navController, id)
        }
        composable(
            route = Route.NotifDetail.PATH,
            arguments = listOf(navArgument(Route.NotifDetail.ARG_ID) { type = NavType.StringType })
        ) { entry ->
            val id = entry.arguments?.getString(Route.NotifDetail.ARG_ID) ?: ""
            NotifDetailScreen(navController, id)
        }
        composable(Route.Deduction.path) { DeductionScreen(navController) }
        composable(Route.RollCall.path) { RollCallScreen(navController) }
        composable(Route.Settings.path) { SettingsScreen(navController) }

        // ── community 7 屏 ────────
        composable(Route.Music.path) { MusicScreen(navController) }
        composable(Route.Study.path) { StudyScreen(navController) }
        composable(Route.LostFound.path) { LostFoundScreen(navController) }
        composable(Route.Schedule.path) { ScheduleScreen(navController) }
        composable(Route.Feedback.path) { FeedbackScreen(navController) }
        composable(Route.Bus.path) { BusScreen(navController) }
        composable(Route.Delivery.path) { DeliveryScreen(navController) }
    }
}
