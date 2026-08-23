import requests
import time
import os
from datetime import datetime
import pytz

# ===== دریافت توکن از متغیرهای محیطی =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ خطا: توکن ربات پیدا نشد! متغیر محیطی BOT_TOKEN را تنظیم کنید.")
    exit(1)

CHANNEL_ID = -1004305793408  # آیدی کانال خودت رو اینجا بذار
# =========================================

# دیکشنری تبدیل اعداد به فونت پررنگ
bold_numbers = {
    '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
    '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
}

def convert_to_bold(text):
    """تبدیل اعداد به فونت پررنگ"""
    result = ''
    for char in text:
        if char in bold_numbers:
            result += bold_numbers[char]
        else:
            result += char
    return result

def send_telegram_request(method, params):
    """ارسال درخواست به API تلگرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        response = requests.post(url, json=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ وضعیت غیرعادی: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ خطا در درخواست: {e}")
        return None

IRAN_TZ = pytz.timezone('Asia/Tehran')
last_message_id = None

def update_channel_name():
    global last_message_id
    
    print("✅ ربات زمان‌سنج شروع به کار کرد...")
    print(f"🆔 آیدی کانال: {CHANNEL_ID}")
    
    while True:
        try:
            # گرفتن زمان به صورت ساعت:دقیقه
            now = datetime.now(IRAN_TZ).strftime("%H:%M")
            # تبدیل اعداد به فونت پررنگ
            bold_time = convert_to_bold(now)
            new_title = f"🕐 {bold_time}"
            
            # تغییر نام کانال
            result = send_telegram_request('setChatTitle', {
                'chat_id': CHANNEL_ID,
                'title': new_title
            })
            
            if result and result.get('ok'):
                print(f"✅ نام تغییر یافت: {new_title}")
                
                # حذف پیام قبلی
                if last_message_id is not None:
                    delete_result = send_telegram_request('deleteMessage', {
                        'chat_id': CHANNEL_ID,
                        'message_id': last_message_id
                    })
                    if delete_result and delete_result.get('ok'):
                        print(f"🗑️ پیام قبلی حذف شد")
                
                # ارسال پیام جدید
                message_text = f"✅ نام کانال به «{new_title}» تغییر یافت"
                send_result = send_telegram_request('sendMessage', {
                    'chat_id': CHANNEL_ID,
                    'text': message_text
                })
                
                if send_result and send_result.get('ok'):
                    last_message_id = send_result['result']['message_id']
                    print(f"📨 پیام جدید ارسال شد (ID: {last_message_id})")
                else:
                    print(f"❌ خطا در ارسال پیام: {send_result}")
                    last_message_id = None
            else:
                print(f"❌ خطا در تغییر نام: {result}")
                if result and result.get('description') == "Forbidden: bot is not a member of the channel chat":
                    print("❌ ربات عضو کانال نیست یا ادمین نیست!")
                    break
                elif result and result.get('error_code') == 429:
                    print("⚠️ محدودیت تعداد درخواست! ۲ دقیقه صبر می‌کنم...")
                    time.sleep(120)
                    continue
            
            time.sleep(60)  # هر ۶۰ ثانیه یک بار
            
        except Exception as e:
            print(f"❌ خطای غیرمنتظره: {e}")
            time.sleep(60)

if __name__ == "__main__":
    update_channel_name()
