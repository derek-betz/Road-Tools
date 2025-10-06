#!/bin/bash

# Repository Preparation Script
# This script prepares each application in a temp directory ready for pushing
# It does NOT push - that step requires authentication

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORK_DIR="/tmp/repo-split"

echo "Creating working directory: $WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Function to clone, copy, and commit an application (but not push)
prepare_app() {
    local app_name=$1
    local repo_url=$2
    local source_dir=$3
    
    echo ""
    echo "========================================="
    echo "Processing: $app_name"
    echo "========================================="
    
    # Clone the empty repository
    echo "Cloning $repo_url..."
    git clone "$repo_url" "$app_name"
    cd "$app_name"
    
    # Configure git
    git config user.name "Repository Split Bot"
    git config user.email "noreply@github.com"
    
    # Copy all files from the application directory
    echo "Copying files from $source_dir..."
    cp -r "$source_dir"/* .
    cp "$source_dir/.gitignore" . 2>/dev/null || true
    cp -r "$source_dir/.github" . 2>/dev/null || true
    
    # Add and commit all files
    echo "Committing files..."
    git add .
    git commit -m "Initial commit - extracted from Road-Tools monorepo

This repository contains the $app_name application that was previously
part of the Road-Tools monorepo. All files have been extracted and are
now independent.

For history prior to this point, see: https://github.com/derek-betz/Road-Tools"
    
    echo "✓ $app_name is prepared and ready to push"
    cd "$WORK_DIR"
}

# Prepare each application
echo "Starting repository preparation process..."
echo "Source repository: $REPO_ROOT"
echo ""

prepare_app "CostEstimateGenerator" \
    "https://github.com/derek-betz/CostEstimateGenerator.git" \
    "$REPO_ROOT/CostEstimateGenerator"

prepare_app "submittal-packager" \
    "https://github.com/derek-betz/submittal-packager.git" \
    "$REPO_ROOT/submittal-packager"

prepare_app "commitments-reconciler" \
    "https://github.com/derek-betz/commitments-reconciler.git" \
    "$REPO_ROOT/commitments-reconciler"

echo ""
echo "========================================="
echo "Repository preparation completed!"
echo "========================================="
echo ""
echo "The repositories are ready in: $WORK_DIR"
echo ""
echo "To push them, run:"
echo "  cd $WORK_DIR/CostEstimateGenerator && git push -u origin main"
echo "  cd $WORK_DIR/submittal-packager && git push -u origin main"
echo "  cd $WORK_DIR/commitments-reconciler && git push -u origin main"
echo ""
echo "Or use the push script:"
echo "  $REPO_ROOT/scripts/push_split_repositories.sh"
