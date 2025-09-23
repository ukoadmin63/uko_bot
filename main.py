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

# video yoki fayl saqlash
@bot.message_handler(content_types=['video','document'])
def save_video(m):
    if m.from_user.id != ADMIN: return
    if not m.caption or not m.caption.startswith("/add "): return
    code = m.caption.split()[1]
    f = m.video or m.document
    file = bot.get_file(f.file_id)
    data = bot.download_file(file.file_path)

    # Fayl extensionini olish (.mp4, .mkv, .zip va hokazo)
    ext = os.path.splitext(file.file_path)[1] or ".mp4"
    path = f"movies/{code}{ext}"

    with open(path, "wb") as v: 
        v.write(data)
    movies[code] = path
    json.dump(movies, open("movies.json", "w"))
    bot.reply_to(m, f"✅ Saqlandi: {code} ({path})")

# kod orqali video olish
@bot.message_handler(func=lambda m: True)
def get(m):
    code = m.text.strip()
    if code in movies and os.path.exists(movies[code]):
        with open(movies[code], 'rb') as v:
            try:
                bot.send_video(m.chat.id, v)
            except:
                # Agar video sifatida yuborilmasa → document sifatida yuboradi
                v.seek(0)
                bot.send_document(m.chat.id, v)
    else:
        bot.reply_to(m, "❌ Kod topilmadi")

bot.infinity_polling()

