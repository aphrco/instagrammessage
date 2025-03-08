import os
import time
import random
from instagrapi import Client

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

ACCOUNTS = [
    # {"username": "tablighatche1", "password": "a1s2a3ASD!@#"},
    # {"username": "mrtablighat2", "password": "Ariyo14528!"},
    # {"username": "social.panel5", "password": "a1s2a3ASD!@#"},
    # {"username": "social.panel6", "password": "a1s2a3ASD!@#"},
    {"username": "tablighads1", "password": "a1s2a3ASD!@#"},

]

def get_client(account):
    """بررسی و بارگذاری سشن، در صورت عدم وجود لاگین می‌کند و سشن را ذخیره می‌کند."""
    username = account["username"]
    session_file = os.path.join(SESSION_DIR, f"{username}.json")
    cl = Client()

    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
            cl.login(username, account["password"])
            print(f"✅ {username} با سشن موجود لاگین شد.")
            return cl
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری سشن {username}: {e}")

    # اگر سشن معتبر نبود، لاگین جدید انجام دهد
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