#!/bin/bash

# Push Prepared Repositories Script
# This script pushes the three prepared repository splits to GitHub
# 
# Prerequisites:
# - The split_repositories.sh script has been run to prepare the repositories
# - You have push access to the target repositories
# - Git is configured with proper credentials

set -e

WORK_DIR="/tmp/repo-split"

echo "========================================="
echo "Pushing Prepared Repositories"
echo "========================================="
echo ""

# Check if repositories are prepared
if [ ! -d "$WORK_DIR/CostEstimateGenerator" ]; then
    echo "Error: Repositories not prepared. Please run split_repositories.sh first."
    exit 1
fi

# Function to push a repository
push_repo() {
    local repo_name=$1
    local repo_url=$2
    
    echo "Pushing $repo_name..."
    cd "$WORK_DIR/$repo_name"
    
    # Show what we're about to push
    echo "  Commits to push:"
    git log --oneline origin/main..HEAD 2>/dev/null || git log --oneline HEAD
    
    # Push
    git push -u origin main
    
    echo "✓ Successfully pushed $repo_name"
    echo ""
}

# Push each repository
push_repo "CostEstimateGenerator" "https://github.com/derek-betz/CostEstimateGenerator.git"
push_repo "submittal-packager" "https://github.com/derek-betz/submittal-packager.git"
push_repo "commitments-reconciler" "https://github.com/derek-betz/commitments-reconciler.git"

echo "========================================="
echo "All repositories pushed successfully!"
echo "========================================="
echo ""
echo "You can now verify the repositories at:"
echo "  - https://github.com/derek-betz/CostEstimateGenerator"
echo "  - https://github.com/derek-betz/submittal-packager"
echo "  - https://github.com/derek-betz/commitments-reconciler"
