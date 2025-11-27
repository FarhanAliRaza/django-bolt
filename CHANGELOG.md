# Changelog

All notable changes to this project will be documented in this file.

## [0.3.6]

### Fixed

- **CORS preflight for non-existent routes** - OPTIONS preflight requests to non-existent routes now return 204 (success) instead of 404, allowing browsers to proceed with the actual request and display proper error messages.
- **CORS headers on 404 responses** - Non-existent routes now include CORS headers using global config, so browsers can read error responses.

### Changed

- Updated CORS documentation to emphasize Django settings-based configuration as the preferred approach.

## [0.3.5]

### Changed

- **Extended Serializer class** - Added more features like write_only, more built-in types to better work with django models.
- **Serializer Config class** - Renamed `Meta` to `Config` to avoid conflicts with `msgspec.Meta`.
- **Field configuration** - Removed direct Meta constraints from `field()` function; validation constraints now require `Annotated` and `Meta`.

### Fixed

- Fixed Python 3.14 annotation errors.

## [0.3.4]

### Added

- Python 3.14 support with msgspec 0.20.
- Advanced Serializer features including `kw_only` support.

### Changed

- Refactored concurrency handling in `sync_to_thread` function.
- Updated logging levels to DEBUG for improved debugging.

## [0.3.3]

### Added

- Docs changes related to serializer.

### Changed

- When None is returned from field validation function it uses the old value instead of setting it into None.

- dispatch function clean for performance.

### Fixed

## [0.3.2]

### Added

- `Serializer` class that extends msgspec struct using which we can validate response data using python function.

### Changed

- sync views are not handled by a thread not called directly in the dispatch function.

### Fixed

- Fixed Exception when orm query evaludated inside of the sync function.

- Fixed `response_model` not working.

## [0.3.1]

### Added

- **`request.user`** - Eager-loaded user objects for authenticated endpoints (eager-loaded at dispatch time)
- Type-safe dependency injection with runtime validation
- `preload_user` parameter to control user loading behavior (default: True for auth endpoints)
- New `user_loader.py` module for extensible user resolution
- Custom user model support via `get_user_model()`
- Override `get_user()` in auth backends for custom user resolution
- Authentication benchmarks for `/auth/me`, `/auth/me-dependency`, and `/auth/context` endpoints

### Changed

- Replaced `is_admin` with `is_superuser` (Django standard naming)
- Optimized Python request/response hot path
- Auth context type system improvements in `python/django_bolt/types.py`
- Guards module updated to use `is_superuser` instead of `is_admin`

### Fixed

-
