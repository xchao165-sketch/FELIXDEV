#!/usr/bin/env python3
"""
generate_project.py - FELIXDEV Clean & Working iOS Project Generator
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

# ===================== Core Models & Interfaces =====================
write_file("Sources/FELIXDEV/Core.swift", """\
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

# ===================== App Dependencies & Entry =====================
write_file("Sources/FELIXDEV/App.swift", """\
import SwiftUI

struct AppDependencies {
    let license: any LicenseProviding
    let packageSource: any PackageSource
    let features: any FeatureFlagProviding
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
            RootView(dependencies: dependencies)
        }
    }
}
""")

# ===================== SwiftUI Views =====================
write_file("Sources/FELIXDEV/Views.swift", """\
import SwiftUI

struct RootView: View {
    let dependencies: AppDependencies
    var body: some View {
        TabView {
            DashboardView(dependencies: dependencies).tabItem { Label("Dashboard", systemImage: "house") }
            FileBrowserView(dependencies: dependencies).tabItem { Label("Files", systemImage: "folder") }
            PatchesView(dependencies: dependencies).tabItem { Label("Patches", systemImage: "wrench.and.screwdriver") }
            CleanerView().tabItem { Label("Cleaner", systemImage: "trash") }
            SettingsView().tabItem { Label("Settings", systemImage: "gear") }
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
                        for child in children {
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

# ===================== Localizations =====================
write_file("Resources/en.lproj/Localizable.strings", '"Dashboard" = "Dashboard";\n')

# ===================== GITHUB WORKFLOW =====================
write_file(".github/workflows/qa.yml", """\
name: FELIXDEV QA Offline
on:
  push: { branches: [ main ] }
  pull_request:
  workflow_dispatch:
jobs:
  build:
    name: Build unsigned device app
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Clean previous outputs
        run: rm -rf FELIXDEV DerivedData output
      - name: Generate FELIXDEV project
        run: python3 generate_project.py
      - name: Install XcodeGen
        run: brew install xcodegen
      - name: Generate Xcode project
        run: cd FELIXDEV && xcodegen generate
      - name: Build device app (unsigned)
        run: |
          xcodebuild -project FELIXDEV/FELIXDEV.xcodeproj -scheme FELIXDEV -configuration QA -sdk iphoneos -destination 'generic/platform=iOS' -derivedDataPath DerivedData CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY="" build
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

print("✅ Đã dọn dẹp cấu trúc nguồn và cập nhật generator.")
