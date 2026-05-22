// UIAtoms.swift
// ⭐ Foundation · 小原子组件集合（Pill / Avatar / Card / Section / Toggle / Radio / EmptyState / Skeleton）

import SwiftUI

// MARK: - Pill (badge)

struct Pill: View {
    let text: String
    var tone: Tone = .neutral

    enum Tone { case neutral, ok, warn, danger, accent }

    var body: some View {
        Text(text)
            .font(.system(size: 11, weight: .semibold))
            .padding(.horizontal, 10).padding(.vertical, 4)
            .foregroundStyle(fg)
            .background {
                Capsule().fill(bg)
            }
    }

    private var fg: Color {
        switch tone {
        case .neutral: return T.inkSub
        case .ok: return T.okDeep
        case .warn: return T.warnDeep
        case .danger: return T.danger
        case .accent: return T.primary
        }
    }
    private var bg: Color {
        switch tone {
        case .neutral: return T.hair
        case .ok: return T.okBg
        case .warn: return T.warnBg
        case .danger: return T.dangerBg
        case .accent: return T.pill
        }
    }
}

// MARK: - Avatar (头文字)

struct Avatar: View {
    let letter: String
    var size: CGFloat = 44

    var body: some View {
        Circle()
            .fill(T.pill)
            .overlay {
                Text(letter)
                    .font(.system(size: size * 0.44, weight: .bold))
                    .foregroundStyle(T.primary)
            }
            .frame(width: size, height: size)
    }
}

// MARK: - Card

struct Card<Content: View>: View {
    var padding: CGFloat = 14
    var radius: CGFloat = T.Radius.md
    @ViewBuilder var content: () -> Content

    var body: some View {
        content()
            .padding(padding)
            .background {
                RoundedRectangle(cornerRadius: radius, style: .continuous)
                    .fill(T.paper)
                    .shadow(color: T.ink.opacity(0.05), radius: 14, x: 0, y: 4)
                    .shadow(color: T.ink.opacity(0.04), radius: 2, x: 0, y: 1)
            }
    }
}

// MARK: - Section header

struct SectionHeader: View {
    let title: String
    var right: AnyView? = nil

    var body: some View {
        HStack {
            Text(title)
                .font(.system(size: 13, weight: .bold))
                .foregroundStyle(T.inkSub)
                .textCase(.uppercase)
                .kerning(1)
            Spacer()
            if let right { right }
        }
    }
}

// MARK: - Toggle (iOS style)

struct TToggle: View {
    @Binding var on: Bool

    var body: some View {
        Toggle("", isOn: $on)
            .labelsHidden()
            .toggleStyle(.switch)
            .tint(T.primary)
    }
}

// MARK: - Radio card

struct RadioCard<Value: Hashable>: View {
    @Binding var selection: Value
    let value: Value
    let title: String
    var detail: String? = nil

    var body: some View {
        Button { selection = value } label: {
            HStack(alignment: .top, spacing: 12) {
                ZStack {
                    Circle()
                        .stroke(selection == value ? T.primary : T.inkFaint, lineWidth: 2)
                        .frame(width: 22, height: 22)
                    if selection == value {
                        Circle().fill(T.primary).frame(width: 10, height: 10)
                    }
                }
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundStyle(T.ink)
                    if let detail {
                        Text(detail)
                            .font(.system(size: 12))
                            .foregroundStyle(T.inkSub)
                    }
                }
                Spacer()
            }
            .padding(14)
            .background {
                RoundedRectangle(cornerRadius: T.Radius.md, style: .continuous)
                    .fill(selection == value ? T.pill : T.hairSoft)
            }
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Empty state

struct EmptyState: View {
    var icon: String = "tray"
    var title: String
    var message: String? = nil

    var body: some View {
        VStack(spacing: 10) {
            Image(systemName: icon)
                .font(.system(size: 40))
                .foregroundStyle(T.inkMute)
            Text(title)
                .font(.system(size: 14, weight: .semibold))
                .foregroundStyle(T.inkSub)
            if let message {
                Text(message)
                    .font(.system(size: 12))
                    .foregroundStyle(T.inkMute)
                    .multilineTextAlignment(.center)
            }
        }
        .padding(40)
    }
}

// MARK: - Skeleton (loading)

struct Skeleton: View {
    var height: CGFloat = 14
    @State private var animate = false

    var body: some View {
        RoundedRectangle(cornerRadius: 6)
            .fill(LinearGradient(
                colors: [T.hair, T.hairSoft, T.hair],
                startPoint: animate ? .leading : .trailing,
                endPoint: animate ? .trailing : .leading
            ))
            .frame(height: height)
            .onAppear {
                withAnimation(.easeInOut(duration: 1.4).repeatForever(autoreverses: false)) {
                    animate = true
                }
            }
    }
}
