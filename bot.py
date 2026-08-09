import logging
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest

# ==================== SOZLAMALAR ====================
BOT_TOKEN = "8733278270:AAGOm869v7tgtd7LY1XPIN8MfRgR-JPT1JQ"

# Kanalingiz IDsi (masalan: -1001234567890) yoki username (masalan: "@kanalingiz_nomi")
CHANNEL_ID = "@kanalingiz_nomi" 

# Yopiq (zayavka) kanalingizga taklif havolasi (Invite Link)
CHANNEL_INVITE_LINK = "https://t.me/+SizningZayavkaLinkasiz"

# Kinolar bazasi: Code -> Telegram Video File ID
# Izoh: Kinolarni bir marta botga yuborib File ID'sini joylaysiz yoki xabar matnini berishingiz mumkin
MOVIES = {
    "3": "BAACAgIAAxkBAAE... (3-kino video_id)",  # Yoki shunchaki text / link
    "4": "BAACAgIAAxkBAAE... (4-kino video_id)"
}
# ===================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Obunani tekshirish tugmasi
def get_sub_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=CHANNEL_INVITE_LINK)],
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")]
        ]
    )
    return keyboard

# Obuna holatini tekshirish funksiyasi
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Obuna bo'lgan, admin yoki kanal egasi bo'lsa True
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception:
        # Agar kanal yopiq (zayavka) bo'lib, bot tekshira olmasa
        return True 

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    is_sub = await check_subscription(message.from_user.id)
    if not is_sub:
        await message.answer(
            "⚠️ **Botdan foydalanish uchun avval kanalimizga obuna bo'ling!**\n\n"
            "So'rov (zayavka) yuborganingizdan so'ng 'Obunani tekshirish' tugmasini bosing.",
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
        await callback.answer("❌ Hali kanalga obuna bo'lmadingiz yoki so'rov yubormadingiz!", show_alert=True)

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
        # Agar video file_id bo'lsa video yuboradi, aks holda matn
        if movie_data.startswith("BAAC") or movie_data.startswith("AgAC"):
            await message.answer_video(video=movie_data, caption=f"🍿 Kino kodi: {code}")
        else:
            await message.answer(f"🍿 Siz so'ragan kino:\n{movie_data}")
    else:
        await message.answer("❌ Bunday kodli kino topilmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
