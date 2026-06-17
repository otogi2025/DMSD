package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.ApplicationOut
import jp.tomoshibi.android.data.network.ApplicationUpdateBody
import jp.tomoshibi.android.data.network.AuditLogOut

// ApplicationsAPI.kt
// data/network/endpoints — 出寮届相关端点包装（对齐 iOS Endpoints/ApplicationsAPI.swift）
//
// 包 backend 的 /api/v1/applications/* 端点（学生侧能用的部分）：
//   - POST /applications              create（提交）
//   - GET  /applications/mine         listMine（我的一览）
//   - GET  /applications/:id          detail（详细）
//   - PUT  /applications/:id          update（变更届）
//   - GET  /applications/:id/audit    audit（改动履历）
//
// DTO 引用 data/network/NetworkModels.kt（ApplicationOut / ApplicationUpdateBody / AuditLogOut
// 以及 create 用的 KisheiCreateBody / GaihakuCreateBody / KikokuCreateBody）。

object ApplicationsAPI {
    // 出寮届提交。body 是 KisheiCreateBody / GaihakuCreateBody / KikokuCreateBody 之一。
    // backend 按 kind 字段 dispatch 到对应 schema（discriminated union，按 kind 区分的联合类型）。
    //
    // iOS 用 create<Body: Encodable>（泛型 body），这里用 reified 泛型 Body 对齐：
    // 三种 create body 是不同类型，靠 reified 让 kotlinx.serialization 在编译期拿到具体类型序列化。
    suspend inline fun <reified Body> create(body: Body): ApplicationOut = ApiClient.post("/api/v1/applications", body)

    // 我的申请一览（最近优先）
    suspend fun listMine(): List<ApplicationOut> = ApiClient.get("/api/v1/applications/mine")

    // 申请详细（含承认 chain 全部 step）。
    // id 是 String（UUID 用 String，跟 NetworkModels.kt 一致）；iOS 那边把 UUID 转小写字符串，
    // 这里直接收已是小写形态的 String，不再二次处理。
    suspend fun detail(id: String): ApplicationOut = ApiClient.get("/api/v1/applications/$id")

    // 变更届（pending / approved_partial / returned 状态时可改）。
    // body 全字段 Optional（可空）。backend 收到后承认 chain 全员重置为 pending。
    suspend fun update(
        id: String,
        body: ApplicationUpdateBody,
    ): ApplicationOut = ApiClient.put("/api/v1/applications/$id", body)

    // 改动履历（提出 / 变更届 / 役职决定 全部按时序记录）
    suspend fun audit(id: String): List<AuditLogOut> = ApiClient.get("/api/v1/applications/$id/audit")
}
