// ApplicationsCreateBodies.swift
// Foundation · Network · Endpoints — 出寮届提交 / 修改届的 Encodable body
//
// backend 用 discriminated union（按 `kind` 字段 dispatch 到 3 个 schema）。
// iOS 侧给 3 个独立 struct，kind 字段硬编码日文，避免出错。
//
// 字段名跟 backend Pydantic schema byte-perfect 对齐（snake_case）。

import Foundation

// MARK: - 共通子模型

/// 滞在先（外泊 / 帰国届的 stay_locations 元素）
struct StayLocationBody: Encodable {
    let kind: String                // "ホテル" / "親戚宅" / "自宅" 等
    let name: String
    let address: String?
    let phone: String?
}

/// 食堂跳过的 1 顿（外泊 / 帰国届的 meals_skip 元素）
struct MealSkipBody: Encodable {
    let date: String                // "2026-05-03"
    let meal: String                // "朝食" | "昼食" | "夕食"
}

// MARK: - 帰省届（最简、不带滞在先和飞机）

struct KisheiCreateBody: Encodable {
    let kind: String = "帰省"        // discriminated union 的判定字段
    let reason: String?
    let contact_phone: String?
    let meal_note: String?
    let is_long_vacation: Bool
    let leave_date: String          // "2026-05-03"
    let leave_method: String
    let leave_time: String          // "19:40:00" — backend 是 time 类型
    let return_date: String
    let return_method: String
    let return_time: String
}

// MARK: - 外泊届（带滞在先 + 食事跳过）

struct GaihakuCreateBody: Encodable {
    let kind: String = "外泊"
    let reason: String?
    let contact_phone: String?
    let meal_note: String?
    let companion: String?
    let dest_cities: String?
    let leave_date: String
    let leave_method: String
    let leave_time: String
    let return_date: String
    let return_method: String
    let return_time: String
    let stay_locations: [StayLocationBody]   // 至少 1 件（backend 校验）
    let meals_skip: [MealSkipBody]            // 0 件以上
}

// MARK: - 帰国届（外泊 + 飞机情报）

struct KikokuCreateBody: Encodable {
    let kind: String = "帰国"
    let reason: String?
    let contact_phone: String?
    let meal_note: String?
    let companion: String?
    let dest_cities: String?
    let leave_date: String
    let leave_method: String
    let leave_time: String
    let return_date: String
    let return_method: String
    let return_time: String
    let stay_locations: [StayLocationBody]
    let meals_skip: [MealSkipBody]
    let flight_dep_air: String      // 出発空港 (例: "羽田")
    let flight_dep_at: String       // ISO 8601 datetime "2026-05-03T18:00:00+09:00"
    let flight_arr_air: String
    let flight_arr_at: String
}

// MARK: - 修改届（PUT /applications/:id 用、全字段 Optional）

struct ApplicationUpdateBody: Encodable {
    var reason: String?
    var contact_phone: String?
    var meal_note: String?
    var companion: String?
    var dest_cities: String?
    var is_long_vacation: Bool?
    var leave_date: String?
    var leave_method: String?
    var leave_time: String?
    var return_date: String?
    var return_method: String?
    var return_time: String?
    var stay_locations: [StayLocationBody]?
    var meals_skip: [MealSkipBody]?
    var flight_dep_air: String?
    var flight_dep_at: String?
    var flight_arr_air: String?
    var flight_arr_at: String?
}
