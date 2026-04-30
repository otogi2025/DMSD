// SheetKind.swift
// ⭐ Foundation · 全局 sheet 枚举（对等 phaseB_src AppCtx.sheetOpen）

import Foundation

enum SheetKind: Hashable {
    case rollcall       // 中央点呼按钮 → Liquid Glass sheet
    case feedback       // 顶部 bar tap → 3 选 1
    case health         // 体調問題を報告
    case absence        // 今回欠席の申請
    case other          // その他の問題
    case logout         // ログアウト 確認
}

enum RollState {
    case idle           // 日常 · 下次点呼预告
    case active         // 点呼中 · 倒计时到迟到判定
    case absent         // 欠席判定 · 寮監に直接連絡（未チェックイン長時間）
    case done           // 已签到 · 绿色显示
}
