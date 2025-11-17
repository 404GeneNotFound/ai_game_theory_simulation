#!/bin/bash

# Script to add files and push to GitHub
# Usage: ./push_files.sh "your commit message"

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📁 Adding files to git...${NC}"

# Add all files (or you can specify specific files/directories)
git add .

echo -e "${GREEN}✅ Files staged${NC}"

# Check if there are changes to commit
if git diff --staged --quiet; then
  echo -e "${YELLOW}⚠️  No changes to commit${NC}"
  exit 0
fi

# Get commit message from argument or use default
COMMIT_MSG="${1:-Update: Add files from local}"

echo -e "${YELLOW}💬 Creating commit...${NC}"
git commit -m "$COMMIT_MSG"

echo -e "${GREEN}✅ Commit created${NC}"

# Get current branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo -e "${YELLOW}🚀 Pushing to branch: ${BRANCH}${NC}"
git push -u origin "$BRANCH"

echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
