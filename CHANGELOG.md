# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Performance

- **Rust hot path optimizations** - Merged GIL acquisitions, removed redundant `to_ascii_lowercase()` calls in header extraction, optimized WebSocket upgrade guards to avoid allocations.
- **Python hot path optimizations** - Changed `_handler_meta` to use `handler_id` (int) keys instead of callable keys for faster O(1) hash lookups.
- **Dispatch loop optimizations** - Eliminated `hasattr()` checks by initializing `_handler_api_map` in `__init__`, cached `isEnabledFor()` timing decisions per logging middleware instance, and reduced redundant `.get()` calls by pre-extracting commonly used metadata before conditional branches.
- **Lazy user loading optimization** - Replaced lambda with `functools.partial` for `SimpleLazyObject` user loader, avoiding closure allocation overhead per authenticated request.
- **Response serialization fast path** - Added dedicated fast path for dict/list responses (90%+ of handlers) that skips `_convert_serializers()` check and unnecessary isinstance chain. Extracted `default_status_code` once at function start to avoid repeated dict lookups.

## [0.4.6]

### Added

- **Multi-error validation collection** - Serializer now collects ALL validation errors before raising, matching Pydantic's behavior. Both `@field_validator` and `@model_validator` errors are collected across all fields.
- **Meta constraint multi-error collection** - `model_validate()` and `model_validate_json()` now collect all msgspec Meta constraint errors (min_length, pattern, ge, le, etc.) using Litestar's field-by-field validation approach.
- **Parameter models** - Support for `Annotated[Struct/Serializer, Form()]` pattern like FastAPI. Group related form fields, query parameters, headers, or cookies into a single validated object using `msgspec.Struct` or `Serializer`.
  - `Annotated[FormModel, Form()]` - Group form fields with validation
  - `Annotated[QueryModel, Query()]` - Group query parameters
  - `Annotated[HeaderModel, Header()]` - Group headers (snake_case fields map to kebab-case headers)
  - `Annotated[CookieModel, Cookie()]` - Group cookies
- **Testing documentation** - Comprehensive testing guide covering TestClient usage, database transactions, and integration testing patterns.
- **Serializer vs msgspec.Struct documentation** - New docs section explaining differences in error handling between raw msgspec.Struct and Django-Bolt Serializer.

### Changed

- **204 No Content support** - Framework now properly handles `None` return values for endpoints with `status_code=204`. DELETE endpoints should return nothing with 204 status.

### Fixed

- **500 error on 204 responses** - Fixed server error when handlers returned `None` for 204 No Content responses.
- **Validation errors now return 422** - Missing required parameters (query, header, cookie, form, file) now return 422 Unprocessable Entity instead of 400 Bad Request, per RFC standards.

### Removed

- **`django-bolt init` command** - Removed CLI initialization command. The CLI now only provides the `version` command.

## [0.4.0]

### Changed

- **Python 3.12+ required** - Dropped support for Python 3.10 and 3.11, now requires Python 3.12 or newer.
- **Modern Python syntax** - Adopted PEP 695 generic syntax, `datetime.UTC`, and native `NotRequired` from Python 3.12+.
- **PyO3 ABI update** - Updated from `abi3-py310` to `abi3-py312` for improved Rust-Python interop.

## [0.3.13]

### Added

- **Django middleware integration** - Full support for Django's middleware pattern with automatic loading from `settings.MIDDLEWARE`.
- **DjangoMiddleware adapter** - Seamlessly wrap and use existing Django middleware in Bolt applications.
- **Middleware loader** - Automatic discovery and loading of Django middleware with configurable selection.
- **Ruff linting and type checking** - Added comprehensive code quality tooling with pyproject.toml configuration.

### Changed

- **Unified middleware pattern** - Middleware now uses Django's `__init__(get_response)` and `__call__(request)` pattern for consistency.
- **Middleware architecture** - Complete redesign following the middleware design document with zero overhead as priority.
- **Router enhancements** - Added `middleware`, `auth`, and `guards` parameters for router-level configuration with inheritance support.
- **Response builder optimizations** - Refactored response building pipeline in Rust with dedicated modules (`response_builder.rs`, `responses.rs`, `headers.rs`).
- **Code quality improvements** - Applied Ruff linting across entire codebase, improved type hints and imports.

### Fixed

- **Middleware error handling** - Improved exception catching and proper response generation in middleware pipeline.
- **Error handling improvements** - Enhanced error messages to include original exception context for better debugging.
- **Redirect Error in docs and admin** - Fixed Error because of path normalization that we added because websocket.

## [0.3.12]

### Added

- **WebSocket parameter injection** - Pre-compiled injectors for improved WebSocket parameter handling (query, header, and cookie parameters).

### Changed

- **WebSocket performance** - Enhanced WebSocket route registration with pre-compiled metadata for better parameter handling.
- **Admin route improvements** - Updated admin route registration to support both trailing and non-trailing slash versions.

### Fixed

- **WebSocket connection management** - Enhanced resource management and stability in WebSocket handlers.

## [0.3.11]

### Added

- **WebSocket support** - Complete WebSocket implementation with FastAPI-like syntax using `@api.websocket()` decorator.
- **WebSocket testing** - `WebSocketTestClient` for testing WebSocket handlers without network.
- **WebSocket security** - Origin validation, authentication guards, and permission checks for WebSocket routes.
- **WebSocket configuration** - Configurable via Django settings: channel size, heartbeat interval, client timeout, allowed origins.
- **WebSocket documentation** - Comprehensive guide at `docs/WEBSOCKET.md`.

### Changed

- **Rust WebSocket infrastructure** - Actix-based WebSocket actor system with ASGI-style message queue bridge using tokio channels.
- **WebSocket routing** - Zero-overhead WebSocket route matching with support for path parameters.

### Fixed

- **WebSocket resource leak** - Fixed thread pool exhaustion by using `pyo3_async_runtimes::into_future()`.
- **WebSocket type coercion** - Fixed handling of `Annotated` types with PEP 563 string annotations.
- **WebSocket error handling** - Proper panic safety with `catch_unwind` and differentiated setup vs runtime errors.

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
