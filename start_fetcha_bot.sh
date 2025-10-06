#!/bin/bash
# Fetcha Bot Startup Script
# Created: 2025-01-06 21:44 AEST (Brisbane)

echo "🚀 Starting Fetcha Bot..."
echo ""

# Change to bot directory
cd /Users/willsimpson/Documents/Fields/Property\ Scraping_V3/07_Telegram_App/Exploration

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "⚠️  Warning: .env file not found"
    echo "Please set TELEGRAM_BOT_TOKEN manually:"
    echo "export TELEGRAM_BOT_TOKEN='your_token_here'"
    exit 1
fi

# Check if token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

echo "✅ Bot token found"
echo ""

# Check if python-telegram-bot is installed
if ! python3 -c "import telegram" 2>/dev/null; then
    echo "📦 Installing python-telegram-bot..."
    pip install python-telegram-bot
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🤖 Launching Fetcha Bot..."
echo "Press Ctrl+C to stop"
echo ""

# Run the bot
python3 telegram_price_tracker_mvp.py
