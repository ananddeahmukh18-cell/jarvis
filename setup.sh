#!/bin/bash
# JARVIS AI Assistant - One-Click Setup for macOS
# Run: bash setup.sh

set -e
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   JARVIS AI — macOS Setup Script     ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python 3 not found. Install from https://python3.org"
  exit 1
fi
echo "✅ Python: $(python3 --version)"

# Create venv
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install deps
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "✅ All dependencies installed!"
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Starting JARVIS...                 ║"
echo "║   Open: http://localhost:5000        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Run
python3 app.py
