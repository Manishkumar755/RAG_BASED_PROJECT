#!/usr/bin/env bash
set -e

echo "========================================================"
echo "Push Innefu Labs RAG Platform to GitHub"
echo "========================================================"
echo ""

if [ -z "$1" ]; then
    read -p "Enter your GitHub repository URL (e.g. https://github.com/Manishkumar755/rag-platform.git): " REPO_URL
else
    REPO_URL=$1
fi

if [ -z "$REPO_URL" ]; then
    echo "[ERROR] No repository URL provided. Exiting."
    exit 1
fi

echo "[1/3] Configuring remote origin: $REPO_URL"
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

echo "[2/3] Setting branch to main"
git branch -M main

echo "[3/3] Pushing to GitHub..."
git push -u origin main

echo ""
echo "========================================================"
echo "Successfully pushed to GitHub!"
echo "Next steps:"
echo "1. Deploy backend on Render (https://render.com)"
echo "2. Deploy frontend on Vercel (https://vercel.com)"
echo "See DEPLOYMENT.md for step-by-step instructions."
echo "========================================================"
