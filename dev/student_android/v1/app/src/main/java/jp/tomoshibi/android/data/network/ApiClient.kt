package jp.tomoshibi.android.data.network

import jp.tomoshibi.android.BuildConfig
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
import java.util.UUID

// HTTP 客户端单例（对应 iOS Foundation/Network/APIClient.swift）。
//   用法：ApiClient.token = "eyJ..."（登录成功后 set）→ val out: XxxOut = ApiClient.get("/api/v1/...")
//   网络层从零搭建蓝图见 内部对齐规格 第 563-958 行。
//   注意：本层是结构对齐（跟 iOS 一致地存在），各屏从 MockData 切到真实联网是渐进式
//   （iOS 自身也只接了一半），整套真实联网 + 真实 NFC 防作弊签到依赖后端实装。
object ApiClient {
    // 基址：DEBUG（模拟器）→ 10.0.2.2:8000（= 宿主机 localhost）；
    // RELEASE（上架包）→ 生产域名。对齐 iOS APIClient.swift #if DEBUG / #else。
    var baseUrl: String =
        if (BuildConfig.DEBUG) {
            "http://10.0.2.2:8000"
        } else {
            "https://api.tomoshibi.cc"
        }

    // 登录后 set，之后所有请求带 Authorization: Bearer（对齐 iOS APIClient.token）
    var token: String? = null

    // 共用 JSON 解析器：忽略未知字段（后端多返字段不报错）+ 序列化默认值
    // explicitNulls = false：null 值字段不写进 JSON，对齐 ApplicationUpdateBody「只传改了的字段」设计前提
    //   （iOS 用 encodeIfPresent 精确控制，这里靠 explicitNulls 达到同效）。
    //   encodeDefaults=true 仍让 KiseiCreateBody.kind="帰省" 等带默认值的非 null 字段正常发出，
    //   两者不冲突——explicitNulls 只影响 null 值字段。
    val json =
        Json {
            ignoreUnknownKeys = true
            encodeDefaults = true
            explicitNulls = false
        }

    private const val TIMEOUT_MS = 15000

    // 通用请求 —— method + path + 可选 JSON body 字符串；返回响应体字符串（已按状态码处理）。
    // 200-299 返 body；401→Unauthorized；422→Unprocessable(后端消息)；其余→Server。
    // 204 / 空 body 时返回空字符串（调用方用 postNoContent / delete / decode 的空体分支处理）。
    suspend fun requestRaw(
        method: String,
        path: String,
        bodyJson: String? = null,
    ): String =
        withContext(Dispatchers.IO) {
            val conn = (URL(baseUrl + path).openConnection() as HttpURLConnection)
            setHttpMethod(conn, method)
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

    // POST 无 body → 解码成 Res（如出寮届撤回 /applications/:id/withdraw，后端不收 body）。
    // bodyJson 传空对象 "{}" 而非 null：FastAPI 端点签名无 body 时空对象也接受，
    // 同时让 doOutput=true 以确保 POST 方法被正确发出。
    suspend inline fun <reified Res> postNoBody(path: String): Res = decode(requestRaw("POST", path, "{}"))

    // POST 带 body、后端返 204 No Content（如学生通知 markRead）。对齐 iOS postNoContent。
    // 不走 JSON 解码——空 body 当成功；若意外带回 body 也忽略（幂等接口只关心成功与否）。
    suspend inline fun <reified Req> postNoContent(
        path: String,
        body: Req,
    ) {
        requestRaw("POST", path, json.encodeToString(body))
    }

    // PUT body → 解码成 Res
    suspend inline fun <reified Req, reified Res> put(
        path: String,
        body: Req,
    ): Res = decode(requestRaw("PUT", path, json.encodeToString(body)))

    // PATCH body → 解码成 Res（如 StudentsAPI.updateMe）
    suspend inline fun <reified Req, reified Res> patch(
        path: String,
        body: Req,
    ): Res = decode(requestRaw("PATCH", path, json.encodeToString(body)))

    // PATCH 无 body → 解码成 Res（如 LostFound resolve / Outings withdraw）
    suspend inline fun <reified Res> patchNoBody(path: String): Res = decode(requestRaw("PATCH", path))

    // DELETE（无返回体）
    suspend fun delete(path: String) {
        requestRaw("DELETE", path)
    }

    // 二进制下载（契約書图片 / PDF）。鉴权 / 超时同 requestRaw，但不走 JSON 信封解码。
    // 对齐 iOS APIClient.download。
    suspend fun download(path: String): ByteArray =
        withContext(Dispatchers.IO) {
            val conn = (URL(baseUrl + path).openConnection() as HttpURLConnection)
            conn.requestMethod = "GET"
            conn.connectTimeout = TIMEOUT_MS
            conn.readTimeout = TIMEOUT_MS
            token?.let { conn.setRequestProperty("Authorization", "Bearer $it") }
            try {
                val code = conn.responseCode
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val bytes = stream?.readBytes() ?: ByteArray(0)
                when (code) {
                    in 200..299 -> {
                        bytes
                    }

                    401 -> {
                        throw ApiError.Unauthorized
                    }

                    422 -> {
                        val text = bytes.toString(Charsets.UTF_8)
                        throw ApiError.Unprocessable(extractDetail(text) ?: "入力エラー")
                    }

                    else -> {
                        val text = bytes.toString(Charsets.UTF_8)
                        throw ApiError.Server(code, extractDetail(text) ?: "")
                    }
                }
            } catch (e: ApiError) {
                throw e
            } catch (e: Exception) {
                throw ApiError.Network(e)
            } finally {
                conn.disconnect()
            }
        }

    // multipart/form-data 单文件上传（契約書照片 / PDF）。对齐 iOS APIClient.upload。
    // 手搓边界 + Content-Disposition；文件名去掉 CR/LF/双引号防破坏 multipart 结构。
    // IO 在非 inline 的 uploadRaw；本方法只做 reified 解码（避免 public inline 访问 private 成员）。
    suspend inline fun <reified Res> upload(
        path: String,
        fileData: ByteArray,
        fileName: String,
        mimeType: String,
        fieldName: String = "file",
    ): Res = decode(uploadRaw(path, fileData, fileName, mimeType, fieldName))

    suspend fun uploadRaw(
        path: String,
        fileData: ByteArray,
        fileName: String,
        mimeType: String,
        fieldName: String = "file",
    ): String =
        withContext(Dispatchers.IO) {
            val boundary = "Boundary-${UUID.randomUUID()}"
            val safeName =
                fileName
                    .replace("\r", "")
                    .replace("\n", "")
                    .replace("\"", "")
            val preamble =
                buildString {
                    append("--$boundary\r\n")
                    append(
                        "Content-Disposition: form-data; name=\"$fieldName\"; filename=\"$safeName\"\r\n",
                    )
                    append("Content-Type: $mimeType\r\n\r\n")
                }.toByteArray(Charsets.UTF_8)
            val epilogue = "\r\n--$boundary--\r\n".toByteArray(Charsets.UTF_8)

            val conn = (URL(baseUrl + path).openConnection() as HttpURLConnection)
            conn.requestMethod = "POST"
            conn.connectTimeout = TIMEOUT_MS
            conn.readTimeout = TIMEOUT_MS
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "multipart/form-data; boundary=$boundary")
            token?.let { conn.setRequestProperty("Authorization", "Bearer $it") }
            try {
                conn.outputStream.use { out ->
                    out.write(preamble)
                    out.write(fileData)
                    out.write(epilogue)
                }
                val code = conn.responseCode
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val bodyText = stream?.bufferedReader()?.use { it.readText() } ?: ""
                when (code) {
                    in 200..299 -> bodyText
                    401 -> throw ApiError.Unauthorized
                    422 -> throw ApiError.Unprocessable(extractDetail(bodyText) ?: "入力エラー")
                    else -> throw ApiError.Server(code, extractDetail(bodyText) ?: "")
                }
            } catch (e: ApiError) {
                throw e
            } catch (e: Exception) {
                throw ApiError.Network(e)
            } finally {
                conn.disconnect()
            }
        }

    // 字符串 → T 解码：先解成功信封 {ok,data} 再取 data。
    // 204 / 空 body：对齐 iOS EmptyResponse 分支——若调用方期望 Unit 则当成功，否则报 Decode。
    inline fun <reified T> decode(text: String): T {
        if (text.isEmpty()) {
            @Suppress("UNCHECKED_CAST")
            if (T::class == Unit::class) return Unit as T
            throw ApiError.Decode(IllegalStateException("成功路径收到空响应体"))
        }
        return try {
            val envelope = json.decodeFromString<ApiEnvelope<T>>(text)
            if (!envelope.ok) {
                throw ApiError.Decode(IllegalStateException("成功路径收到 ok=false 信封"))
            }
            // data 可为 null（如「当前无注册码」）；若 T 非可空会在此抛
            @Suppress("UNCHECKED_CAST")
            envelope.data as T
        } catch (e: ApiError) {
            throw e
        } catch (e: Exception) {
            throw ApiError.Decode(e)
        }
    }

    // 抽取后端错误提示（对齐 iOS DetailError）：
    //   形态 1 新信封 {"ok":false,"error":{"code","message"}}
    //   形态 2 旧 {"detail":"字符串"} / {"detail":{"code","message"}}
    fun extractDetail(text: String): String? =
        try {
            val obj = json.parseToJsonElement(text).jsonObject
            val err = obj["error"]
            if (err is JsonObject) {
                err["message"]
                    ?.jsonPrimitive
                    ?.contentOrNull
                    ?.takeIf { it.isNotEmpty() }
                    ?.let { return it }
            }
            when (val detail = obj["detail"]) {
                is JsonObject -> detail["message"]?.jsonPrimitive?.contentOrNull
                is JsonPrimitive -> detail.contentOrNull
                else -> null
            }?.takeIf { it.isNotEmpty() }
        } catch (e: Exception) {
            null
        }

    // HttpURLConnection 部分 Android 版本 setRequestMethod("PATCH") 会抛 ProtocolException，
    // 反射写入 method 字段兜底（minSdk 26 仍可能踩到）。
    private fun setHttpMethod(
        conn: HttpURLConnection,
        method: String,
    ) {
        try {
            conn.requestMethod = method
        } catch (e: java.net.ProtocolException) {
            try {
                val field = HttpURLConnection::class.java.getDeclaredField("method")
                field.isAccessible = true
                field.set(conn, method)
            } catch (re: Exception) {
                throw ApiError.Network(e)
            }
        }
    }
}

/** 后端成功响应信封（契约 API_CONVENTIONS §1）。 */
@kotlinx.serialization.Serializable
data class ApiEnvelope<T>(
    val ok: Boolean,
    val data: T? = null,
)
