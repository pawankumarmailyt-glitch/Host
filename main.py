import requests
import json
import time

# ========== CONFIG ==========
BOT_TOKEN = "8659209680:AAF0PFICCemksGbnoFk_DgEqNhGsGlDhBiU"   # <-- apna bot token daalo
ADMIN_ID = 8351165824  # <-- apna Telegram ID

# ====== AUTO ADDED APIs ======
NUMBER_API = "https://yash-code-with-ai.alphamovies.workers.dev/"
API_KEY = "7189814021"

SHORTNER_API_KEY = "70a4cdbd945a01d2be1459bef097f66fd742508b"
SHORTNER_WEBSITE = "arolinks.com"

# ========== STORAGE ==========
verified_users = {}
daily_verified = 0
last_day = time.strftime("%Y-%m-%d")

# ========== TELEGRAM ==========
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

def send_message(chat_id, text, keyboard=None):
    url = BASE_URL + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)

    requests.post(url, data=data)

def get_updates(offset):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 100, "offset": offset}
    return requests.get(url, params=params).json()

# ========== KEYBOARD ==========
def keyboard():
    return {
        "keyboard": [[{"text": "📱 Phone Lookup"}]],
        "resize_keyboard": True
    }

# ========== VERIFY ==========
def is_verified(user_id):
    if user_id in verified_users:
        if time.time() - verified_users[user_id] < 12 * 3600:
            return True
    return False

def verify_user(user_id):
    global daily_verified
    verified_users[user_id] = time.time()
    daily_verified += 1

# ========== SHORTNER ==========
def create_link(user_id):
    long_url = f"https://t.me/numbertoinffo1_bot?start=verify_{user_id}"

    try:
        url = f"https://{SHORTNER_WEBSITE}/api"
        params = {
            "api": SHORTNER_API_KEY,
            "url": long_url
        }
        res = requests.get(url, params=params).json()
        return res.get("shortenedUrl")
    except:
        return None

# ========== API CALL ==========
def get_info(number):
    try:
        url = f"{NUMBER_API}?num={number}&key={API_KEY}"
        res = requests.get(url)
        return res.json()
    except:
        return None

# ========== FORMAT ==========
def format_result(data, number):
    try:
        records = data.get("data", [])

        if not records:
            return "❌ No data found"

        text = f"✅ Found {len(records)} record(s) for {number}:\n\n"

        for i, r in enumerate(records, 1):
            text += f"📍 RESULT #{i}\n"
            text += f"🆔 ID: {r.get('id','N/A')}\n"
            text += f"👤 Name: {r.get('name','N/A')}\n"
            text += f"👨‍💼 Father: {r.get('father_name','N/A')}\n"
            text += f"📞 Mobile: {r.get('mobile','N/A')}\n"
            text += f"📱 Alt: {r.get('alt_mobile','N/A')}\n"
            text += f"🌐 Circle: {r.get('circle','N/A')}\n"
            text += f"🏠 Address: {r.get('address','N/A')}\n"
            text += "━━━━━━━━━━━━━━━━━━━━\n\n"

        text += "🛠 Dev: @plus_official01"
        text += "👑 Owner: @plus_official01"
        text += "📢 Subscribe: https://t.me/plus_official01"

        return f"<pre>{text}</pre>"

    except:
        return "❌ Error formatting"

# ========== DAILY REPORT ==========
def daily_report():
    global daily_verified, last_day

    today = time.strftime("%Y-%m-%d")

    if today != last_day:
        send_message(
            ADMIN_ID,
            f"📊 Daily Verification Report\n\n✅ Completed: {daily_verified}"
        )
        daily_verified = 0
        last_day = today

# ========== MAIN ==========
def main():
    offset = 0

    while True:
        try:
            daily_report()

            updates = get_updates(offset)

            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")

                    # START
                    if text.startswith("/start"):
                        if "verify_" in text:
                            verify_user(user_id)
                            send_message(chat_id, "✅ Verification successful!")
                            continue

                        send_message(chat_id, "👋 Welcome!", keyboard())
                        continue

                    # BUTTON
                    if text == "📱 Phone Lookup":
                        if not is_verified(user_id):
                            link = create_link(user_id)
                            if link:
                                send_message(chat_id, f"🔐 Verify first:\n{link}")
                            else:
                                send_message(chat_id, "❌ Shortner error")
                            continue

                        send_message(chat_id, "📞 Send 10 digit mobile number:")
                        continue

                    # NUMBER
                    if text.isdigit() and len(text) == 10:
                        if not is_verified(user_id):
                            send_message(chat_id, "❌ Please verify first")
                            continue

                        data = get_info(text)

                        if data:
                            result = format_result(data, text)
                            send_message(chat_id, result)
                        else:
                            send_message(chat_id, "❌ API Error")
                    else:
                        send_message(chat_id, "❌ Send valid 10 digit number")

            time.sleep(1)

        except Exception as e:
            print("Error:", e)
            time.sleep(3)

# ========== RUN ==========
if __name__ == "__main__":
    main()
