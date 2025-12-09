"""
Compression configuration for Django-Bolt.

Provides configuration options for response compression (gzip, brotli, zstd).
Compression levels are handled automatically by Actix Web with optimized defaults.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass
class CompressionConfig:
    """Configuration for response compression.

    To enable response compression, pass an instance of this class to the BoltAPI
    constructor using the compression parameter.

    Args:
        backend: The compression backend to use (default: "brotli")
            Can be "gzip", "brotli", or "zstd". Built-in compression with optimized defaults.
        minimum_size: Minimum response size in bytes to enable compression (default: 500)
            Responses smaller than this will not be compressed.
        gzip_fallback: Use GZIP if the client doesn't support the configured backend (default: True)
            Falls back to gzip for broader client compatibility.

    Examples:
        # Default compression (brotli with gzip fallback)
        api = BoltAPI(compression=CompressionConfig())

        # Brotli compression with smaller minimum size
        api = BoltAPI(compression=CompressionConfig(
            backend="brotli",
            minimum_size=256
        ))

        # Gzip only (no fallback)
        api = BoltAPI(compression=CompressionConfig(
            backend="gzip",
            gzip_fallback=False
        ))

        # Zstd compression with gzip fallback
        api = BoltAPI(compression=CompressionConfig(
            backend="zstd"
        ))

        # Disable compression
        api = BoltAPI(compression=None)
    """
    backend: Literal["gzip", "brotli", "zstd"] = "brotli"
    minimum_size: int = 500
    gzip_fallback: bool = True

    def __post_init__(self):
        # Validate backend
        valid_backends = {"gzip", "brotli", "zstd"}
        if self.backend not in valid_backends:
            raise ValueError(f"Invalid backend: {self.backend}. Must be one of {valid_backends}")

        # Validate minimum_size
        if self.minimum_size < 0:
            raise ValueError("minimum_size must be non-negative")

    def to_rust_config(self) -> dict:
        """Convert to dictionary for passing to Rust."""
        return {
            "backend": self.backend,
            "minimum_size": self.minimum_size,
            "gzip_fallback": self.gzip_fallback,
        }
