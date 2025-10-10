"""
Compression configuration for Django-Bolt.

Provides configuration options for response compression (gzip, brotli, zstd).
Inspired by Litestar's compression config.
"""
from typing import Optional, Literal
from dataclasses import dataclass


@dataclass
class CompressionConfig:
    """Configuration for response compression.

    To enable response compression, pass an instance of this class to the BoltAPI
    constructor using the compression parameter.

    Args:
        backend: The compression backend to use (default: "brotli")
            If the value is "gzip", "brotli", or "zstd", built-in compression is used.
        minimum_size: Minimum response size in bytes to enable compression (default: 500)
            Responses smaller than this will not be compressed.
        gzip_compress_level: Range [0-9] for gzip compression (default: 9)
            Higher values provide better compression but are slower.
        brotli_quality: Range [0-11] for brotli compression (default: 5)
            Controls compression-speed vs compression-density tradeoff.
        brotli_lgwin: Base 2 logarithm of window size for brotli (default: 22)
            Range is 10 to 24. Larger values can improve compression for large files.
        zstd_level: Range [1-22] for zstd compression (default: 3)
            Higher values provide better compression but are slower.
        gzip_fallback: Use GZIP if the client doesn't support the configured backend (default: True)

    Examples:
        # Default compression (brotli with gzip fallback)
        api = BoltAPI(compression=CompressionConfig())

        # Aggressive brotli compression
        api = BoltAPI(compression=CompressionConfig(
            backend="brotli",
            brotli_quality=11,
            minimum_size=256
        ))

        # Gzip only (maximum compression)
        api = BoltAPI(compression=CompressionConfig(
            backend="gzip",
            gzip_compress_level=9,
            gzip_fallback=False
        ))

        # Fast zstd compression
        api = BoltAPI(compression=CompressionConfig(
            backend="zstd",
            zstd_level=1
        ))

        # Disable compression
        api = BoltAPI(compression=None)
    """
    backend: Literal["gzip", "brotli", "zstd"] = "brotli"
    minimum_size: int = 500
    gzip_compress_level: int = 9
    brotli_quality: int = 5
    brotli_lgwin: int = 22
    zstd_level: int = 3
    gzip_fallback: bool = True

    def __post_init__(self):
        # Validate backend
        valid_backends = {"gzip", "brotli", "zstd"}
        if self.backend not in valid_backends:
            raise ValueError(f"Invalid backend: {self.backend}. Must be one of {valid_backends}")

        # Validate minimum_size
        if self.minimum_size < 0:
            raise ValueError("minimum_size must be non-negative")

        # Validate gzip_compress_level
        if not (0 <= self.gzip_compress_level <= 9):
            raise ValueError("gzip_compress_level must be between 0 and 9")

        # Validate brotli_quality
        if not (0 <= self.brotli_quality <= 11):
            raise ValueError("brotli_quality must be between 0 and 11")

        # Validate brotli_lgwin
        if not (10 <= self.brotli_lgwin <= 24):
            raise ValueError("brotli_lgwin must be between 10 and 24")

        # Validate zstd_level
        if not (1 <= self.zstd_level <= 22):
            raise ValueError("zstd_level must be between 1 and 22")

    def to_rust_config(self) -> dict:
        """Convert to dictionary for passing to Rust."""
        return {
            "backend": self.backend,
            "minimum_size": self.minimum_size,
            "gzip_compress_level": self.gzip_compress_level,
            "brotli_quality": self.brotli_quality,
            "brotli_lgwin": self.brotli_lgwin,
            "zstd_level": self.zstd_level,
            "gzip_fallback": self.gzip_fallback,
        }
