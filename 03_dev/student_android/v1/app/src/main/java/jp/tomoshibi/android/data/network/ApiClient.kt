package jp.tomoshibi.android.data.network

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.net.HttpURLConnection
import java.net.URL

// HTTP 客户端单例（对应 iOS Foundation/Network/APIClient.swift）。
//   用法：ApiClient.token = "eyJ..."（登录成功后 set）→ val out: XxxOut = ApiClient.get("/api/v1/...")
//   网络层从零搭建蓝图见 00_admin/iOS_Android_对齐规格.md 第 563-958 行。
//   注意：本层是结构对齐（跟 iOS 一致地存在），各屏从 MockData 切到真实联网是渐进式
//   （iOS 自身也只接了一半），整套真实联网 + 真实 NFC 防作弊签到依赖后端实装。
object ApiClient {
    // 基址：模拟器用 10.0.2.2（= 宿主机 localhost）连本机后端；发布版应改生产域名。
    // 对齐 iOS DEFAULT_BASE_URL（DEBUG localhost / RELEASE api.tomoshibi.cc）。
    var baseUrl: String = "http://10.0.2.2:8000"

    // 登录后 set，之后所有请求带 Authorization: Bearer（对齐 iOS APIClient.token）
    var token: String? = null

    // 共用 JSON 解析器：忽略未知字段（后端多返字段不报错）+ 序列化默认值
    val json =
        Json {
            ignoreUnknownKeys = true
            encodeDefaults = true
        }

    private const val TIMEOUT_MS = 15000

    // 通用请求 —— method + path + 可选 JSON body 字符串；返回响应体字符串（已按状态码处理）。
    // 200-299 返 body；401→Unauthorized；422→Unprocessable(后端消息)；其余→Server。
    suspend fun requestRaw(
        method: String,
        path: String,
        bodyJson: String? = null,
    ): String =
        withContext(Dispatchers.IO) {
            val conn = (URL(baseUrl + path).openConnection() as HttpURLConnection)
            conn.requestMethod = method
            conn.connectTimeout = TIMEOUT_MS
            conn.readTimeout = TIMEOUT_MS
            conn.setRequestProperty("Content-Type", "application/json")
            token?.let { conn.setRequestProperty("Authorization", "Bearer $it") }
            if (bodyJson != null) conn.doOutput = true
            try {
                if (bodyJson != null) {
                    conn.outputStream.use { it.write(bodyJson.toByteArray(Charsets.UTF_8)) }
                }
                val code = conn.responseCode
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val text = stream?.bufferedReader()?.use { it.readText() } ?: ""
                when (code) {
                    in 200..299 -> text
                    401 -> throw ApiError.Unauthorized
                    422 -> throw ApiError.Unprocessable(extractDetail(text) ?: "入力エラー")
                    else -> throw ApiError.Server(code, extractDetail(text) ?: "")
                }
            } catch (e: ApiError) {
                throw e
            } catch (e: Exception) {
                throw ApiError.Network(e)
            } finally {
                conn.disconnect()
            }
        }

    // GET → 解码成 T
    suspend inline fun <reified T> get(path: String): T = decode(requestRaw("GET", path))

    // POST body → 解码成 Res
    suspend inline fun <reified Req, reified Res> post(
        path: String,
        body: Req,
    ): Res = decode(requestRaw("POST", path, json.encodeToString(body)))

    // PUT body → 解码成 Res
    suspend inline fun <reified Req, reified Res> put(
        path: String,
        body: Req,
    ): Res = decode(requestRaw("PUT", path, json.encodeToString(body)))

    // DELETE（无返回体）
    suspend fun delete(path: String) {
        requestRaw("DELETE", path)
    }

    // 字符串 → T 解码，失败包成 ApiError.Decode
    inline fun <reified T> decode(text: String): T =
        try {
            json.decodeFromString(text)
        } catch (e: Exception) {
            throw ApiError.Decode(e)
        }

    // 抽取后端错误 detail（对齐 iOS DetailError）：
    //   形态 1 {"detail":"字符串"} / 形态 2 {"detail":{"code":..,"message":".."}}
    fun extractDetail(text: String): String? =
        try {
            when (val detail = json.parseToJsonElement(text).jsonObject["detail"]) {
                is JsonObject -> detail["message"]?.jsonPrimitive?.contentOrNull
                is JsonPrimitive -> detail.contentOrNull
                else -> null
            }?.takeIf { it.isNotEmpty() }
        } catch (e: Exception) {
            null
        }
}
