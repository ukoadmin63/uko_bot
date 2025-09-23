import telebot, os, json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

bot = telebot.TeleBot("8354040044:AAF4p0mQiXBX9-dlFnH-L6dC0W0DdeL7gPE")
ADMIN = 7667567483
CHANNEL_ID = "@welcome_rek"  # kanal username sini yoz (bot admin bo‘lishi shart)

os.makedirs("movies", exist_ok=True)

try:
    movies = json.load(open("movies.json"))
except:
    movies = {}

# /start komandasi
@bot.message_handler(commands=['start'])
def welcome(m):
    text = (
        "👋🏻 Botga xush kelibsiz!\n"
        "✅ Ko’rsatilgan kanallarga obuna bo‘ling\n\n"
        "Quyidagi tugmalardan foydalaning 👇"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📥 Kanal", url="https://t.me/welcome_rek"),
        InlineKeyboardButton("🧑🏻‍💻 Admin", url="https://t.me/saric_mee")
    )
    markup.add(InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_sub"))
    bot.send_message(m.chat.id, text, reply_markup=markup)

# obuna tekshirish funksiyasi
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

# "Obuna bo‘ldim" tugmasi bosilganda
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call: CallbackQuery):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Obuna tasdiqlandi!\n📥 Endi kino kodini kiriting...")
    else:
        text = "❌ Siz hali kanalga obuna bo‘lmadingiz!\n👉 Avval obuna bo‘ling!"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📥 Kanal", url="https://t.me/welcome_rek"),
            InlineKeyboardButton("🧑🏻‍💻 Admin", url="https://t.me/saric_mee")
        )
        markup.add(InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_sub"))
        bot.send_message(call.message.chat.id, text, reply_markup=markup)

# video yoki fayl saqlash (/add kod izoh)
@bot.message_handler(content_types=['video','document'])
def save_video(m):
    if m.from_user.id != ADMIN: return
    if not m.caption or not m.caption.startswith("/add "): return

    parts = m.caption.split(maxsplit=2)
    if len(parts) < 2:
        bot.reply_to(m, "❌ Kodni yozmadingiz!")
        return

    code = parts[1]   # kod (masalan, 1)
    title = parts[2] if len(parts) > 2 else ""  # qo‘shimcha matn (agar bo‘lsa)

    f = m.video or m.document
    file = bot.get_file(f.file_id)
    data = bot.download_file(file.file_path)

    # Fayl extensionini olish (.mp4, .mkv, .zip va h.k.)
    ext = os.path.splitext(file.file_path)[1] or ".mp4"
    path = f"movies/{code}{ext}"

    with open(path, "wb") as v: 
        v.write(data)

    # JSON faylga kod + path + title saqlanadi
    movies[code] = {"path": path, "title": title}
    json.dump(movies, open("movies.json", "w"), indent=2)

    bot.reply_to(m, f"✅ Saqlandi: {code}\n📌 {title if title else 'Izoh yo‘q'}")

# kod orqali video olish
@bot.message_handler(func=lambda m: True)
def get(m):
    code = m.text.strip()
    if code in movies and os.path.exists(movies[code]["path"]):
        with open(movies[code]["path"], 'rb') as v:
            bot.send_video(m.chat.id, v, caption=movies[code]["title"])
    else:
        bot.reply_to(m, "❌ Kod topilmadi")

bot.infinity_polling()


