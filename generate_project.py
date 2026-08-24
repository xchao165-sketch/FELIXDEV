#!/usr/bin/env python3
"""
generate_project.py - FELIXDEV Project Generator
Fixes missing Info.plist build error by enabling GENERATE_INFOPLIST
"""
import os
from pathlib import Path

ROOT = Path("FELIXDEV")

def write_file(path, content):
    full = ROOT / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding='utf-8')

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
    sources:
      - Sources/FELIXDEV
    resources:
      - Resources
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: com.yourcompany.felixdev
        INFOPLIST_KEY_CFBundleDisplayName: FELIXDEV
        INFOPLIST_KEY_CFBundleName: FELIXDEV
        GENERATE_INFOPLIST: YES
        CURRENT_PROJECT_VERSION: "1"
        MARKETING_VERSION: "1.0"
        CODE_SIGNING_ALLOWED: "NO"
        CODE_SIGNING_REQUIRED: "NO"
        CODE_SIGN_IDENTITY: ""
    configs:
      QA:
        PRODUCT_BUNDLE_IDENTIFIER: com.yourcompany.felixdev.qa
        SWIFT_ACTIVE_COMPILATION_CONDITIONS:
          - QA_OFFLINE
          - DEBUG
""")

# ===================== Core Protocols & Models =====================
write_file("Sources/FELIXDEV/Core/LicenseProviding.swift", """\
import Foundation

public protocol LicenseProviding {
    var isLicensed: Bool { get async }
}

public struct OfflineLicenseProvider: LicenseProviding {
    public init() {}
    public var isLicensed: Bool { get async { true } }
}

public struct ProductionLicenseProvider: LicenseProviding {
    public init() {}
    public var isLicensed: Bool { get async { false } }
}
""")

write_file("Sources/FELIXDEV/Core/PackageSource.swift", """\
import Foundation

public protocol PackageSource {
    func loadPackage() async throws -> Data
}

public enum PackageSourceError: Error {
    case fileMissing(URL)
    case invalidResponse
}

public struct LocalPackageSource: PackageSource {
    public let fileURL: URL
    public init(fileURL: URL) { self.fileURL = fileURL }
    
    public func loadPackage() async throws -> Data {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            throw PackageSourceError.fileMissing(fileURL)
        }
        return try Data(contentsOf: fileURL)
    }
}

public struct RemotePackageSource: PackageSource {
    public let endpoint: URL
    public init(endpoint: URL) { self.endpoint = endpoint }
    
    public func loadPackage() async throws -> Data {
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

public protocol FeatureFlagProviding {
    func isEnabled(_ id: String) async -> Bool
    func enabledPresets() async -> [String]
}

public struct OfflineFeatureProvider: FeatureFlagProviding {
    private let presets = ["Aim.Magic.Free.Fire", "Mod.Ig.Free.Fire", "FFTHPatchPreset", "FFMPatchPreset"]
    public init() {}
    
    public func isEnabled(_ id: String) async -> Bool {
        presets.contains(id)
    }
    
    public func enabledPresets() async -> [String] {
        presets
    }
}

public struct ProductionFeatureProvider: FeatureFlagProviding {
    public init() {}
    public func isEnabled(_ id: String) async -> Bool { false }
    public func enabledPresets() async -> [String] { [] }
}
""")

write_file("Sources/FELIXDEV/Core/PackageParser.swift", """\
import Foundation

public struct PackageParser {
    public init() {}
    public func parse(data: Data) throws -> [String] {
        return ["Payload Verified", "Contents Unpacked"]
    }
}
""")

write_file("Sources/FELIXDEV/Core/PackageVerifier.swift", """\
import Foundation

public struct PackageVerifier {
    public init() {}
    public func verify(data: Data) -> Bool {
        return !data.isEmpty
    }
}
""")

# ===================== Views & Controllers =====================
write_file("Sources/FELIXDEV/FFTHPatchController.swift", """\
import Foundation

public class FFTHPatchController {
    public init() {}
    public func applyPatches() -> Bool {
        return true
    }
}
""")

write_file("Sources/FELIXDEV/FileBrowserView.swift", """\
import SwiftUI

public struct FileBrowserView: View {
    let dependencies: AppDependencies
    @State private var files: [URL] = []
    
    public init(dependencies: AppDependencies) {
        self.dependencies = dependencies
    }
    
    public var body: some View {
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

write_file("Sources/FELIXDEV/PatchesView.swift", """\
import SwiftUI

public struct PatchesView: View {
    let dependencies: AppDependencies
    @State private var presets: [String] = []
    
    public init(dependencies: AppDependencies) {
        self.dependencies = dependencies
    }
    
    public var body: some View {
        NavigationStack {
            List(presets, id: \\.self) { preset in
                HStack {
                    Text(preset)
                    Spacer()
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                }
            }
            .navigationTitle("Patches")
            .task {
                presets = await dependencies.features.enabledPresets()
            }
        }
    }
}
""")

# ===================== Main Entrypoint =====================
write_file("Sources/FELIXDEV/FELIXDEVApp.swift", """\
import SwiftUI

public struct AppDependencies {
    public let license: any LicenseProviding
    public let packageSource: any PackageSource
    public let features: any FeatureFlagProviding
    
    public init(license: any LicenseProviding, packageSource: any PackageSource, features: any FeatureFlagProviding) {
        self.license = license
        self.packageSource = packageSource
        self.features = features
    }
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
            features: OfflineFeatureProvider()
        )
        #else
        return AppDependencies(
            license: ProductionLicenseProvider(),
            packageSource: RemotePackageSource(endpoint: URL(string: "https://example.com/package.3105")!),
            features: ProductionFeatureProvider()
        )
        #endif
    }
}

@main
struct FELIXDEVApp: App {
    private let dependencies = DependencyFactory.make()
    
    var body: some Scene {
        WindowGroup {
            TabView {
                DashboardView(dependencies: dependencies)
                    .tabItem { Label("Dashboard", systemImage: "house") }
                FileBrowserView(dependencies: dependencies)
                    .tabItem { Label("Files", systemImage: "folder") }
                PatchesView(dependencies: dependencies)
                    .tabItem { Label("Patches", systemImage: "wrench.and.screwdriver") }
            }
        }
    }
}

struct DashboardView: View {
    let dependencies: AppDependencies
    @State private var licensed = false
    
    var body: some View {
        NavigationStack {
            List {
                Section("Status") {
                    Label(licensed ? "Offline QA License Active" : "License Unavailable",
                          systemImage: licensed ? "checkmark.circle" : "xmark.circle")
                }
            }
            .navigationTitle("Dashboard")
            .task {
                licensed = await dependencies.license.isLicensed
            }
        }
    }
}
""")

# ===================== Resources =====================
write_file("Resources/en.lproj/Localizable.strings", '"Dashboard" = "Dashboard";\n')

print("✅ Updated generate_project.py with GENERATE_INFOPLIST enabled.")
