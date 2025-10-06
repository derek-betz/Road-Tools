#!/bin/bash

# Repository Split Script
# This script automates the process of moving each application to its respective repository

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORK_DIR="/tmp/repo-split-$$"

echo "Creating working directory: $WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Function to clone, copy, and push an application
split_app() {
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
    
    # Push to the new repository
    echo "Pushing to $repo_url..."
    git push -u origin main
    
    echo "✓ Successfully pushed $app_name to its new repository"
    cd "$WORK_DIR"
}

# Split each application
echo "Starting repository split process..."
echo "Source repository: $REPO_ROOT"
echo ""

split_app "CostEstimateGenerator" \
    "https://github.com/derek-betz/CostEstimateGenerator.git" \
    "$REPO_ROOT/CostEstimateGenerator"

split_app "submittal-packager" \
    "https://github.com/derek-betz/submittal-packager.git" \
    "$REPO_ROOT/submittal-packager"

split_app "commitments-reconciler" \
    "https://github.com/derek-betz/commitments-reconciler.git" \
    "$REPO_ROOT/commitments-reconciler"

echo ""
echo "========================================="
echo "Repository split completed successfully!"
echo "========================================="
echo ""
echo "The following repositories have been populated:"
echo "  - https://github.com/derek-betz/CostEstimateGenerator"
echo "  - https://github.com/derek-betz/submittal-packager"
echo "  - https://github.com/derek-betz/commitments-reconciler"
echo ""
echo "Cleaning up working directory..."
rm -rf "$WORK_DIR"
echo "Done!"
