# Road-Tools

This repository has been split into separate repositories for better modularity and maintenance. Each application now has its own dedicated repository:

## Individual Repositories

- **[CostEstimateGenerator](CostEstimateGenerator/)** - Ingests historical pay-item pricing data, computes summary statistics, and updates estimate workbooks
- **[submittal-packager](submittal-packager/)** - Python CLI for validating and packaging INDOT roadway plan submittals
- **[commitments-reconciler](commitments-reconciler/)** - Integration tests and utilities for commitments reconciliation

Each application directory is now self-contained with:
- README with setup and usage instructions
- Dependencies and requirements
- Tests and documentation
- Configuration files
- LICENSE file
- GitHub Actions CI/CD workflows

## Migration Note

Each folder in this repository can be extracted into its own standalone repository. All necessary files (LICENSE, .gitignore, .github/workflows, etc.) have been added to make each application fully independent.

To extract an application into its own repository:
1. Copy the application folder (e.g., `CostEstimateGenerator/`)
2. Initialize a new git repository in that folder
3. The application is ready to use as a standalone repository
