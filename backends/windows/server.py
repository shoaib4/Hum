"""Backwards-compatible shim.

``WhisperServer`` is platform-neutral and now lives in ``backends.common.server``.
This module is kept so existing imports of ``backends.windows.server`` keep working.
"""

from backends.common.server import WhisperServer

__all__ = ["WhisperServer"]
