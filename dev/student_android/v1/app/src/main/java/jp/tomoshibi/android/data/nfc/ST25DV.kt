package jp.tomoshibi.android.data.nfc

import java.nio.ByteBuffer
import java.util.UUID

// ST25DV.kt
// data/nfc — ST25DV16K Mailbox 载荷格式 + 命令常量（对齐 iOS ST25DVWriter.swift 的 ST25DV 枚举）
//
// 写进 Mailbox 的载荷格式 = specs/rollcall/Device_Contract.md §7（唯一真值，双端逐字节对齐）：
//   [0]     1 字节  格式版本 = 0x01
//   [1]     1 字节  签到类型（0x01=点呼 / 0x02=晚自习 v1.1）
//   [2..17] 16 字节 student_id UUID 原始值（RFC 4122 字节序）
//   [18..33]16 字节 idempotency_key UUID 原始值（每次写入尝试新生成）
//   总长恒 34 字节。点呼机读取侧 st25dv.py 依同表解析。
//
// 凡标「待硬件联调核实」= 硬件已到货但尚未组装，真机上无法坐实。

/** 签到类型（写进 Mailbox 载荷第 2 字节 [1]）。Device_Contract §7：0x01=点呼 / 0x02=晚自习。 */
enum class CheckinType(
    val code: Byte,
) {
    ROLLCALL(0x01),
    STUDY(0x02),
}

/**
 * ST25DV16K 的 RF 自定义命令码 / 动态寄存器 / 载荷格式常量集中处。
 * 出处：ST25DV16K datasheet（DS12550）Custom commands + Dynamic registers。
 */
object ST25DV {
    // ── 载荷格式（Device_Contract §7）──

    /** 载荷第 0 字节：格式版本号。 */
    const val PAYLOAD_VERSION: Byte = 0x01

    /** 载荷总长（恒定）。 */
    const val PAYLOAD_LENGTH = 34

    /**
     * 组装 Mailbox 载荷（恒 34 字节）。纯函数供单测锁字节序 + 长度（不碰 NFC）。
     * UUID 按 RFC 4122 原始字节序写入（most/least significant bits 大端），对齐 iOS uuid 元组。
     */
    fun buildPayload(
        type: CheckinType,
        studentId: UUID,
        idempotencyKey: UUID,
    ): ByteArray {
        val data = ByteArray(PAYLOAD_LENGTH)
        data[0] = PAYLOAD_VERSION
        data[1] = type.code
        uuidToRfc4122Bytes(studentId).copyInto(data, destinationOffset = 2)
        uuidToRfc4122Bytes(idempotencyKey).copyInto(data, destinationOffset = 18)
        return data
    }

    /** UUID → RFC 4122 16 字节（大端，不翻转）。 */
    fun uuidToRfc4122Bytes(uuid: UUID): ByteArray {
        val buf = ByteBuffer.allocate(16)
        buf.putLong(uuid.mostSignificantBits)
        buf.putLong(uuid.leastSignificantBits)
        return buf.array()
    }

    // ── 厂商码 ──

    /**
     * IC 厂商码：STMicroelectronics = 0x02。
     * ⚠️ iOS CoreNFC 的 customCommand 会自动插厂商码，Android NfcV.transceive 必须手拼进帧。
     * 待硬件联调核实：手拼位置是否与真机接受的帧一致。
     */
    const val MANUFACTURER_CODE_ST: Byte = 0x02

    // ── RF 自定义命令码（ISO15693 自定义范围 0xA0–0xDF）──

    /** Write Message：把数据写进 Mailbox。参数 = [MSGlength=长度-1] + [数据]。 */
    const val CMD_WRITE_MESSAGE: Byte = 0xAA.toByte()

    /** Read Dynamic Configuration：读一个动态寄存器。参数 = [寄存器指针]。 */
    const val CMD_READ_DYNAMIC_CONFIGURATION: Byte = 0xAD.toByte()

    // ── 动态寄存器指针 ──

    /** MB_CTRL_Dyn：邮箱控制动态寄存器，指针 0x06。 */
    const val REG_MB_CTRL_DYN: Byte = 0x06

    // ── MB_CTRL_Dyn 位定义 ──

    /** bit0 MB_EN：邮箱已使能。 */
    const val MB_CTRL_MAILBOX_ENABLED: Int = 1 shl 0

    /** bit1 HOST_PUT_MSG：宿主（点呼机 I2C）有未读消息。 */
    const val MB_CTRL_HOST_PUT_MSG: Int = 1 shl 1

    /** bit2 RF_PUT_MSG：RF 侧（上一台手机）有未读消息。待硬件联调核实位号。 */
    const val MB_CTRL_RF_PUT_MSG: Int = 1 shl 2

    /**
     * ISO15693 Request Flags：High Data Rate（对齐 iOS `.highDataRate`）。
     * 待硬件联调核实：真机是否还需 Address / Option 等位。
     */
    const val REQUEST_FLAGS_HIGH_DATA_RATE: Byte = 0x02

    /** Write Message 的 MSGlength 字段 = 载荷长 - 1（datasheet：写 N 字节填 N-1）。 */
    val writeMessageLengthField: Byte
        get() = (PAYLOAD_LENGTH - 1).toByte()
}

/** ST25DV 写入失败细分（对齐 iOS ST25DVError + userMessageJP）。 */
sealed class ST25DVError(
    val userMessageJP: String,
) : Exception(userMessageJP) {
    /** 本机不支持 NFC / 未开 NFC */
    data object Unavailable : ST25DVError("この端末は NFC に対応していません")

    /** 检测到的不是 ISO15693（NFC Type 5）标签 */
    data object WrongTagType : ST25DVError("点呼機の NFC ではありません")

    /** 连接失败 / 标签中途走开（detail 仅日志，不进用户文案） */
    class TagLost(
        val detail: String,
    ) : ST25DVError("スマートフォンが離れました。もう一度かざしてください")

    /** MB_EN=0：点呼机侧未开邮箱 */
    data object MailboxDisabled : ST25DVError(
        "点呼機が受付状態ではありません。しばらく待ってからお試しください",
    )

    /** HOST_PUT_MSG 或 RF_PUT_MSG：邮箱被占 */
    data object MailboxBusy : ST25DVError(
        "点呼機が処理中です。少し待ってからもう一度かざしてください",
    )

    /** 命令被拒 / 空响应（detail 仅日志） */
    class CommandRejected(
        val detail: String,
    ) : ST25DVError("書き込みに失敗しました。もう一度お試しください")

    /** 载荷长度不是 34（编程期不变量） */
    data object PayloadInvalid : ST25DVError("送信データの生成に失敗しました")
}
