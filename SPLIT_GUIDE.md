# Repository Split Guide

This document explains how to extract each application from this repository into its own standalone repository.

## Overview

The Road-Tools repository has been restructured to prepare for splitting into three separate repositories:

1. **CostEstimateGenerator** - Cost estimation tool for INDOT projects
2. **submittal-packager** - INDOT roadway plan submittal packager
3. **commitments-reconciler** - Commitments reconciliation utilities

Each application directory is now fully self-contained with all necessary files for independent operation.

## What Each Application Has

Each application directory contains:

- ✓ `README.md` - Complete documentation for setup and usage
- ✓ `LICENSE` - MIT License
- ✓ `.gitignore` - Appropriate ignore rules for the application
- ✓ `.github/workflows/ci.yml` - GitHub Actions CI/CD workflow
- ✓ `pyproject.toml` - Python package configuration
- ✓ Source code in `src/` or application directory
- ✓ Tests in `tests/`
- ✓ Additional resources (examples, templates, data, scripts)

## How to Extract an Application

To extract any application into its own repository:

### Method 1: Simple Copy (Recommended for New Repositories)

1. Create a new repository on GitHub (e.g., `derek-betz/CostEstimateGenerator`)
2. Clone the new empty repository locally
3. Copy all contents from the application folder:
   ```bash
   cp -r /path/to/Road-Tools/CostEstimateGenerator/* /path/to/new-repo/
   cp /path/to/Road-Tools/CostEstimateGenerator/.gitignore /path/to/new-repo/
   cp -r /path/to/Road-Tools/CostEstimateGenerator/.github /path/to/new-repo/
   ```
4. Commit and push to the new repository

### Method 2: Git Filter (Preserves History)

If you want to preserve the git history for a specific application:

```bash
# Clone the original repository
git clone https://github.com/derek-betz/Road-Tools.git CostEstimateGenerator
cd CostEstimateGenerator

# Filter to keep only CostEstimateGenerator files
git filter-branch --subdirectory-filter CostEstimateGenerator -- --all

# Update remote and push
git remote set-url origin https://github.com/derek-betz/CostEstimateGenerator.git
git push -u origin main
```

## Verification

After extraction, verify the application works independently:

1. Install dependencies:
   ```bash
   pip install -e .[test]
   ```

2. Run tests:
   ```bash
   pytest -q
   ```

3. Verify CI/CD workflow runs on the new repository

## Next Steps After Split

Once applications are in separate repositories:

1. Update cross-references in documentation
2. Set up separate issue tracking for each project
3. Configure branch protection rules
4. Set up appropriate access controls
5. Archive or remove the original monorepo (optional)

## Benefits of the Split

- **Independent versioning**: Each tool can have its own release cycle
- **Focused CI/CD**: Workflows only run for relevant code changes
- **Clearer ownership**: Teams can own specific tools
- **Simpler dependencies**: No confusion about which dependencies belong to which tool
- **Easier contribution**: Contributors can focus on one tool at a time
