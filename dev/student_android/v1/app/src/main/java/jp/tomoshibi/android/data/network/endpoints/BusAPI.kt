package jp.tomoshibi.android.data.network.endpoints

import jp.tomoshibi.android.data.network.ApiClient
import jp.tomoshibi.android.data.network.BusRouteListOut
import jp.tomoshibi.android.data.network.BusRouteOut

// BusAPI.kt
// data/network/endpoints — 巴士便（寮生特別運行 / 平日上下学班车）endpoint 包装
//
// 对齐 iOS BusAPI.swift（enum BusAPI）。后端 spec §7.6:
//   GET /api/v1/bus/routes            — 列巴士便（学生 + 老师都可看）
//   GET /api/v1/bus/routes?kind=...   — 按种类过滤（daily_commute / dorm_special）
object BusAPI {
    // 列巴士便。kind 传 null = 全部；传 "dorm_special" / "daily_commute" = 只看该种类。
    // 后端返回 { "items": [...] } 包装，这里解包成数组返回。
    suspend fun listRoutes(kind: String? = null): List<BusRouteOut> {
        var path = "/api/v1/bus/routes"
        if (kind != null) {
            path += "?kind=$kind"
        }
        val out: BusRouteListOut = ApiClient.get(path)
        return out.items
    }
}
