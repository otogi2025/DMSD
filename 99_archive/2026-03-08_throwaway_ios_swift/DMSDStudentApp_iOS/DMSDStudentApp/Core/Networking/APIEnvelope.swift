import Foundation

struct APIErrorPayload: Codable {
    let code: String
    let message: String
    let detail: String?
}

struct APIEnvelope<T: Codable>: Codable {
    let ok: Bool
    let data: T?
    let error: APIErrorPayload?
}
