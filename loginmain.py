import os
import time
import random
from instagrapi import Client

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)
 
ACCOUNTS = [
    # {"username": "tablighatche1", "password": "a1s2a3ASD!@#"},
    {"username": "mrtablighat2", "password": "Ariyo14528!"},
    {"username": "social.panel5", "password": "a1s2a3ASD!@#"},
    {"username": "social.panel6", "password": "a1s2a3ASD!@#"},


]

def get_client(account):
    """بررسی و بارگذاری سشن؛ در صورت عدم وجود یا عدم اعتبار، لاگین جدید و ذخیره سشن."""
    username = account["username"]
    session_file = os.path.join(SESSION_DIR, f"{username}.json")
    cl = Client()

    # اگر سشن موجود است، آن را بارگذاری و از آن استفاده می‌کند
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(username, account["password"])
            print(f"✅ {username} با سشن موجود لاگین شد.")
            return cl
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری سشن {username}: {e}")

    # اگر سشن موجود نباشد یا دچار مشکل باشد، لاگین جدید انجام می‌دهد
    try:
        delay = random.uniform(10, 60)
        time.sleep(delay)
        cl.login(username, account["password"])
        cl.dump_settings(session_file)
        print(f"✅ {username} با موفقیت لاگین و سشن ذخیره شد.")
        return cl
    except Exception as e:
        print(f"❌ خطای لاگین برای {username}: {e}")
        return None

def login_accounts():
    """لاگین به همه اکانت‌ها و بازگرداندن کلاینت‌های آماده استفاده"""
    clients = []
    for account in ACCOUNTS:
        client = get_client(account)
        if client:
            clients.append(client)
    return clients

if __name__ == '__main__':
    # عملیات لاگین و ذخیره سشن‌ها اجرا می‌شود
    clients = login_accounts()
    print("✅ تمامی اکانت‌ها لاگین شدند و سشن‌ها ذخیره گردید.")
