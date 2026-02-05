# Design considerations: custom fields (#122)

This document outlines design options for **custom fields** in Django-Bolt serializers: reusable, validated field types that can be composed and reused across serializers (e.g. `Email`, `Slug`, or user-defined types like `EvenInt`).

## Current state

### What exists today

1. **`field()` and `FieldConfig`**  
   Metadata for a field: `read_only`, `write_only`, `source`, `alias`, `default`, `default_factory`, OpenAPI (`description`, `title`, `examples`, `deprecated`), `exclude`, `include_in_schema`.  
   Does **not** define validation; it only configures serialization and schema.

2. **`@field_validator(field_name)`**  
   Class-level validators bound by field name. Run after msgspec parsing, support transform (return value) and multi-error collection.  
   Validation is **per-serializer**, not reusable by type.

3. **`msgspec.Meta` in `Annotated`**  
   Declarative constraints (e.g. `min_length`, `max_length`, `pattern`, `ge`, `le`).  
   Validated by msgspec during decode; no custom Python logic.

4. **Built-in type aliases (`types.py`)**  
   Reusable types built from `Annotated[T, Meta(...)]`, e.g. `Email`, `Slug`, `PositiveInt`, `Char100`.  
   All validation is via Meta; no custom callables.

5. **`Validator` in `fields.py`**  
   Documented as: `Annotated[int, Validator(validate_even)]`.  
   **Not** exported from `serializers` and **not** executed during validation today. So “custom” validation in annotations is not yet implemented.

### Gaps

- **Reusable custom validation**: No way to attach a reusable validator to a *type* (e.g. “all `EvenInt` fields”) instead of repeating `@field_validator` on every serializer.
- **`Validator` in `Annotated`**: The pattern is documented but not wired; annotations like `Annotated[T, Validator(fn)]` are ignored at runtime.
- **Composition**: Combining `field()` metadata with custom validation in one place (e.g. “email field that is write_only and validated”) is ad hoc.

---

## Goals for custom fields

- **Reusability**: Define a validated type once (e.g. `EvenInt`, `NonEmptySlug`) and use it on many serializers.
- **Composability**: Work with existing tools: `field()`, `Meta`, `@field_validator`, and OpenAPI.
- **Performance**: Prefer msgspec/Meta where possible; custom Python only where needed.
- **Consistency**: Same error shape and multi-error behavior as existing validators.
- **Discoverability**: Clear, documented way to define and use custom field types.

---

## Design options

### Option A: Implement `Annotated[T, Validator(fn)]` (wire existing `Validator`)

**Idea**: In `Serializer` validation (e.g. when building or running field validators), resolve each field’s type annotation; if it is `Annotated[T, ..., Validator(fn), ...]`, run `fn(value)` after msgspec and optionally replace value with the return value.

**Pros**  
- Matches the existing docstring in `fields.py`.  
- Small API surface: one concept (`Validator`).  
- Reusable: `EvenInt = Annotated[int, Validator(validate_even)]` then `count: EvenInt` in any serializer.  
- Composes with `Meta` and `field()` (e.g. `count: Annotated[int, Validator(validate_even)] = field(description="...")`).

**Cons**  
- Need to define order: Meta (msgspec) → Validator from Annotated → `@field_validator`.  
- Must extract and cache `Validator` from `get_args(Annotated(...))` per field to avoid repeated reflection.  
- `Validator.sub_error` is unimplemented; need a clear contract for error wrapping (e.g. to match `RequestValidationError` structure).

**Implementation sketch**  
- In `__init_subclass__` or a lazy step, for each struct field, get the annotation, and if it’s `Annotated`, collect all `Validator` instances from the metadata.  
- In `_run_field_validators()` (or a shared path), after msgspec and before/after `@field_validator`, run these Validator callables; on exception, append to the same error list used by other validators (same `loc`/`msg`/`type`).  
- Export `Validator` from `serializers` and document it in the serializers doc.

---

### Option B: Custom “field type” protocol (e.g. `BoltField`)

**Idea**: Introduce a protocol or base type that knows how to validate and optionally describe itself for OpenAPI, e.g. `BoltField[T]` with `validate(value) -> T` and optional `schema()`.

**Pros**  
- Single place for validation + schema.  
- Could support complex types (e.g. custom decimal or date format).

**Cons**  
- Diverges from msgspec’s `Annotated` + metadata style.  
- Requires the serializer to understand this protocol and call it at the right time; more moving parts than Option A.  
- Risk of duplicating what Meta already does (length, pattern, etc.).

---

### Option C: Only document and encourage type aliases + `@field_validator`

**Idea**: No new runtime behavior. “Custom fields” = type aliases (e.g. `Annotated[str, Meta(...)]`) plus optional base serializers or mixins that attach `@field_validator` for shared logic.

**Pros**  
- No implementation work.  
- Fits current architecture.

**Cons**  
- Validators are still bound by field name, so reuse requires mixins or inheritance, not “use this type and get this validation.”  
- The existing `Validator` docstring in `fields.py` would be misleading unless removed or clarified.

---

### Option D: Pydantic-style `Field()` with validation and metadata

**Idea**: Something like `Field(..., validator=fn, description="...")` used as default, similar to Pydantic’s `Field()`.

**Pros**  
- Familiar to Pydantic users.  
- Puts validation and metadata in one place.

**Cons**  
- We already have `field()` for metadata only; overloading it with validators changes its semantics and could conflict with `default`/`default_factory`.  
- Would need a clear story for order of execution (Meta vs `Field(validator=...)` vs `@field_validator`).

---

## Recommendation

- **Short term**: **Option A** — implement and export `Validator` so that `Annotated[T, Validator(fn)]` is actually run during serializer validation.  
  - Aligns with existing docstring and with msgspec’s annotation-based style.  
  - Enables reusable custom fields (e.g. `EvenInt`, `NonEmptySlug`) without new concepts.  
  - Document in serializers doc: how to define custom types with `Validator`, execution order (Meta → Annotated Validators → `@field_validator`), and that errors are collected like other field validators.

- **Clarify `Validator.sub_error`**: Either implement a simple rule (e.g. wrap exception in a standard structure and set `type`) or drop it until there is a concrete use case.

- **Keep type aliases + Meta as the preferred path** for constraints that Meta can express (length, pattern, range); reserve `Validator` for logic that must be in Python.

- **Option B** can be revisited if we later need custom schema generation or complex types that don’t fit in `Annotated[T, Validator(...)]`.

---

## Open questions

1. **Order of execution**: Confirm: msgspec (including Meta) → Validators from `Annotated` → `@field_validator` (mode before/after) → model validators.  
2. **Caching**: Cache “list of Validator instances per field” at class build/lazy-init so we don’t re-scan annotations on every instance.  
3. **OpenAPI**: Should `Validator` support optional schema hints (e.g. description, format) for generated docs, or is that out of scope for #122?  
4. **`field()` + `Validator`**: Ensure that a field can use both `field(read_only=True)` and `Annotated[T, Validator(fn)]` without conflict (metadata from `field()`, validation from `Validator`).

---

## Summary

| Approach                         | Reusable by type | Fits current codebase | Effort   |
|---------------------------------|------------------|------------------------|----------|
| A: Wire `Validator` in Annotated| Yes              | Yes                    | Moderate |
| B: BoltField protocol           | Yes              | New concept            | High     |
| C: Type aliases + validators    | Via mixins only  | Yes                    | None     |
| D: Field(validator=...)         | Yes              | Overloads `field()`    | Moderate |

Implementing **Option A** and documenting it gives a clear, low-friction path for custom fields (#122) while staying consistent with msgspec and the existing serializer design.
