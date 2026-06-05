package jp.tomoshibi.android.data.network

// API 错误类型（对应 iOS Foundation/Network/APIError.swift）
// display 字段即给用户看的日语提示文案，跟 iOS errorDescription 一字不差。
sealed class ApiError(
    val display: String,
) : Exception(display) {
    // 通信失败（Wi-Fi 断 / 连不上）
    data class Network(
        val err: Throwable,
    ) : ApiError("通信エラーが発生しました。電波を確認してください")

    // JSON 解码失败
    data class Decode(
        val err: Throwable,
    ) : ApiError("データの読み込みに失敗しました")

    // 401 — 需重新登录
    data object Unauthorized : ApiError("ログインが必要です")

    // 422 — 输入错误（后端返回的日语消息）
    data class Unprocessable(
        val msg: String,
    ) : ApiError(msg)

    // 5xx 等预期外错误
    data class Server(
        val code: Int,
        val msg: String,
    ) : ApiError("サーバーエラー ($code): $msg")

    // 未知错误
    data object Unknown : ApiError("不明なエラー")
}
