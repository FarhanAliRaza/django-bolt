# Platform Support

Django-Bolt provides pre-built wheels for the most common platforms. For unsupported platforms, pip will automatically compile from source.

## Supported Platforms (Pre-built Wheels)

### Linux
- **x86_64** (64-bit Intel/AMD)
  - glibc-based distributions (manylinux2014+): Ubuntu 20.04+, Debian 10+, RHEL 8+, etc.
  - musl-based distributions (musllinux_1_2+): Alpine Linux 3.13+
- **Python versions**: 3.10, 3.11, 3.12, 3.13, 3.14

### macOS
- **Universal2** (works on both Intel and Apple Silicon Macs)
  - x86_64 (Intel Macs)
  - aarch64 (Apple Silicon M1/M2/M3)
- **Python versions**: 3.10, 3.11, 3.12, 3.13, 3.14

### Windows
- **x64** (64-bit Intel/AMD)
- **Python versions**: 3.10, 3.11, 3.12, 3.13, 3.14

## Installation

For supported platforms:
```bash
pip install django-bolt
```

The correct wheel will be automatically downloaded and installed.

## Unsupported Platforms (Source Build)

For platforms without pre-built wheels, pip will compile from source. This requires:

1. **Rust toolchain** (1.64+):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Python development headers**:
   - Ubuntu/Debian: `apt-get install python3-dev`
   - RHEL/CentOS: `yum install python3-devel`
   - macOS: Included with Xcode Command Line Tools
   - Windows: Included with Python installer

3. **C compiler**:
   - Linux: `gcc` (usually pre-installed)
   - macOS: Xcode Command Line Tools (`xcode-select --install`)
   - Windows: Microsoft Visual C++ 14.0+ (Visual Studio Build Tools)

Then install:
```bash
pip install django-bolt
```

Source builds take 2-5 minutes depending on your machine.

## Why No ARM64 Linux?

Currently, we don't provide pre-built wheels for ARM64 Linux (aarch64) due to cross-compilation challenges with the `ring` cryptography library used by `jsonwebtoken`.

**Workarounds:**

1. **Source build** (recommended): Install Rust on your ARM64 machine and pip will compile automatically
2. **Docker multi-arch builds**: Use native ARM64 runners in CI/CD

We plan to add ARM64 Linux support in a future release once the `ring` crate improves cross-compilation support.

## Why No ARM64 Windows?

ARM64 Windows (Windows on ARM) is still relatively rare. If you need this platform:

1. Install Rust on your Windows ARM device
2. Run: `pip install django-bolt`

Pip will compile from source. If you regularly need this platform, please open an issue and we'll consider adding pre-built wheels.

## Performance Considerations

- **Pre-built wheels**: Optimized with `--release` flag, maximum performance
- **Source builds**: Also compiled with optimizations, same runtime performance
- **Build time**: Source builds add 2-5 minutes to installation

## Checking Your Platform

To see which wheel was installed:
```bash
pip show django-bolt
```

Look for the "Location" line. If it contains:
- `.whl` - pre-built wheel was used
- Built from source if it took several minutes to install

## Future Plans

We're tracking these platform additions:

- [ ] Linux ARM64 (aarch64) - waiting for better `ring` cross-compilation
- [ ] Windows ARM64 - waiting for user demand
- [ ] Linux ARMv7 (32-bit ARM) - lower priority
- [ ] Linux PowerPC (ppc64le) - enterprise demand
- [ ] FreeBSD - if there's community interest

Want a platform? [Open an issue](https://github.com/your-username/django-bolt/issues) to let us know!

## Testing Wheels Locally

To test wheel builds for your platform:

```bash
# Install build tools
pip install maturin

# Build wheel
maturin build --release

# Install local wheel
pip install target/wheels/*.whl
```

## CI/CD Platform Matrix

Our GitHub Actions workflow builds and tests on:

| Platform | Architecture | OS Versions | Python Versions |
|----------|-------------|-------------|-----------------|
| Linux (glibc) | x86_64 | manylinux2014+ | 3.10-3.14 |
| Linux (musl) | x86_64 | musllinux_1_2+ | 3.10-3.14 |
| macOS | universal2 | 11+ | 3.10-3.14 |
| Windows | x64 | 10+ | 3.10-3.14 |

All tests run on these exact configurations before each release.
