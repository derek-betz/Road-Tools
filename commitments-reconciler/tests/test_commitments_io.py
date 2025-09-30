from __future__ import annotations

from commitments_reconciler import (
    CommitmentRecord,
    read_commitments_workbook,
    read_environment_document,
    summarise_commitments,
)


def test_read_commitments_workbook(commitments_workbook):
    records = read_commitments_workbook(commitments_workbook)
    assert [record.identifier for record in records] == ["C-1001", "C-1002", "C-1003"]
    assert records[0] == CommitmentRecord("C-1001", "Acme Builders", "Design", 125000.50)
    assert records[2].vendor == "Acme Builders"


def test_read_environment_document(environment_doc):
    details = read_environment_document(environment_doc)
    assert details["Project"] == "River Crossing"
    assert details["Region"] == "North"
    assert details["Total Budget"] == "$238,750.75"


def test_summarise_commitments(commitments_workbook):
    records = read_commitments_workbook(commitments_workbook)
    summary = summarise_commitments(records)
    expected_total = 125000.50 + 98000.00 + 15750.25
    assert summary["total_amount"] == expected_total
    assert summary["by_vendor"]["Acme Builders"] == 125000.50 + 15750.25
