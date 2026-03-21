import requests
import json
import time

# ========= CONFIG =========
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"   # ADD TOKEN
API_URL = "https://yash-code-with-ai.alphamovies.workers.dev/?num=9918824247&key=7189814021"     # ADD YOUR API (example: https://api.com/?num=)

ADMIN_ID = 8351165824

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

user_state = {}

# ========= SEND MESSAGE =========
def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, data=data)

# ========= KEYBOARD =========
def keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }

# ========= GET UPDATES =========
def get_updates(offset):
    url = BASE_URL + "getUpdates"
    params = {"offset": offset, "timeout": 30}
    return requests.get(url, params=params).json()

# ========= FORMAT RESPONSE =========
def format_data(data):
    try:
        name = data.get("name", "N/A")
        father = data.get("father_name", "N/A")
        gmail = data.get("email", "N/A")
        city = data.get("city", "N/A")
        address = data.get("address", "N/A")

        msg = f"""
<b>📱 PHONE LOOKUP RESULT</b>

━━━━━━━━━━━━━━━
👤 <b>NAME:</b> {name}
👨‍👦 <b>FATHER NAME:</b> {father}
📧 <b>GMAIL:</b> {gmail}
🏙️ <b>CITY:</b> {city}
🏠 <b>ADDRESS:</b> {address}
━━━━━━━━━━━━━━━

🔎 <i>Powered by Lookup System</i>

📢 Subscribe: https://t.me/plus_official01
"""
        return msg
    except:
        return "<b>❌ Error formatting data</b>"

# ========= HANDLE =========
def handle(msg):
    chat_id = msg["chat"]["id"]
    user_id = msg["from"]["id"]
    text = msg.get("text", "")

    if text == "/start":
        send_message(chat_id, "👋 Welcome!\nSelect option below:", keyboard())
        return

    if text == "📱 Phone Lookup":
        send_message(chat_id, "📞 Send 10 digit mobile number:")
        user_state[user_id] = "wait"
        return

    if user_state.get(user_id) == "wait":
        if text.isdigit() and len(text) == 10:
            try:
                res = requests.get(API_URL + text)
                data = res.json()

                formatted = format_data(data)

                send_message(chat_id, formatted)

            except:
                send_message(chat_id, "❌ API Error")

            user_state[user_id] = None
        else:
            send_message(chat_id, "❌ Invalid number")

# ========= MAIN LOOP =========
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

if __name__ == "__main__":
    main()
