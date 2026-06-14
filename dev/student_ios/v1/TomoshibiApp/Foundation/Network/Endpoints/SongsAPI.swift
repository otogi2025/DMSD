// SongsAPI.swift
// Foundation · Network · Endpoints — 点歌（UI「リクエスト曲」）endpoint 包装
//
// 后端路由 app/routers/songs.py（prefix /api/v1/songs）：
//   POST /api/v1/songs           投稿（dorm_unit 后端按登录学生的寮自动取，无需传）
//   GET  /api/v1/songs?dorm=     一览（投稿顺，新→旧；dorm 参数给老师男/女寮 tab，学生不传=全部）
//
// 最小版只做「投稿 + 一览」—— 通报 / 封禁 / 投票（賛否）是 v1.1，本期生产版不做（演示版保留）。

import Foundation

/// POST /api/v1/songs 请求 body（对齐后端 SongRequestCreateIn）。
struct SongRequestBody: Encodable {
    let song_title: String
    let artist: String?
    let note: String?
}

/// 点歌投稿（对齐后端 SongRequestOut）。
/// 后端无 投稿者名 / 賛否票数 字段（投票 v1.1）→ 生产版列表 / 详情只显曲名 / 艺术家 / 投稿理由。
struct SongRequestOut: Decodable, Identifiable, Hashable {
    let id: UUID
    let student_id: UUID
    let dorm_unit: Int
    let song_title: String
    let artist: String?
    let note: String? // 投稿理由
    let created_at: Date // 排序由后端做（新→旧），客户端只解码不展示
}

enum SongsAPI {
    /// 点歌投稿。
    @MainActor
    static func create(_ body: SongRequestBody) async throws -> SongRequestOut {
        return try await APIClient.shared.post(path: "/api/v1/songs", body: body)
    }

    /// 点歌一览（后端按投稿顺新→旧返回；学生不传 dorm = 全部）。
    @MainActor
    static func list() async throws -> [SongRequestOut] {
        return try await APIClient.shared.get(path: "/api/v1/songs")
    }
}
