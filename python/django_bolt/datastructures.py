"""Data structures for request handling in Django-Bolt."""

from __future__ import annotations

import asyncio
from tempfile import SpooledTemporaryFile
from typing import Any

from django.core.files.base import File

__all__ = ["UploadFile"]

# Default max spool size before rolling to disk (1MB)
DEFAULT_MAX_SPOOL_SIZE = 1024 * 1024


class UploadFile:
    """
    Represents an uploaded file with Django-first interface.

    Provides both sync and async file operations, with direct Django FileField/ImageField
    compatibility via the .file property which returns a Django File object.

    Attributes:
        filename: Original filename from the upload
        content_type: MIME type of the file
        size: Size in bytes
        headers: Additional headers from the multipart part
        file: Django File wrapper for direct use with FileField/ImageField

    Example:
        # Async handler - save directly to Django FileField
        @api.post("/avatar")
        async def upload(avatar: Annotated[UploadFile, File(max_size=2_000_000)]):
            content = await avatar.read()
            profile.avatar.save(avatar.filename, avatar.file)

        # Sync handler - same pattern works
        @api.post("/avatar")
        def upload(avatar: Annotated[UploadFile, File()]):
            content = avatar.file.read()
            profile.avatar.save(avatar.filename, avatar.file)
    """

    __slots__ = ("filename", "content_type", "size", "headers", "_file", "_django_file")

    def __init__(
        self,
        filename: str,
        content_type: str = "application/octet-stream",
        size: int = 0,
        headers: dict[str, str] | None = None,
        file_data: bytes | None = None,
        max_spool_size: int = DEFAULT_MAX_SPOOL_SIZE,
    ) -> None:
        """
        Initialize an UploadFile.

        Args:
            filename: Original filename from the upload
            content_type: MIME type of the file
            size: Size in bytes
            headers: Additional headers from the multipart part
            file_data: File content as bytes
            max_spool_size: Size threshold before spooling to disk (default 1MB)
        """
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.headers: dict[str, str] = headers or {}
        # File must persist beyond a context manager - closed in close() method
        self._file: SpooledTemporaryFile[bytes] = SpooledTemporaryFile(max_size=max_spool_size)  # noqa: SIM115
        self._django_file: File | None = None

        if file_data:
            self._file.write(file_data)
            self._file.seek(0)

    @classmethod
    def from_file_info(cls, file_info: dict[str, Any], max_spool_size: int = DEFAULT_MAX_SPOOL_SIZE) -> UploadFile:
        """
        Create UploadFile from the file_info dict returned by request parsing.

        Args:
            file_info: Dict with keys: filename, content, content_type, size
            max_spool_size: Size threshold before spooling to disk

        Returns:
            UploadFile instance
        """
        return cls(
            filename=file_info.get("filename", ""),
            content_type=file_info.get("content_type", "application/octet-stream"),
            size=file_info.get("size", 0),
            headers=file_info.get("headers"),
            file_data=file_info.get("content"),
            max_spool_size=max_spool_size,
        )

    @property
    def file(self) -> File:
        """
        Django File wrapper for the uploaded file.

        Returns a Django File object that can be directly used with FileField/ImageField:
            profile.avatar.save(upload.filename, upload.file)

        The Django File wraps the underlying SpooledTemporaryFile without reading
        all content into memory, making it efficient for large files.
        """
        if self._django_file is None:
            self._django_file = File(self._file, name=self.filename)
        return self._django_file

    @property
    def raw_file(self) -> SpooledTemporaryFile[bytes]:
        """Direct access to the underlying SpooledTemporaryFile."""
        return self._file

    @property
    def rolled_to_disk(self) -> bool:
        """Check if file exceeded memory threshold and is stored on disk."""
        return getattr(self._file, "_rolled", False)

    # === ASYNC METHODS ===
    # These use run_in_executor when file is on disk to avoid blocking

    async def read(self, size: int = -1) -> bytes:
        """
        Read file contents asynchronously.

        Args:
            size: Number of bytes to read (-1 for all)

        Returns:
            File content as bytes
        """
        if self.rolled_to_disk:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._file.read, size)
        return self._file.read(size)

    async def seek(self, offset: int, whence: int = 0) -> int:
        """
        Seek to position asynchronously.

        Args:
            offset: Position offset
            whence: Reference point (0=start, 1=current, 2=end)

        Returns:
            New absolute position
        """
        if self.rolled_to_disk:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._file.seek, offset, whence)
        return self._file.seek(offset, whence)

    async def write(self, data: bytes) -> int:
        """
        Write data to file asynchronously.

        Args:
            data: Bytes to write

        Returns:
            Number of bytes written
        """
        if self.rolled_to_disk:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._file.write, data)
        return self._file.write(data)

    async def close(self) -> None:
        """Close the file asynchronously."""
        if self._file.closed:
            return
        if self.rolled_to_disk:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._file.close)
        else:
            self._file.close()

    def __repr__(self) -> str:
        rolled = " (on disk)" if self.rolled_to_disk else ""
        return f"UploadFile(filename={self.filename!r}, content_type={self.content_type!r}, size={self.size}{rolled})"
