package jp.tomoshibi.android.data.store

import android.content.Context
import android.util.Log
import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import jp.tomoshibi.android.BuildConfig
import jp.tomoshibi.android.data.format.JstDate
import jp.tomoshibi.android.data.model.AppState
import jp.tomoshibi.android.data.model.ChangeLogEntry
import jp.tomoshibi.android.data.model.ListLoadState
import jp.tomoshibi.android.data.model.Notification
import jp.tomoshibi.android.data.model.RollState
import jp.tomoshibi.android.data.model.StudyState
import jp.tomoshibi.android.data.model.User
import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.ApiError
import jp.tomoshibi.android.data.network.ApiErrorPresenter
import jp.tomoshibi.android.data.network.StudentNotificationItem
import jp.tomoshibi.android.data.network.endpoints.AnnouncementsAPI
import jp.tomoshibi.android.data.network.endpoints.CleaningAPI
import jp.tomoshibi.android.data.network.endpoints.CleaningAssignmentOut
import jp.tomoshibi.android.data.network.endpoints.DisciplineAPI
import jp.tomoshibi.android.data.network.endpoints.FrontDeskAPI
import jp.tomoshibi.android.data.network.endpoints.FrontDeskItemOut
import jp.tomoshibi.android.data.network.endpoints.MyRollCallTodaySession
import jp.tomoshibi.android.data.network.endpoints.ProfileDemeritEntry
import jp.tomoshibi.android.data.network.endpoints.ProfileRollCallEntry
import jp.tomoshibi.android.data.network.endpoints.RollCallAPI
import jp.tomoshibi.android.data.network.endpoints.StudentMeOut
import jp.tomoshibi.android.data.network.endpoints.StudentNotificationsAPI
import jp.tomoshibi.android.data.network.endpoints.StudentProfileAPI
import jp.tomoshibi.android.data.network.endpoints.StudentsAPI
import jp.tomoshibi.android.data.network.endpoints.StudyAPI
import jp.tomoshibi.android.data.notifications.NotificationMapper
import jp.tomoshibi.android.data.notifications.NotificationsLoadState
import jp.tomoshibi.android.data.rollcall.RollSession
import jp.tomoshibi.android.data.rollcall.RollStateMachine
import jp.tomoshibi.android.data.seed.MockData
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.time.Instant

// AppStore — 对应 React StoreProvider + iOS AppStore 的会话层。
// 把整个 AppState JSON 序列化存进 DataStore Preferences 一个 key
// （比拆 30+ keys 简单，性能也够 — v1.0 数据量 < 100KB）
//
// 令牌例外：authToken 单独走 SecureTokenStore（EncryptedSharedPreferences），
// DataStore JSON 不再落明文 JWT。对齐 iOS KeychainService。
//
// 会话方法（对齐 iOS AppStore.swift）：
//   setAuthToken / clearSession / handleIfUnauthorized / loadMe / restoreSessionIfNeeded

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "tomoshibi-app-state-v1",
)

private val APP_STATE_KEY = stringPreferencesKey("app_state_json")

// 共享 JSON 编解码器。ignoreUnknownKeys = 解码时忽略 JSON 里有、但 AppState 已删掉的字段，
// 这样删字段后老用户本地存档不会解析失败回落、丢掉其余本地数据。
// internal（非 private）：TokenRoundtripTest 直接用这份真配置做往返测试。
internal val appJson = Json { ignoreUnknownKeys = true }

class AppStore(
    private val context: Context,
) {
    private val tokenStore = SecureTokenStore(context)

    // 启动时异步：旧版 DataStore JSON 里若还有明文 authToken → 写入加密存储 → 删明文
    private val migrateScope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    // UI 瞬时态（toast / 面包屑）用主线程 scope，不落盘
    private val uiScope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

    // 今日点呼场次缓存（对齐 iOS todaySessions）— 内存态，供每秒 tickCountdown 重算，不落盘
    private var cachedRollSessions: List<RollSession> = emptyList()

    // 每秒刷新点呼状态（对齐 iOS HomeView countdownTimer → tickCountdown）
    private var rollTickJob: Job? = null

    // ── 全局 Toast（对齐 iOS AppStore.toast / showToast，2.2 秒自动清）──
    private val _toast = MutableStateFlow<String?>(null)
    val toast: StateFlow<String?> = _toast.asStateFlow()
    private var toastGeneration: Int = 0
    private var toastClearJob: Job? = null

    // ── 面包屑弹窗开关（对齐 iOS AppStore.breadcrumbOpen）──
    private val _breadcrumbOpen = MutableStateFlow(false)
    val breadcrumbOpen: StateFlow<Boolean> = _breadcrumbOpen.asStateFlow()

    // ── 通知中心内存态（对齐 iOS @Published；不落 DataStore，防 SEED 假通知泄漏）──
    private val _studentNotifications = MutableStateFlow<List<StudentNotificationItem>>(emptyList())
    val studentNotifications: StateFlow<List<StudentNotificationItem>> = _studentNotifications.asStateFlow()

    private val _packages = MutableStateFlow<List<FrontDeskItemOut>>(emptyList())
    val packages: StateFlow<List<FrontDeskItemOut>> = _packages.asStateFlow()

    // Android 暂无真实推送入库；预留空列表，聚合公式与 iOS 一致。
    private val _pushNotifications = MutableStateFlow<List<Notification>>(emptyList())
    val pushNotifications: StateFlow<List<Notification>> = _pushNotifications.asStateFlow()

    private val _notificationsState =
        MutableStateFlow<NotificationsLoadState>(NotificationsLoadState.Idle)
    val notificationsState: StateFlow<NotificationsLoadState> = _notificationsState.asStateFlow()

    // ── 个人页：点呼/减点聚合、罚扫履历、变更履历（内存态，对齐 iOS @Published）──
    private val _myRollcallEvents = MutableStateFlow<List<ProfileRollCallEntry>>(emptyList())
    val myRollcallEvents: StateFlow<List<ProfileRollCallEntry>> = _myRollcallEvents.asStateFlow()

    private val _myDemeritEvents = MutableStateFlow<List<ProfileDemeritEntry>>(emptyList())
    val myDemeritEvents: StateFlow<List<ProfileDemeritEntry>> = _myDemeritEvents.asStateFlow()

    private val _profileState = MutableStateFlow<ListLoadState>(ListLoadState.Idle)
    val profileState: StateFlow<ListLoadState> = _profileState.asStateFlow()

    private val _cleaningHistory = MutableStateFlow<List<CleaningAssignmentOut>>(emptyList())
    val cleaningHistory: StateFlow<List<CleaningAssignmentOut>> = _cleaningHistory.asStateFlow()

    private val _cleaningHistoryState = MutableStateFlow<ListLoadState>(ListLoadState.Idle)
    val cleaningHistoryState: StateFlow<ListLoadState> = _cleaningHistoryState.asStateFlow()

    private val _changeLog = MutableStateFlow<List<ChangeLogEntry>>(emptyList())
    val changeLog: StateFlow<List<ChangeLogEntry>> = _changeLog.asStateFlow()

    /** 夜学习 upcoming 倒计时秒数（对齐 iOS studyCountdownSec；默认 10 分） */
    private val _studyCountdownSec = MutableStateFlow(600)
    val studyCountdownSec: StateFlow<Int> = _studyCountdownSec.asStateFlow()

    /**
     * 生产没拉到 /me 时占位（对齐 iOS profileIsPlaceholder）。
     * 已登录但 myStudentId 仍空 → 点数等应显「—」而非假 0。
     */
    fun isProfilePlaceholder(snap: AppState): Boolean = snap.authed && snap.myStudentId == null

    /** 三源聚合快照（对齐 iOS allNotifications）。 */
    fun currentAllNotifications(): List<Notification> =
        NotificationMapper.allNotifications(
            _pushNotifications.value,
            _studentNotifications.value,
            _packages.value,
        )

    /** 铃铛未読数快照（对齐 iOS unreadNotificationCount）。 */
    suspend fun currentUnreadNotificationCount(): Int {
        val fallback = snapshot().studentNotificationUnreadCount
        return NotificationMapper.unreadCount(
            _pushNotifications.value,
            _studentNotifications.value,
            fallback,
            _packages.value,
        )
    }

    /** 显示全局 Toast；连续调用时旧定时器不会清掉新文案（代次令牌）。 */
    fun showToast(text: String) {
        toastGeneration += 1
        val gen = toastGeneration
        _toast.value = text
        toastClearJob?.cancel()
        toastClearJob =
            uiScope.launch {
                delay(2200)
                if (toastGeneration == gen) {
                    _toast.value = null
                }
            }
    }

    fun openBreadcrumb() {
        _breadcrumbOpen.value = true
    }

    fun closeBreadcrumb() {
        _breadcrumbOpen.value = false
    }

    init {
        migrateScope.launch {
            migratePlainTokenIfNeeded()
        }
    }

    val state: Flow<AppState> =
        context.dataStore.data.map { prefs ->
            val decoded = decodePrefs(prefs)
            // 读路径也做一次同步迁移（EncryptedSharedPreferences 是同步 API），
            // 保证 Splash 自动登录在异步 migrate 完成前也能拿到 token。
            val plain = decoded.authToken
            if (!plain.isNullOrEmpty() && tokenStore.get() == null) {
                tokenStore.save(plain)
            }
            decoded.copy(authToken = tokenStore.get())
        }

    suspend fun update(transform: (AppState) -> AppState) {
        context.dataStore.edit { prefs ->
            val current = decodePrefs(prefs).copy(authToken = tokenStore.get())
            val next = transform(current)
            // token 单独加密存；DataStore JSON 永不落明文
            if (next.authToken.isNullOrEmpty()) {
                tokenStore.clear()
            } else if (next.authToken != tokenStore.get()) {
                // 值没变不重存——AES-GCM 随机 IV 会让同值重存也产生新密文、真实落盘（R1-Grok#5）。
                tokenStore.save(next.authToken)
            }
            prefs[APP_STATE_KEY] = appJson.encodeToString(next.copy(authToken = null))
        }
    }

    suspend fun reset() {
        tokenStore.clear()
        ApiClient.token = null
        context.dataStore.edit { it.remove(APP_STATE_KEY) }
    }

    suspend fun snapshot(): AppState {
        migratePlainTokenIfNeeded()
        return state.first()
    }

    // ── 会话：存令牌 + 过期时刻（对齐 iOS setAuthToken）────────────────

    /** 登录 / 注册成功后调：写令牌、过期绝对时刻、同步 ApiClient。 */
    suspend fun setAuthToken(
        token: String,
        expiresIn: Int,
    ) {
        val expiresAt = System.currentTimeMillis() + expiresIn * 1000L
        ApiClient.token = token
        update {
            it.copy(
                authed = true,
                authToken = token,
                tokenExpiresAtEpochMs = expiresAt,
            )
        }
    }

    /**
     * 清会话（登出 / 401 / 令牌过期）。
     * 对齐 iOS authToken=nil 的 didSet：清 Keychain + currentUser + 用户绑定字段。
     */
    suspend fun clearSession() {
        stopRollTicker()
        cachedRollSessions = emptyList()
        ApiClient.token = null
        update { current ->
            current.copy(
                authed = false,
                authToken = null,
                tokenExpiresAtEpochMs = null,
                myStudentId = null,
                needsRenewal = false,
                studyLeaveCountThisMonth = 0,
                announcementUnreadCount = 0,
                studentNotificationUnreadCount = 0,
                checkinKind = null,
                user = MockData.DEFAULT_USER,
                rollState = RollState.IDLE,
                rollCountdownSec = 170,
                checkinAt = null,
                studyState = StudyState.OFF,
            )
        }
        // 清通知中心 / 个人页内存态，防 A 登出 B 登入看到旧数据
        _studentNotifications.value = emptyList()
        _packages.value = emptyList()
        _pushNotifications.value = emptyList()
        _notificationsState.value = NotificationsLoadState.Idle
        _myRollcallEvents.value = emptyList()
        _myDemeritEvents.value = emptyList()
        _profileState.value = ListLoadState.Idle
        _cleaningHistory.value = emptyList()
        _cleaningHistoryState.value = ListLoadState.Idle
        _changeLog.value = emptyList()
        _studyCountdownSec.value = 600
    }

    /**
     * 启动恢复会话：有令牌且未过期 → 同步 ApiClient 并返回 true；
     * 已过期 → 清令牌不恢复，返回 false（对齐 iOS AppStore.init IX-036）。
     * 没存过期时刻的旧令牌 → 保守恢复，由后续 401 兜底。
     */
    suspend fun restoreSessionIfNeeded(): Boolean {
        migratePlainTokenIfNeeded()
        val snap = snapshot()
        val token = snap.authToken
        if (token.isNullOrEmpty()) {
            ApiClient.token = null
            if (snap.authed) {
                update { it.copy(authed = false) }
            }
            return false
        }
        val expiry = snap.tokenExpiresAtEpochMs
        if (expiry != null && System.currentTimeMillis() >= expiry) {
            clearSession()
            return false
        }
        ApiClient.token = token
        if (!snap.authed) {
            update { it.copy(authed = true) }
        }
        return true
    }

    /**
     * 集中处理 401：比对进入时令牌后清会话。
     * @return true = 是 401（已尝试清令牌，调用方应 return）；false = 非 401。
     */
    suspend fun handleIfUnauthorized(
        error: Throwable,
        tokenAtStart: String?,
    ): Boolean {
        if (error !is ApiError.Unauthorized) return false
        val current = snapshot().authToken
        // 只在仍是当初那个登录令牌时才清，防误踢已换上的新用户（对齐 iOS IX-034）。
        if (current == tokenAtStart) {
            clearSession()
        }
        return true
    }

    // ── loadMe 级联（对齐 iOS AppStore.loadMe）────────────────────────

    /**
     * 登录成功 / 启动恢复令牌后调。
     * GET /students/me → 扣分汇总 → 夜学習欠席次数 → 公告未読 → 学生通知 → 今日点呼 → 罚扫。
     * 401 → 清令牌；其余错误静默（保留占位 user，不打断登录）。
     */
    suspend fun loadMe() {
        val tokenAtStart = snapshot().authToken ?: return
        try {
            val me = StudentsAPI.me()
            if (snapshot().authToken != tokenAtStart) return

            var mapped = SessionMapper.mapMeToUser(me)

            // 当月扣分汇总（拉不到保持 0，不打断）
            try {
                val summary = DisciplineAPI.mySummary()
                if (snapshot().authToken != tokenAtStart) return
                mapped =
                    mapped.copy(
                        points = summary.totalPoints,
                        lateCount = summary.lateCount,
                        absentCount = summary.absentCount,
                        needsCleaning = summary.needsCleaning ?: (summary.totalPoints >= 4.0),
                    )
            } catch (e: ApiError.Unauthorized) {
                handleIfUnauthorized(e, tokenAtStart)
                return
            } catch (_: Exception) {
                // 静默
            }

            // 当月夜学習欠席届次数
            var absenceCount: Int? = null
            try {
                absenceCount = StudyAPI.myAbsenceSummary().count
            } catch (e: ApiError.Unauthorized) {
                handleIfUnauthorized(e, tokenAtStart)
                return
            } catch (_: Exception) {
                // 静默
            }

            if (snapshot().authToken != tokenAtStart) return

            update { current ->
                current.copy(
                    user = mapped,
                    myStudentId = me.id,
                    needsRenewal = me.needsRenewal ?: false,
                    studyLeaveCountThisMonth = absenceCount ?: current.studyLeaveCountThisMonth,
                )
            }

            // 以下级联：各自吞非 401；401 统一清会话
            loadAnnouncementUnreadCount(tokenAtStart)
            loadStudentNotifications(tokenAtStart, reflectFailure = false)
            loadMyPackages(tokenAtStart, reflectFailure = false)
            loadTodayRollcall(tokenAtStart)
            loadCleaningHistoryQuiet(tokenAtStart)
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, tokenAtStart)
        } catch (e: Exception) {
            // 生产包不打日志（对齐 iOS §22.2：Release 不把后端错误细节写进系统日志）
            if (BuildConfig.DEBUG) {
                Log.w("AppStore", "loadMe /students/me 失败（保留占位）", e)
            }
        }
    }

    private suspend fun loadAnnouncementUnreadCount(tokenAtStart: String?) {
        try {
            val count = AnnouncementsAPI.unreadCount().unreadCount
            if (snapshot().authToken != tokenAtStart) return
            update { it.copy(announcementUnreadCount = count) }
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, tokenAtStart)
        } catch (_: Exception) {
            // 静默
        }
    }

    /**
     * 拉学生通知 feed（items + 未読数）。
     * @param reflectFailure true = 写失败态给通知中心 UI；false = loadMe 级联静默（不打断首屏）。
     */
    suspend fun loadStudentNotifications(
        tokenAtStart: String? = null,
        reflectFailure: Boolean = true,
    ) {
        val token = tokenAtStart ?: snapshot().authToken
        if (reflectFailure) {
            _notificationsState.value = NotificationsLoadState.Loading
        }
        try {
            val feed = StudentNotificationsAPI.feed()
            if (snapshot().authToken != token) return
            _studentNotifications.value = feed.items
            update { it.copy(studentNotificationUnreadCount = feed.unreadCount) }
            if (reflectFailure) {
                _notificationsState.value = NotificationsLoadState.Loaded
            }
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, token)
        } catch (e: ApiError) {
            if (snapshot().authToken != token) return
            if (reflectFailure) {
                _notificationsState.value =
                    NotificationsLoadState.Failed(e.display.ifBlank { "通知の取得に失敗しました" })
            }
        } catch (e: Exception) {
            if (snapshot().authToken != token) return
            if (reflectFailure) {
                _notificationsState.value =
                    NotificationsLoadState.Failed("通知の取得に失敗しました")
            }
        }
    }

    /**
     * 拉当前学生包裹（通知中心「宅配」源）。
     * @param reflectFailure 包裹失败不单独盖通知中心态（对齐 iOS：只动 packagesState）；
     *   这里 Android 通知中心以 feed 态为准，包裹失败时保留旧缓存。
     */
    suspend fun loadMyPackages(
        tokenAtStart: String? = null,
        reflectFailure: Boolean = true,
    ) {
        val token = tokenAtStart ?: snapshot().authToken
        try {
            val items = FrontDeskAPI.listMine()
            if (snapshot().authToken != token) return
            _packages.value = items
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, token)
        } catch (_: Exception) {
            // 包裹失败不盖写通知中心 feed 态；旧缓存保留
            if (!reflectFailure) {
                // loadMe 级联静默
            }
        }
    }

    /** 宅配屏拉到列表后写回缓存（避免重复请求）。 */
    fun replacePackages(items: List<FrontDeskItemOut>) {
        _packages.value = items
    }

    /** 进入通知中心时刷新三源（feed + 包裹）。 */
    suspend fun refreshNotificationSources() {
        val tokenAtStart = snapshot().authToken
        loadStudentNotifications(tokenAtStart, reflectFailure = true)
        loadMyPackages(tokenAtStart, reflectFailure = true)
    }

    /**
     * 点 feed 通知卡标已读：先调后端，成功后再翻本地（对齐 iOS markStudentNotificationRead）。
     * 找不到 / 已读 → 不发请求。非 401 失败静默。
     */
    suspend fun markStudentNotificationRead(
        kind: String,
        refId: String,
    ) {
        val tokenAtStart = snapshot().authToken
        val list = _studentNotifications.value
        val idx = list.indexOfFirst { it.kind == kind && it.refId == refId }
        if (idx < 0 || list[idx].isRead) return
        try {
            StudentNotificationsAPI.markRead(kind = kind, refId = refId)
            if (snapshot().authToken != tokenAtStart) return
            val latest = _studentNotifications.value
            val i = latest.indexOfFirst { it.kind == kind && it.refId == refId }
            if (i >= 0 && !latest[i].isRead) {
                val copy = latest.toMutableList()
                copy[i] = copy[i].copy(isRead = true)
                _studentNotifications.value = copy
                update {
                    it.copy(
                        studentNotificationUnreadCount =
                            maxOf(0, it.studentNotificationUnreadCount - 1),
                    )
                }
            }
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, tokenAtStart)
        } catch (_: Exception) {
            // 非 401：静默，下次刷新 feed 带回真实已読态
        }
    }

    private suspend fun loadTodayRollcall(tokenAtStart: String?) {
        try {
            val sessions = RollCallAPI.myToday()
            if (snapshot().authToken != tokenAtStart) return
            cachedRollSessions = mapApiSessionsToRollSessions(sessions)
            applyRollDecisionFromCache()
            startRollTicker()
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, tokenAtStart)
        } catch (_: Exception) {
            // 静默；仍开 ticker，用已有缓存（可能空）每秒重算
            startRollTicker()
        }
    }

    private suspend fun loadCleaningHistoryQuiet(tokenAtStart: String?) {
        // loadMe 级联：静默填缓存，不写失败态（个人页进入时再 loadCleaningHistory 显三态）
        try {
            val items = CleaningAPI.listMine()
            if (snapshot().authToken != tokenAtStart) return
            _cleaningHistory.value = items
            _cleaningHistoryState.value = ListLoadState.Loaded
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, tokenAtStart)
        } catch (_: Exception) {
            // 静默
        }
    }

    /**
     * 拉本人点呼 + 减点聚合（GET /students/{id}/profile）。
     * 对齐 iOS loadMyProfile：冷启动 myStudentId 为空时先补 loadMe。
     */
    suspend fun loadMyProfile() {
        val tokenAtStart = snapshot().authToken
        _profileState.value = ListLoadState.Loading
        if (snapshot().myStudentId == null) {
            loadMe()
            if (snapshot().authToken != tokenAtStart) return
        }
        val sid = snapshot().myStudentId
        if (sid == null) {
            _profileState.value = ListLoadState.Failed("学生情報の取得に失敗しました")
            return
        }
        try {
            val out = StudentProfileAPI.profile(studentId = sid)
            if (snapshot().authToken != tokenAtStart) return
            _myRollcallEvents.value = out.rollcallEvents
            _myDemeritEvents.value = out.demeritEvents
            _profileState.value = ListLoadState.Loaded
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, tokenAtStart)
        } catch (e: Exception) {
            if (snapshot().authToken != tokenAtStart) return
            _profileState.value =
                ListLoadState.Failed(
                    ApiErrorPresenter.userMessage(e, "点呼・減点情報の取得に失敗しました"),
                )
        }
    }

    /** 拉罚扫履历（对齐 iOS loadCleaningHistory；写三态给个人页）。 */
    suspend fun loadCleaningHistory() {
        val tokenAtStart = snapshot().authToken
        _cleaningHistoryState.value = ListLoadState.Loading
        try {
            val items = CleaningAPI.listMine()
            if (snapshot().authToken != tokenAtStart) return
            _cleaningHistory.value = items
            _cleaningHistoryState.value = ListLoadState.Loaded
        } catch (e: ApiError.Unauthorized) {
            handleIfUnauthorized(e, tokenAtStart)
        } catch (e: Exception) {
            if (snapshot().authToken != tokenAtStart) return
            _cleaningHistoryState.value =
                ListLoadState.Failed(
                    ApiErrorPresenter.userMessage(e, "罰則清掃の取得に失敗しました"),
                )
        }
    }

    /** 记录字段变更（before == after 则跳过；新记录插到最前）。 */
    fun appendChange(
        field: String,
        label: String,
        before: String,
        after: String,
    ) {
        if (before == after) return
        val entry = ChangeLogEntry(field = field, label = label, before = before, after = after)
        _changeLog.value = listOf(entry) + _changeLog.value
    }

    /** 本地刷新当前用户房间/邮箱/电话（PATCH 成功后）。 */
    suspend fun applyLocalUserContact(
        room: String,
        email: String,
        phone: String,
    ) {
        update { current ->
            current.copy(user = current.user.copy(room = room, email = email, phone = phone))
        }
    }

    /**
     * 每秒由 rollTicker 调（对齐 iOS tickCountdown 生产分支）：
     * 用缓存场次 + 当前时刻重算 rollState / checkinKind / 倒计时，驱动 idle→active→absent 自动流转。
     */
    suspend fun tickCountdown() {
        applyRollDecisionFromCache()
    }

    private fun startRollTicker() {
        if (rollTickJob?.isActive == true) return
        rollTickJob =
            migrateScope.launch {
                while (true) {
                    delay(1000)
                    applyRollDecisionFromCache()
                }
            }
    }

    private fun stopRollTicker() {
        rollTickJob?.cancel()
        rollTickJob = null
    }

    private fun mapApiSessionsToRollSessions(sessions: List<MyRollCallTodaySession>): List<RollSession> =
        sessions.mapNotNull { s ->
            val windowStart = SessionMapper.parseInstantMillis(s.scheduledWindowStartAt) ?: return@mapNotNull null
            val onTimeEnd = SessionMapper.parseInstantMillis(s.scheduledOnTimeEndAt) ?: return@mapNotNull null
            val lateEnd = SessionMapper.parseInstantMillis(s.scheduledLateEndAt) ?: return@mapNotNull null
            val autoEnd = SessionMapper.parseInstantMillis(s.scheduledAutoEndAt) ?: return@mapNotNull null
            RollSession(
                windowStartMillis = windowStart,
                onTimeEndMillis = onTimeEnd,
                lateEndMillis = lateEnd,
                autoEndMillis = autoEnd,
                checkedInAtMillis = s.myCheckedInAt?.let { SessionMapper.parseInstantMillis(it) },
                myStatus = s.myStatus,
            )
        }

    private suspend fun applyRollDecisionFromCache() {
        val decision = RollStateMachine.decide(cachedRollSessions, System.currentTimeMillis())
        val checkinAtText =
            decision.checkedInAtMillis?.let { ms -> JstDate.formatHm(ms) }
        // 无变化直接返回、不进 update()——否则 idle 时段也每秒重存令牌 + 写 DataStore
        // （加密存储 AES-GCM 随机 IV 让同值重存也真实落盘；三方审查 R1-Grok#5）。
        // 已知残留：ACTIVE 受付窗内倒计时每秒真变，仍每秒落盘（窗口仅数分钟/天，可接受）。
        val cur = snapshot()
        val nextCountdown = decision.countdownSec?.toInt() ?: cur.rollCountdownSec
        if (cur.rollState == decision.state &&
            cur.checkinKind == decision.checkinKind &&
            cur.checkinAt == checkinAtText &&
            cur.rollCountdownSec == nextCountdown
        ) {
            return
        }
        update { current ->
            current.copy(
                rollState = decision.state,
                checkinKind = decision.checkinKind,
                checkinAt = checkinAtText,
                rollCountdownSec = decision.countdownSec?.toInt() ?: current.rollCountdownSec,
            )
        }
    }

    // 读旧明文 → 写加密 → 删旧明文（幂等）
    private suspend fun migratePlainTokenIfNeeded() {
        context.dataStore.edit { prefs ->
            val current = decodePrefs(prefs)
            val plain = current.authToken
            if (!plain.isNullOrEmpty()) {
                if (tokenStore.get() == null) {
                    tokenStore.save(plain)
                }
                prefs[APP_STATE_KEY] = appJson.encodeToString(current.copy(authToken = null))
            }
        }
    }

    private fun decodePrefs(prefs: Preferences): AppState {
        val json = prefs[APP_STATE_KEY] ?: return MockData.INITIAL_STATE
        return try {
            appJson.decodeFromString<AppState>(json)
        } catch (e: Exception) {
            if (BuildConfig.DEBUG) {
                Log.e("AppStore", "AppState 解析失败，回落 MockData（本地数据可能丢失）", e)
            }
            MockData.INITIAL_STATE
        }
    }
}

/**
 * 纯函数：/me → User 映射。
 * 抽出来方便单测，不依赖 Android Context。
 */
object SessionMapper {
    fun mapMeToUser(me: StudentMeOut): User {
        val genderLabel = if (me.gender == "female") "女" else "男"
        val dormLabel = if (me.dormUnit == 4) "女寮" else "男寮"
        val avatarChar = me.name.take(1).ifEmpty { "？" }
        val seat = me.seatNo.toIntOrNull() ?: 0
        val grade = gradeLabel(me.gradeCode)
        val clazz = classLabel(me.classCode)
        return User(
            name = me.name,
            kana = me.nameKana.orEmpty(),
            email = me.email.orEmpty(),
            dorm = dormLabel,
            room = me.roomNo,
            avatar = avatarChar,
            studentNo = me.studentNo,
            gradeClass = "$grade ${clazz}組 ${seat}番",
            category = me.category,
            phone = me.phone.orEmpty(),
            birthDate = "",
            gender = genderLabel,
            isStudyTarget = false,
            points = 0.0,
            lateCount = 0,
            absentCount = 0,
            needsCleaning = false,
        )
    }

    fun gradeLabel(code: String): String =
        when (code) {
            "01" -> "中1"
            "02" -> "中2"
            "03" -> "中3"
            "04" -> "高1"
            "05" -> "高2"
            "06" -> "高3"
            else -> code
        }

    fun classLabel(code: String): String {
        val n = code.toIntOrNull() ?: return code
        if (n !in 1..26) return code
        return ('A' + n - 1).toString()
    }

    fun parseInstantMillis(iso: String): Long? =
        try {
            Instant.parse(iso).toEpochMilli()
        } catch (_: Exception) {
            try {
                // 后端偶发无 Z 后缀的本地时间串 → 按 UTC 解析失败时再试 OffsetDateTime
                java.time.OffsetDateTime
                    .parse(iso)
                    .toInstant()
                    .toEpochMilli()
            } catch (_: Exception) {
                null
            }
        }
}

// CompositionLocal 让任何 Composable 通过 LocalAppStore.current 拿到 AppStore 实例
// 在 Activity setContent 顶层 provide
val LocalAppStore =
    staticCompositionLocalOf<AppStore> {
        error("AppStore not provided — wrap your composable in CompositionLocalProvider(LocalAppStore provides ...)")
    }

object AppStoreAccess {
    val current: AppStore
        @Composable get() = LocalAppStore.current
}
