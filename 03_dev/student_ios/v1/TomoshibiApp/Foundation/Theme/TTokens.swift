// TTokens.swift
// ⭐ Foundation · Design tokens（对等 phaseB_src c281cafa T 对象）
// 名称: 涼 Suzu · 主色: #1f6b74 teal dark

import SwiftUI

enum T {
    // MARK: Colors
    static let primary      = Color(hex: 0x1f6b74)     // teal dark
    static let primaryDk    = Color(hex: 0x0e3840)     // teal very dark
    static let accent       = Color(hex: 0x5fbec8)     // teal bright
    static let accentSoft   = Color(hex: 0xa8dce2)     // teal light
    static let pearl        = Color(hex: 0xeff2f3)     // off-white
    static let paper        = Color.white              // white
    static let ink          = Color(hex: 0x0f1e22)     // very dark
    static let inkSub       = Color(hex: 0x56707a)     // subtitle
    static let inkMute      = Color(hex: 0x93a4ac)     // muted
    static let inkFaint     = Color(hex: 0xc4d0d5)     // light gray

    static let hair         = Color(hex: 0x0f1e22, alpha: 0.08)
    static let hairSoft     = Color(hex: 0x0f1e22, alpha: 0.04)

    // MARK: Status
    static let warn         = Color(hex: 0xd1984a)
    static let warnBg       = Color(hex: 0xfdf4e1)
    static let warnDeep     = Color(hex: 0x7a4a0e)
    static let danger       = Color(hex: 0xc44848)
    static let dangerBg     = Color(hex: 0xfde8e8)
    static let ok           = Color(hex: 0x4a9478)
    static let okBg         = Color(hex: 0xe3f1ea)
    static let okDeep       = Color(hex: 0x2c6048)

    // MARK: Glass (for fallback — iOS 26 真 glass 走 .glassEffect())
    static let glassNav      = Color.white.opacity(0.68)
    static let glassBar      = Color.white.opacity(0.70)
    static let glassSheet    = Color.white.opacity(0.85)
    static let glassBackdrop = Color(hex: 0x0f1e22, alpha: 0.35)

    // MARK: Pill
    static let pill          = Color(hex: 0x1f6b74, alpha: 0.08)
    static let pillFg        = primary

    // MARK: Gradients
    static let amberGrad = LinearGradient(
        colors: [Color(hex: 0xffe9b5), Color(hex: 0xf4c677)],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let redGrad = LinearGradient(
        colors: [Color(hex: 0xfdd7d2), Color(hex: 0xe88a80)],
        startPoint: .topLeading, endPoint: .bottomTrailing
    )
    static let greenGrad = LinearGradient(
        colors: [Color(hex: 0xd2ebda), Color(hex: 0x8bc6a3)],
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
    static let fontName      = "HiraginoSans-W3"
    static let fontNameBold  = "HiraginoSans-W6"
    static let monoFontName  = "SFMono-Regular"
}

// MARK: - Color hex helper

extension Color {
    init(hex: UInt32, alpha: Double = 1.0) {
        let r = Double((hex >> 16) & 0xff) / 255
        let g = Double((hex >> 8) & 0xff) / 255
        let b = Double(hex & 0xff) / 255
        self.init(.sRGB, red: r, green: g, blue: b, opacity: alpha)
    }
}
