#!/bin/bash

# Quick Push Script for Split Repositories
# This script pushes all three prepared repositories to GitHub in one command
#
# Prerequisites: 
# - Repositories must be prepared in /tmp/repo-split/
# - You must have push access to the target repositories
# - Git must be configured with proper authentication

set -e

WORK_DIR="/tmp/repo-split"

echo "========================================="
echo "Pushing Split Repositories to GitHub"
echo "========================================="
echo ""

# Check if repositories are prepared
if [ ! -d "$WORK_DIR" ]; then
    echo "❌ Error: $WORK_DIR does not exist"
    echo ""
    echo "Please run the preparation script first:"
    echo "  ./scripts/prepare_split_repositories.sh"
    exit 1
fi

# Function to push a repository
push_repo() {
    local repo_name=$1
    local repo_path="$WORK_DIR/$repo_name"
    
    if [ ! -d "$repo_path" ]; then
        echo "❌ Error: $repo_path does not exist"
        return 1
    fi
    
    echo "Pushing $repo_name..."
    cd "$repo_path"
    
    # Show what we're about to push
    echo "  Branch: $(git branch --show-current)"
    echo "  Commits ahead: $(git rev-list --count @{u}..HEAD 2>/dev/null || git rev-list --count HEAD)"
    
    # Push
    if git push -u origin main; then
        echo "  ✅ Successfully pushed $repo_name"
    else
        echo "  ❌ Failed to push $repo_name"
        return 1
    fi
    echo ""
}

# Push each repository
echo "Starting push process..."
echo ""

if push_repo "CostEstimateGenerator" && \
   push_repo "submittal-packager" && \
   push_repo "commitments-reconciler"; then
    echo "========================================="
    echo "✅ All repositories pushed successfully!"
    echo "========================================="
    echo ""
    echo "Verify the repositories at:"
    echo "  - https://github.com/derek-betz/CostEstimateGenerator"
    echo "  - https://github.com/derek-betz/submittal-packager"
    echo "  - https://github.com/derek-betz/commitments-reconciler"
    echo ""
    echo "Next steps:"
    echo "  1. Check that all files are present on GitHub"
    echo "  2. Verify CI/CD workflows run successfully"
    echo "  3. Clone and test each repository locally"
    echo "  4. Update Road-Tools repository links"
    exit 0
else
    echo "========================================="
    echo "❌ Push failed for one or more repositories"
    echo "========================================="
    echo ""
    echo "Please check the error messages above and:"
    echo "  1. Verify you have push access to all repositories"
    echo "  2. Check your Git authentication (SSH keys or PAT)"
    echo "  3. Ensure the remote repositories are accessible"
    exit 1
fi
