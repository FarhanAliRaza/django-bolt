# Publishing Django-Bolt to PyPI

This guide explains how to publish django-bolt wheels to PyPI using GitHub Actions and trusted publishing.

## Overview

Django-Bolt uses a modern publishing setup:
- **Maturin**: Builds Rust extensions as Python wheels
- **PyO3 abi3**: Single wheel supports Python 3.12-3.14+ (no per-version builds needed)
- **GitHub Actions**: Automated multi-platform wheel building
- **PyPI Trusted Publishing**: Secure OIDC-based authentication (no API tokens)

## How It Works

### Wheel Building Strategy

When you create a git tag, GitHub Actions automatically:

1. **Builds wheels for all platforms**:
   - **Linux**: x86_64, aarch64 (manylinux2014 + musllinux)
   - **macOS**: x86_64, aarch64, universal2
   - **Windows**: x64, aarch64

2. **Leverages abi3 stable ABI**: Thanks to `abi3-py312` in `Cargo.toml`, we build ONE wheel per platform that works for Python 3.12, 3.13, 3.14+ instead of separate wheels for each version.

3. **Validates wheels**: Runs `twine check --strict` on all artifacts

4. **Publishes to PyPI**: Uses OIDC trusted publishing (secure, no API tokens needed)

5. **Creates GitHub Release**: Attaches all wheels + source distribution

### Supported Platforms

The published wheels support:

| Platform | Architectures | Python Versions |
|----------|---------------|-----------------|
| Linux (glibc) | x86_64, aarch64 | 3.12+ |
| Linux (musl) | x86_64, aarch64 | 3.12+ |
| macOS | x86_64, aarch64, universal2 | 3.12+ |
| Windows | x64, aarch64 | 3.12+ |

## One-Time Setup

### 1. Create PyPI Account

If you don't have one already:
1. Go to https://pypi.org/account/register/
2. Verify your email
3. Enable 2FA (required for new projects)

### 2. Register the Project on PyPI

**Option A: Register Empty Project First (Recommended)**

1. Go to https://pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Fill in the form:
   - **PyPI Project Name**: `django-bolt`
   - **Owner**: `your-github-username`
   - **Repository name**: `django-bolt`
   - **Workflow filename**: `CI.yml`
   - **Environment name**: `pypi`
4. Click "Add"

This creates a "pending publisher" that will claim the package name on first release.

**Option B: Create First Release Manually**

If you prefer to register the package first:
1. Build locally: `uv run maturin build --release`
2. Upload manually: `uv publish` (requires API token)
3. Then add trusted publisher as described above

### 3. Configure GitHub Environment

1. Go to your GitHub repo → Settings → Environments
2. Click "New environment"
3. Name it `pypi` (must match workflow)
4. (Optional) Add protection rules:
   - Required reviewers (for manual approval before publishing)
   - Wait timer
   - Deployment branches (e.g., only `main` or tags)

## Publishing a Release

### Automated Release (Recommended)

Use the provided release script to automate version bumping, committing, and tag pushing:

```bash
# Standard release
./scripts/release.sh 0.2.2

# Pre-release versions
./scripts/release.sh 0.3.0-alpha1
./scripts/release.sh 0.3.0-beta1
./scripts/release.sh 0.3.0-rc1

# Dry-run (test without making changes)
./scripts/release.sh 0.2.2 --dry-run
```

The script will:
1. ✓ Validate version format and git status
2. ✓ Update version in both `pyproject.toml` and `Cargo.toml`
3. ✓ Commit changes with proper message
4. ✓ Create and push git tag
5. ✓ Trigger GitHub Actions CI/CD pipeline
6. ✓ Provide monitoring links and next steps

### Manual Release Process

If you prefer to release manually:

1. **Update version** in `pyproject.toml` and `Cargo.toml`

2. **Commit changes**:
   ```bash
   git add pyproject.toml Cargo.toml
   git commit -m "Bump version to 0.2.0"
   git push
   ```

3. **Create and push tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

### What Happens After Tag Push

**GitHub Actions automatically**:
- Runs tests across Python 3.12-3.14
- Builds wheels for all platforms
- Validates all wheels
- Publishes to PyPI (if tests pass)
- Creates GitHub release with artifacts

**Monitor progress**:
- Go to Actions tab in GitHub
- Watch the CI workflow complete (~10-15 minutes)
- Check PyPI: https://pypi.org/project/django-bolt/

### Pre-release (Alpha/Beta/RC)

For pre-release versions, include the identifier in the tag:

```bash
git tag v0.2.0-alpha1
git push origin v0.2.0-alpha1
```

The workflow automatically marks releases as "prerelease" if the tag contains:
- `alpha`
- `beta`
- `rc`

### Test Release (TestPyPI)

To test the release process without publishing to production PyPI:

1. Set up TestPyPI trusted publishing at https://test.pypi.org/
2. Create a separate workflow or modify `CI.yml` to use:
   ```bash
   uv publish --publish-url https://test.pypi.org/legacy/ --trusted-publishing always
   ```
3. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ django-bolt
   ```

## Troubleshooting

### Build Failures

**Linux build fails with glibc errors**:
- Ensure maturin-action uses `manylinux: auto` (automatically uses manylinux2014)
- Rust 1.64+ requires glibc 2.17+ (manylinux2014 minimum)

**macOS universal2 build fails**:
- Check that both x86_64 and aarch64 dependencies are compatible
- May need to disable certain features for universal builds

**Windows aarch64 build fails**:
- Windows ARM64 support is relatively new
- May need specific Rust target installation

### Publishing Failures

**PyPI rejects upload**:
- Verify project name matches PyPI registration exactly
- Check version isn't already published (can't overwrite)
- Ensure trusted publisher is configured correctly

**Trusted publishing fails**:
- Verify environment name in workflow matches GitHub environment (`pypi`)
- Check `id-token: write` permission is set in workflow
- Ensure tag triggers the workflow (must start with `refs/tags/`)

**Wheel validation fails**:
- Run `twine check --strict dist/*` locally
- Check for missing metadata in `pyproject.toml`
- Verify README.md exists (required if `readme = "README.md"`)

### Workflow Debugging

**View detailed logs**:
1. Go to Actions tab in GitHub
2. Click on the failed workflow run
3. Click on the failed job
4. Expand the failing step

**Test locally**:
```bash
# Build wheel for current platform
uv run maturin build --release

# Check wheel
twine check --strict target/wheels/*

# Test install
pip install target/wheels/*.whl
```

## How Popular Projects Do This

Django-Bolt's publishing setup is based on battle-tested patterns from:

- **pydantic-core**: Rust validation engine for Pydantic
- **ruff**: Extremely fast Python linter written in Rust
- **polars**: Fast DataFrame library with Rust core
- **cryptography**: Cryptographic primitives with Rust/C extensions

All use:
- ✅ Maturin for wheel building
- ✅ PyO3 with abi3 for broad Python version support
- ✅ GitHub Actions matrix builds for all platforms
- ✅ PyPI trusted publishing (no API tokens)
- ✅ Automated validation and testing

## Additional Resources

- **Maturin Documentation**: https://www.maturin.rs/
- **PyO3 Guide**: https://pyo3.rs/
- **PyPI Trusted Publishing**: https://docs.pypi.org/trusted-publishers/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Python Packaging Guide**: https://packaging.python.org/

## Architecture: Why This Setup?

### Problem: Multiple Wheels Needed

Traditional pure-Rust Python extensions need separate wheels for:
- Each Python version (3.12, 3.13, 3.14)
- Each platform (Linux, macOS, Windows)
- Each architecture (x86_64, aarch64, etc.)

**Result**: 3 Python versions × 3 platforms × 2 architectures = **18+ wheels!**

### Solution: abi3 Stable ABI

PyO3's `abi3-py310` uses Python's stable ABI:
- Build once per platform/architecture
- Works for ALL Python versions ≥ 3.12
- Reduces to: 3 platforms × 2-3 architectures = **~10 wheels**

### Why Maturin?

Maturin handles complex build requirements:
- **manylinux compliance**: Bundles dependencies, ensures portability
- **Cross-compilation**: Build for ARM64 from x86_64 runners
- **Automatic platform tags**: Assigns correct wheel names
- **PyO3 integration**: Seamless Rust ↔ Python bindings

### Why Trusted Publishing?

Traditional API tokens have problems:
- Long-lived credentials stored in CI
- Hard to rotate
- High blast radius if leaked

Trusted publishing (OIDC):
- ✅ No stored credentials
- ✅ Tokens expire in 15 minutes
- ✅ Scoped to specific repo + workflow
- ✅ GitHub-PyPI cryptographic verification

## Performance Notes

**Build time**: ~10-15 minutes for all platforms in parallel

**Caching**: The workflow uses `sccache: 'true'` to cache Rust compilation artifacts, significantly speeding up subsequent builds.

**Optimization**: Wheels are built with `--release` flag for maximum runtime performance (~10-100x faster than debug builds).

## License & Distribution

Django-Bolt is distributed under the MIT License. Ensure all dependencies are compatible:
- Rust crates: Check `Cargo.toml` licenses
- Python packages: Check `pyproject.toml` licenses
- Platform libraries: manylinux ensures compatibility

The built wheels bundle necessary Rust standard library components but dynamically link to system libraries (glibc, etc.) as allowed by manylinux policy.
