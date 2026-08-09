import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== SOZLAMALAR ====================
# @BotFather'dan olgan YANGI tokeningizni tirnoq ichiga yozing:
BOT_TOKEN = "8733278270:AAGOm869v7tgtd7LY1XPIN8MfRgR-JPT1JQ"

# Skrinshotdagi kanalingiz ma'lumotlari:
CHANNEL_ID = "@lekxbrkfb"
CHANNEL_INVITE_LINK = "https://t.me/lekxbrkfb"

# Kinolar bazasi (Kod -> Video havola/ID yoki Matn)
MOVIES = {
    "3": "🍿 3-sonli kino tayyor! (Bu yerga videoni yuborasiz)",
    "4": "🍿 4-sonli kino tayyor!"
}
# ===================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Obuna tugmasi
def get_sub_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")]
        ]
    )
    return keyboard

# Obunani tekshirish
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception as e:
        print(f"Xatolik: {e}")
        return True 

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer(
            "⚠️ **Botdan foydalanish uchun avval kanalimizga obuna bo'ling!**\n\n"
            "Kanalga a'zo bo'lgach, **'Obunani tekshirish'** tugmasini bosing.",
            reply_markup=get_sub_keyboard(),
            parse_mode="Markdown"
        )
        return

    await message.answer("Xush kelibsiz! Kino kodini yuboring (masalan: 3)")

@dp.callback_query(F.data == "check_sub")
async def check_callback(callback: types.CallbackQuery):
    is_sub = await check_subscription(callback.from_user.id)
    if is_sub:
        await callback.message.delete()
        await callback.message.answer("✅ Obuna tasdiqlandi! Endi kino kodini yuborishingiz mumkin.")
    else:
        await callback.answer("❌ Hali kanalga obuna bo'lmadingiz!", show_alert=True)

@dp.message()
async def movie_handler(message: types.Message):
    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer(
            "⚠️ **Kino ko'rish uchun avval kanalga obuna bo'ling!**",
            reply_markup=get_sub_keyboard(),
            parse_mode="Markdown"
        )
        return

    code = message.text.strip().replace("/", "")
    if code in MOVIES:
        movie_data = MOVIES[code]
        if movie_data.startswith("BAAC") or movie_data.startswith("AgAC"):
            await message.answer_video(video=movie_data, caption=f"🍿 Kino kodi: {code}")
        else:
            await message.answer(f"🍿 Siz so'ragan kino ({code}):\n\n{movie_data}")
    else:
        await message.answer("❌ Bunday kodli kino topilmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
