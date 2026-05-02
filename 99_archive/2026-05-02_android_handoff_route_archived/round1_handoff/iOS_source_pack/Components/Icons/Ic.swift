// Ic.swift
// ⭐ Foundation · Icon library（SF Symbols 优先 + 自定义 Path 补罕见 icon）
// 对等 phaseB_src Ic object 23 icons

import SwiftUI

enum Ic {
    /// 默认 icon size
    static let defaultSize: CGFloat = 22

    // SF Symbols 直接映射
    static func home(_ s: CGFloat = defaultSize) -> some View      { sym("house", s) }
    static func back(_ s: CGFloat = defaultSize) -> some View      { sym("chevron.left", s, weight: .medium) }
    static func close(_ s: CGFloat = 18) -> some View              { sym("xmark", s, weight: .medium) }
    static func bell(_ s: CGFloat = defaultSize) -> some View      { sym("bell", s) }
    static func mail(_ s: CGFloat = defaultSize) -> some View      { sym("envelope", s) }
    static func person(_ s: CGFloat = defaultSize) -> some View    { sym("person", s) }
    static func badge(_ s: CGFloat = 24) -> some View              { sym("shield.checkered", s) }
    static func chevR(_ s: CGFloat = 18) -> some View              { sym("chevron.right", s, weight: .medium) }
    static func chevD(_ s: CGFloat = 18) -> some View              { sym("chevron.down", s, weight: .medium) }
    static func check(_ s: CGFloat = 18) -> some View              { sym("checkmark", s, weight: .bold) }
    static func x(_ s: CGFloat = 18) -> some View                  { sym("xmark", s) }
    static func dot(_ s: CGFloat = 8) -> some View                 { sym("circle.fill", s) }
    static func search(_ s: CGFloat = 20) -> some View             { sym("magnifyingglass", s) }
    static func plus(_ s: CGFloat = defaultSize) -> some View      { sym("plus", s, weight: .medium) }
    static func camera(_ s: CGFloat = defaultSize) -> some View    { sym("camera", s) }
    static func calendar(_ s: CGFloat = defaultSize) -> some View  { sym("calendar", s) }
    static func bus(_ s: CGFloat = defaultSize) -> some View       { sym("bus", s) }
    static func package(_ s: CGFloat = defaultSize) -> some View   { sym("shippingbox", s) }
    static func music(_ s: CGFloat = defaultSize) -> some View     { sym("music.note", s) }
    static func heart(_ s: CGFloat = 18, filled: Bool = false) -> some View {
        sym(filled ? "heart.fill" : "heart", s)
    }
    static func comment(_ s: CGFloat = 18) -> some View            { sym("bubble.left", s) }
    static func flag(_ s: CGFloat = 18) -> some View               { sym("flag", s) }
    static func up(_ s: CGFloat = 16) -> some View                 { sym("arrow.up", s, weight: .medium) }
    static func down(_ s: CGFloat = 16) -> some View               { sym("arrow.down", s, weight: .medium) }
    static func lock(_ s: CGFloat = 28) -> some View               { sym("lock", s) }
    static func phoneTap(_ s: CGFloat = 40) -> some View           { sym("iphone.radiowaves.left.and.right", s) }
    static func myMoon(_ s: CGFloat = defaultSize) -> some View    { sym("moon.stars", s) }

    // 内部辅助
    private static func sym(_ name: String, _ size: CGFloat, weight: Font.Weight = .regular) -> some View {
        Image(systemName: name)
            .font(.system(size: size * 0.85, weight: weight))
            .frame(width: size, height: size)
    }
}
