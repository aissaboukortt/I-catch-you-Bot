import os, subprocess, time, threading
from telegram.ext import ApplicationBuilder, CommandHandler
from flask import Flask

# 1. السيرفر الوهمي لإرضاء Render ومنع خطأ No open ports
app_web = Flask(__name__)
@app_web.route('/')
def home(): return "Bot is running"
def run_web(): app_web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
threading.Thread(target=run_web, daemon=True).start()

# 2. إعدادات البوت
BOT_TOKEN = "8612074749:AAHGvzF43cf5AkwzGhEDJHgvwNRF2KaO2qg"
AUTHORIZED_CHAT_ID = 5087545397
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
flask_process = None

# 3. الدوال
async def start(u, c):
    global flask_process
    if u.effective_chat.id != AUTHORIZED_CHAT_ID: return
    if flask_process is None:
        flask_process = subprocess.Popen(["python", "app.py"], cwd=BASE_DIR)
        await u.message.reply_text("✅ Server Started!\n🌍 Link: https://i-catch-you-bot.onrender.com/")
    else:
        await u.message.reply_text("⚠️ Server already running")

async def stop(u, c):
    global flask_process
    if u.effective_chat.id != AUTHORIZED_CHAT_ID: return
    if flask_process:
        flask_process.kill()
        flask_process = None
        await u.message.reply_text("🛑 Server stopped")

async def images(u, c):
    if u.effective_chat.id != AUTHORIZED_CHAT_ID: return
    img_dir = os.path.join(BASE_DIR, "images")
    files = [f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    if not files:
        await u.message.reply_text("⚠️ No images")
        return
    for f in files:
        with open(os.path.join(img_dir, f), "rb") as img:
            await u.message.reply_photo(photo=img)
        os.replace(os.path.join(img_dir, f), os.path.join(BASE_DIR, "sent", f))

# 4. تشغيل البوت
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("images", images))

print("🤖 Bot running...")
app.run_polling()
