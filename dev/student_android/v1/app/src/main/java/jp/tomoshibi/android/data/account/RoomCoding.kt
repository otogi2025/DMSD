package jp.tomoshibi.android.data.account

// RoomCoding — 房号前缀 / 寮判定 / 房号-寮-性别一致性校验的纯逻辑。
//
// 对齐 iOS RegistrationDraft.assembleRoomNo / dormUnit（AppStore.swift）+ 后端 §5.0：
//   1 寮 = M[0-9]{3} (male) / 2 寮 = A[0-9]{1,2} (male) / 4 寮 = W[0-9]{3} (female)
// ⭐ 判寮看字母前缀，绝不能被性别或数字覆盖（6-17 五处散布 bug 根因）。

object RoomCoding {
    /**
     * 房号后缀 + 性别 → 完整 room_no。
     * - 空串 → 空（交后端拒绝）
     * - 首位已是字母（如 "A5" / "M101"）→ 原样返回，不再加前缀（防 "MA5"）
     * - 纯数字 → male 加 "M" / 其余加 "W"
     */
    fun assembleRoomNo(
        suffix: String,
        gender: String,
    ): String {
        if (suffix.isEmpty()) return ""
        if (suffix.first().isLetter()) return suffix
        val prefix = if (gender == "male") "M" else "W"
        return prefix + suffix
    }

    /**
     * 房号后缀 + 性别 → dorm_unit。
     * female → 4；male 且 A 前缀 → 2；其余 male → 1。
     */
    fun dormUnit(
        suffix: String,
        gender: String,
    ): Int {
        if (gender == "female") return 4
        if (suffix.firstOrNull()?.uppercaseChar() == 'A') return 2
        return 1
    }

    /** 性别 → 寮名（男寮 / 女寮）。注册预览用；真值以 dormUnit 为准。 */
    fun dormLabel(gender: String): String = if (gender == "male") "男寮" else "女寮"

    /** dorm_unit → 寮名。 */
    fun dormLabelFromUnit(unit: Int): String = if (unit == 4) "女寮" else "男寮"

    /**
     * B1：性别与房号字母前缀是否矛盾。
     * 女生只住 W；男生只住 M / A。纯数字 / 尚未输前缀 → false（不误挡）。
     */
    fun roomGenderMismatch(
        room: String,
        gender: String,
    ): Boolean {
        if (gender != "male" && gender != "female") return false
        val first = room.trim().firstOrNull()?.uppercaseChar() ?: return false
        return if (gender == "female") {
            first == 'M' || first == 'A'
        } else {
            first == 'W'
        }
    }

    // 兼容旧调用名：fullRoom = assembleRoomNo
    fun fullRoom(
        gender: String,
        roomDigit: String,
    ): String = assembleRoomNo(roomDigit, gender)

    // 房号正则（与后端 _ROOM_PATTERN_BY_DORM 逐条同源）
    private val roomPatternByDorm: Map<Int, Regex> =
        mapOf(
            1 to Regex("^M[0-9]{3}$"),
            2 to Regex("^A[0-9]{1,2}$"),
            4 to Regex("^W[0-9]{3}$"),
        )

    /**
     * 房号 ↔ 寮 ↔ 性别 三者一致性校验（对齐后端 validate_room_dorm_match）。
     * 返回 true = 合法组合。
     */
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
