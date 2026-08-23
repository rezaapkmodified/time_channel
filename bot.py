import requests
import time
from datetime import datetime
import pytz

BOT_TOKEN = '5198891980:AAFqrf9xrZifj8Vxsbpm7UpGQxWMPjUVneQ'
CHANNEL_ID = -1004305793408

# ایجاد session برای درخواست‌ها
session = requests.Session()
session.trust_env = False  # غیرفعال کردن پراکسی خودکار

bold_numbers = {
    '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
    '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
}

def convert_to_bold(text):
    result = ''
    for char in text:
        if char in bold_numbers:
            result += bold_numbers[char]
        else:
            result += char
    return result

def send_telegram_request(method, params):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        response = session.post(url, json=params, timeout=30)
        return response.json()
    except Exception as e:
        print(f"❌ خطا: {e}")
        return None

IRAN_TZ = pytz.timezone('Asia/Tehran')
last_message_id = None

def update_channel_name():
    global last_message_id

    while True:
        now = datetime.now(IRAN_TZ).strftime("%H:%M")
        bold_time = convert_to_bold(now)
        new_title = f"🕐 {bold_time}"

        result = send_telegram_request('setChatTitle', {
            'chat_id': CHANNEL_ID,
            'title': new_title
        })

        if result and result.get('ok'):
            print(f"✅ نام تغییر یافت: {new_title}")

            if last_message_id is not None:
                delete_result = send_telegram_request('deleteMessage', {
                    'chat_id': CHANNEL_ID,
                    'message_id': last_message_id
                })

            message_text = f"✅ نام کانال به «{new_title}» تغییر یافت"
            send_result = send_telegram_request('sendMessage', {
                'chat_id': CHANNEL_ID,
                'text': message_text
            })

            if send_result and send_result.get('ok'):
                last_message_id = send_result['result']['message_id']
                print(f"📨 پیام جدید ارسال شد")
        else:
            print(f"❌ خطا: {result}")

        time.sleep(60)

if __name__ == "__main__":
    print("ربات زمان‌سنج شروع به کار کرد...")
    update_channel_name()
