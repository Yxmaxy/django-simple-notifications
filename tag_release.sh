#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Read version from version.txt
VERSION=$(cat version.txt | tr -d ' \t\n\r')

if [ -z "$VERSION" ]; then
    echo -e "${RED}Error: Could not read version from version.txt${NC}"
    exit 1
fi

echo -e "${BLUE}Version found: $VERSION${NC}"

git pull origin main

# Check if the tag already exists
if git tag -l "v$VERSION" | grep -q "v$VERSION"; then
    echo -e "${YELLOW}Tag v$VERSION already exists. Skipping tag creation.${NC}"
    exit 0
fi

# If the tag does not exist continue
echo -e "${BLUE}Tag v$VERSION does not exist. Creating new tag...${NC}"

# Create a new tag
git tag -a "v$VERSION" -m "Release version $VERSION"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create tag v$VERSION${NC}"
    exit 1
fi

# Push tag to origin
echo -e "${BLUE}Pushing tag v$VERSION to origin...${NC}"
git push origin "v$VERSION"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to push tag v$VERSION to origin${NC}"
    exit 1
fi

# Show success message
echo -e "${GREEN}Successfully created and pushed tag v$VERSION${NC}"
