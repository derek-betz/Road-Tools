"""Small subset of the :mod:`python-docx` API used in tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


class Paragraph:
    """Represents a paragraph of text."""

    __slots__ = ("text",)

    def __init__(self, text: str) -> None:
        self.text = text


class SimpleDocument:
    """Very small document model compatible with the project tests."""

    def __init__(self, paragraphs: List[Paragraph] | None = None) -> None:
        self._paragraphs: List[Paragraph] = paragraphs or []

    @property
    def paragraphs(self) -> List[Paragraph]:
        return list(self._paragraphs)

    # -- authoring helpers ------------------------------------------------
    def add_paragraph(self, text: str) -> Paragraph:
        paragraph = Paragraph(text)
        self._paragraphs.append(paragraph)
        return paragraph

    def add_heading(self, text: str, level: int = 1) -> Paragraph:  # noqa: D401 - documented by add_paragraph
        return self.add_paragraph(text)

    # -- persistence ------------------------------------------------------
    def save(self, filename: str | Path) -> None:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"paragraphs": [paragraph.text for paragraph in self._paragraphs]}
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def Document(filename: str | Path | None = None) -> SimpleDocument:
    if filename is None:
        return SimpleDocument()
    path = Path(filename)
    payload = json.loads(path.read_text(encoding="utf-8"))
    paragraphs = [Paragraph(text) for text in payload.get("paragraphs", [])]
    return SimpleDocument(paragraphs)


__all__ = ["Document", "Paragraph", "SimpleDocument"]
