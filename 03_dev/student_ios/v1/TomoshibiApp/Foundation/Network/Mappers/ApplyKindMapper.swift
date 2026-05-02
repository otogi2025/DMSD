// ApplyKindMapper.swift
// Foundation · Network · Mappers — iOS 内部コード ↔ backend 日本語 kind 変換 (F1)
//
// iOS は英語 enum で管理し、API 送受信時だけ日本語に変換する。

import Foundation

enum ApplyKindMapper {
    // iOS 内部コード → backend 日本語 (POST /applications body の kind フィールド)
    static let toBackend: [String: String] = [
        "stay":          "外泊",
        "holiday":       "帰省",
        "returncountry": "帰国",
        "study_absence": "学習欠席",
    ]

    // backend 日本語 → iOS 内部コード (GET レスポンスのデシリアライズ用)
    static let fromBackend: [String: String] = Dictionary(
        uniqueKeysWithValues: toBackend.map { ($1, $0) }
    )

    /// iOS コード → backend 日本語。変換できなければ元の値を返す
    static func encode(_ iosKind: String) -> String {
        toBackend[iosKind] ?? iosKind
    }

    /// backend 日本語 → iOS コード。変換できなければ元の値を返す
    static func decode(_ backendKind: String) -> String {
        fromBackend[backendKind] ?? backendKind
    }
}
