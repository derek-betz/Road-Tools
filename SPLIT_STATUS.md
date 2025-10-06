# Repository Split - Ready to Push

## Status

✅ New repositories have been created:
- https://github.com/derek-betz/CostEstimateGenerator
- https://github.com/derek-betz/submittal-packager
- https://github.com/derek-betz/commitments-reconciler

✅ Each application directory is fully self-contained and ready to be moved

✅ **All three repositories have been prepared in `/tmp/repo-split/` with:**
  - CostEstimateGenerator: 165 files committed (commit: 9999b73)
  - submittal-packager: 29 files committed (commit: 8a2d644)
  - commitments-reconciler: 12 files committed (commit: cd2ce64)

⏳ **Ready to push - requires authentication (final step)**

## Automated Push Options

### Option 1: GitHub Actions Workflow (Recommended)

A GitHub Actions workflow has been created to automate the split:

1. Go to: https://github.com/derek-betz/Road-Tools/actions/workflows/split-repository.yml
2. Click "Run workflow"
3. Type "yes" to confirm
4. Click "Run workflow" button

**Prerequisites:**
- Create a Personal Access Token (PAT) with `repo` scope
- Add it as a repository secret named `SPLIT_REPO_TOKEN`
- The token must have push access to all three target repositories

### Option 2: Manual Push Script

If the repositories have been prepared in `/tmp/repo-split/`:

```bash
cd /path/to/Road-Tools
chmod +x scripts/push_split_repositories.sh
./scripts/push_split_repositories.sh
```

### Option 3: Full Automation Script

Run the complete split process locally:

```bash
cd /path/to/Road-Tools
chmod +x scripts/split_repositories.sh
./scripts/split_repositories.sh
```

This script will:
1. Clone each empty repository
2. Copy all files from the application directories
3. Commit and push to the respective repositories

## Manual Steps (if preferred)

If you prefer to move each repository manually, follow these steps for each application:

### CostEstimateGenerator

```bash
# Clone the new repository
git clone https://github.com/derek-betz/CostEstimateGenerator.git
cd CostEstimateGenerator

# Copy files from Road-Tools
cp -r /path/to/Road-Tools/CostEstimateGenerator/* .
cp /path/to/Road-Tools/CostEstimateGenerator/.gitignore .
cp -r /path/to/Road-Tools/CostEstimateGenerator/.github .

# Commit and push
git add .
git commit -m "Initial commit - extracted from Road-Tools monorepo"
git push -u origin main
```

### submittal-packager

```bash
# Clone the new repository
git clone https://github.com/derek-betz/submittal-packager.git
cd submittal-packager

# Copy files from Road-Tools
cp -r /path/to/Road-Tools/submittal-packager/* .
cp /path/to/Road-Tools/submittal-packager/.gitignore .
cp -r /path/to/Road-Tools/submittal-packager/.github .

# Commit and push
git add .
git commit -m "Initial commit - extracted from Road-Tools monorepo"
git push -u origin main
```

### commitments-reconciler

```bash
# Clone the new repository
git clone https://github.com/derek-betz/commitments-reconciler.git
cd commitments-reconciler

# Copy files from Road-Tools
cp -r /path/to/Road-Tools/commitments-reconciler/* .
cp /path/to/Road-Tools/commitments-reconciler/.gitignore .
cp -r /path/to/Road-Tools/commitments-reconciler/.github .

# Commit and push
git add .
git commit -m "Initial commit - extracted from Road-Tools monorepo"
git push -u origin main
```

## Verification

After moving the applications, verify each repository:

1. Check that all files are present
2. Install dependencies: `pip install -e .[test]`
3. Run tests: `pytest -q`
4. Verify CI/CD workflows trigger correctly

## Next Steps

Once all applications are successfully moved:

1. Update the Road-Tools README to point to the new repositories
2. Consider archiving the Road-Tools repository
3. Set up branch protection rules on the new repositories
4. Configure appropriate access controls
