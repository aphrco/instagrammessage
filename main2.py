import time
import random
import json
import sys
from tqdm import tqdm
from login import login_accounts  # دریافت کلاینت‌ها از فایل login.py

def read_ids_from_file(filename):
    """خواندن نام‌های کاربری از فایل و حذف خطوط خالی"""
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def write_to_file(filename, data):
    """نوشتن داده در فایل (با مدیریت خطا)"""
    try:
        with open(filename, "a", encoding="utf-8") as file:
            file.write(data + "\n")
    except Exception as e:
        print(f"⚠️ خطا در نوشتن در فایل {filename}: {e}")

def send_messages(clients, user_ids):
    """ارسال پیام‌ها به کاربران با مدیریت محدودیت‌های اینستاگرام"""
    total_sent = 0
    start_time = time.time()

    for i, user in enumerate(tqdm(user_ids, desc="📨 Sending Messages")):
        client_index = i % len(clients)  # تغییر تصادفی اکانت برای هر پیام
        cl = clients[client_index]

        try:
            # تأخیر تصادفی برای طبیعی‌تر شدن ارسال‌ها (2 تا 5 دقیقه)
            delay = random.uniform(120, 300)
            print(f"⏳ در انتظار {int(delay)} ثانیه قبل از ارسال پیام به {user}...")
            sys.stdout.flush()
            time.sleep(delay)

            # دریافت شناسه کاربری از نام کاربری
            try:
                user_id = cl.user_id_from_username(user)
                if not user_id:
                    raise ValueError("User ID is None")
            except Exception as e:
                error_msg = f"⚠️ خطا در دریافت شناسه‌ی {user}: {e}"
                print(error_msg)
                write_to_file("error_log.txt", error_msg)

                if "429" in str(e) or "Too Many Requests" in str(e):
                    write_to_file("429_users.txt", user)
                    sleep_time = random.uniform(1800, 2400)  # بین 30 تا 40 دقیقه توقف
                    print(f"🚨 اینستاگرام محدودیت اعمال کرده، توقف برای {int(sleep_time / 60)} دقیقه...")
                    sys.stdout.flush()
                    time.sleep(sleep_time)

                continue  # رد کردن این کاربر و رفتن به بعدی

            # پیام اول
            message = f"""
سلام {user}
یک فرصت لوکس برای چهره‌ای درخشان! ✨💖

جوان‌تر، شاداب‌تر، درخشان‌تر!
ما به شما تزریق رایگان جوانساز هدیه می‌دهیم! 🎁 کافیست ۱۰ نفر از دوستانتان را زیر آخرین پست پیج @drazamkhanzadeh تگ کنید و این پیشنهاد خاص را از آن خود کنید. 

💆‍♀️ زیبایی، لایق شماست! 💆‍♂️
زمان محدود است، پس همین حالا اقدام کنید. 📩
کلینیک زیبایی دکتر اعظم خانزاده 
جهت اطلاعات بیشتر میتوانید از طریق دایرکت و چت آنلاین پیج نیز اقدام نمایید 
@drazamkhanzadeh
https://drazamkhanzadeh.com/
"""

#             # پیام دوم
#             message2 = """کلینیک زیبایی دکتر اعظم خانزاده 
# جهت اطلاعات بیشتر میتوانید از طریق دایرکت و چت آنلاین پیج نیز اقدام نمایید 
# @drazamkhanzadeh
# https://drazamkhanzadeh.com/"""

            # ارسال پیام اول
            try:
                cl.direct_send(message, [user_id])
                print(f"✅ پیام اول به {user} ارسال شد.")
                sys.stdout.flush()
            except Exception as e:
                if "403" in str(e) or "Action Blocked" in str(e):
                    print(f"🚨 حساب {client_index} بلاک شد! توقف 45 تا 60 دقیقه...")
                    write_to_file("blocked_accounts.txt", f"Account {client_index} blocked.")
                    sleep_time = random.uniform(2700, 3600)  # بین 45 تا 60 دقیقه توقف
                    time.sleep(sleep_time)
                    continue  # عبور از این کاربر و رفتن به بعدی

            # تأخیر تصادفی بین پیام اول و دوم (30 تا 90 ثانیه)
            time.sleep(random.uniform(30, 90))

            # ارسال پیام دوم
            # try:
            #     cl.direct_send(message2, [user_id])
            #     print(f"✅ پیام دوم به {user} ارسال شد.")
            #     sys.stdout.flush()
            # except Exception as e:
            #     if "403" in str(e) or "Action Blocked" in str(e):
            #         print(f"🚨 حساب {client_index} بلاک شد! توقف 45 تا 60 دقیقه...")
            #         write_to_file("blocked_accounts.txt", f"Account {client_index} blocked.")
            #         sleep_time = random.uniform(2700, 3600)
            #         time.sleep(sleep_time)
            #         continue

            # ثبت نام کاربر در فایل ارسال‌شدگان
            write_to_file("senduser.txt", user)

            # حذف کاربر از لیست اصلی
            user_ids.remove(user)
            with open("followers.txt", "w", encoding="utf-8") as file:
                file.writelines("\n".join(user_ids))

            total_sent += 1

            # ذخیره وضعیت ارسال در JSON
            with open("status.json", "w", encoding="utf-8") as status_file:
                json.dump({"sent": total_sent, "remaining": len(user_ids)}, status_file)

            # گزارش هر ۱ ساعت
            if time.time() - start_time > 3600:
                write_to_file("report.txt", f"{total_sent} پیام در ۱ ساعت ارسال شد.")
                total_sent = 0
                start_time = time.time()

        except Exception as e:
            error_msg = f"⚠️ خطا در ارسال پیام به {user}: {e}"
            print(error_msg)
            write_to_file("error_log.txt", error_msg)

if __name__ == "__main__":
    user_ids = read_ids_from_file("followers.txt")
    time.sleep(random.uniform(10, 60))  # تأخیر اولیه برای طبیعی‌تر شدن رفتار
    clients = login_accounts()
    
    if clients:
        send_messages(clients, user_ids)
    else:
        print("❌ هیچ اکانتی لاگین نشد. بررسی کنید!")
