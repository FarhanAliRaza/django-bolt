# Changelog

All notable changes to this project will be documented in this file.

## [0.3.10]

### Changed

- **Lazy user loading by default** - User loading now uses Django's `SimpleLazyObject` to defer database queries until `request.user` is first accessed. This avoids unnecessary DB calls when user data isn't needed.

## [0.3.9]

### Changed

- **Precompile optimizations** - Handler metadata (parameter extraction, validation, injectors) is now precompiled at route registration time instead of per-request. This eliminates repeated introspection overhead during request handling.

### Added

- **Static analysis for sync handlers** - New `analysis.py` module performs AST-based analysis of handler source code to detect Django ORM usage and blocking I/O patterns. Sync handlers without blocking calls can skip thread pool dispatch for better performance.

## [0.3.8]

### Fixed

- **Static file serving** - Fixed static route handler missing `is_async` and `injector` metadata, which caused static file routes to fail.

### Added

- **CLI `version` command** - Added `django-bolt version` command to display the installed version.
- **`llm.txt`** - Added LLM-friendly project summary file.

## [0.3.7]

### Fixed

- **CORS `@cors()` decorator validation** - The `@cors()` decorator now requires an explicit `origins` argument. Using `@cors()` without arguments previously created an empty CORS config that silently overrode global Django CORS settings, causing credentials and other headers to be missing. Now raises `ValueError` with helpful examples.
- **CORS for POST-only routes** - Routes that only had POST/PUT/PATCH methods (no GET) were not finding their CORS config during preflight, causing CORS failures.

### Changed

- **Shared CORS implementation** - Unified CORS handling between production server and test infrastructure. Test client now reads all CORS settings from Django (`CORS_ALLOWED_ORIGINS`, `CORS_ALLOW_CREDENTIALS`, `CORS_ALLOW_METHODS`, `CORS_ALLOW_HEADERS`, `CORS_EXPOSE_HEADERS`, `CORS_PREFLIGHT_MAX_AGE`).

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
