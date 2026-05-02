// Field.swift · 通用 form field wrapper + Input / Textarea
// ⭐ Foundation · form 基础

import SwiftUI

/// Label + hint + error 包裹
struct Field<Content: View>: View {
    let label: String
    var hint: String? = nil
    var error: String? = nil
    var required: Bool = false
    @ViewBuilder var content: () -> Content

    var body: some View {
        // JSX: label fontSize 13 · fontWeight 600 · marginBottom 7 · T.inkSub
        VStack(alignment: .leading, spacing: 7) {
            HStack(spacing: 4) {
                Text(label)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(T.inkSub)
                if required { Text("*").foregroundStyle(T.danger) }
            }
            content()
            if let error {
                Text(error)
                    .font(.system(size: 11))
                    .foregroundStyle(T.danger)
                    .padding(.top, -2)
            } else if let hint {
                Text(hint)
                    .font(.system(size: 11))
                    .foregroundStyle(T.inkMute)
                    .lineSpacing(3)
                    .padding(.top, -2)
            }
        }
    }
}

/// 单行 input · 对等 JSX Input
/// JSX 规格: height 48 · radius 12 · border T.hair → T.primary on focus · bg T.pearl · fontSize 15 · T.ink
struct TField: View {
    @Binding var text: String
    var placeholder: String = ""
    var keyboard: UIKeyboardType = .default
    var secure: Bool = false
    @FocusState private var focused: Bool

    var body: some View {
        Group {
            if secure {
                SecureField(placeholder, text: $text)
            } else {
                TextField(placeholder, text: $text)
                    .keyboardType(keyboard)
            }
        }
        .font(.system(size: 15))
        .foregroundStyle(T.ink)
        .focused($focused)
        .padding(.horizontal, 14)
        .frame(height: 48)
        .background {
            RoundedRectangle(cornerRadius: T.Radius.sm, style: .continuous)
                .fill(T.pearl)
        }
        .overlay {
            RoundedRectangle(cornerRadius: T.Radius.sm, style: .continuous)
                .stroke(focused ? T.primary : T.hair, lineWidth: focused ? 1.5 : 1)
        }
    }
}

/// 多行 textarea
struct TArea: View {
    @Binding var text: String
    var placeholder: String = ""
    var rows: Int = 4

    var body: some View {
        TextEditor(text: $text)
            .frame(height: CGFloat(rows) * 22 + 20)
            .padding(8)
            .background {
                RoundedRectangle(cornerRadius: T.Radius.sm, style: .continuous)
                    .fill(T.hairSoft)
            }
            .overlay {
                RoundedRectangle(cornerRadius: T.Radius.sm, style: .continuous)
                    .stroke(T.hair, lineWidth: 1)
            }
            .overlay(alignment: .topLeading) {
                if text.isEmpty {
                    Text(placeholder)
                        .foregroundStyle(T.inkMute)
                        .font(.system(size: 14))
                        .padding(14)
                        .allowsHitTesting(false)
                }
            }
    }
}
