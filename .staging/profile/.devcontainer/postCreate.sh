#!/bin/bash
# Post-create script for devcontainer setup

set -e

echo "🚀 Setting up development environment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get install -y jq curl shellcheck

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Install svgo for SVG optimization
echo "🎨 Installing SVG optimization tools..."
sudo npm install -g svgo

# Install act for running GitHub Actions locally
echo "🎭 Installing act (GitHub Actions runner)..."
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Create mock data directory
echo "📁 Creating mock data directory..."
mkdir -p data/mock

# Note: .actrc and .secrets.example are already in the repository
# They don't need to be created here

# Ensure .secrets is in .gitignore
if ! grep -q "^\.secrets$" .gitignore 2>/dev/null; then
    echo ".secrets" >> .gitignore
fi

echo "✅ Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  - Run tests: python -m pytest tests/ -v"
echo "  - Run pre-commit: pre-commit run --all-files"
echo "  - Generate cards: See scripts/ directory"
echo "  - Run GitHub Actions locally: act -j <job-name>"
echo ""
echo "📝 GitHub Actions (act) setup:"
echo "  1. Copy .secrets.example to .secrets and add your tokens"
echo "  2. Run 'act -l' to list available workflows"
echo "  3. Run 'act -j <job-name>' to run a specific job"
echo "  4. Example: 'act -j test-python' to run Python tests"
echo ""
echo "Happy coding! 🎉"
