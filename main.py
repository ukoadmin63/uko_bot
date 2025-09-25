import telebot
import json
import os

API_KEY = "8354040044:AAF4p0mQiXBX9-dlFnH-L6dC0W0DdeL7gPE"
bot = telebot.TeleBot(API_KEY)

# Admin ID
ADMIN = 7667567483  # o'zgartiring

# Kino fayllari saqlanadigan json
KINO_FILE = "movies.json"

# Agar json mavjud bo'lmasa yaratamiz
if not os.path.exists(KINO_FILE):
    with open(KINO_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

# Funktsiya: kino qo'shish
def add_kino(title, link):
    with open(KINO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.append({"title": title, "link": link})
    with open(KINO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Start komanda
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, f"Salom {msg.from_user.first_name}!\nKinoni raqam bilan olishingiz mumkin.\nMasalan: 1, 2, 3...")

# Admin /add komanda
@bot.message_handler(commands=["add"])
def add(msg):
    if msg.from_user.id != ADMIN:
        bot.send_message(msg.chat.id, "Siz admin emassiz!")
        return
    # format: /add Kino nomi | Kino linki
    try:
        text = msg.text.split("/add ",1)[1]
        title, link = text.split("|")
        title = title.strip()
        link = link.strip()
        add_kino(title, link)
        bot.send_message(msg.chat.id, f"Kino qo'shildi:\n{title}\n{link}")
    except:
        bot.send_message(msg.chat.id, "Xato format! Misol:\n/add Kino nomi | https://kino_link")

# Foydalanuvchi raqam yozganda
@bot.message_handler(func=lambda m: m.text.isdigit())
def send_kino(msg):
    index = int(msg.text) - 1  # 1 -> 0 indeksi
    with open(KINO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if index < 0 or index >= len(data):
        bot.send_message(msg.chat.id, f"Kinolar soni: {len(data)}. To'g'ri raqam kiriting!")
        return
    kino = data[index]
    bot.send_message(msg.chat.id, f"{kino['title']}\n{kino['link']}")

# Botni ishga tushirish
bot.polling(none_stop=True)
