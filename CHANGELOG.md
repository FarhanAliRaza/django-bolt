# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Request user support for dependency injection
- Type-safe dependency injection with runtime validation

### Changed
- Optimized Python request/response hot path

### Fixed
- Streaming response handling improvements

## [0.3.0] - 2025-11-08

### Added
- Integrated Rust parameter type conversion into hot path for better performance
- Wired parameter metadata from Python to Rust layer
- Simplified computed field API (no @classmethod required)
- Enhanced ORM integration with validators and computed fields

### Fixed
- Fixed streaming response handling with proper async/sync support
- Server-sent events (SSE) improvements for concurrent requests

### Changed
- Performance optimizations in serialization layer

## [0.2.9] - 2025-11-07

### Added
- Sync views support for class-based views
- Support for sync functions with inline parameter
- Better error messaging for serialization
- QuerySet serialization optimization
- Test infrastructure improvements with Claude Code GitHub Workflow
- Python 3.14 test support

### Fixed
- Sync function bug fixes
- Django views registration improvements
- Test layer bug fixes
