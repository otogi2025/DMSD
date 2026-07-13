// RoomAssemblyTests.swift
// 房号前缀组装 + 寮判定 纯函数单测（C2 #6-8）
//
// 被测：RegistrationDraft.assembleRoomNo(suffix:gender:) / dormUnit(suffix:gender:)
//   —— 从 AppStore.swift 里 computedRoomNo / computedDormUnit 抽出的纯函数（行为逐字不变）。
//
// §5.0 房号编码规则：字母前缀编码楼栋 —— M = 1 寮男 / A = 2 寮男 / W = 4 寮女。
// ⭐ 核心不变量（#7）：判寮/前缀看房号字母前缀，绝不能被性别或数字覆盖。
//   这是 6-17「五处散布 bug」的根因场景 —— 2 寮男生房号是 A 前缀，用性别或「数字首位」永远推不出 2 寮。

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
        // 小写 a 同样是字母 → 原样保留（isLetter 判定）
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
