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

# ========= SEND =========
def send_message(chat_id, text):
    requests.post(BASE_URL + "sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })

def send_photo(chat_id, file_path, caption):
    with open(file_path, "rb") as photo:
        requests.post(BASE_URL + "sendPhoto",
            files={"photo": photo},
            data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
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

# ========= AI PARSER =========
def extract_all(obj, res):
    if isinstance(obj, dict):
        for k, v in obj.items():
            res.append((k.lower(), v))
            extract_all(v, res)
    elif isinstance(obj, list):
        for i in obj:
            extract_all(i, res)

def smart_parse(data):
    res = []
    extract_all(data, res)

    parsed = {
        "name": "N/A",
        "father": "N/A",
        "gmail": "N/A",
        "city": "N/A",
        "address": "N/A"
    }

    for k, v in res:
        val = str(v)

        if parsed["name"] == "N/A" and "name" in k and "father" not in k:
            parsed["name"] = val

        elif parsed["father"] == "N/A" and ("father" in k or "fname" in k):
            parsed["father"] = val

        elif parsed["gmail"] == "N/A" and ("mail" in k or "email" in k):
            parsed["gmail"] = val

        elif parsed["city"] == "N/A" and ("city" in k or "district" in k):
            parsed["city"] = val

        elif parsed["address"] == "N/A" and ("address" in k or "location" in k):
            parsed["address"] = val

    return parsed

# ========= ULTRA PREMIUM CARD =========
def create_card(data):
    width, height = 1000, 600
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for i in range(height):
        r = int(10 + (i / height) * 50)
        g = int(20 + (i / height) * 100)
        b = int(40 + (i / height) * 160)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    try:
        title_font = ImageFont.truetype("arial.ttf", 50)
        label_font = ImageFont.truetype("arial.ttf", 30)
        value_font = ImageFont.truetype("arial.ttf", 32)
    except:
        title_font = label_font = value_font = ImageFont.load_default()

    draw.text((300, 30), "PHONE LOOKUP", font=title_font, fill=(0, 255, 220))

    box = [80, 130, 920, 520]

    # Glow border
    for i in range(5):
        draw.rectangle(
            [box[0]-i, box[1]-i, box[2]+i, box[3]+i],
            outline=(0,255,200)
        )

    # Data
    y = 170
    gap = 70

    def row(label, value):
        nonlocal y
        draw.text((120, y), label, font=label_font, fill=(0,255,200))
        draw.text((350, y), f": {value}", font=value_font, fill=(255,255,255))
        y += gap

    row("👤 NAME", data['name'])
    row("👨‍👦 FATHER", data['father'])
    row("📧 EMAIL", data['gmail'])
    row("🏙️ CITY", data['city'])
    row("🏠 ADDRESS", data['address'])

    draw.text((320, 550), "Premium Lookup System", font=label_font, fill=(180,180,180))

    path = "ultra_result.png"
    img.save(path)
    return path

# ========= FORMAT =========
def format_text(d):
    return f"""
<b>📱 PHONE LOOKUP RESULT</b>

━━━━━━━━━━━━━━━
👤 <b>NAME:</b> {d['name']}
👨‍👦 <b>FATHER:</b> {d['father']}
📧 <b>EMAIL:</b> {d['gmail']}
🏙️ <b>CITY:</b> {d['city']}
🏠 <b>ADDRESS:</b> {d['address']}
━━━━━━━━━━━━━━━

📢 <a href="https://t.me/plus_official01">Join Channel</a>
"""

# ========= LOOKUP =========
def process_lookup(chat_id, number):
    try:
        url = f"{API_URL}{number}&key={API_KEY}"
        res = requests.get(url)

        data = res.json()
        print("API:", data)

        parsed = smart_parse(data)

        send_message(chat_id, format_text(parsed))

        img = create_card(parsed)
        send_photo(chat_id, img, "📊 Premium Result")

    except Exception as e:
        send_message(chat_id, f"❌ Error: {e}")

# ========= HANDLE =========
def handle(msg):
    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    text = msg.get("text","")
    chat_type = msg["chat"]["type"]

    if text == "/start":
        send_message(chat_id, "👋 Welcome")
        requests.post(BASE_URL+"sendMessage", data={
            "chat_id": chat_id,
            "text": "Select option:",
            "reply_markup": json.dumps(keyboard())
        })
        return

    # GROUP COMMAND
    if text.startswith("/num"):
        num = text.replace("/num","").strip()

        if num.isdigit() and len(num)==10:
            process_lookup(chat_id, num)
        else:
            send_message(chat_id, "❌ Use:\n/num 9876543210")
        return

    # PRIVATE
    if chat_type == "private":

        if text == "📱 Phone Lookup":
            send_message(chat_id, "📞 Send number:")
            user_state[user_id] = "wait"
            return

        if user_state.get(user_id) == "wait":
            if text.isdigit() and len(text)==10:
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
                for u in updates["result"]:
                    offset = u["update_id"] + 1

                    if "message" in u:
                        handle(u["message"])

        except Exception as e:
            print("Error:", e)

        time.sleep(1)

# ========= RUN =========
if __name__ == "__main__":
    main()
