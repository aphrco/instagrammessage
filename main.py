import time
import random
import json
from tqdm import tqdm
from login import login_accounts  # دریافت کلاینت‌ها از فایل login.py

def read_ids_from_file(filename):
    """خواندن نام‌های کاربری از فایل و حذف خطوط خالی"""
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]

def send_messages(clients, user_ids):
    """ارسال پیام‌ها به کاربران با تغییر تصادفی حساب کاربری و تأخیرات مختلف"""
    total_sent = 0
    start_time = time.time()

    for i, user in enumerate(tqdm(user_ids, desc="📨 Sending Messages")):
        client_index = i % len(clients)  # انتخاب اکانت متفاوت برای هر پیام
        cl = clients[client_index]

        try:
            # تأخیر تصادفی قبل از هر درخواست (2 تا 3 دقیقه)
            delay = random.uniform(120, 180)
            print(f"⏳ در انتظار {int(delay)} ثانیه قبل از ارسال پیام به {user}...")
            time.sleep(delay)

            # دریافت شناسه کاربری از نام کاربری (مدیریت خطا)
            try:
                user_id = cl.user_id_from_username(user)
                if not user_id:
                    raise ValueError("User ID is None")
            except Exception as e:
                print(f"⚠️ خطا در دریافت شناسه‌ی {user}: {e}")
                with open("error_log.txt", "a", encoding="utf-8") as error_file:
                    error_file.write(f"خطا در دریافت شناسه‌ی {user}: {e}\n")
                continue  # رد کردن این کاربر و رفتن به بعدی

            # پیام اول
            message = f"""
سلام {user}
یک فرصت لوکس برای چهره‌ای درخشان! ✨💖

جوان‌تر، شاداب‌تر، درخشان‌تر!
ما به شما تزریق رایگان جوانساز هدیه می‌دهیم! 🎁 کافیست ۱۰ نفر از دوستانتان را زیر اخرین پست پیج @drazamkhanzadeh  تگ کنید و این پیشنهاد خاص را از آن خود کنید. 

💆‍♀️ زیبایی، لایق شماست! 💆‍♂️
زمان محدود است، پس همین حالا اقدام کنید. 📩
"""
            # پیام دوم
            message2 = """کلینیک زیبایی دکتر اعظم خانزاده 
جهت اطلاعات بیشتر میتوانید از طریق دایرکت و چت آنلاین پیج نیز اقدام نمایید 
@drazamkhanzadeh
https://drazamkhanzadeh.com/"""

            # ارسال پیام اول
            cl.direct_send(message, [user_id])
            print(f"✅ پیام اول به {user} ارسال شد.")

            # تأخیر تصادفی بین پیام اول و دوم (30 تا 90 ثانیه)
            time.sleep(random.uniform(30, 90))

            # ارسال پیام دوم
            cl.direct_send(message2, [user_id])
            print(f"✅ پیام دوم به {user} ارسال شد.")

            # ثبت نام کاربر در فایل ارسال‌شدگان
            with open("senduser.txt", "a", encoding="utf-8") as send_file:
                send_file.write(f"{user}\n")

            total_sent += 1

            # ذخیره وضعیت ارسال در JSON
            with open("status.json", "w", encoding="utf-8") as status_file:
                json.dump({"sent": total_sent, "remaining": len(user_ids) - total_sent}, status_file)

            # گزارش هر ۱ ساعت
            if time.time() - start_time > 3600:
                with open("report.txt", "a", encoding="utf-8") as report_file:
                    report_file.write(f"{total_sent} پیام در ۱ ساعت ارسال شد.\n")
                total_sent = 0
                start_time = time.time()

        except Exception as e:
            # مدیریت خطاهای مربوط به محدودیت ارسال پیام
            print(f"⚠️ خطا در ارسال پیام به {user}: {e}")
            with open("error_log.txt", "a", encoding="utf-8") as error_file:
                error_file.write(f"خطا در ارسال پیام به {user}: {e}\n")

            # اگر خطا از نوع "Too Many Requests" بود، استراحت طولانی‌تر
            if "429" in str(e) or "Too Many Requests" in str(e):
                sleep_time = random.uniform(900, 1800)  # بین 15 تا 30 دقیقه
                print(f"🚨 اینستاگرام محدودیت اعمال کرده، توقف برای {int(sleep_time / 60)} دقیقه...")
                time.sleep(sleep_time)

if __name__ == "__main__":
    # خواندن لیست فالوورها
    user_ids = read_ids_from_file("followers.txt")
    
    # تأخیر تصادفی قبل از لاگین (برای طبیعی‌تر شدن رفتار)
    time.sleep(random.uniform(10, 60))
    
    # دریافت کلاینت‌ها
    clients = login_accounts()
    
    if clients:
        send_messages(clients, user_ids)
    else:
        print("❌ هیچ اکانتی لاگین نشد. بررسی کنید!")
