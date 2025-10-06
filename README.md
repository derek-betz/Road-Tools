# Road-Tools

**⚠️ Repository Split In Progress**

This repository is being split into three separate repositories. The split is prepared and ready to execute. See [SPLIT_STATUS.md](SPLIT_STATUS.md) for details and instructions.

**New Repositories (Ready to Populate):**
- [derek-betz/CostEstimateGenerator](https://github.com/derek-betz/CostEstimateGenerator)
- [derek-betz/submittal-packager](https://github.com/derek-betz/submittal-packager)
- [derek-betz/commitments-reconciler](https://github.com/derek-betz/commitments-reconciler)

---

This repository has been restructured to prepare for splitting into separate repositories. Each application is now fully self-contained and ready to be extracted into its own repository.

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

## Extracting Applications

See **[SPLIT_GUIDE.md](SPLIT_GUIDE.md)** for detailed instructions on how to extract each application into its own repository.

### Quick Extract Steps

1. Copy the application folder (e.g., `CostEstimateGenerator/`) to a new location
2. Initialize a new git repository: `git init`
3. Add and commit all files: `git add . && git commit -m "Initial commit"`
4. Push to a new GitHub repository

Each application is ready to function independently with all necessary configuration files included.
