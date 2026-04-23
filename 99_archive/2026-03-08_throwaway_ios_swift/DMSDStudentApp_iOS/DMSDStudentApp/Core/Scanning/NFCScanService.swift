import CoreNFC
import Foundation
import Combine

final class NFCScanService: NSObject, ObservableObject {
    enum ScanResult {
        case success
        case failure(String, retryable: Bool)
    }

    private var session: NFCTagReaderSession?
    private var timeoutWorkItem: DispatchWorkItem?
    private var completion: ((ScanResult) -> Void)?
    private var hasReportedResult = false

    func start(timeout: TimeInterval = 12, completion: @escaping (ScanResult) -> Void) {
        stop()

        guard NFCTagReaderSession.readingAvailable else {
            completion(.failure("当前设备不支持 NFC 扫描", retryable: false))
            return
        }

        self.completion = completion
        hasReportedResult = false

        guard let session = NFCTagReaderSession(
            pollingOption: [.iso14443, .iso15693, .iso18092],
            delegate: self,
            queue: nil
        ) else {
            completion(.failure("无法创建 NFC 会话，请稍后重试", retryable: true))
            return
        }
        session.alertMessage = "请将手机贴近点呼机器完成签到"
        self.session = session
        session.begin()

        let timeoutTask = DispatchWorkItem { [weak self] in
            guard let self else { return }
            self.finish(.failure("扫描超时，请再次触碰机器", retryable: true))
            self.session?.invalidate()
            self.session = nil
        }

        timeoutWorkItem = timeoutTask
        DispatchQueue.main.asyncAfter(deadline: .now() + timeout, execute: timeoutTask)
    }

    func stop() {
        timeoutWorkItem?.cancel()
        timeoutWorkItem = nil
        completion = nil

        session?.invalidate()
        session = nil
        hasReportedResult = false
    }

    private func finish(_ result: ScanResult) {
        guard !hasReportedResult else { return }
        hasReportedResult = true

        timeoutWorkItem?.cancel()
        timeoutWorkItem = nil

        completion?(result)
        completion = nil
    }
}

extension NFCScanService: NFCTagReaderSessionDelegate {
    nonisolated func tagReaderSessionDidBecomeActive(_ session: NFCTagReaderSession) {}

    nonisolated func tagReaderSession(_ session: NFCTagReaderSession, didDetect tags: [NFCTag]) {
        Task { @MainActor in
            finish(.success)
            session.invalidate()
            self.session = nil
        }
    }

    nonisolated func tagReaderSession(_ session: NFCTagReaderSession, didInvalidateWithError error: Error) {
        Task { @MainActor in
            guard let readerError = error as? NFCReaderError else {
                finish(.failure("扫描失败，请重试", retryable: true))
                self.session = nil
                return
            }

            switch readerError.code {
            case .readerSessionInvalidationErrorUserCanceled:
                finish(.failure("扫描已取消", retryable: false))
            case .readerSessionInvalidationErrorSessionTimeout:
                finish(.failure("扫描超时，请再次触碰机器", retryable: true))
            default:
                finish(.failure("扫描失败，请再次触碰机器", retryable: true))
            }

            self.session = nil
        }
    }
}
