import time
import random
import json
from tqdm import tqdm

def add_user_info_to_cache(username, user_id, full_name, cache):
    """افزودن اطلاعات کاربر به کش"""
    cache[username] = {"user_id": user_id, "full_name": full_name}

def load_cache():
    """بارگذاری کش از فایل"""
    try:
        with open("cache.json", "r", encoding="utf-8") as cache_file:
            return json.load(cache_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_cache(cache):
    """ذخیره‌ی کش در فایل"""
    with open("cache.json", "w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file, ensure_ascii=False, indent=4)

def get_user_info_from_cache(username, cache):
    """دریافت اطلاعات کاربر از کش"""
    return cache.get(username, None)

def fetch_user_info_batch(clients, usernames, cache):
    """دریافت اطلاعات ۲۰ کاربر به‌صورت گروهی و ذخیره در کش"""
    client_index = 0
    for i, username in enumerate(usernames):
        cl = clients[client_index]
        try:
            user_id = cl.user_id_from_username(username)
            if not user_id:
                raise ValueError("User ID is None")

            user_info = cl.user_info(user_id)
            full_name = user_info.full_name

            # افزودن اطلاعات کاربر به کش
            add_user_info_to_cache(username, user_id, full_name, cache)
            save_cache(cache)  # ذخیره‌ی کش بلافاصله پس از تغییر
            print(f"✅ اطلاعات کاربر {username} به کش اضافه شد.")

            # تغییر اکانت برای کاربر بعدی
            client_index = (client_index + 1) % len(clients)

            # تاخیر بین درخواست‌ها
            if (i + 1) % 20 == 0:  # پس از هر ۲۰ کاربر
                delay = random.uniform(300, 600)  # تاخیر بین ۵ تا ۱۰ دقیقه
                print(f"⏳ در انتظار {int(delay)} ثانیه قبل از دریافت اطلاعات کاربران بعدی...")
                time.sleep(delay)

        except Exception as e:
            print(f"⚠️ خطا در دریافت اطلاعات کاربر {username}: {e}")
            with open("error_log.txt", "a", encoding="utf-8") as error_file:
                error_file.write(f"خطا در دریافت اطلاعات کاربر {username}: {e}\n")

def send_messages(clients, user_ids, messages):
    total_sent = 0
    start_time = time.time()

    # خواندن لیست فالوورها
    try:
        with open("followers.txt", "r", encoding="utf-8") as file:
            followers = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("⚠️ فایل followers.txt یافت نشد. لطفاً فایل را بررسی کنید.")
        return

    cache = load_cache()  # بارگذاری کش

    # دریافت اطلاعات ۲۰ کاربر به‌صورت گروهی
    fetch_user_info_batch(clients, user_ids[:20], cache)

    client_index = 0  # شروع از اولین اکانت

    for i, user in enumerate(tqdm(user_ids, desc="📨 Sending Messages")):
        cl = clients[client_index]

        try:
            delay = random.uniform(60, 120)  # تاخیر بین ۱ تا ۲ دقیقه
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
                    save_cache(cache)  # ذخیره‌ی کش بلافاصله پس از تغییر
                    print(f"✅ اطلاعات کاربر {user} به کش اضافه شد.")
                except Exception as e:
                    print(f"⚠️ خطا در دریافت اطلاعات کاربر {user}: {e}")
                    continue

            message_index = random.randint(0, len(messages) - 1)
            message = messages[message_index].replace("{user}", full_name)

            try:
                cl.direct_send(message, [user_id])
                print(f"✅ پیام {message_index + 1} به {full_name} ارسال شد.")
            except Exception as e:
                print(f"⚠️ خطا در ارسال پیام به {user}: {e}")
                continue

            with open("senduser.txt", "a", encoding="utf-8") as send_file:
                send_file.write(f"{full_name} - پیام {message_index + 1}\n")

            # حذف کاربر از لیست followers.txt پس از ارسال موفق
            if user in followers:
                followers.remove(user)
                with open("followers.txt", "w", encoding="utf-8") as file:
                    file.writelines(f"{f}\n" for f in followers)

            total_sent += 1

            # ذخیره وضعیت ارسال
            with open("status.json", "w", encoding="utf-8") as status_file:
                json.dump({"sent": total_sent, "remaining": len(followers)}, status_file)

            # بررسی محدودیت زمانی ۱ ساعته
            if time.time() - start_time > 3600:
                with open("report.txt", "a", encoding="utf-8") as report_file:
                    report_file.write(f"{total_sent} پیام در ۱ ساعت ارسال شد.\n")
                total_sent = 0
                start_time = time.time()

        except Exception as e:
            print(f"⚠️ خطا در ارسال پیام به {user}: {e}")

            if "429" in str(e) or "Too Many Requests" in str(e):
                sleep_time = random.uniform(3600, 7200)  # توقف بین ۱ تا ۲ ساعت
                print(f"🚨 اینستاگرام محدودیت اعمال کرده، توقف برای {int(sleep_time / 60)} دقیقه...")
                time.sleep(sleep_time)

        # تغییر اکانت برای پیام بعدی
        client_index = (client_index + 1) % len(clients)

    # ذخیره‌ی کش در فایل
    save_cache(cache)

    # نوشتن لیست جدید کاربران باقی‌مانده در followers.txt
    with open("followers.txt", "w", encoding="utf-8") as file:
        file.writelines(f"{f}\n" for f in followers)