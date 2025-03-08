import time
import random
import json
from tqdm import tqdm
from login import login_accounts

# تنظیمات کش
CACHE_FILE = "cache.json"

def load_cache():
    """بارگذاری کش از فایل"""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    """ذخیره‌ی کش در فایل"""
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=4)

def get_user_info_from_cache(username, cache):
    """دریافت اطلاعات کاربر از کش"""
    return cache.get(username, None)

def add_user_info_to_cache(username, user_id, full_name, cache):
    """افزودن اطلاعات کاربر به کش"""
    cache[username] = {"user_id": user_id, "full_name": full_name}

def read_ids_from_file(filename):
    """خواندن شناسه‌های کاربران از فایل"""
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def read_messages_from_file(filename):
    """خواندن پیام‌ها از فایل"""
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read().strip()
        messages = content.split("\n--*--\n")
        messages = [message.replace("*", "").strip() for message in messages]
        return messages if messages else ["سلام! پیچ @ali.bakhtiarib را فالوو داری؟."]

def send_messages(clients, user_ids, messages):
    """ارسال پیام‌ها به کاربران"""
    total_sent = 0
    start_time = time.time()

    with open("followers.txt", "r", encoding="utf-8") as file:
        followers = [line.strip() for line in file if line.strip()]

    cache = load_cache()  # بارگذاری کش
    client_index = 0  # شروع از اولین اکانت

    for i, user in enumerate(tqdm(user_ids, desc="📨 Sending Messages")):
        cl = clients[client_index]
        delay = random.uniform(1, 10)
        print(f"⏳ در انتظار {int(delay)} ثانیه برای تغییر اکانت...")
        time.sleep(delay)

        try:
            delay = random.uniform(60, 500)  # افزایش تاخیر
            print(f"⏳ در انتظار {int(delay)} ثانیه قبل از ارسال پیام به {user}...")
            time.sleep(delay)

            # بررسی کش برای اطلاعات کاربر
            cached_info = get_user_info_from_cache(user, cache)
            if cached_info:
                user_id = cached_info["user_id"]
                full_name = cached_info["full_name"]
                print(f"✅ اطلاعات کاربر {user} از کش بازیابی شد.")
            else:
                try:
                    user_id = cl.user_id_from_username(user)
                    if not user_id:
                        raise ValueError("User ID is None")

                    user_info = cl.user_info(user_id)
                    full_name = user_info.full_name

                    # افزودن اطلاعات کاربر به کش
                    add_user_info_to_cache(user, user_id, full_name, cache)
                    print(f"✅ اطلاعات کاربر {user} به کش اضافه شد.")
                except Exception as e:
                    print(f"⚠️ خطا در دریافت اطلاعات کاربر {user}: {e}")
                    with open("error_log.txt", "a", encoding="utf-8") as error_file:
                        error_file.write(f"خطا در دریافت اطلاعات کاربر {user}: {e}\n")
                    continue

            message_index = random.randint(0, len(messages) - 1)
            message = messages[message_index].replace("{user}", full_name)

            cl.direct_send(message, [user_id])
            print(f"✅ پیام {message_index + 1} به {full_name} ارسال شد.")

            with open("senduser.txt", "a", encoding="utf-8") as send_file:
                send_file.write(f"{full_name} - پیام {message_index + 1}\n")

            # حذف کاربر از لیست followers.txt پس از ارسال موفق
            if user in followers:
                followers.remove(user)
                with open("followers.txt", "w", encoding="utf-8") as file:
                    file.writelines(f"{f}\n" for f in followers)

            total_sent += 1

            with open("status.json", "w", encoding="utf-8") as status_file:
                json.dump({"sent": total_sent, "remaining": len(followers)}, status_file)

            if time.time() - start_time > 3600:
                with open("report.txt", "a", encoding="utf-8") as report_file:
                    report_file.write(f"{total_sent} پیام در ۱ ساعت ارسال شد.\n")
                total_sent = 0
                start_time = time.time()

        except Exception as e:
            print(f"⚠️ خطا در ارسال پیام به {user}: {e}")
            with open("error_log.txt", "a", encoding="utf-8") as error_file:
                error_file.write(f"خطا در ارسال پیام به {user}: {e}\n")

            if "429" in str(e) or "Too Many Requests" in str(e):
                sleep_time = random.uniform(1800, 3600)  # توقف بین ۳۰ تا ۶۰ دقیقه
                print(f"🚨 اینستاگرام محدودیت اعمال کرده، توقف برای {int(sleep_time / 60)} دقیقه...")
                time.sleep(sleep_time)

        # تغییر اکانت برای پیام بعدی
        client_index = (client_index + 1) % len(clients)

    # ذخیره‌ی کش در فایل
    save_cache(cache)

    # نوشتن لیست جدید کاربران باقی‌مانده در followers.txt
    with open("followers.txt", "w", encoding="utf-8") as file:
        for follower in followers:
            file.write(f"{follower}\n")

if __name__ == "__main__":
    user_ids = read_ids_from_file("followers.txt")
    messages = read_messages_from_file("messages.txt")

    time.sleep(random.uniform(10, 60))
    clients = login_accounts()

    if clients:
        send_messages(clients, user_ids, messages)
    else:
        print("❌ هیچ اکانتی لاگین نشد. بررسی کنید!")