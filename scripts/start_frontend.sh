#!/bin/bash

set -e

cd "$(dirname "$0")/../frontend"

echo "Installing frontend dependencies..."
npm install

echo "Starting Next.js frontend..."
npm run dev
