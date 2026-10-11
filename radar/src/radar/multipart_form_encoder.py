"""Build multipart/form-data bodies with the standard library (no third-party HTTP client)."""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class FormPart:
    name: str
    content: str
    content_type: str


def encode_multipart_form(parts: list[FormPart], boundary: str | None = None) -> tuple[str, bytes]:
    boundary = boundary or uuid.uuid4().hex
    lines: list[str] = []
    for part in parts:
        lines.append(f"--{boundary}")
        lines.append(f'Content-Disposition: form-data; name="{part.name}"')
        lines.append(f"Content-Type: {part.content_type}")
        lines.append("")
        lines.append(part.content)
    lines.append(f"--{boundary}--")
    body = "\r\n".join(lines) + "\r\n"
    return f"multipart/form-data; boundary={boundary}", body.encode("utf-8")
