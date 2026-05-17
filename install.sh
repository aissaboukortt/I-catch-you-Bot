#!/bin/bash

set -e

PROJECT_DIR="$HOME/cam-capture"

echo "📦 Updating Termux..."
pkg update -y && pkg upgrade -y

echo "📦 Installing dependencies..."
pkg install -y python git cloudflared

echo "📦 Removing old project..."
rm -rf $PROJECT_DIR

echo "📥 Cloning repository..."
git clone https://github.com/aissaboukortt/Termux-Scripts.git $PROJECT_DIR

cd $PROJECT_DIR || {
    echo "❌ Failed to enter project directory"
    exit 1
}

echo "📂 Detecting project structure..."

# تحديد مكان bot.py بشكل ذكي
if [ -f "bot.py" ]; then
    echo "✅ bot.py found in root"

elif [ -f "cam-capture/bot.py" ]; then
    echo "📁 bot.py found in cam-capture folder"
    cd cam-capture

elif find . -name "bot.py" | grep -q "bot.py"; then
    BOT_PATH=$(find . -name "bot.py" | head -n 1)
    BOT_DIR=$(dirname "$BOT_PATH")
    echo "📁 bot.py found at: $BOT_DIR"
    cd "$BOT_DIR"

else
    echo "❌ bot.py NOT FOUND!"
    echo "📂 Full project structure:"
    ls -R
    exit 1
fi

echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install flask python-telegram-bot

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To start bot:"
echo "python bot.py"
echo ""
echo "⚡ Recommended:"
echo "python bot.py (control everything from Telegram)"
