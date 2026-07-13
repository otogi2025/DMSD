package jp.tomoshibi.android.data.account

// RoomCoding — 房号前缀 / 寮名 / 房号-寮-性别一致性校验的纯逻辑（对齐 iOS AppStore RegistrationDraft + 后端 §5.0）。
//
// 为什么抽出来：这些判定原本散在 AccountScreen 的 private 函数里（跟 Compose FormData 耦合、测不了）。
// 抽成只吃基本类型的纯函数放这里，AccountScreen 调用它、行为不变，同时可单测 + 跟 iOS/后端对齐。
//
// §5.0 房号编码（后端 validate_room_dorm_match 单源）：
//   1 寮 = M[0-9]{3} (male) / 2 寮 = A[0-9]{1,2} (male) / 4 寮 = W[0-9]{3} (female)

object RoomCoding {
    // / 性别 → 房号前缀（male → "M"，female → "W"）。
    // / 注意：这是 AccountScreen 现行行为的等价抽取——只按性别加 M/W 前缀，
    // / 不含 iOS 的「房号首位已是字母(A5)则不再加前缀」继承规则（双端差异见本文件下方注记）。
    fun roomPrefix(gender: String): String = if (gender == "male") "M" else "W"

    // / 性别 + 数字房号 → 完整房号（前缀 + 数字）。等价于 AccountScreen.fullRoom 现行行为。
    fun fullRoom(
        gender: String,
        roomDigit: String,
    ): String = roomPrefix(gender) + roomDigit

    // / 性别 → 寮名（男寮 / 女寮）。等价于 AccountScreen.dormName 现行行为。
    fun dormLabel(gender: String): String = if (gender == "male") "男寮" else "女寮"

    // ⚠️ iOS 差异（未在本端实装、留给主会话决策）：
    //   iOS RegistrationDraft.computedRoomNo 对「首位已是字母」的房号(如 "A5") 直接原样保留、不加 M/W 前缀，
    //   并据 A 前缀把 dorm_unit 判为 2 寮；Android 现行 fullRoom 对 "A5" 会拼成 "MA5"（双前缀），
    //   且没有 dorm_unit 推导。故 2 寮男生场景两端不一致——本次仅锁定 Android 现行行为，不擅自改注册行为。

    // 房号正则（与后端 _ROOM_PATTERN_BY_DORM 逐条同源）
    private val roomPatternByDorm: Map<Int, Regex> =
        mapOf(
            1 to Regex("^M[0-9]{3}$"),
            2 to Regex("^A[0-9]{1,2}$"),
            4 to Regex("^W[0-9]{3}$"),
        )

    // / 房号 ↔ 寮 ↔ 性别 三者一致性校验（对齐后端 validate_room_dorm_match，§5.0 + §8.1 DB CHECK）。
    // / 返回 true = 合法组合；false = 非法（前端可据此在注册时提前拦，跟后端 422 INVALID_ROOM_FORMAT 口径一致）。
    // /   dorm_unit 1/2 期望 male，4 期望 female；其余 dorm_unit 一律非法。
    fun validateRoomDormMatch(
        roomNo: String,
        dormUnit: Int,
        gender: String,
    ): Boolean {
        val expectedGender = if (dormUnit == 1 || dormUnit == 2) "male" else "female"
        val pattern = roomPatternByDorm[dormUnit] ?: return false
        return gender == expectedGender && pattern.matches(roomNo)
    }
}
