import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN", "8733278270:AAEZbRvV8fLQSPpX-4VcXhtYicBa7KWtjT4")
ADMIN_ID = 8051030380
MOVIES_FILE = "movies.json"

if os.path.exists(MOVIES_FILE):
    with open(MOVIES_FILE, "r") as f:
        try:
            movies = json.load(f)
        except Exception:
            movies = {}
else:
    movies = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Salom!\n\nKino kodini yuboring.\nMasalan: 7"
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Siz kino qo'sha olmaysiz.")
        return
    context.user_data["video_id"] = update.message.video.file_id
    await update.message.reply_text(
        "✅ Video qabul qilindi!\nEndi kino kodini yuboring. Masalan: 7"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.strip()
    
    if code.startswith("/"):
        return

    if update.effective_user.id == ADMIN_ID and "video_id" in context.user_data:
        video_id = context.user_data.pop("video_id")
        movies[code] = video_id
        with open(MOVIES_FILE, "w") as f:
            json.dump(movies, f)
        await update.message.reply_text(f"✅ Kino saqlandi! Kodu: {code}")
        return

    if code in movies:
        await update.message.reply_video(video=movies[code], caption=f"🍿 Kino kodi: {code}")
    else:
        await update.message.reply_text("❌ Bunday kodli kino topilmadi.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
  
