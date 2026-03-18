#!/usr/bin/env bash
set -euo pipefail

python3 -m pytest --cov=src --cov-report=term-missing --cov-report=html
echo "HTML coverage report generated at: htmlcov/index.html"
