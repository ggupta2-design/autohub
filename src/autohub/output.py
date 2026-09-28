"""Safe local report output."""

from __future__ import annotations

import os
from pathlib import Path

from .models import AutoHubError


def write_output(path: str | Path, content: str) -> Path:
    """Create a private UTF-8 report atomically without overwriting."""

    destination = Path(path)
    if not isinstance(content, str):
        raise AutoHubError("output content must be text")
    if destination.exists() or destination.is_symlink():
        raise AutoHubError("output already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(destination, flags, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise AutoHubError("output already exists") from exc
    except OSError as exc:
        if destination.exists():
            try:
                destination.unlink()
            except OSError:
                pass
        raise AutoHubError("could not write output") from exc
    return destination
