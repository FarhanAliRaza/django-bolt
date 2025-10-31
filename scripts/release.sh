#!/usr/bin/env bash
set -euo pipefail

# Django-Bolt Release Script
# Automates version bumping, committing, and tag pushing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

info() {
    echo -e "${BLUE}$1${NC}"
}

success() {
    echo -e "${GREEN}$1${NC}"
}

warning() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if version argument is provided
if [ $# -eq 0 ]; then
    error "Usage: $0 <version> [--dry-run]

Examples:
  $0 0.2.2              # Standard release
  $0 0.3.0-alpha1       # Alpha release
  $0 0.3.0-beta1        # Beta release
  $0 0.3.0-rc1          # Release candidate
  $0 0.2.2 --dry-run    # Test without making changes"
fi

VERSION="$1"
DRY_RUN=false

# Check for dry-run flag
if [ $# -eq 2 ] && [ "$2" = "--dry-run" ]; then
    DRY_RUN=true
    warning "DRY RUN MODE - No changes will be made"
fi

# Validate version format (supports semver with optional pre-release)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$ ]]; then
    error "Invalid version format: $VERSION
Expected format: X.Y.Z or X.Y.Z-prerelease (e.g., 0.2.2, 0.3.0-alpha1)"
fi

# Check if we're in the project root
if [ ! -f "pyproject.toml" ] || [ ! -f "Cargo.toml" ]; then
    error "Must be run from the project root directory (where pyproject.toml and Cargo.toml exist)"
fi

# Check if git is clean (skip in dry-run mode)
if [ "$DRY_RUN" = false ] && ! git diff-index --quiet HEAD -- 2>/dev/null; then
    error "Working directory has uncommitted changes. Commit or stash them first."
fi

# Check if we're on main/master branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ]; then
    warning "You are on branch '$CURRENT_BRANCH', not main/master. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        error "Release cancelled"
    fi
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -m1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
info "Current version: $CURRENT_VERSION"
info "New version: $VERSION"

# Check if tag already exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    error "Tag v$VERSION already exists!"
fi

# Confirm before proceeding
if [ "$DRY_RUN" = false ]; then
    warning "\nThis will:
  1. Update version in pyproject.toml: $CURRENT_VERSION → $VERSION
  2. Update version in Cargo.toml: $CURRENT_VERSION → $VERSION
  3. Commit changes with message: 'Bump version to $VERSION'
  4. Create and push tag: v$VERSION
  5. Trigger GitHub Actions CI/CD pipeline

Proceed? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        info "Release cancelled"
        exit 0
    fi
fi

# Step 1: Update pyproject.toml
info "\n[1/6] Updating pyproject.toml..."
if [ "$DRY_RUN" = true ]; then
    info "Would update: version = \"$CURRENT_VERSION\" → version = \"$VERSION\""
else
    # Use sed with backup for safety (portable across Linux and macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" pyproject.toml
    else
        sed -i "s/^version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" pyproject.toml
    fi
    success "Updated pyproject.toml"
fi

# Step 2: Update Cargo.toml
info "\n[2/6] Updating Cargo.toml..."
if [ "$DRY_RUN" = true ]; then
    info "Would update: version = \"$CURRENT_VERSION\" → version = \"$VERSION\""
else
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/^version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" Cargo.toml
    else
        sed -i "s/^version = \"$CURRENT_VERSION\"/version = \"$VERSION\"/" Cargo.toml
    fi
    success "Updated Cargo.toml"
fi

# Step 3: Verify changes
info "\n[3/6] Verifying changes..."
if [ "$DRY_RUN" = true ]; then
    info "Would verify that both files contain version = \"$VERSION\""
else
    PYPROJECT_VERSION=$(grep -m1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    CARGO_VERSION=$(grep -m1 '^version = ' Cargo.toml | sed 's/version = "\(.*\)"/\1/')

    if [ "$PYPROJECT_VERSION" != "$VERSION" ] || [ "$CARGO_VERSION" != "$VERSION" ]; then
        error "Version mismatch after update:
  pyproject.toml: $PYPROJECT_VERSION
  Cargo.toml: $CARGO_VERSION
  Expected: $VERSION"
    fi
    success "Version verified in both files: $VERSION"
fi

# Step 4: Commit changes
info "\n[4/6] Committing changes..."
if [ "$DRY_RUN" = true ]; then
    info "Would run: git add pyproject.toml Cargo.toml"
    info "Would run: git commit -m 'Bump version to $VERSION'"
else
    git add pyproject.toml Cargo.toml
    # Check if there are any changes staged
    if git diff --cached --quiet; then
        warning "No changes to commit (version already at $VERSION)"
    else
        git commit -m "Bump version to $VERSION"
        success "Changes committed"
    fi
fi

# Step 5: Create and push tag
info "\n[5/6] Creating and pushing tag v$VERSION..."
if [ "$DRY_RUN" = true ]; then
    info "Would run: git tag v$VERSION"
    info "Would run: git push origin $CURRENT_BRANCH"
    info "Would run: git push origin v$VERSION"
else
    git tag "v$VERSION"
    git push origin "$CURRENT_BRANCH"
    git push origin "v$VERSION"
    success "Tag v$VERSION created and pushed"
fi

# Step 6: Summary and next steps
info "\n[6/6] Release initiated!"
success "\n✓ Version bumped: $CURRENT_VERSION → $VERSION"
success "✓ Changes committed and pushed"
success "✓ Tag v$VERSION created and pushed"

if [ "$DRY_RUN" = false ]; then
    info "\nNext steps:
  1. Monitor GitHub Actions: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions
  2. Wait for CI to complete (~10-15 minutes)
  3. Check PyPI: https://pypi.org/project/django-bolt/$VERSION/
  4. Verify GitHub Release: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/releases/tag/v$VERSION

  The CI workflow will:
  - Run tests across Python 3.10-3.14
  - Build wheels for Linux, macOS, Windows
  - Publish to PyPI (requires trusted publishing setup)
  - Create GitHub release with artifacts"

    # Detect pre-release
    if [[ "$VERSION" =~ -(alpha|beta|rc) ]]; then
        warning "\n⚠ This is a pre-release version (contains ${BASH_REMATCH[1]})
  The GitHub release will be marked as 'prerelease' automatically."
    fi
else
    warning "\nDRY RUN completed - no changes were made"
    info "Run without --dry-run to execute the release"
fi
