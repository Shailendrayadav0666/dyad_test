"""Bridges FastAPI's async UploadFile to the synchronous file-like interface
expected by PDFProcessor (filename, read, seek, tell)."""

import io


class UploadFileWrapper:
    def __init__(self, content: bytes, filename: str):
        self._buf = io.BytesIO(content)
        self.filename = filename

    def read(self, size: int = -1) -> bytes:
        return self._buf.read() if size < 0 else self._buf.read(size)

    def seek(self, pos: int, whence: int = 0) -> int:
        return self._buf.seek(pos, whence)

    def tell(self) -> int:
        return self._buf.tell()
