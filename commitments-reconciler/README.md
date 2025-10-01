# Commitments Reconciler

This directory contains integration tests and utilities for the commitments
reconciliation prototype. Historically, binary Office documents were checked
into version control to support the tests. They have been removed in favour of
deterministic factories that generate the documents on demand using helper
functions.

## Generating example documents

Use the convenience script to create fresh examples inside
`commitments-reconciler/examples/`:

```bash
python commitments-reconciler/scripts/generate_examples.py
```

The script synthesises `sample_commitments.xlsx` and `sample_env_doc.docx` using
the same factories that power the automated tests. Files in the examples
directory are ignored by Git, ensuring that binaries never sneak back into the
repository.

## Testing

All tests use the runtime factories, so no additional preparation is required.
Simply run the root test command:

```bash
pytest -q
```

This collects the commitments tests alongside the rest of the suite.
