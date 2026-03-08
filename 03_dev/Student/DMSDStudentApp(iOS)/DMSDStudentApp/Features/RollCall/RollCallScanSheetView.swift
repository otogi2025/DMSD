import SwiftUI

enum RollCallScanSheetState: Equatable {
    case scanning
    case success
    case error(String)
}

struct RollCallScanOverlay: View {
    let state: RollCallScanSheetState
    let onCancel: () -> Void

    var body: some View {
        ZStack(alignment: .bottom) {
            Color.black.opacity(0.24)
                .ignoresSafeArea()

            RollCallScanSheetView(
                state: state,
                onCancel: onCancel
            )
            .padding(.horizontal, 16)
            .padding(.bottom, 12)
            .transition(.move(edge: .bottom).combined(with: .opacity))
        }
    }
}

private struct RollCallScanSheetView: View {
    let state: RollCallScanSheetState
    let onCancel: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            HStack {
                Spacer()

                Button(action: onCancel) {
                    Image(systemName: "xmark")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundColor(.black.opacity(0.82))
                        .frame(width: 28, height: 28)
                        .background(Color.white.opacity(0.65), in: Circle())
                }
                .buttonStyle(.plain)
            }

            Text("スキャンの準備ができました")
                .font(.system(size: 24, weight: .bold))
                .foregroundColor(.black.opacity(0.88))

            VStack(alignment: .leading, spacing: 6) {
                Text("1. 自販機または点呼機のボタンを押してください")
                Text("2. スマホを対応機器に近づけてタッチしてください")
            }
            .font(.system(size: 13, weight: .regular))
            .foregroundColor(.black.opacity(0.64))

            ScanAnimationView(state: state)
                .frame(maxWidth: .infinity)
                .padding(.top, 4)

            if case .error(let message) = state {
                Text(message)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.red.opacity(0.9))
            }

            Button(action: onCancel) {
                Text("キャンセル")
                    .font(.system(size: 17, weight: .semibold))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .frame(height: 52)
                    .background(Color(red: 0.12, green: 0.44, blue: 0.96), in: Capsule())
            }
            .buttonStyle(PrimaryCancelButtonStyle())
            .padding(.top, 4)
        }
        .padding(.horizontal, 20)
        .padding(.top, 14)
        .padding(.bottom, 20)
        .background(
            ZStack {
                RoundedRectangle(cornerRadius: 28, style: .continuous)
                    .fill(.regularMaterial)

                RoundedRectangle(cornerRadius: 28, style: .continuous)
                    .fill(Color.white.opacity(0.24))
            }
        )
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [.white.opacity(0.66), .clear],
                        startPoint: .top,
                        endPoint: .center
                    )
                )
                .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(Color.white.opacity(0.9), lineWidth: 1)
        )
        .shadow(color: .black.opacity(0.1), radius: 20, x: 0, y: 8)
        .overlay(alignment: .topLeading) {
            Circle()
                .fill(Color.white.opacity(0.35))
                .frame(width: 120, height: 120)
                .blur(radius: 24)
                .offset(x: -40, y: -48)
                .allowsHitTesting(false)
        }
    }
}

private struct ScanAnimationView: View {
    let state: RollCallScanSheetState

    @State private var pulse = false
    @State private var wave = false

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color(red: 0.12, green: 0.44, blue: 0.96).opacity(0.4), lineWidth: 6)
                .frame(width: 84, height: 84)
                .scaleEffect(pulse ? 1.04 : 0.96)
                .animation(.easeInOut(duration: 1.0).repeatForever(autoreverses: true), value: pulse)

            Circle()
                .stroke(Color(red: 0.38, green: 0.72, blue: 1.0).opacity(0.5), lineWidth: 4)
                .frame(width: 92, height: 92)
                .scaleEffect(wave ? 1.25 : 0.92)
                .opacity(wave ? 0 : 0.45)
                .animation(.easeOut(duration: 1.2).repeatForever(autoreverses: false), value: wave)

            if case .success = state {
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 40, weight: .semibold))
                    .foregroundColor(.green)
            } else {
                Image(systemName: "iphone.gen3.radiowaves.left.and.right")
                    .font(.system(size: 34, weight: .semibold))
                    .foregroundColor(Color(red: 0.38, green: 0.72, blue: 1.0))
            }
        }
        .frame(height: 106)
        .onAppear {
            pulse = true
            wave = true
        }
    }
}

private struct PrimaryCancelButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .brightness(configuration.isPressed ? -0.1 : 0)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .animation(.easeOut(duration: 0.14), value: configuration.isPressed)
    }
}

#Preview {
    ZStack {
        Color.gray.opacity(0.3).ignoresSafeArea()
        RollCallScanOverlay(state: .scanning, onCancel: {})
    }
}
