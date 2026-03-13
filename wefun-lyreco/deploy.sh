#!/bin/bash
set -e

DEPLOY_DIR=$(mktemp -d)
trap "rm -rf $DEPLOY_DIR" EXIT

echo "Copying site files to $DEPLOY_DIR..."

# Copy only the site assets
cp index.html "$DEPLOY_DIR/"
cp gate.html "$DEPLOY_DIR/"
cp meeting-brief.html "$DEPLOY_DIR/" 2>/dev/null || true
cp robots.txt "$DEPLOY_DIR/" 2>/dev/null || true
cp -r css "$DEPLOY_DIR/"
cp -r js "$DEPLOY_DIR/"
cp -r chapters "$DEPLOY_DIR/"
cp -r assets "$DEPLOY_DIR/" 2>/dev/null || true
cp -r docs "$DEPLOY_DIR/" 2>/dev/null || true
cp -r functions "$DEPLOY_DIR/"

echo "Deploying to Cloudflare Pages..."
npx wrangler pages deploy "$DEPLOY_DIR" --project-name projectadam --commit-dirty=true --branch production
