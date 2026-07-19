package jp.tomoshibi.android.data.store

import jp.tomoshibi.android.data.model.AppState
import kotlinx.serialization.encodeToString
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

// 登录 token 存取往返测试（C2 Android #19）。
// AppStore 把整个 AppState 序列化成 JSON 存进 DataStore，authToken 即随之持久化 → 实现自动登录。
// 这里用 AppStore 真正在用的那份 appJson（同包 internal）做「编码→解码」往返，守住 401 处理与
// 自动登录的地基：token 不能在往返中丢。不自建配置副本——appJson 将来改配置，本测试跟着测真身。
class TokenRoundtripTest {
    private val json = appJson

    @Test
    fun `authToken 经 JSON 往返不丢`() {
        val original = AppState(authed = true, authToken = "eyJhbGciOi.payload.sig")
        val restored = json.decodeFromString<AppState>(json.encodeToString(original))
        assertEquals("eyJhbGciOi.payload.sig", restored.authToken)
        assertTrue(restored.authed)
    }

    @Test
    fun `未登录 authToken 为 null 往返仍是 null`() {
        val original = AppState(authed = false, authToken = null)
        val restored = json.decodeFromString<AppState>(json.encodeToString(original))
        assertNull(restored.authToken)
    }

    @Test
    fun `登出 token 置 null 覆盖旧 token`() {
        // 先有 token 的状态，登出后置 null → 往返后应确实是 null（不残留旧 token）
        val loggedIn = AppState(authed = true, authToken = "old-token")
        val loggedOut = loggedIn.copy(authed = false, authToken = null)
        val restored = json.decodeFromString<AppState>(json.encodeToString(loggedOut))
        assertNull(restored.authToken)
    }

    @Test
    fun `会话字段 needsRenewal 与过期时刻往返不丢`() {
        val original =
            AppState(
                authed = true,
                authToken = "tok",
                tokenExpiresAtEpochMs = 1_800_000_000_000L,
                needsRenewal = true,
                myStudentId = "uuid-abc",
                studyLeaveCountThisMonth = 2,
                loginFailCount = 3,
                lockoutRemainingSec = 900,
                lockoutMessage = "アカウントロック中（残り約 15 分）",
            )
        val restored = json.decodeFromString<AppState>(json.encodeToString(original))
        assertEquals(1_800_000_000_000L, restored.tokenExpiresAtEpochMs)
        assertTrue(restored.needsRenewal)
        assertEquals("uuid-abc", restored.myStudentId)
        assertEquals(2, restored.studyLeaveCountThisMonth)
        assertEquals(3, restored.loginFailCount)
        assertEquals(900, restored.lockoutRemainingSec)
        assertEquals("アカウントロック中（残り約 15 分）", restored.lockoutMessage)
    }
}
