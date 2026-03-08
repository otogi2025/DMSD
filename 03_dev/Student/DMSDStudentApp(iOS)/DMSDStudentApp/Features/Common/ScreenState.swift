import Foundation

enum ScreenState: Equatable {
    case loading
    case content
    case empty
    case error(String)
}
