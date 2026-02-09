#!/bin/bash

set -e

REPO_URL="https://github.com/iam-sayco/cyclon.git@master"

echo "🚀 Installing Cyclon from GitHub..."
echo ""

# Check for pipx first (recommended for CLI apps)
if command -v pipx &> /dev/null; then
    echo "✓ Found pipx (recommended)"
    echo "Installing with pipx..."
    pipx install --suffix="" git+${REPO_URL}
    echo ""
    echo "✅ Cyclon installed successfully!"
    echo "Run: cyclon"
    exit 0
fi

# Fall back to pip
if command -v pip &> /dev/null; then
    echo "✓ Found pip"
    echo "Installing with pip..."
    pip install git+${REPO_URL}
    echo ""
    echo "✅ Cyclon installed successfully!"
    echo "Run: cyclon"
    exit 0
fi

# Check for pip3 (some systems have separate commands)
if command -v pip3 &> /dev/null; then
    echo "✓ Found pip3"
    echo "Installing with pip3..."
    pip3 install git+${REPO_URL}
    echo ""
    echo "✅ Cyclon installed successfully!"
    echo "Run: cyclon"
    exit 0
fi

# Nothing found
echo "❌ Error: Neither pip nor pipx found on your system."
echo ""
echo "Please install one of them first:"
echo ""
echo "  For pipx (recommended for CLI apps):"
echo "    pip install pipx"
echo "    pipx ensurepath"
echo ""
echo "  For pip:"
echo "    sudo apt install python3-pip        # Debian/Ubuntu"
echo "    sudo dnf install python-pip         # Fedora/RHEL"
echo "    brew install python                  # macOS"
echo ""
echo "Then run this script again."
exit 1
