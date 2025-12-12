#!/bin/bash
# Quick script to push PromptGuard to GitHub

echo "🚀 Pushing PromptGuard to GitHub..."
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "⚠️  Remote 'origin' already exists. Removing it..."
    git remote remove origin
fi

# Add remote
echo "📡 Adding remote repository..."
git remote add origin https://github.com/rohitgurnani1/promptguard.git

# Set branch to main
echo "🌿 Setting branch to main..."
git branch -M main

# Push
echo "⬆️  Pushing to GitHub..."
echo ""
echo "⚠️  If you get authentication errors:"
echo "   1. Use a Personal Access Token (not password)"
echo "   2. Or run: gh auth login"
echo ""
git push -u origin main

echo ""
echo "✅ Done! Check your repo at: https://github.com/rohitgurnani1/promptguard"



