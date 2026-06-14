#!/bin/bash

set -e

cd "$(dirname "$0")/../backend"

if [ ! -d "venv" ]; then
  echo "Creating backend virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Starting FastAPI backend..."
uvicorn main:app --reload
