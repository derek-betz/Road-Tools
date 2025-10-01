# Submittal Packager

A Python CLI for validating and packaging INDOT roadway plan submittals. Built with Typer, Pydantic, Rich, and other modern libraries.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
submittal-packager init-config config.yml
submittal-packager validate examples/sample --stage Stage2 --config config.yml
```

## Example Configuration

See [`examples/config.example.yml`](examples/config.example.yml) for a complete configuration file with comments and defaults.

## Commands

* `validate PATH --stage Stage2 --config config.yml`: Validate the project folder.
* `package PATH --stage Stage2 --config config.yml`: Validate and create manifest, checksums, transmittal, and ZIP package.
* `report PATH --stage Stage2 --config config.yml`: Rebuild the HTML report from the last validation run.
* `init-config PATH`: Write a starter `config.yml` to the given path.

## Extending Filename Rules

Update the `conventions` section of the configuration file. You can supply a new `filename_pattern`, `regex`, and optional `exceptions` list to allow vendor-specific file names. The parser converts the format string to a validation regex and exposes the parsed fields to manifest generation and reporting.

## Troubleshooting

* **Missing Python dependencies**: install build tools such as Microsoft C++ Build Tools on Windows if `python-docx` fails to build.
* **PDF text extraction**: ensure PDFs are text-based. Scanned PDFs may require OCR before validation.

## Tests

Run the unit tests with:

```bash
pytest -q
```
