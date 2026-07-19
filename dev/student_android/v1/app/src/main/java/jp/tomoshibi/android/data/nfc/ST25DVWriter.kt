package jp.tomoshibi.android.data.nfc

import android.app.Activity
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.TagLostException
import android.nfc.tech.NfcV
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.suspendCancellableCoroutine
import java.io.IOException
import java.util.UUID
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

// ST25DVWriter.kt
// data/nfc — 手机点呼签到：用 android.nfc.tech.NfcV（ISO15693）把学号写进墙上 ST25DV16K 的 Mailbox
//
// ⭐ 架构（对齐 iOS ST25DVWriter.swift / flow_design §3）：
//   手机全程不联网。学生点签到 → App 把身份数据写进点呼机 ST25DV Mailbox → 点呼机读走 POST 后端。
//
// 写入流程（与 iOS 同序）：
//   enableReaderMode 等标签 → connect → Read Dynamic Configuration(0xAD) 读 MB_CTRL_Dyn
//   → 检查 bit0/1/2 → Write Message(0xAA) 写 34 字节。
//
// ⚠️ 平台差：iOS CoreNFC customCommand 自动插厂商码 0x02；Android NfcV.transceive 必须手拼进帧。
// 凡标「待硬件联调核实」= 硬件未组装，真机无法坐实。

/**
 * 把学号写进墙上 ST25DV16K 的 Mailbox。
 * 用法：`ST25DVWriter(activity).writeCheckin(studentId, CheckinType.ROLLCALL)`
 */
class ST25DVWriter(
    private val activity: Activity,
) {
    private val cancelRequested = AtomicBoolean(false)
    private val finished = AtomicBoolean(false)
    private val continuationRef =
        AtomicReference<kotlin.coroutines.Continuation<Unit>?>(null)

    /**
     * 写点呼 / 学習签到到 Mailbox。成功返回；失败抛 [ST25DVError]。
     * 调用方应在弹窗关闭时 [cancel]。
     */
    suspend fun writeCheckin(
        studentId: UUID,
        type: CheckinType,
    ) {
        val adapter =
            NfcAdapter.getDefaultAdapter(activity)
                ?: throw ST25DVError.Unavailable
        if (!adapter.isEnabled) throw ST25DVError.Unavailable

        val payload = ST25DV.buildPayload(type, studentId, UUID.randomUUID())
        if (payload.size != ST25DV.PAYLOAD_LENGTH) throw ST25DVError.PayloadInvalid

        cancelRequested.set(false)
        finished.set(false)

        try {
            suspendCancellableCoroutine { cont ->
                continuationRef.set(cont)
                if (cancelRequested.get()) {
                    finishFailure(CancellationException())
                    return@suspendCancellableCoroutine
                }

                // 只扫 NFC-V（ISO15693 / Type 5）；跳过 NDEF 解析加快发现
                // 待硬件联调核实：Reader Mode 参数 / 是否需额外 flag
                adapter.enableReaderMode(
                    activity,
                    { tag -> onTagDiscovered(adapter, tag, payload) },
                    NfcAdapter.FLAG_READER_NFC_V or NfcAdapter.FLAG_READER_SKIP_NDEF_CHECK,
                    null,
                )

                cont.invokeOnCancellation {
                    cancelRequested.set(true)
                    runCatching { adapter.disableReaderMode(activity) }
                    // 不在这里 finish——外层 cancel 已由 CancellationException 路径处理
                }
            }
        } finally {
            runCatching { adapter.disableReaderMode(activity) }
            continuationRef.set(null)
        }
    }

    /** 取消（用户关签到弹窗时调）：关掉 Reader Mode，结束挂起的 writeCheckin。 */
    fun cancel() {
        cancelRequested.set(true)
        val adapter = NfcAdapter.getDefaultAdapter(activity)
        runCatching { adapter?.disableReaderMode(activity) }
        finishFailure(CancellationException())
    }

    private fun onTagDiscovered(
        adapter: NfcAdapter,
        tag: Tag,
        payload: ByteArray,
    ) {
        if (cancelRequested.get() || finished.get()) return
        try {
            val nfcV =
                NfcV.get(tag)
                    ?: throw ST25DVError.WrongTagType
            nfcV.connect()
            try {
                // 步骤①：读 MB_CTRL_Dyn，确认邮箱可写
                val mbctrl = readMailboxControl(nfcV)
                if (mbctrl and ST25DV.MB_CTRL_MAILBOX_ENABLED == 0) {
                    throw ST25DVError.MailboxDisabled
                }
                if (mbctrl and ST25DV.MB_CTRL_HOST_PUT_MSG != 0) {
                    throw ST25DVError.MailboxBusy
                }
                if (mbctrl and ST25DV.MB_CTRL_RF_PUT_MSG != 0) {
                    // 前一学生消息未读走 —— 现在写会覆盖；同 iOS 归 mailboxBusy
                    throw ST25DVError.MailboxBusy
                }
                // 步骤②：写 34 字节载荷
                writeMailbox(nfcV, payload)
                finishSuccess(adapter)
            } finally {
                runCatching { nfcV.close() }
            }
        } catch (e: ST25DVError) {
            runCatching { adapter.disableReaderMode(activity) }
            finishFailure(e)
        } catch (e: TagLostException) {
            runCatching { adapter.disableReaderMode(activity) }
            finishFailure(ST25DVError.TagLost(e.message ?: "tag lost"))
        } catch (e: IOException) {
            runCatching { adapter.disableReaderMode(activity) }
            finishFailure(ST25DVError.TagLost(e.message ?: "io"))
        } catch (e: Exception) {
            runCatching { adapter.disableReaderMode(activity) }
            finishFailure(ST25DVError.CommandRejected(e.message ?: "unknown"))
        }
    }

    /**
     * 发 Read Dynamic Configuration（0xAD）读 MB_CTRL_Dyn。
     * 帧：[Flags][0xAD][厂商码 0x02][寄存器指针 0x06]
     * 待硬件联调核实：响应是否含 flags 字节；用 last 取值兼容两种结构（对齐 iOS response.last）。
     */
    private fun readMailboxControl(nfcV: NfcV): Int {
        val cmd =
            byteArrayOf(
                ST25DV.REQUEST_FLAGS_HIGH_DATA_RATE,
                ST25DV.CMD_READ_DYNAMIC_CONFIGURATION,
                ST25DV.MANUFACTURER_CODE_ST,
                ST25DV.REG_MB_CTRL_DYN,
            )
        val response =
            try {
                nfcV.transceive(cmd)
            } catch (e: TagLostException) {
                throw ST25DVError.TagLost(e.message ?: "read lost")
            } catch (e: IOException) {
                throw ST25DVError.CommandRejected(e.message ?: "read io")
            }
        if (response == null || response.isEmpty()) {
            throw ST25DVError.CommandRejected("空応答")
        }
        // 响应 flags bit0=1 表示错误（ISO15693）
        if (response[0].toInt() and 0x01 != 0) {
            throw ST25DVError.CommandRejected("読取エラー flags=${response[0]}")
        }
        // 待硬件联调核实：寄存器值取 last（兼容「仅值」/「flags+值」）
        return response.last().toInt() and 0xFF
    }

    /**
     * 发 Write Message（0xAA）写 34 字节。
     * 帧：[Flags][0xAA][厂商码 0x02][MSGlength=33][34 字节载荷]
     * 待硬件联调核实：MSGlength 与厂商码位置。
     */
    private fun writeMailbox(
        nfcV: NfcV,
        payload: ByteArray,
    ) {
        val cmd =
            ByteArray(3 + 1 + payload.size).also { buf ->
                buf[0] = ST25DV.REQUEST_FLAGS_HIGH_DATA_RATE
                buf[1] = ST25DV.CMD_WRITE_MESSAGE
                buf[2] = ST25DV.MANUFACTURER_CODE_ST
                buf[3] = ST25DV.writeMessageLengthField // 33
                payload.copyInto(buf, destinationOffset = 4)
            }
        val response =
            try {
                nfcV.transceive(cmd)
            } catch (e: TagLostException) {
                throw ST25DVError.TagLost(e.message ?: "write lost")
            } catch (e: IOException) {
                throw ST25DVError.CommandRejected(e.message ?: "write io")
            }
        if (response != null && response.isNotEmpty() && (response[0].toInt() and 0x01 != 0)) {
            throw ST25DVError.CommandRejected("書込エラー flags=${response[0]}")
        }
    }

    private fun finishSuccess(adapter: NfcAdapter) {
        if (!finished.compareAndSet(false, true)) return
        runCatching { adapter.disableReaderMode(activity) }
        continuationRef.getAndSet(null)?.resume(Unit)
    }

    private fun finishFailure(error: Throwable) {
        if (!finished.compareAndSet(false, true)) return
        continuationRef.getAndSet(null)?.resumeWithException(error)
    }
}
