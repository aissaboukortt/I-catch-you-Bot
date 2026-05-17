from telegram.ext import ApplicationBuilder, CommandHandler
import subprocess
import re
import os

BOT_TOKEN = "Enter the bot token"
AUTHORIZED_CHAT_ID = enter chat id

flask_process = None
cloudflared_process = None

# إنشاء المجلدات
os.makedirs("images", exist_ok=True)
os.makedirs("sent", exist_ok=True)
os.makedirs("metadata", exist_ok=True)


# START SERVER
async def start(update, context):

    global flask_process
    global cloudflared_process

    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return

    if flask_process is None:

        flask_process = subprocess.Popen(
            ["python", "app.py"]
        )

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
