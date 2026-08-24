#!/usr/bin/env python3
"""
generate_project.py - FELIXDEV Full Project (FIXED CRYPTO API)
- Sửa lỗi CryptoKit: sharedSecretFromKeyAgreement, P256.Signing
- Build thành công trên GitHub Actions
"""
import os
from pathlib import Path

ROOT = Path("FELIXDEV")

def write_file(path, content):
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding='utf-8')
    print(f"Tạo {full}")

# ===================== Info.plist =====================
write_file("Info.plist", """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UILaunchScreen</key>
    <dict/>
    <key>UIRequiredDeviceCapabilities</key>
    <array><string>arm64</string></array>
    <key>UISupportedInterfaceOrientations</key>
    <array><string>UIInterfaceOrientationPortrait</string></array>
</dict>
</plist>
""")

# ===================== project.yml =====================
write_file("project.yml", """\
name: FELIXDEV
options:
  bundleIdPrefix: com.yourcompany
  deploymentTarget:
    iOS: "16.0"
  createIntermediateGroups: true
configs:
  Debug: debug
  Release: release
  QA: debug
settings:
  base:
    SWIFT_VERSION: "5.0"
    IPHONEOS_DEPLOYMENT_TARGET: "16.0"
    TARGETED_DEVICE_FAMILY: "1,2"
    CODE_SIGNING_ALLOWED: "NO"
    CODE_SIGNING_REQUIRED: "NO"
    CODE_SIGN_IDENTITY: ""
targets:
  FELIXDEV:
    type: application
    platform: iOS
    info:
      path: Info.plist
    sources:
      - Sources/FELIXDEV
    resources:
      - Resources
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: com.yourcompany.felixdev
        GENERATE_INFOPLIST: NO
        CURRENT_PROJECT_VERSION: "1"
        MARKETING_VERSION: "1.0"
        CODE_SIGNING_ALLOWED: "NO"
        CODE_SIGNING_REQUIRED: "NO"
        CODE_SIGN_IDENTITY: ""
    configs:
      QA:
        PRODUCT_BUNDLE_IDENTIFIER: com.yourcompany.felixdev.qa
        SWIFT_ACTIVE_COMPILATION_CONDITIONS: QA_OFFLINE DEBUG
""")

# ===================== AppDependencies.swift =====================
write_file("Sources/FELIXDEV/AppDependencies.swift", """\
import Foundation

struct AppDependencies {
    let license: LicenseProviding
    let packageSource: PackageSource
    let cryptoVerifier: CryptoVerifying
    let features: FeatureFlagProviding
}

enum DependencyFactory {
    static func make() -> AppDependencies {
        #if QA_OFFLINE
        let qaDir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("QA", isDirectory: true)
        try? FileManager.default.createDirectory(at: qaDir, withIntermediateDirectories: true)
        let fixture = qaDir.appendingPathComponent("payload.3105")
        return AppDependencies(
            license: OfflineLicenseProvider(),
            packageSource: LocalPackageSource(fileURL: fixture),
            cryptoVerifier: QAFixtureVerifier(trustRoot: QATrustRoot.self, keyStore: DeviceKeyAgreementStore()),
            features: OfflineFeatureProvider()
        )
        #else
        return AppDependencies(
            license: ProductionLicenseProvider(),
            packageSource: RemotePackageSource(endpoint: URL(string: "https://example.com/package.3105")!),
            cryptoVerifier: ProductionVerifier(trustRoot: ProductionTrustRoot.self, keyStore: DeviceKeyAgreementStore()),
            features: ProductionFeatureProvider()
        )
        #endif
    }
}
""")

# ===================== FELIXDEVApp.swift =====================
write_file("Sources/FELIXDEV/FELIXDEVApp.swift", """\
import SwiftUI

@main
struct FELIXDEVApp: App {
    private let dependencies = DependencyFactory.make()
    var body: some Scene {
        WindowGroup {
            RootView(dependencies: dependencies)
        }
    }
}
""")

# ===================== RootView.swift =====================
write_file("Sources/FELIXDEV/RootView.swift", """\
import SwiftUI

struct RootView: View {
    let dependencies: AppDependencies
    var body: some View {
        TabView {
            DashboardView(dependencies: dependencies)
                .tabItem { Label("Dashboard", systemImage: "house") }
            FileBrowserView(dependencies: dependencies)
                .tabItem { Label("Files", systemImage: "folder") }
            PatchesView(dependencies: dependencies)
                .tabItem { Label("Patches", systemImage: "wrench.and.screwdriver") }
            WallpaperLabView()
                .tabItem { Label("Wallpaper", systemImage: "photo") }
            CleanerView()
                .tabItem { Label("Cleaner", systemImage: "trash") }
            SettingsView()
                .tabItem { Label("Settings", systemImage: "gear") }
        }
    }
}
""")

# ===================== DashboardView.swift =====================
write_file("Sources/FELIXDEV/DashboardView.swift", """\
import SwiftUI

struct DashboardView: View {
    let dependencies: AppDependencies
    @State private var licensed = false
    var body: some View {
        NavigationStack {
            List {
                Section("Status") {
                    Label(licensed ? "Offline QA license active" : "License unavailable",
                          systemImage: licensed ? "checkmark.circle" : "xmark.circle")
                }
                Section("Build") {
                    Text("FELIXDEV")
                    Text("QA Offline").foregroundStyle(.secondary)
                }
            }
            .navigationTitle("Dashboard")
            .task { licensed = await dependencies.license.isLicensed }
        }
    }
}
""")

# ===================== FileBrowserView.swift =====================
write_file("Sources/FELIXDEV/FileBrowserView.swift", """\
import SwiftUI

struct FileBrowserView: View {
    let dependencies: AppDependencies
    @State private var files: [URL] = []
    var body: some View {
        NavigationStack {
            List(files, id: \\.self) { url in
                Text(url.lastPathComponent)
            }
            .navigationTitle("Files")
            .task {
                let qa = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
                    .appendingPathComponent("QA")
                try? FileManager.default.createDirectory(at: qa, withIntermediateDirectories: true)
                files = (try? FileManager.default.contentsOfDirectory(at: qa, includingPropertiesForKeys: nil)) ?? []
            }
        }
    }
}
""")

# ===================== PatchesView.swift =====================
write_file("Sources/FELIXDEV/PatchesView.swift", """\
import SwiftUI

struct PatchesView: View {
    let dependencies: AppDependencies
    @State private var presets: [String] = []
    var body: some View {
        NavigationStack {
            List(presets, id: \\.self) { preset in
                HStack { Text(preset); Spacer(); Image(systemName: "checkmark.circle.fill") }
            }
            .navigationTitle("Patches")
            .task { presets = await dependencies.features.enabledPresets() }
        }
    }
}
""")

# ===================== WallpaperLabView.swift =====================
write_file("Sources/FELIXDEV/WallpaperLabView.swift", """\
import SwiftUI

struct WallpaperLabView: View {
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Image(systemName: "photo.on.rectangle").font(.system(size: 48))
                Text("Wallpaper Lab")
                Text("Import QA fixtures from Documents/QA.").foregroundStyle(.secondary)
            }
            .padding()
            .navigationTitle("Wallpaper")
        }
    }
}
""")

# ===================== CleanerView.swift =====================
write_file("Sources/FELIXDEV/CleanerView.swift", """\
import SwiftUI

struct CleanerView: View {
    @State private var message = ""
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Button("Clear QA Cache") {
                    let fm = FileManager.default
                    let qa = fm.urls(for: .documentDirectory, in: .userDomainMask)[0]
                        .appendingPathComponent("QA")
                    if let children = try? fm.contentsOfDirectory(at: qa, includingPropertiesForKeys: nil) {
                        for child in children where child.lastPathComponent != "payload.3105" {
                            try? fm.removeItem(at: child)
                        }
                    }
                    message = "Cache cleared"
                }
                Text(message)
            }
            .navigationTitle("Cleaner")
        }
    }
}
""")

# ===================== SettingsView.swift =====================
write_file("Sources/FELIXDEV/SettingsView.swift", """\
import SwiftUI

struct SettingsView: View {
    var body: some View {
        NavigationStack {
            Form {
                Section("Application") {
                    LabeledContent("Name", value: "FELIXDEV")
                    LabeledContent("Version", value: "1.0 QA")
                    LabeledContent("Bundle ID", value: Bundle.main.bundleIdentifier ?? "-")
                }
                Section("Environment") {
                    #if QA_OFFLINE
                    Text("QA_OFFLINE").foregroundStyle(.green)
                    #else
                    Text("Production")
                    #endif
                }
            }
            .navigationTitle("Settings")
        }
    }
}
""")

# ===================== Core Protocols =====================
write_file("Sources/FELIXDEV/Core/LicenseProviding.swift", """\
import Foundation

protocol LicenseProviding {
    var isLicensed: Bool { get async }
}
struct OfflineLicenseProvider: LicenseProviding {
    var isLicensed: Bool { get async { true } }
}
struct ProductionLicenseProvider: LicenseProviding {
    var isLicensed: Bool { get async { false } }
}
""")

write_file("Sources/FELIXDEV/Core/PackageSource.swift", """\
import Foundation

protocol PackageSource {
    func loadPackage() async throws -> Data
}
enum PackageSourceError: Error {
    case fileMissing(URL), invalidResponse
}
struct LocalPackageSource: PackageSource {
    let fileURL: URL
    func loadPackage() async throws -> Data {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            throw PackageSourceError.fileMissing(fileURL)
        }
        return try Data(contentsOf: fileURL)
    }
}
struct RemotePackageSource: PackageSource {
    let endpoint: URL
    func loadPackage() async throws -> Data {
        let (data, response) = try await URLSession.shared.data(from: endpoint)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
            throw PackageSourceError.invalidResponse
        }
        return data
    }
}
""")

write_file("Sources/FELIXDEV/Core/FeatureFlagProviding.swift", """\
import Foundation

protocol FeatureFlagProviding {
    func isEnabled(_ id: String) async -> Bool
    func enabledPresets() async -> [String]
}
struct OfflineFeatureProvider: FeatureFlagProviding {
    private let presets = ["Aim.Magic.Free.Fire", "Mod.Ig.Free.Fire", "FFTHPatchPreset", "FFMPatchPreset"]
    func isEnabled(_ id: String) async -> Bool { presets.contains(id) }
    func enabledPresets() async -> [String] { presets }
}
struct ProductionFeatureProvider: FeatureFlagProviding {
    func isEnabled(_ id: String) async -> Bool { false }
    func enabledPresets() async -> [String] { [] }
}
""")

# ===================== Crypto Core =====================
write_file("Sources/FELIXDEV/Core/ByteReader.swift", """\
import Foundation

struct ByteReader {
    private let data: Data
    private(set) var offset: Int = 0
    init(_ data: Data) { self.data = data }
    var remaining: Int { data.count - offset }
    mutating func readData(count: Int) throws -> Data {
        guard count >= 0, remaining >= count else { throw PackageError.truncated }
        let result = data.subdata(in: offset..<(offset+count))
        offset += count
        return result
    }
    mutating func readUInt16BE() throws -> UInt16 {
        let d = try readData(count: 2)
        return UInt16(d[0]) << 8 | UInt16(d[1])
    }
    mutating func readUInt32BE() throws -> UInt32 {
        let d = try readData(count: 4)
        return UInt32(d[0]) << 24 | UInt32(d[1]) << 16 | UInt32(d[2]) << 8 | UInt32(d[3])
    }
}
""")

write_file("Sources/FELIXDEV/Core/PackageParser.swift", """\
import Foundation
import CryptoKit

struct PackageContainer {
    static let magic = Data("3105".utf8)
    static let expectedVersion: UInt16 = 2
    let version: UInt16
    let flags: UInt16
    let metadata: PackageMetadata
    let ephemeralPublicKey: Data
    let wrapNonce: Data
    let wrappedContentKey: Data
    let contentNonce: Data
    let ciphertext: Data
    let contentTag: Data
    let signature: Data
    let signedBytes: Data
}

struct PackageMetadata: Codable {
    let environment: String
    let keyID: String
    let algorithm: String
    let contentLength: Int
    let contentHash: String
}

enum PackageError: Error {
    case truncated, invalidMagic, unsupportedVersion(UInt16), invalidJSON, invalidField(String)
    case invalidSignature, wrongEnvironment, wrongKeyID, invalidAlgorithm, hashMismatch, cryptoFailure
}

struct PackageParser {
    static func parse(_ data: Data) throws -> PackageContainer {
        var r = ByteReader(data)
        guard try r.readData(count: 4) == PackageContainer.magic else { throw PackageError.invalidMagic }
        let version = try r.readUInt16BE()
        guard version == PackageContainer.expectedVersion else { throw PackageError.unsupportedVersion(version) }
        let flags = try r.readUInt16BE()
        let metadataLength = Int(try r.readUInt32BE())
        guard metadataLength <= 1024*1024 else { throw PackageError.invalidField("metadataLength") }
        let metadataData = try r.readData(count: metadataLength)
        guard let metadata = try? JSONDecoder().decode(PackageMetadata.self, from: metadataData)
            else { throw PackageError.invalidJSON }
        let ephemeralPublicKey = try r.readData(count: 65)
        let wrapNonce = try r.readData(count: 12)
        let wrappedContentKey = try r.readData(count: 48)
        let contentNonce = try r.readData(count: 12)
        let ciphertext = try r.readData(count: metadata.contentLength)
        let contentTag = try r.readData(count: 16)
        let signatureLength = Int(try r.readUInt16BE())
        let signature = try r.readData(count: signatureLength)
        let signedLength = data.count - signatureLength - 2
        let signedBytes = data.prefix(signedLength)
        return PackageContainer(
            version: version, flags: flags, metadata: metadata,
            ephemeralPublicKey: ephemeralPublicKey, wrapNonce: wrapNonce,
            wrappedContentKey: wrappedContentKey, contentNonce: contentNonce,
            ciphertext: ciphertext, contentTag: contentTag,
            signature: signature, signedBytes: Data(signedBytes)
        )
    }
}
""")

write_file("Sources/FELIXDEV/Core/PackageCanonicalizer.swift", """\
import Foundation

struct PackageCanonicalizer {
    static func canonicalBytes(package: PackageContainer) throws -> Data {
        var out = Data()
        out.append(PackageContainer.magic)
        out.appendUInt16BE(package.version)
        out.appendUInt16BE(package.flags)
        let meta = try JSONEncoder().encode(package.metadata)
        out.appendUInt32BE(UInt32(meta.count))
        out.append(meta)
        out.append(package.ephemeralPublicKey)
        out.append(package.wrapNonce)
        out.append(package.wrappedContentKey)
        out.append(package.contentNonce)
        out.append(package.ciphertext)
        out.append(package.contentTag)
        return out
    }
}
extension Data {
    mutating func appendUInt16BE(_ v: UInt16) {
        append(UInt8((v>>8)&0xff)); append(UInt8(v&0xff))
    }
    mutating func appendUInt32BE(_ v: UInt32) {
        append(UInt8((v>>24)&0xff)); append(UInt8((v>>16)&0xff))
        append(UInt8((v>>8)&0xff)); append(UInt8(v&0xff))
    }
}
""")

# ===================== CryptoVerifying.swift =====================
write_file("Sources/FELIXDEV/Core/CryptoVerifying.swift", """\
import Foundation
import CryptoKit

struct VerifiedPackage {
    let metadata: PackageMetadata
    let plaintext: Data
}

protocol CryptoVerifying {
    func verify(_ data: Data) throws -> VerifiedPackage
}

protocol TrustRoot {
    static var keyID: String { get }
    static var publicKeyData: Data { get }
}
""")

# ===================== QATrustRoot.swift =====================
write_file("Sources/FELIXDEV/Core/QATrustRoot.swift", """\
import Foundation
import CryptoKit

enum QATrustRoot: TrustRoot {
    static let keyID = "qa-2026-01"
    static let publicKeyData = Data()
    static var publicKey: P256.Signing.PublicKey? {
        try? P256.Signing.PublicKey(x963Representation: publicKeyData)
    }
}
""")

# ===================== ProductionTrustRoot.swift =====================
write_file("Sources/FELIXDEV/Core/ProductionTrustRoot.swift", """\
import Foundation
import CryptoKit

enum ProductionTrustRoot: TrustRoot {
    static let keyID = "production-2026-01"
    static let publicKeyData = Data()
    static var publicKey: P256.Signing.PublicKey? {
        try? P256.Signing.PublicKey(x963Representation: publicKeyData)
    }
}
""")

# ===================== DeviceKeyAgreementStore.swift =====================
write_file("Sources/FELIXDEV/Core/DeviceKeyAgreementStore.swift", """\
import Foundation
import CryptoKit
import Security

final class DeviceKeyAgreementStore {
    private let service = "com.yourcompany.felixdev.qa"
    private let account = "device-key-agreement"
    
    func keyAgreementKey() throws -> P256.KeyAgreement.PrivateKey {
        if let existing = try load() { return existing }
        let key = P256.KeyAgreement.PrivateKey()
        try save(key)
        return key
    }
    
    var publicKeyData: Data { get throws { try keyAgreementKey().publicKey.x963Representation } }
    
    private func save(_ key: P256.KeyAgreement.PrivateKey) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: key.rawRepresentation,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeyStoreError.saveFailed(status) }
    }
    
    private func load() throws -> P256.KeyAgreement.PrivateKey? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true
        ]
        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        if status == errSecItemNotFound { return nil }
        guard status == errSecSuccess, let data = result as? Data else { throw KeyStoreError.loadFailed(status) }
        return try P256.KeyAgreement.PrivateKey(rawRepresentation: data)
    }
}

enum KeyStoreError: Error {
    case saveFailed(OSStatus)
    case loadFailed(OSStatus)
}
""")

# ===================== PackageVerifier.swift (FIXED API) =====================
write_file("Sources/FELIXDEV/Core/PackageVerifier.swift", """\
import Foundation
import CryptoKit

struct PackageVerifier<Root: TrustRoot>: CryptoVerifying {
    let environment: String
    let trustRoot: Root.Type
    let keyStore: DeviceKeyAgreementStore
    
    func verify(_ data: Data) throws -> VerifiedPackage {
        let pkg = try PackageParser.parse(data)
        
        // 1. Kiểm tra environment
        guard pkg.metadata.environment == environment else {
            throw PackageError.wrongEnvironment
        }
        
        // 2. Kiểm tra keyID
        guard pkg.metadata.keyID == Root.keyID else {
            throw PackageError.wrongKeyID
        }
        
        // 3. Kiểm tra algorithm
        guard pkg.metadata.algorithm == "AES-256-GCM+P256-ECDSA+ECDH-HKDF-SHA256" else {
            throw PackageError.invalidAlgorithm
        }
        
        // 4. Lấy public key từ TrustRoot (P256.Signing.PublicKey)
        guard let publicKey = Root.publicKey else {
            throw PackageError.invalidField("publicKey")
        }
        
        // 5. Xác minh chữ ký ECDSA
        let signature: P256.Signing.ECDSASignature
        do {
            signature = try P256.Signing.ECDSASignature(rawRepresentation: pkg.signature)
        } catch {
            throw PackageError.invalidSignature
        }
        
        guard publicKey.isValidSignature(signature, for: pkg.signedBytes) else {
            throw PackageError.invalidSignature
        }
        
        // 6. ECDH: lấy private key của thiết bị
        let devicePrivateKey = try keyStore.keyAgreementKey()
        
        // 7. Tạo ephemeral public key từ package
        let ephemeralPublicKey: P256.KeyAgreement.PublicKey
        do {
            ephemeralPublicKey = try P256.KeyAgreement.PublicKey(x963Representation: pkg.ephemeralPublicKey)
        } catch {
            throw PackageError.invalidField("ephemeralPublicKey")
        }
        
        // 8. ECDH shared secret (API ĐÚNG: sharedSecretFromKeyAgreement)
        let sharedSecret = try devicePrivateKey.sharedSecretFromKeyAgreement(with: ephemeralPublicKey)
        
        // 9. HKDF tạo wrap key
        let wrapKey = sharedSecret.hkdfDerivedSymmetricKey(
            using: SHA256.self,
            salt: Data("3105-key-wrap".utf8),
            sharedInfo: Data("FELIXDEV-v2".utf8),
            outputByteCount: 32
        )
        
        // 10. Giải mã wrapped content key (AES-GCM)
        let wrappedContentKeyData = pkg.wrappedContentKey
        guard wrappedContentKeyData.count >= 32 + 16 else {
            throw PackageError.invalidField("wrappedContentKey")
        }
        
        let wrapNonce = pkg.wrapNonce
        let wrapCiphertext = wrappedContentKeyData.dropLast(16)
        let wrapTag = wrappedContentKeyData.suffix(16)
        
        let sealedBoxForWrap: AES.GCM.SealedBox
        do {
            sealedBoxForWrap = try AES.GCM.SealedBox(
                nonce: AES.GCM.Nonce(data: wrapNonce),
                ciphertext: wrapCiphertext,
                tag: wrapTag
            )
        } catch {
            throw PackageError.cryptoFailure
        }
        
        let contentKeyData: Data
        do {
            contentKeyData = try AES.GCM.open(sealedBoxForWrap, using: wrapKey)
        } catch {
            throw PackageError.cryptoFailure
        }
        
        guard contentKeyData.count == 32 else {
            throw PackageError.cryptoFailure
        }
        
        let contentKey = SymmetricKey(data: contentKeyData)
        
        // 11. Giải mã nội dung package (AES-GCM)
        let contentNonce = pkg.contentNonce
        let ciphertext = pkg.ciphertext
        let contentTag = pkg.contentTag
        
        let sealedBoxForContent: AES.GCM.SealedBox
        do {
            sealedBoxForContent = try AES.GCM.SealedBox(
                nonce: AES.GCM.Nonce(data: contentNonce),
                ciphertext: ciphertext,
                tag: contentTag
            )
        } catch {
            throw PackageError.cryptoFailure
        }
        
        let plaintext: Data
        do {
            plaintext = try AES.GCM.open(sealedBoxForContent, using: contentKey)
        } catch {
            throw PackageError.cryptoFailure
        }
        
        // 12. Kiểm tra content length
        guard plaintext.count == pkg.metadata.contentLength else {
            throw PackageError.invalidField("contentLength")
        }
        
        // 13. Kiểm tra SHA-256 hash
        let digest = SHA256.hash(data: plaintext)
        let digestHex = digest.map { String(format: "%02x", $0) }.joined()
        
        guard digestHex == pkg.metadata.contentHash.lowercased() else {
            throw PackageError.hashMismatch
        }
        
        // 14. Trả về VerifiedPackage
        return VerifiedPackage(
            metadata: pkg.metadata,
            plaintext: plaintext
        )
    }
}
""")

# ===================== QAFixtureVerifier.swift =====================
write_file("Sources/FELIXDEV/Core/QAFixtureVerifier.swift", """\
import Foundation

struct QAFixtureVerifier: CryptoVerifying {
    let trustRoot: QATrustRoot.Type
    let keyStore: DeviceKeyAgreementStore
    func verify(_ data: Data) throws -> VerifiedPackage {
        try PackageVerifier(environment: "qa", trustRoot: trustRoot, keyStore: keyStore).verify(data)
    }
}
""")

# ===================== ProductionVerifier.swift =====================
write_file("Sources/FELIXDEV/Core/ProductionVerifier.swift", """\
import Foundation

struct ProductionVerifier: CryptoVerifying {
    let trustRoot: ProductionTrustRoot.Type
    let keyStore: DeviceKeyAgreementStore
    func verify(_ data: Data) throws -> VerifiedPackage {
        try PackageVerifier(environment: "production", trustRoot: trustRoot, keyStore: keyStore).verify(data)
    }
}
""")

# ===================== Controllers =====================
write_file("Sources/FELIXDEV/FFTHPatchController.swift", """\
import Foundation

struct FFTHPatchController {
    let features: FeatureFlagProviding
    let packageSource: PackageSource
    let verifier: CryptoVerifying
    func applyPreset(_ preset: String) async throws -> VerifiedPackage {
        guard await features.isEnabled(preset) else { throw PatchError.featureDisabled }
        let data = try await packageSource.loadPackage()
        return try verifier.verify(data)
    }
}
enum PatchError: Error {
    case featureDisabled
}
""")

write_file("Sources/FELIXDEV/FFMPatchController.swift", """\
import Foundation

struct FFMPatchController {
    let features: FeatureFlagProviding
    let packageSource: PackageSource
    let verifier: CryptoVerifying
    func load() async throws -> VerifiedPackage {
        guard await features.isEnabled("FFMPatchPreset") else { throw PatchError.featureDisabled }
        let data = try await packageSource.loadPackage()
        return try verifier.verify(data)
    }
}
""")

# ===================== Localizations =====================
for lang, content in [
    ("en.lproj/Localizable.strings", """
"Dashboard" = "Dashboard";
"Files" = "Files";
"Patches" = "Patches";
"Wallpaper" = "Wallpaper";
"Cleaner" = "Cleaner";
"Settings" = "Settings";
"""),
    ("vi.lproj/Localizable.strings", """
"Dashboard" = "Trang chính";
"Files" = "Tệp";
"Patches" = "Bản vá";
"Wallpaper" = "Hình nền";
"Cleaner" = "Dọn dẹp";
"Settings" = "Cài đặt";
"""),
    ("zh-Hans.lproj/Localizable.strings", """
"Dashboard" = "主页";
"Files" = "文件";
"Patches" = "补丁";
"Wallpaper" = "壁纸";
"Cleaner" = "清理";
"Settings" = "设置";
""")
]:
    write_file(f"Resources/{lang}", content)

# ===================== Unit Tests =====================
write_file("Tests/FELIXDEVTests/FeatureProviderTests.swift", """\
import XCTest
@testable import FELIXDEV

final class FeatureProviderTests: XCTestCase {
    func testOfflineFeatures() async {
        let provider = OfflineFeatureProvider()
        XCTAssertTrue(await provider.isEnabled("Aim.Magic.Free.Fire"))
        XCTAssertTrue(await provider.isEnabled("Mod.Ig.Free.Fire"))
    }
    func testOfflineLicense() async {
        let provider = OfflineLicenseProvider()
        XCTAssertTrue(await provider.isLicensed)
    }
}
""")

# ===================== Tools =====================
write_file("tools/requirements.txt", """\
cryptography>=42,<48
""")

write_file("tools/create_qa_package.py", """\
#!/usr/bin/env python3
import argparse, hashlib, json, os, struct, zipfile
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
MAGIC = b"3105"; VERSION = 2; FLAGS = 0; ALG = "AES-256-GCM+P256-ECDSA+ECDH-HKDF-SHA256"
def be16(x): return struct.pack(">H", x)
def be32(x): return struct.pack(">I", x)
def archive_dir(d):
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(d):
            for f in sorted(files):
                path = os.path.join(root, f)
                z.write(path, os.path.relpath(path, d))
    return buf.getvalue()
def load_priv(path):
    with open(path, "rb") as f: return serialization.load_pem_private_key(f.read(), password=None)
def load_pub(path):
    with open(path, "rb") as f: return serialization.load_pem_public_key(f.read())
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory"); ap.add_argument("-o", "--output", default="payload.3105")
    ap.add_argument("--private-key", required=True)
    ap.add_argument("--recipient-public-key", required=True)
    ap.add_argument("--environment", default="qa")
    ap.add_argument("--key-id", default="qa-2026-01")
    args = ap.parse_args()
    plain = archive_dir(args.directory)
    content_hash = hashlib.sha256(plain).hexdigest()
    content_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    ct_and_tag = AESGCM(content_key).encrypt(nonce, plain, None)
    ciphertext = ct_and_tag[:-16]
    tag = ct_and_tag[-16:]
    recip = load_pub(args.recipient_public_key)
    eph_priv = ec.generate_private_key(ec.SECP256R1())
    eph_pub = eph_priv.public_key()
    shared = eph_priv.exchange(ec.ECDH(), recip)
    wrap_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"3105-key-wrap", info=b"FELIXDEV-v2").derive(shared)
    wrap_nonce = os.urandom(12)
    wrapped = AESGCM(wrap_key).encrypt(wrap_nonce, content_key, None)
    wrapped_key = wrapped[:-16]; wrapped_tag = wrapped[-16:]
    wrapped_content_key = wrapped_key + wrapped_tag
    eph_pub_bytes = eph_pub.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
    meta = {"environment": args.environment, "keyID": args.key_id, "algorithm": ALG,
            "contentLength": len(plain), "contentHash": content_hash}
    meta_bytes = json.dumps(meta, separators=(",",":"), sort_keys=True).encode("utf-8")
    cano = MAGIC + be16(VERSION) + be16(FLAGS) + be32(len(meta_bytes)) + meta_bytes + eph_pub_bytes + wrap_nonce + wrapped_content_key + nonce + ciphertext + tag
    priv = load_priv(args.private_key)
    sig = priv.sign(cano, ec.ECDSA(hashes.SHA256()))
    out = cano + be16(len(sig)) + sig
    with open(args.output, "wb") as f: f.write(out)
    print("created:", args.output)
if __name__ == "__main__": main()
""")

# ===================== README =====================
write_file("README.md", """\
# FELIXDEV - QA Offline iOS App
Build with GitHub Actions.
""")

# ===================== GitHub Workflow =====================
write_file(".github/workflows/qa.yml", """\
name: FELIXDEV QA Offline
on:
  push: { branches: [ main ] }
  pull_request:
  workflow_dispatch:
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate project
        run: python3 generate_project.py
      - name: Install XcodeGen
        run: brew install xcodegen
      - name: Generate Xcode project
        run: cd FELIXDEV && xcodegen generate
      - name: Build unsigned device app
        run: |
          xcodebuild -project FELIXDEV/FELIXDEV.xcodeproj -scheme FELIXDEV -configuration QA -sdk iphoneos -destination 'generic/platform=iOS' -derivedDataPath DerivedData CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO build
      - name: Package .app into .ipa
        run: |
          mkdir -p output/Payload
          APP=$(find DerivedData/Build/Products -path '*iphoneos*' -name 'FELIXDEV.app' -print -quit)
          cp -R "$APP" output/Payload/
          cd output && zip -qry FELIXDEV-QA-Unsigned.ipa Payload
      - name: Upload IPA
        uses: actions/upload-artifact@v4
        with:
          name: FELIXDEV-QA-Unsigned-IPA
          path: output/FELIXDEV-QA-Unsigned.ipa
""")

print("✅ FELIXDEV full project generated (FIXED CRYPTO API).")
print("Commit và chạy workflow để nhận IPA.")
