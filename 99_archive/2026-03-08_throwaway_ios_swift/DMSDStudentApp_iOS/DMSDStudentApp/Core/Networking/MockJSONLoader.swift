import Foundation

enum MockJSONLoader {
    static func load<T: Decodable>(_ fileName: String, as type: T.Type) -> T? {
        guard let url = Bundle.main.url(forResource: fileName, withExtension: "json", subdirectory: "Mocks/v1") else {
            return nil
        }

        guard let data = try? Data(contentsOf: url) else {
            return nil
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try? decoder.decode(type, from: data)
    }
}
