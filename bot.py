import json
import os
import http.server
import socketserver
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Render porti uchun
def start_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

threading.Thread(target=start_dummy_server, daemon=True).start()

# --- SOZLAMALAR ---
TOKEN = os.environ.get("BOT_TOKEN", "8733278270:AAHAgD29DvrxxQNNEoR5AOv7kE5VtYMBM")
ADMIN_ID = 8051030380

# Kanalingiz username'i (@ bering yoki username bo'lmasa ID yozing)
CHANNEL_USERNAME = "@lekxbrkfb"
CHANNEL_LINK = "https://t.me/lekxbrkfb"


MOVIES_FILE = "movies.json"

if os.path.exists(MOVIES_FILE):
    with open(MOVIES_FILE, "r") as f:
        try:
            movies = json.load(f)
        except Exception:
            movies = {}
else:
    movies = {}

# Obunani tekshirish funksiyasi
async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception:
        return True # Agar kanal sozlamalarida xatolik bo'lsa, foydalanuvchini bloklab qo'ymaslik uchun

# Obuna tugmasini chiqarish
def get_sub_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        await update.message.reply_text(
            "❌ **Botdan foydalanish uchun rasmiy kanalimizga a'zo bo'ling!**",
            reply_markup=get_sub_keyboard(),
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text("🎬 Salom!\n\nKino kodini yuboring.\nMasalan: 7")

async def check_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await check_subscription(user_id, context):
        await query.edit_message_text("✅ Rahmat! Endi kino kodini yuborishingiz mumkin.")
    else:
        await query.answer("❌ Siz hali kanalga a'zo bo'lmadingiz!", show_alert=True)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz kino qo'sha olmaysiz.")
        return
    context.user_data["video_id"] = update.message.video.file_id
    await update.message.reply_text("✅ Video qabul qilindi!\nEndi kino kodini yuboring. Masalan: 7")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    code = update.message.text.strip()
    
    if code.startswith("/"):
        return

    # Admin kino saqlayotgan bo'lsa
    if user_id == ADMIN_ID and "video_id" in context.user_data:
        video_id = context.user_data.pop("video_id")
        movies[code] = video_id
        with open(MOVIES_FILE, "w") as f:
            json.dump(movies, f)
        await update.message.reply_text(f"✅ Kino saqlandi! Kodu: {code}")
        return

    # Oddiy foydalanuvchilar uchun obunani tekshirish
    if not await check_subscription(user_id, context):
        await update.message.reply_text(
            "❌ **Kino olish uchun avval kanalimizga a'zo bo'ling!**",
            reply_markup=get_sub_keyboard(),
            parse_mode="Markdown"
        )
        return

    if code in movies:
        await update.message.reply_video(video=movies[code], caption=f"🍿 Kino kodi: {code}")
    else:
        await update.message.reply_text("❌ Bunday kodli kino topilmadi.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_button_callback, pattern="^check_sub$"))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
    
