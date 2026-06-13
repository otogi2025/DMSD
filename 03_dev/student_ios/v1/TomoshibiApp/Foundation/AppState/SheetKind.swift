// SheetKind.swift
// ⭐ Foundation · 全局 sheet 枚举（对等 phaseB_src AppCtx.sheetOpen）

import Foundation

enum SheetKind: Hashable {
    case rollcall // 中央点呼按钮 → Liquid Glass sheet
    case feedback // 顶部 bar tap → 3 选 1
    case health // 体调问题上报
    case absence // 本次欠席申请
    case other // 其他问题
    case logout // 退出登录确认
    case studyCheckin // 学习 NFC 2 次碰签到 (system_features §7.3.3)
    case songReport(songId: Int) // 点歌举报 sheet (system_features §7.11.2)
    case renewStudentNo // 番号重新设定 — 学年更新时学生自设番号 (system_features §4.2)
}

enum RollState {
    case idle // 日常 · 下次点呼预告
    case active // 点呼中 · 倒计时到迟到判定
    case absent // 欠席判定 · 长时间未签到，请直接联系寮监
    case done // 已签到 · 绿色显示
}
