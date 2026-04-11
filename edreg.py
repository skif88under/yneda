import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- LOAD ENV ---
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
REG_URL = os.getenv("REG_URL")

if not TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# --- KEYBOARDS ---
def check_sub_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 Я подписался", callback_data="check_sub")
    return kb.as_markup()


def register_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(
        text="🚴 Регистрация",
        url=REG_URL
    )
    return kb.as_markup()


# --- CHECK SUB ---
async def is_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "creator", "administrator")
    except:
        return False


# --- START ---
@dp.message(CommandStart())
async def start(message: Message):
    text = (
        "🚴‍♂️ Работа курьером Яндекс Еда\n\n"
        "📌 Чтобы начать:\n"
        "1. Подпишись на канал\n"
        "2. Пройди регистрацию\n"
        "3. Начни получать заказы\n\n"
        "Нажми кнопку ниже 👇"
    )

    await message.answer(text, reply_markup=check_sub_keyboard())


# --- CHECK SUB CALLBACK ---
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await is_subscribed(user_id):
        await callback.message.answer(
            "✅ Подписка подтверждена!\n\n"
            "Теперь переходи к регистрации:",
            reply_markup=register_keyboard()
        )
    else:
        await callback.message.answer(
            "❌ Ты ещё не подписан на канал.\n"
            "Подпишись и нажми кнопку снова."
        )


# --- START BOT ---
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
