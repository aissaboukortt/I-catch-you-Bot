import os
import subprocess
import time
from telegram.ext import ApplicationBuilder, CommandHandler

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8612074749:AAGLniCsu_LAn3rUos4aZaqs5mRlz0QxCgE"
AUTHORIZED_CHAT_ID = 5087545397

flask_process = None

# مسارات المجلدات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
images_folder = os.path.join(BASE_DIR, "images")
sent_folder = os.path.join(BASE_DIR, "sent")
metadata_folder = os.path.join(BASE_DIR, "metadata")
sent_info_folder = os.path.join(BASE_DIR, "infos_sent")

# إنشاء المجلدات
os.makedirs(images_folder, exist_ok=True)
os.makedirs(sent_folder, exist_ok=True)
os.makedirs(metadata_folder, exist_ok=True)
os.makedirs(sent_info_folder, exist_ok=True)

def is_file_ready(filepath):
    try:
        if not os.path.exists(filepath):
            return False
        initial_size = os.path.getsize(filepath)
        time.sleep(0.3)
        return initial_size == os.path.getsize(filepath) and initial_size > 0
    except:
        return False

# =========================
# FUNCTIONS
# =========================
async def start(update, context):
    global flask_process
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    if flask_process is None:
        flask_process = subprocess.Popen(["python", "app.py"], cwd=BASE_DIR)
        await update.message.reply_text("✅ Server (Flask) Started!")
    else:
        await update.message.reply_text("⚠️ Server already running")

async def stop(update, context):
    global flask_process
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    if flask_process:
        flask_process.kill()
        flask_process = None
        await update.message.reply_text("🛑 Server stopped")
    else:
        await update.message.reply_text("⚠️ Server not running")

async def status(update, context):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    if flask_process and flask_process.poll() is None:
        await update.message.reply_text("🟢 Server online")
    else:
        await update.message.reply_text("🔴 Server offline")

async def images(update, context):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    try:
        all_files = os.listdir(images_folder)
        files = [f for f in all_files if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        files.sort()
        if not files:
            await update.message.reply_text("⚠️ No new images")
            return
        await update.message.reply_text(f"📸 Sending {len(files)} images...")
        for file in files:
            image_path = os.path.join(images_folder, file)
            target_path = os.path.join(sent_folder, file)
            if not is_file_ready(image_path):
                continue
            with open(image_path, "rb") as img:
                await update.message.reply_photo(photo=img)
            os.replace(image_path, target_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def infos(update, context):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    try:
        all_files = os.listdir(metadata_folder)
        files = [f for f in all_files if f.lower().endswith(".json")]
        files.sort()
        if not files:
            await update.message.reply_text("📭 No new metadata")
            return
        latest_file = files[-1]
        metadata_path = os.path.join(metadata_folder, latest_file)
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = f.read()
        await update.message.reply_text(f"📄 Info:\n\n{data}")
        os.replace(metadata_path, os.path.join(sent_info_folder, latest_file))
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# =========================
# BOT INIT
# =========================
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("images", images))
app.add_handler(CommandHandler("infos", infos))

print("🤖 Bot running...")
app.run_polling()
