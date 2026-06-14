#!/bin/bash

set -e

cd "$(dirname "$0")/../backend"

echo "Removing local SQLite demo database..."
rm -f risk_intel.db

echo "Demo data reset complete. Restart the backend to recreate tables."
