#!/bin/bash
# Install script 
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi
echo "venv + req + node.js + flask backend starting..."
. venv/bin/activate
venv/bin/pip install -r requirements.txt

echo "📥 Installing Node.js dependencies..."
npm install

