import telebot, os, json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

bot = telebot.TeleBot("8354040044:AAF4p0mQiXBX9-dlFnH-L6dC0W0DdeL7gPE")
ADMIN = 8365701342
CHANNEL_ID = "@welcome_rek"

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

# obuna tekshirish
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription(call: CallbackQuery):
    if is_subscribed(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Obuna tasdiqlandi!\n📥 Endi kodni kiriting...")
    else:
        text = "❌ Siz hali kanalga obuna bo‘lmadingiz!\n👉 Avval obuna bo‘ling!"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📥 Kanal", url="https://t.me/welcome_rek"),
            InlineKeyboardButton("🧑🏻‍💻 Admin", url="https://t.me/saric_mee")
        )
        markup.add(InlineKeyboardButton("✅ Obuna bo‘ldim", callback_data="check_sub"))
        bot.send_message(call.message.chat.id, text, reply_markup=markup)

# ADMIN kino/video qo‘shadi
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN)
def save_entry(m):
    if not m.text or not m.text.startswith("/add "): 
        return

    parts = m.text.split(maxsplit=2)  # 3 qism: /add, kod, nom
    if len(parts) < 3:
        bot.reply_to(m, "❌ Format: /add kod nomi")
        return

    code = parts[1]
    title = parts[2]

    movies[code] = {"title": title}
    json.dump(movies, open("movies.json", "w"), indent=2)

    bot.reply_to(m, f"✅ Saqlandi: {code}\n📌 {title}")

# ADMIN panel
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN)
def admin_panel(m):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Obunachilar soni", callback_data="show_subs"))
    bot.send_message(m.chat.id, "Admin panelga xush kelibsiz 👑", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "show_subs")
def show_subscribers(call: CallbackQuery):
    if call.from_user.id != ADMIN:
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz")
        return

    try:
        chat = bot.get_chat(CHANNEL_ID)
        members_count = chat.get_members_count()
        text = f"📊 Kanal: {CHANNEL_ID}\n👥 Umumiy obunachilar: {members_count}\n✅ Faol obunachilar: {members_count}"
        bot.send_message(call.message.chat.id, text)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xatolik: {str(e)}")

# foydalanuvchi kodi
@bot.message_handler(func=lambda m: True)
def get_movie(m):
    code = m.text.strip()
    if code in movies:
        bot.send_message(m.chat.id, movies[code]["title"])
    else:
        bot.reply_to(m, "❌ Kod topilmadi")

bot.infinity_polling()

