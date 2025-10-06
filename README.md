# Road-Tools

**⚠️ Repository Split - Ready for Final Push**

This repository is being split into three separate repositories. All applications have been extracted and prepared in `/tmp/repo-split/` with all files committed. **Only the final `git push` step remains.** See [FINAL_PUSH_INSTRUCTIONS.md](FINAL_PUSH_INSTRUCTIONS.md) for complete instructions.

**New Repositories (Prepared and Ready):**
- [derek-betz/CostEstimateGenerator](https://github.com/derek-betz/CostEstimateGenerator) - 165 files ready to push
- [derek-betz/submittal-packager](https://github.com/derek-betz/submittal-packager) - 29 files ready to push
- [derek-betz/commitments-reconciler](https://github.com/derek-betz/commitments-reconciler) - 12 files ready to push

**Quick Push:**
```bash
cd /tmp/repo-split/CostEstimateGenerator && git push -u origin main
cd /tmp/repo-split/submittal-packager && git push -u origin main
cd /tmp/repo-split/commitments-reconciler && git push -u origin main
```

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
