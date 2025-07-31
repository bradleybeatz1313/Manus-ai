#!/bin/bash

# AI Voice Receptionist - Start Script
# Simple script to start the AI Voice Receptionist system

echo "🤖 Starting AI Voice Receptionist..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Configuration file (.env) not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "🚀 Starting server on http://localhost:5000"
python src/main.py

