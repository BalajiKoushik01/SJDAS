# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-03-27
### Added
- **Enterprise Cloud Sync:** Dedicated navigation for synchronizing local designs with the SJDAS Cloud.
- **Cloud Backup:** "Backup to Cloud" feature in Premium Designer to ensure data persistence and multi-tenant availability.
- **Dynamic Loom Export:** Updated `export_to_loom` to utilize real-time loom specifications (hooks, weave types) from the user session.

### Changed
- **Security Hardening:** Enforced SSL/TLS verification across all network requests (`CloudService`, `CloudSyncWorker`).
- **Standardized Export:** Unified multiple fragmented loom export stubs into a single, robust asynchronous cloud worker flow.
- **Branding:** Transitioned documentation and metadata to an "Enterprise Studio" focus for commercial release.

### Fixed
- **SSL Bypass Vulnerabilities:** Resolved insecure `verify=False` requests that posed risks in production environments.
- **Redundant Logic:** Removed legacy export stubs in `ModernDesignerView` to streamline the codebase.

## [2.0.0] - 2026-02-15
### Added
- **AI Orchestration:** Integration of SAM2 for autonomous motif extraction.
- **FastAPI Backend:** Introduction of the asynchronous cloud-worker architecture for heavy lifting.
- **B2B Web Portal:** Next.js based factory management dashboard.

## [1.0.0] - 2025-11-20
### Added
- **Core Engine:** Initial release of the PyQt6 Jacquard Designer.
- **Loom Drivers:** Basic JC5 and BMP export for industrial looms.
