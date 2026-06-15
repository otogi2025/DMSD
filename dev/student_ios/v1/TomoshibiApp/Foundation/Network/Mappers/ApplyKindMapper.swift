// ApplyKindMapper.swift
// Foundation · Network · Mappers — iOS 内部代码 ↔ backend 日语 kind 转换 (F1)
//
// iOS 内部用英语 enum 管理，仅在 API 收发时转换为日语。

import Foundation

enum ApplyKindMapper {
    /// iOS 内部代码 → backend 日语（POST /applications body 的 kind 字段）
    static let toBackend: [String: String] = [
        "stay": "外泊",
        "holiday": "帰省",
        "returncountry": "帰国",
        "studyAbsence": "晩自習欠席",
    ]

    /// backend 日语 → iOS 内部代码（GET 响应反序列化用）
    static let fromBackend: [String: String] = Dictionary(
        uniqueKeysWithValues: toBackend.map { ($1, $0) }
    )

    /// iOS 代码 → backend 日语。无法转换则返回原值
    static func encode(_ iosKind: String) -> String {
        toBackend[iosKind] ?? iosKind
    }

    /// backend 日语 → iOS 代码。无法转换则返回原值
    static func decode(_ backendKind: String) -> String {
        fromBackend[backendKind] ?? backendKind
    }
}
