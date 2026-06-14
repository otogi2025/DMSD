// ContractFilePicker.swift
// Foundation · Components — 契約書（合同 = 网课报名凭证）文件选择
//
// 点「添付」从屏幕底部弹三选项：「写真を撮る」（拍照）/「アルバムから選ぶ」（相册）/「ファイルを選ぶ」（选文件）。
// iPhone 拍照默认 HEIC，但老师网页（浏览器）显示 HEIC 兼容差 →
// 这里把所有图片统一转成 JPEG 再交出去（顺带缩放压缩）；PDF 原样。

import PhotosUI
import SwiftUI
import UIKit
import UniformTypeIdentifiers

/// 选好的契約書文件（已转成后端 / 老师网页都能处理的格式）。
struct PickedContract: Equatable {
    var data: Data
    var fileName: String
    var mime: String // "image/jpeg" | "application/pdf"

    var sizeText: String {
        ByteCountFormatter.string(fromByteCount: Int64(data.count), countStyle: .file)
    }
}

struct ContractFilePicker: View {
    @Binding var picked: PickedContract?

    @State private var showDialog = false
    @State private var showCamera = false
    @State private var showPhotos = false
    @State private var showFileImporter = false
    @State private var photoItem: PhotosPickerItem?
    @State private var errorText: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if let picked {
                selectedRow(picked)
            } else {
                addButton
            }
            if let errorText {
                Text(errorText)
                    .font(.system(size: 12))
                    .foregroundStyle(T.danger)
            }
        }
        // 底部弹三选项菜单（很多 App 都有的样式）
        .confirmationDialog("契約書を追加", isPresented: $showDialog, titleVisibility: .visible) {
            // 相机不可用（模拟器 / 无摄像头设备）时不显示拍照项，避免点了崩溃
            if UIImagePickerController.isSourceTypeAvailable(.camera) {
                Button("写真を撮る") { showCamera = true }
            }
            Button("アルバムから選ぶ") { showPhotos = true }
            Button("ファイルを選ぶ") { showFileImporter = true }
            Button("キャンセル", role: .cancel) {}
        }
        // 拍照 — 用 UIImagePickerController 包装
        .fullScreenCover(isPresented: $showCamera) {
            CameraPicker(
                onCapture: { image in
                    showCamera = false
                    handleImage(image)
                },
                onCancel: { showCamera = false }
            )
            .ignoresSafeArea()
        }
        // 相册选图（系统选择器，不需相册权限）
        .photosPicker(isPresented: $showPhotos, selection: $photoItem, matching: .images)
        .onChangeCompat(of: photoItem) { newItem in
            guard let newItem else { return }
            Task { await handlePhotoItem(newItem) }
        }
        // 选文件（PDF / 图片）
        .fileImporter(
            isPresented: $showFileImporter,
            allowedContentTypes: [.pdf, .image],
            allowsMultipleSelection: false
        ) { result in
            handleFileImport(result)
        }
    }

    private var addButton: some View {
        Button {
            errorText = nil
            showDialog = true
        } label: {
            HStack(spacing: 8) {
                Image(systemName: "paperclip")
                    .font(.system(size: 14, weight: .semibold))
                Text("契約書を添付")
                    .font(.system(size: 13, weight: .bold))
            }
            .foregroundStyle(T.primary)
            .frame(maxWidth: .infinity, minHeight: 44)
            .background {
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(
                        T.primary.opacity(0.4),
                        style: StrokeStyle(lineWidth: 1, dash: [4, 3])
                    )
            }
        }
        .buttonStyle(.plain)
    }

    private func selectedRow(_ p: PickedContract) -> some View {
        HStack(spacing: 10) {
            Image(systemName: p.mime == "application/pdf" ? "doc.fill" : "photo.fill")
                .font(.system(size: 18))
                .foregroundStyle(T.primary)
            VStack(alignment: .leading, spacing: 2) {
                Text(p.fileName)
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundStyle(T.ink)
                    .lineLimit(1)
                Text(p.sizeText)
                    .font(.system(size: 11))
                    .foregroundStyle(T.inkSub)
            }
            Spacer()
            Button {
                picked = nil
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .font(.system(size: 20))
                    .foregroundStyle(T.inkFaint)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(Text("契約書を削除"))
        }
        .padding(12)
        .background {
            RoundedRectangle(cornerRadius: 12, style: .continuous).fill(T.pill)
        }
    }

    // MARK: - 处理选中结果

    private func handleImage(_ image: UIImage?) {
        guard let image, let data = ContractImage.jpegData(image) else {
            errorText = "画像の読み込みに失敗しました"
            return
        }
        setPicked(data: data, fileName: "contract.jpg", mime: "image/jpeg")
    }

    private func handlePhotoItem(_ item: PhotosPickerItem) async {
        do {
            guard let raw = try await item.loadTransferable(type: Data.self),
                  let image = UIImage(data: raw),
                  let jpeg = ContractImage.jpegData(image)
            else {
                errorText = "画像の読み込みに失敗しました"
                return
            }
            setPicked(data: jpeg, fileName: "contract.jpg", mime: "image/jpeg")
        } catch {
            errorText = "画像の読み込みに失敗しました"
        }
    }

    private func handleFileImport(_ result: Result<[URL], Error>) {
        switch result {
        case let .success(urls):
            guard let url = urls.first else { return }
            let scoped = url.startAccessingSecurityScopedResource()
            defer { if scoped { url.stopAccessingSecurityScopedResource() } }
            // PDF 不压缩，原始大小即最终大小 → 先看文件大小属性，超 10 MB 直接拒，避免把超大 PDF 整包读进内存才校验。
            // 图片不在这里硬拒：走下面「读取 → 压缩 → 压缩后校验」原路径，否则会误挡掉能压到 10 MB 以内的大图。
            if url.pathExtension.lowercased() == "pdf",
               let fileSize = (try? url.resourceValues(forKeys: [.fileSizeKey]))?.fileSize,
               fileSize > ContractImage.maxBytes
            {
                errorText = "ファイルが大きすぎます（10 MB 以下にしてください）"
                return
            }
            guard let raw = try? Data(contentsOf: url) else {
                errorText = "ファイルの読み込みに失敗しました"
                return
            }
            if url.pathExtension.lowercased() == "pdf" {
                setPicked(data: raw, fileName: url.lastPathComponent, mime: "application/pdf")
            } else if let image = UIImage(data: raw), let jpeg = ContractImage.jpegData(image) {
                setPicked(data: jpeg, fileName: "contract.jpg", mime: "image/jpeg")
            } else {
                errorText = "対応していないファイル形式です"
            }
        case .failure:
            errorText = "ファイルの選択に失敗しました"
        }
    }

    /// 统一落地 — 超 10 MB 拦在客户端（后端也会拦，这里给即时反馈）。
    private func setPicked(data: Data, fileName: String, mime: String) {
        if data.count > ContractImage.maxBytes {
            errorText = "ファイルが大きすぎます（10 MB 以下にしてください）"
            return
        }
        picked = PickedContract(data: data, fileName: fileName, mime: mime)
        errorText = nil
    }
}

/// 图片 → JPEG（缩放 + 压缩），统一交后端 / 老师网页。
enum ContractImage {
    static let maxBytes = 10 * 1024 * 1024
    private static let maxEdge: CGFloat = 2400

    static func jpegData(_ image: UIImage) -> Data? {
        downscale(image, maxEdge: maxEdge).jpegData(compressionQuality: 0.8)
    }

    private static func downscale(_ image: UIImage, maxEdge: CGFloat) -> UIImage {
        let w = image.size.width
        let h = image.size.height
        let longest = max(w, h)
        guard longest > maxEdge, longest > 0 else { return image }
        let scale = maxEdge / longest
        let newSize = CGSize(width: w * scale, height: h * scale)
        let renderer = UIGraphicsImageRenderer(size: newSize)
        return renderer.image { _ in
            image.draw(in: CGRect(origin: .zero, size: newSize))
        }
    }
}

/// UIImagePickerController 包装 — 拍照（SwiftUI 没有原生相机视图，必须桥 UIKit）。
struct CameraPicker: UIViewControllerRepresentable {
    var onCapture: (UIImage?) -> Void
    var onCancel: () -> Void

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_: UIImagePickerController, context _: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    final class Coordinator: NSObject, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
        let parent: CameraPicker
        init(_ parent: CameraPicker) {
            self.parent = parent
        }

        func imagePickerController(
            _: UIImagePickerController,
            didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
        ) {
            parent.onCapture(info[.originalImage] as? UIImage)
        }

        func imagePickerControllerDidCancel(_: UIImagePickerController) {
            parent.onCancel()
        }
    }
}
