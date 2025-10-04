"""Request parsing utilities for form and multipart data."""
from typing import Any, Dict, Optional, Tuple


def parse_form_data(request: Dict[str, Any], headers_map: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Parse form and multipart data from request."""
    form_map: Dict[str, Any] = {}
    files_map: Dict[str, Any] = {}
    content_type = headers_map.get("content-type", "")

    if content_type.startswith("application/x-www-form-urlencoded"):
        from urllib.parse import parse_qs
        body_bytes: bytes = request["body"]
        form_data = parse_qs(body_bytes.decode("utf-8"))
        # parse_qs returns lists, but for single values we want the value directly
        form_map = {k: v[0] if len(v) == 1 else v for k, v in form_data.items()}
    elif content_type.startswith("multipart/form-data"):
        form_map, files_map = parse_multipart_data(request, content_type)

    return form_map, files_map


def parse_multipart_data(request: Dict[str, Any], content_type: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Parse multipart form data."""
    form_map: Dict[str, Any] = {}
    files_map: Dict[str, Any] = {}

    boundary_idx = content_type.find("boundary=")
    if boundary_idx < 0:
        return form_map, files_map

    boundary = content_type[boundary_idx + 9:].strip()
    body_bytes: bytes = request["body"]
    parts = body_bytes.split(f"--{boundary}".encode())

    for part in parts[1:-1]:  # Skip first empty and last closing
        if b"\r\n\r\n" not in part:
            continue

        header_section, content = part.split(b"\r\n\r\n", 1)
        content = content.rstrip(b"\r\n")
        headers_text = header_section.decode("utf-8", errors="ignore")

        name, filename = parse_content_disposition(headers_text)

        if name:
            if filename:
                add_file_to_map(files_map, name, filename, content)
            else:
                value = content.decode("utf-8", errors="ignore")
                form_map[name] = value

    return form_map, files_map


def parse_content_disposition(headers_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse Content-Disposition header to extract name and filename."""
    name = None
    filename = None

    for line in headers_text.split("\r\n"):
        if not line.startswith("Content-Disposition:"):
            continue

        disp = line[20:].strip()
        for param in disp.split("; "):
            if param.startswith('name="'):
                name = param[6:-1]
            elif param.startswith('filename="'):
                filename = param[10:-1]

    return name, filename


def add_file_to_map(files_map: Dict[str, Any], name: str, filename: str, content: bytes) -> None:
    """Add file info to files map, handling multiple files with same name."""
    file_info = {
        "filename": filename,
        "content": content,
        "size": len(content)
    }

    if name in files_map:
        if isinstance(files_map[name], list):
            files_map[name].append(file_info)
        else:
            files_map[name] = [files_map[name], file_info]
    else:
        files_map[name] = file_info
