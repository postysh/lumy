#!/bin/bash
# Quick script to push Lumy to GitHub
# 
# INSTRUCTIONS:
# 1. First, create the repo on GitHub (should open in your browser)
# 2. Replace YOUR_USERNAME below with your GitHub username
# 3. Run this script: ./PUSH_TO_GITHUB.sh

set -e

# CHANGE THIS TO YOUR GITHUB USERNAME
GITHUB_USERNAME="postysh"

# Check if username was changed
if [ "$GITHUB_USERNAME" = "YOUR_USERNAME" ]; then
    echo "❌ Error: Please edit this script and set your GitHub username!"
    echo "   Open PUSH_TO_GITHUB.sh and change YOUR_USERNAME to your actual GitHub username"
    exit 1
fi

cd /Users/evan/Desktop/lumy

echo "📦 Lumy - GitHub Push Script"
echo "=============================="
echo ""

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "⚠️  Remote 'origin' already exists. Removing it..."
    git remote remove origin
fi

# Add new remote
echo "🔗 Adding GitHub remote..."
git remote add origin "https://github.com/${GITHUB_USERNAME}/lumy.git"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Success! Your code is now on GitHub at:"
echo "   https://github.com/${GITHUB_USERNAME}/lumy"
echo ""
echo "📱 To install on Raspberry Pi, run:"
echo "   git clone https://github.com/${GITHUB_USERNAME}/lumy.git"
echo "   cd lumy && ./scripts/install.sh"
echo ""
