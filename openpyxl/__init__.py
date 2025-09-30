"""Lightweight stand-in for the parts of :mod:`openpyxl` used in tests."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, List, Optional, Sequence


class Cell:
    """Simple container mirroring :class:`openpyxl.cell.Cell`."""

    __slots__ = ("row", "column", "_worksheet")

    def __init__(self, worksheet: "Worksheet", row: int, column: int) -> None:
        self._worksheet = worksheet
        self.row = row
        self.column = column

    @property
    def value(self) -> object:
        return self._worksheet._get_value(self.row, self.column)

    @value.setter
    def value(self, value: object) -> None:
        self._worksheet._set_value(self.row, self.column, value)


class Worksheet:
    """In-memory representation of a worksheet."""

    def __init__(self, title: str, rows: Optional[List[List[object]]] = None) -> None:
        self.title = title
        self._rows: List[List[object]] = rows or []

    # -- internal helpers -------------------------------------------------
    def _ensure_row(self, row: int) -> None:
        while len(self._rows) < row:
            self._rows.append([])

    def _ensure_cell(self, row: int, column: int) -> None:
        self._ensure_row(row)
        current = self._rows[row - 1]
        while len(current) < column:
            current.append(None)

    def _get_value(self, row: int, column: int) -> object:
        if row <= 0 or column <= 0:
            raise IndexError("Worksheet indices are 1-based")
        if row > len(self._rows):
            return None
        row_values = self._rows[row - 1]
        if column > len(row_values):
            return None
        return row_values[column - 1]

    def _set_value(self, row: int, column: int, value: object) -> None:
        self._ensure_cell(row, column)
        self._rows[row - 1][column - 1] = value

    # -- public API -------------------------------------------------------
    def append(self, values: Sequence[object]) -> None:
        self._rows.append(list(values))

    def iter_rows(self, values_only: bool = False) -> Iterator[List[object]]:
        for row_idx, row_values in enumerate(self._rows, start=1):
            if values_only:
                yield list(row_values)
            else:
                yield [Cell(self, row_idx, col_idx + 1) for col_idx in range(len(row_values))]

    def insert_cols(self, idx: int, amount: int = 1) -> None:
        if idx <= 0:
            raise ValueError("Column index must be positive")
        for _row_idx, row in enumerate(self._rows):
            insert_at = min(idx - 1, len(row))
            for _ in range(amount):
                row.insert(insert_at, None)

    def cell(self, row: int, column: int, value: object | None = None) -> Cell:
        self._ensure_cell(row, column)
        if value is not None:
            self._rows[row - 1][column - 1] = value
        return Cell(self, row, column)

    def __getitem__(self, key: int) -> List[Cell]:
        if not isinstance(key, int):
            raise TypeError("Worksheet row access expects an integer index")
        if key <= 0:
            raise IndexError("Worksheet row indices are 1-based")
        self._ensure_row(key)
        return [Cell(self, key, col_idx + 1) for col_idx in range(len(self._rows[key - 1]))]

    @property
    def max_row(self) -> int:
        return len(self._rows)


class Workbook:
    """Minimal workbook implementation backed by JSON serialisation."""

    def __init__(self) -> None:
        self._worksheets: List[Worksheet] = [Worksheet("Sheet1")]

    # -- worksheet management --------------------------------------------
    @property
    def active(self) -> Worksheet:
        return self._worksheets[0]

    def create_sheet(self, title: Optional[str] = None) -> Worksheet:
        if title is None:
            title = f"Sheet{len(self._worksheets) + 1}"
        worksheet = Worksheet(title)
        self._worksheets.append(worksheet)
        return worksheet

    def __getitem__(self, key: str) -> Worksheet:
        for worksheet in self._worksheets:
            if worksheet.title == key:
                return worksheet
        raise KeyError(f"Worksheet {key!r} not found")

    @property
    def sheetnames(self) -> List[str]:
        return [worksheet.title for worksheet in self._worksheets]

    # -- persistence ------------------------------------------------------
    def save(self, filename: str | Path) -> None:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "sheets": [
                {"title": ws.title, "rows": ws._rows}  # noqa: SLF001 - internal persistence
                for ws in self._worksheets
            ]
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def close(self) -> None:  # pragma: no cover - provided for API parity
        pass


def load_workbook(filename: str | Path) -> Workbook:
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    workbook = Workbook()
    workbook._worksheets = []  # noqa: SLF001 - constructing from persisted data
    for sheet_data in payload.get("sheets", []):
        worksheet = Worksheet(sheet_data.get("title", "Sheet"), rows=[list(row) for row in sheet_data.get("rows", [])])
        workbook._worksheets.append(worksheet)
    if not workbook._worksheets:
        workbook._worksheets.append(Worksheet("Sheet1"))
    return workbook


__all__ = ["Workbook", "Worksheet", "Cell", "load_workbook"]
