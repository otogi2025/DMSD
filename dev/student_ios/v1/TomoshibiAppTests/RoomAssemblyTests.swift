// RoomAssemblyTests.swift
// 房号前缀组装 + 寮判定 纯函数单测（C2 #6-8）
//
// 被测：RegistrationDraft.assembleRoomNo(suffix:gender:) / dormUnit(suffix:gender:)
//   —— 从 AppStore.swift 里 computedRoomNo / computedDormUnit 抽出的纯函数（行为逐字不变）。
//
// §5.0 房号编码规则：字母前缀编码楼栋 —— M = 1 寮男 / A = 2 寮男 / W = 4 寮女。
// ⭐ 核心不变量（#7）：在「男生房号」里，判寮/前缀看字母前缀（A→2 寮 / 非 A→1 寮），
//   绝不能被「数字首位」覆盖 —— 这是 6-17「五处散布 bug」的根因（2 寮男生房号是 A 前缀，
//   用「数字首位==2」永远推不出 2 寮）。
// ⚠️ 该不变量的边界（ios#113 修正原注释的过度概括）：「不被性别覆盖」只对 assembleRoomNo 的前缀拼接成立；
//   dormUnit 对 female 会先短路返回 4 寮（line 63 `if gender=="female"`，见 #43 的 A1+female==4 用例）。
//   这不是矛盾：4 寮=女生寮、A 前缀本就是男生 2 寮，female+A 属非法输入、默认落 4 是有意行为，非违反不变量。

import Foundation
import Testing
@testable import TomoshibiApp

struct RoomAssemblyTests {
    // MARK: - #6 性别 → 前缀正确拼接（纯数字房号）

    @Test("#6 男 male → M 前缀 / 女 female → W 前缀，数字房号正确拼接")
    func genderPrefixAssembly() {
        #expect(RegistrationDraft.assembleRoomNo(suffix: "101", gender: "male") == "M101")
        #expect(RegistrationDraft.assembleRoomNo(suffix: "205", gender: "female") == "W205")
        // 寮判定：数字房号男 → 1 寮，女 → 4 寮
        #expect(RegistrationDraft.dormUnit(suffix: "101", gender: "male") == 1)
        #expect(RegistrationDraft.dormUnit(suffix: "205", gender: "female") == 4)
    }

    // MARK: - #7 A 前缀（2 寮）不被性别覆盖 —— 回归风险最高

    @Test("#7 房号已带 A 前缀时原样保留，男/女性别都不覆盖成 M/W（防 MA5 / WA5）")
    func aPrefixNotOverriddenByGender() {
        // 男生 A 房号：保持 A5，不拼成 "MA5"
        #expect(RegistrationDraft.assembleRoomNo(suffix: "A5", gender: "male") == "A5")
        #expect(RegistrationDraft.assembleRoomNo(suffix: "A12", gender: "male") == "A12")
        // 就算性别字段传成 female，A 前缀依旧不被 "W" 覆盖（前缀由字母编码、非性别）
        #expect(RegistrationDraft.assembleRoomNo(suffix: "A1", gender: "female") == "A1")
        // 小写 a 同样是字母 → assembleRoomNo 原样保留（isLetter 判定，不做大小写规范化）。
        // ⚠️ 契约说明（ios#113/#114）：后端 §5.0 room_no 正则大小写敏感、只收大写
        //   （accounts.py validate_room_dorm_match 用 re.match 无 IGNORECASE），小写 room_no 会被 422 拒。
        //   但生产注册流在 UI 输入处已 `.uppercased()`（AuthStubs.swift:958 onChangeCompat 过滤+转大写写回），
        //   小写永远到不了 assembleRoomNo；此处小写用例仅测纯函数容错，不代表生产会发出小写房号。
        //   规范化的唯一真值 = UI 输入层；assembleRoomNo 刻意不重复规范化（保持纯函数行为单一、防回归）。
        #expect(RegistrationDraft.assembleRoomNo(suffix: "a3", gender: "male") == "a3")
    }

    @Test("#7 寮判定：A 前缀男生 = 2 寮（看字母不看数字/性别），非 A 男生 = 1 寮")
    func aPrefixMapsToDormTwo() {
        // ⭐ 根因钉死：A1〜A12 男生必须判到 2 寮，而不是 1 寮
        #expect(RegistrationDraft.dormUnit(suffix: "A1", gender: "male") == 2)
        #expect(RegistrationDraft.dormUnit(suffix: "A12", gender: "male") == 2)
        // 小写 a 也按 A 处理（dormUnit 用 uppercased() 比较）
        #expect(RegistrationDraft.dormUnit(suffix: "a7", gender: "male") == 2)
        // 非 A 前缀数字男生 = 1 寮
        #expect(RegistrationDraft.dormUnit(suffix: "301", gender: "male") == 1)
        // 女生一律 4 寮，与前缀无关（现行行为：female 优先返回 4）
        #expect(RegistrationDraft.dormUnit(suffix: "A1", gender: "female") == 4)
    }

    // MARK: - #8 空 / 纯数字 / 非法后缀容错（不崩 + 合理默认）

    @Test("#8 空后缀 → 空串（交后端拒绝），不崩")
    func emptySuffixReturnsEmpty() {
        #expect(RegistrationDraft.assembleRoomNo(suffix: "", gender: "male") == "")
        #expect(RegistrationDraft.assembleRoomNo(suffix: "", gender: "female") == "")
        // 空后缀寮判定：男默认 1、女默认 4（first 为 nil，不崩）
        #expect(RegistrationDraft.dormUnit(suffix: "", gender: "male") == 1)
        #expect(RegistrationDraft.dormUnit(suffix: "", gender: "female") == 4)
    }

    @Test("#8 非法 / 边角后缀不崩，走合理默认")
    func illegalSuffixDoesNotCrash() {
        // 非字母首位的符号 → 当作非字母，仍按性别加前缀（不崩、行为可预期）
        #expect(RegistrationDraft.assembleRoomNo(suffix: "!!!", gender: "male") == "M!!!")
        // 未知/异常 gender 值（非 "male"）→ 落 female 分支 "W"（现行三元判定：只认 male）
        #expect(RegistrationDraft.assembleRoomNo(suffix: "101", gender: "unknown") == "W101")
        // 纯字母后缀（无数字）→ 原样返回，不崩
        #expect(RegistrationDraft.assembleRoomNo(suffix: "A", gender: "male") == "A")
        // 寮判定：符号首位既非 female 也非 A → 男默认 1 寮，不崩
        #expect(RegistrationDraft.dormUnit(suffix: "!!!", gender: "male") == 1)
    }
}
