import requests
import json
import time
from PIL import Image, ImageDraw, ImageFont

# ========= CONFIG =========
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"   # <-- apna bot token daalo
API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/?num="
API_KEY = "7189814021"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

user_state = {}

# ========= SEND MESSAGE =========
def send_message(chat_id, text):
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })

# ========= SEND PHOTO =========
def send_photo(chat_id, file_path, caption):
    with open(file_path, "rb") as photo:
        requests.post(BASE_URL + "sendPhoto",
            files={"photo": photo},
            data={
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
        )

# ========= KEYBOARD =========
def keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }

# ========= GET UPDATES =========
def get_updates(offset):
    return requests.get(BASE_URL + "getUpdates", params={
        "offset": offset,
        "timeout": 30
    }).json()

# ========= PARSE DATA =========
def parse_data(data):
    info = data.get("data", data)

    return {
        "name": info.get("name") or info.get("Name") or "N/A",
        "father": info.get("father_name") or info.get("father") or "N/A",
        "gmail": info.get("email") or info.get("gmail") or "N/A",
        "city": info.get("city") or "N/A",
        "address": info.get("address") or info.get("full_address") or "N/A"
    }

# ========= HD IMAGE CARD =========
def create_card(data):
    width, height = 900, 550
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for i in range(height):
        r = int(20 + (i / height) * 40)
        g = int(20 + (i / height) * 80)
        b = int(40 + (i / height) * 120)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        text_font = ImageFont.truetype("arial.ttf", 30)
        small_font = ImageFont.truetype("arial.ttf", 22)
    except:
        title_font = text_font = small_font = ImageFont.load_default()

    # Title
    draw.text((250, 30), "PHONE LOOKUP", font=title_font, fill=(0, 255, 200))

    # Box
    draw.rectangle([50, 120, 850, 500], outline=(0,255,200), width=3)

    # Data
    y = 150
    gap = 65

    draw.text((80, y), f"👤 Name: {data['name']}", font=text_font, fill=(255,255,255)); y+=gap
    draw.text((80, y), f"👨‍👦 Father: {data['father']}", font=text_font, fill=(255,255,255)); y+=gap
    draw.text((80, y), f"📧 Gmail: {data['gmail']}", font=text_font, fill=(255,255,255)); y+=gap
    draw.text((80, y), f"🏙️ City: {data['city']}", font=text_font, fill=(255,255,255)); y+=gap
    draw.text((80, y), f"🏠 Address: {data['address']}", font=text_font, fill=(255,255,255))

    # Footer
    draw.text((250, 510), "Powered by Premium Lookup", font=small_font, fill=(200,200,200))

    path = "hd_result.png"
    img.save(path)
    return path

# ========= TEXT FORMAT =========
def format_text(d):
    return f"""
<b>📱 PHONE LOOKUP RESULT</b>

━━━━━━━━━━━━━━━
👤 <b>NAME:</b> {d['name']}
👨‍👦 <b>FATHER NAME:</b> {d['father']}
📧 <b>GMAIL:</b> {d['gmail']}
🏙️ <b>CITY:</b> {d['city']}
🏠 <b>ADDRESS:</b> {d['address']}
━━━━━━━━━━━━━━━

🔎 <i>Premium Lookup Service</i>

📢 <a href="https://t.me/plus_official01">Join Channel</a>
"""

# ========= LOOKUP =========
def process_lookup(chat_id, number):
    try:
        res = requests.get(API_URL + number + "&key=" + API_KEY)
        data = res.json()

        parsed = parse_data(data)

        # Text
        send_message(chat_id, format_text(parsed))

        # HD Card
        img = create_card(parsed)
        send_photo(chat_id, img, "📊 Premium Result Card")

    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")

# ========= HANDLE =========
def handle(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")
    chat_type = message["chat"]["type"]

    # START
    if text == "/start":
        send_message(chat_id, "👋 Welcome!\nUse button below")

        requests.post(BASE_URL + "sendMessage", data={
            "chat_id": chat_id,
            "text": "Choose option:",
            "reply_markup": json.dumps(keyboard())
        })
        return

    # GROUP COMMAND (/num)
    if text.startswith("/num"):
        number = text.replace("/num", "").strip()

        if number.isdigit() and len(number) == 10:
            process_lookup(chat_id, number)
        else:
            send_message(chat_id, "❌ Use:\n/num 9876543210")
        return

    # PRIVATE
    if chat_type == "private":

        if text == "📱 Phone Lookup":
            send_message(chat_id, "📞 Send 10 digit number:")
            user_state[user_id] = "wait"
            return

        if user_state.get(user_id) == "wait":
            if text.isdigit() and len(text) == 10:
                process_lookup(chat_id, text)
                user_state[user_id] = None
            else:
                send_message(chat_id, "❌ Invalid number")

# ========= MAIN =========
def main():
    offset = 0
    print("Bot Running...")

    while True:
        try:
            updates = get_updates(offset)

            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1

                    if "message" in update:
                        handle(update["message"])

        except Exception as e:
            print("Error:", e)

        time.sleep(1)

# ========= RUN =========
if __name__ == "__main__":
    main()
