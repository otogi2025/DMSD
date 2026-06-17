// TTokens.swift
// ⭐ Foundation · Design tokens（对等 phaseB_src c281cafa T 对象）
// 名称: 涼 Suzu · 主色: #1f6b74 teal dark

import SwiftUI

enum T {
    // MARK: Colors

    static let primary = Color(hex: 0x1F6B74) // teal dark
    static let primaryDk = Color(hex: 0x0E3840) // teal very dark
    static let accent = Color(hex: 0x5FBEC8) // teal bright
    static let accentSoft = Color(hex: 0xA8DCE2) // teal light
    static let pearl = Color(hex: 0xEFF2F3) // off-white
    static let paper = Color.white // white
    static let ink = Color(hex: 0x0F1E22) // very dark
    static let inkSub = Color(hex: 0x56707A) // subtitle
    static let inkMute = Color(hex: 0x93A4AC) // muted
    static let inkFaint = Color(hex: 0xC4D0D5) // light gray

    static let hair = Color(hex: 0x0F1E22, alpha: 0.08)
    static let hairSoft = Color(hex: 0x0F1E22, alpha: 0.04)

    // MARK: Status

    static let warn = Color(hex: 0xD1984A)
    static let warnBg = Color(hex: 0xFDF4E1)
    static let warnDeep = Color(hex: 0x7A4A0E)
    static let danger = Color(hex: 0xC44848)
    static let dangerBg = Color(hex: 0xFDE8E8)
    static let ok = Color(hex: 0x4A9478)
    static let okBg = Color(hex: 0xE3F1EA)
    static let okDeep = Color(hex: 0x2C6048)

    // MARK: Glass (for fallback — iOS 26 真 glass 走 .glassEffect())

    static let glassNav = Color.white.opacity(0.68)
    static let glassBar = Color.white.opacity(0.70)
    static let glassSheet = Color.white.opacity(0.85)
    static let glassBackdrop = Color(hex: 0x0F1E22, alpha: 0.35)

    // MARK: Pill

    static let pill = Color(hex: 0x1F6B74, alpha: 0.08)
    static let pillFg = primary

    // MARK: Gradients

    static let amberGrad = LinearGradient(
        colors: [Color(hex: 0xFFE9B5), Color(hex: 0xF4C677)],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let redGrad = LinearGradient(
        colors: [Color(hex: 0xFDD7D2), Color(hex: 0xE88A80)],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let greenGrad = LinearGradient(
        colors: [Color(hex: 0xD2EBDA), Color(hex: 0x8BC6A3)],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let btnGrad = LinearGradient(
        colors: [accent, primary],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let rollBtnGrad = RadialGradient(
        colors: [accentSoft, accent, primary],
        center: .init(x: 0.35, y: 0.28),
        startRadius: 0, endRadius: 70
    )

    // MARK: Radius

    enum Radius { static let xs: CGFloat = 8; static let sm: CGFloat = 12; static let md: CGFloat = 16; static let lg: CGFloat = 22; static let pill: CGFloat = 9999 }

    // MARK: Spacing

    enum Space { static let xs: CGFloat = 4; static let sm: CGFloat = 8; static let md: CGFloat = 12; static let lg: CGFloat = 16; static let xl: CGFloat = 24; static let xxl: CGFloat = 32 }

    // MARK: Fonts

    static let fontName = "HiraginoSans-W3"
    static let fontNameBold = "HiraginoSans-W6"
    static let monoFontName = "SFMono-Regular"
}

// MARK: - Color hex helper

extension Color {
    init(hex: UInt32, alpha: Double = 1.0) {
        let r = Double((hex >> 16) & 0xFF) / 255
        let g = Double((hex >> 8) & 0xFF) / 255
        let b = Double(hex & 0xFF) / 255
        self.init(.sRGB, red: r, green: g, blue: b, opacity: alpha)
    }
}

// MARK: - 版本号显示常量

//
// 版本号从 Bundle 的 CFBundleShortVersionString 读（= project.yml 的 MARKETING_VERSION），
// 不再手写字符串，避免与工程配置漂移（原写死 "v0.15.0" 早已落后于 project.yml）。
// production 版 = "v<版本>" / demo 版 = "v<版本>-demo"。

enum AppVersionTag {
    static let full: String = {
        let version = (Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String) ?? "?"
        #if DEMO
            return "v\(version)-demo"
        #else
            return "v\(version)"
        #endif
    }()
}
