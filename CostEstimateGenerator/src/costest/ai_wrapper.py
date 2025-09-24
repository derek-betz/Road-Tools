"""Optional OpenAI helper used for future enhancements."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class AIHelper:
    """Wrapper that encapsulates access to OpenAI-like APIs."""

    api_key: Optional[str]
    disabled: bool = False

    def __post_init__(self) -> None:
        if self.disabled:
            LOGGER.info("AI assistance disabled via flag or environment.")
        elif not self.api_key:
            LOGGER.info("No API key provided; AI assistance inactive.")
            self.disabled = True

    def summarize(self, item_code: str, stats: Dict[str, Any]) -> Optional[str]:
        """Return a short AI-generated summary if enabled.

        The current implementation intentionally avoids calling any external
        services when disabled. It returns ``None`` when AI is unavailable.
        """

        if self.disabled or not self.api_key:
            return None

        # Placeholder for future integration. We avoid external calls to keep the
        # project offline-friendly, but structure the method for extensibility.
        LOGGER.debug("AI summary requested for %s with stats %s", item_code, stats)
        return None


__all__ = ["AIHelper"]
